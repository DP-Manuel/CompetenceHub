import hmac
from datetime import UTC, datetime, timedelta
from typing import Any, TypeVar

from fastapi import APIRouter, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from competence_hub_api.auth.login_service import (
    LOGIN_CHALLENGE_LIFETIME,
    LoginAccepted,
    LoginService,
    normalize_email,
)
from competence_hub_api.auth.account_lifecycle import (
    AccountLifecycleService,
    LifecycleAccepted,
    LifecycleRateLimited,
)
from competence_hub_api.auth.mfa_service import (
    MfaService,
    MfaSessionCreated,
    TotpEnrollmentCreated,
)
from competence_hub_api.auth.session_repository import (
    SessionPrincipal,
    SessionRepository,
)
from competence_hub_api.security.cookies import (
    LOGIN_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    clear_login_cookie,
    clear_session_cookie,
    set_login_cookie,
    set_session_cookie,
)
from competence_hub_api.security.email_addresses import is_single_email_address
from competence_hub_api.security.tokens import digest_token, issue_token
from competence_hub_api.security.passwords import PasswordPolicyError
from competence_hub_api.web.problems import problem_response

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
MAX_AUTH_REQUEST_BYTES = 32 * 1024


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = normalize_email(value)
        if not is_single_email_address(normalized):
            raise ValueError("invalid email")
        return normalized


class MfaCodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=64)


class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=254)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = normalize_email(value)
        if not is_single_email_address(normalized):
            raise ValueError("invalid email")
        return normalized


class TokenPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=128)


RequestModel = TypeVar("RequestModel", bound=BaseModel)


def _repository(request: Request) -> SessionRepository | None:
    return request.app.state.session_repository


def _login_service(request: Request) -> LoginService | None:
    return request.app.state.login_service


def _mfa_service(request: Request) -> MfaService | None:
    return request.app.state.mfa_service


def _account_lifecycle_service(request: Request) -> AccountLifecycleService | None:
    return request.app.state.account_lifecycle_service


def _now(request: Request) -> datetime:
    return request.app.state.clock()


def _session_digest(request: Request) -> bytes | None:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token is None:
        return None

    try:
        return digest_token(token)
    except ValueError:
        return None


def _session_payload(principal: SessionPrincipal) -> dict[str, Any]:
    return {
        "user": {
            "id": str(principal.user_id),
            "display_name": principal.display_name,
            "roles": list(principal.roles),
        },
        "authenticated_at": principal.authenticated_at,
        "idle_expires_at": principal.idle_expires_at,
        "absolute_expires_at": principal.absolute_expires_at,
    }


def _authentication_failed() -> Response:
    return problem_response(
        status=401,
        code="authentication_failed",
        title="Authentifizierung erforderlich",
    )


async def _read_json_request(
    request: Request,
    model: type[RequestModel],
) -> RequestModel | None:
    content_type = request.headers.get("content-type", "")
    if content_type.split(";", 1)[0].strip().casefold() != "application/json":
        return None

    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_AUTH_REQUEST_BYTES:
                return None
        except ValueError:
            return None

    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > MAX_AUTH_REQUEST_BYTES:
            return None
        body.extend(chunk)

    try:
        return model.model_validate_json(bytes(body))
    except ValidationError:
        return None


async def _read_login_request(request: Request) -> LoginRequest | None:
    return await _read_json_request(request, LoginRequest)


async def _read_mfa_code_request(request: Request) -> MfaCodeRequest | None:
    return await _read_json_request(request, MfaCodeRequest)


def _origin_is_valid(request: Request) -> bool:
    allowed_origin = request.app.state.allowed_origin
    return bool(
        allowed_origin is not None
        and request.headers.get("origin") == allowed_origin
    )


def _rate_limited_response(outcome: LifecycleRateLimited) -> Response:
    response = problem_response(
        status=429,
        code="rate_limit_exceeded",
        title="Anfrage voruebergehend nicht moeglich",
    )
    response.headers["Retry-After"] = str(outcome.retry_after_seconds)
    return response


def _pre_auth_context(request: Request) -> tuple[str, str] | Response:
    login_token = request.cookies.get(LOGIN_COOKIE_NAME)
    if login_token is None:
        return _authentication_failed()
    allowed_origin = request.app.state.allowed_origin
    csrf_token = request.headers.get("x-csrf-token")
    if (
        allowed_origin is None
        or request.headers.get("origin") != allowed_origin
        or csrf_token is None
    ):
        return problem_response(
            status=403,
            code="request_verification_failed",
            title="Anfrage konnte nicht verifiziert werden",
        )
    return login_token, csrf_token


def _mfa_outcome_response(outcome) -> Response:
    if outcome.status == "rate_limited":
        response = problem_response(
            status=429,
            code="rate_limit_exceeded",
            title="Authentifizierung voruebergehend nicht moeglich",
        )
        response.headers["Retry-After"] = str(outcome.retry_after_seconds)
        return response
    return _authentication_failed()


def _session_created_response(
    outcome: MfaSessionCreated,
    *,
    include_recovery_codes: bool,
) -> Response:
    if include_recovery_codes:
        response: Response = JSONResponse(
            status_code=200,
            content={"recovery_codes": list(outcome.recovery_codes)},
        )
    else:
        response = Response(status_code=204)
    clear_login_cookie(response)
    set_session_cookie(response, outcome.session_token)
    response.headers["X-CSRF-Token"] = outcome.csrf_token
    return response


@router.post("/login")
async def login(request: Request) -> Response:
    service = _login_service(request)
    if service is None:
        return problem_response(
            status=503,
            code="authentication_unavailable",
            title="Anmeldung derzeit nicht verfuegbar",
        )

    login_request = await _read_login_request(request)
    if login_request is None:
        return problem_response(
            status=400,
            code="invalid_request",
            title="Anfrage ist ungueltig",
        )

    peer_ip = request.client.host if request.client is not None else "unavailable"
    outcome = await service.authenticate(
        normalized_email=login_request.email,
        password=login_request.password,
        client_ip=peer_ip,
        now=_now(request),
    )

    if outcome.status == "rate_limited":
        response = problem_response(
            status=429,
            code="rate_limit_exceeded",
            title="Anmeldung voruebergehend nicht moeglich",
        )
        response.headers["Retry-After"] = str(outcome.retry_after_seconds)
        return response
    if outcome.status == "rejected":
        return problem_response(
            status=401,
            code="authentication_failed",
            title="Anmeldung nicht moeglich",
        )

    assert isinstance(outcome, LoginAccepted)
    response = JSONResponse(
        status_code=202,
        content={"state": outcome.state, "csrf_token": outcome.csrf_token},
    )
    set_login_cookie(
        response,
        outcome.login_token,
        max_age=int(LOGIN_CHALLENGE_LIFETIME.total_seconds()),
    )
    return response


@router.post("/password-reset/request", status_code=202)
async def request_password_reset(request: Request) -> Response:
    service = _account_lifecycle_service(request)
    if service is None:
        return problem_response(
            status=503,
            code="authentication_unavailable",
            title="Anfrage derzeit nicht verfuegbar",
        )
    if not _origin_is_valid(request):
        return problem_response(
            status=403,
            code="request_verification_failed",
            title="Anfrage konnte nicht verifiziert werden",
        )
    payload = await _read_json_request(request, PasswordResetRequest)
    if payload is None:
        return problem_response(
            status=400,
            code="invalid_request",
            title="Anfrage ist ungueltig",
        )
    peer_ip = request.client.host if request.client is not None else "unavailable"
    outcome = await service.request_password_reset(
        email=payload.email,
        client_ip=peer_ip,
        now=_now(request),
    )
    if isinstance(outcome, LifecycleRateLimited):
        return _rate_limited_response(outcome)
    return JSONResponse(status_code=202, content={"status": "accepted"})


@router.post("/password-reset/confirm")
async def confirm_password_reset(request: Request) -> Response:
    return await _complete_account_token(request, purpose="password_reset")


@router.post("/invitations/accept")
async def accept_invitation(request: Request) -> Response:
    return await _complete_account_token(request, purpose="invitation")


async def _complete_account_token(request: Request, *, purpose: str) -> Response:
    service = _account_lifecycle_service(request)
    if service is None:
        return problem_response(
            status=503,
            code="authentication_unavailable",
            title="Anfrage derzeit nicht verfuegbar",
        )
    if not _origin_is_valid(request):
        return problem_response(
            status=403,
            code="request_verification_failed",
            title="Anfrage konnte nicht verifiziert werden",
        )
    payload = await _read_json_request(request, TokenPasswordRequest)
    if payload is None:
        return problem_response(
            status=400,
            code="invalid_request",
            title="Anfrage ist ungueltig",
        )
    peer_ip = request.client.host if request.client is not None else "unavailable"
    try:
        if purpose == "invitation":
            outcome = await service.accept_invitation(
                token=payload.token,
                password=payload.password,
                client_ip=peer_ip,
                now=_now(request),
            )
        else:
            outcome = await service.confirm_password_reset(
                token=payload.token,
                password=payload.password,
                client_ip=peer_ip,
                now=_now(request),
            )
    except PasswordPolicyError:
        return problem_response(
            status=400,
            code="request_not_accepted",
            title="Anfrage konnte nicht angenommen werden",
        )
    if isinstance(outcome, LifecycleRateLimited):
        return _rate_limited_response(outcome)
    if not isinstance(outcome, LifecycleAccepted):
        return problem_response(
            status=400,
            code="request_not_accepted",
            title="Anfrage konnte nicht angenommen werden",
        )
    if purpose == "password_reset":
        response = Response(status_code=204)
        clear_login_cookie(response)
        clear_session_cookie(response)
        return response
    if outcome.login_token is None or outcome.csrf_token is None:
        return problem_response(
            status=503,
            code="authentication_unavailable",
            title="Anfrage derzeit nicht verfuegbar",
        )
    response = JSONResponse(
        status_code=202,
        content={
            "state": "mfa_enrollment_required",
            "csrf_token": outcome.csrf_token,
        },
    )
    clear_session_cookie(response)
    set_login_cookie(
        response,
        outcome.login_token,
        max_age=int(LOGIN_CHALLENGE_LIFETIME.total_seconds()),
    )
    return response


@router.post("/mfa/totp/enrollment")
async def start_totp_enrollment(request: Request) -> Response:
    service = _mfa_service(request)
    if service is None:
        return problem_response(
            status=503,
            code="authentication_unavailable",
            title="Authentifizierung derzeit nicht verfuegbar",
        )
    context = _pre_auth_context(request)
    if isinstance(context, Response):
        return context
    login_token, csrf_token = context
    outcome = await service.start_totp_enrollment(
        login_token=login_token,
        csrf_token=csrf_token,
        now=_now(request),
    )
    if outcome.status != "enrollment_created":
        return _mfa_outcome_response(outcome)
    assert isinstance(outcome, TotpEnrollmentCreated)
    return JSONResponse(
        status_code=201,
        content={"provisioning_uri": outcome.provisioning_uri},
    )


@router.post("/mfa/totp/enrollment/confirm")
async def confirm_totp_enrollment(request: Request) -> Response:
    return await _verify_mfa_code(request, method="confirm_totp_enrollment")


@router.post("/mfa/totp/verify")
async def verify_totp_code(request: Request) -> Response:
    return await _verify_mfa_code(request, method="verify_totp")


@router.post("/mfa/recovery/verify")
async def verify_recovery_code(request: Request) -> Response:
    return await _verify_mfa_code(request, method="verify_recovery_code")


async def _verify_mfa_code(request: Request, *, method: str) -> Response:
    service = _mfa_service(request)
    if service is None:
        return problem_response(
            status=503,
            code="authentication_unavailable",
            title="Authentifizierung derzeit nicht verfuegbar",
        )
    context = _pre_auth_context(request)
    if isinstance(context, Response):
        return context
    code_request = await _read_mfa_code_request(request)
    if code_request is None:
        return problem_response(
            status=400,
            code="invalid_request",
            title="Anfrage ist ungueltig",
        )
    login_token, csrf_token = context
    peer_ip = request.client.host if request.client is not None else "unavailable"
    verifier = getattr(service, method)
    outcome = await verifier(
        login_token=login_token,
        csrf_token=csrf_token,
        code=code_request.code,
        client_ip=peer_ip,
        now=_now(request),
    )
    if outcome.status != "session_created":
        return _mfa_outcome_response(outcome)
    assert isinstance(outcome, MfaSessionCreated)
    return _session_created_response(
        outcome,
        include_recovery_codes=method == "confirm_totp_enrollment",
    )


@router.get("/session")
async def get_session(request: Request) -> Response:
    repository = _repository(request)
    token_hash = _session_digest(request)
    if repository is None or token_hash is None:
        return _authentication_failed()

    principal = await repository.refresh_active_session(
        token_hash,
        now=_now(request),
        idle_timeout=request.app.state.session_idle_timeout,
    )
    if principal is None:
        return _authentication_failed()

    return JSONResponse(jsonable_encoder(_session_payload(principal)))


@router.post("/session/csrf", status_code=204)
async def rotate_session_csrf(request: Request) -> Response:
    repository = _repository(request)
    token_hash = _session_digest(request)
    if repository is None or token_hash is None:
        return _authentication_failed()
    if not _origin_is_valid(request):
        return problem_response(
            status=403,
            code="request_verification_failed",
            title="Anfrage konnte nicht verifiziert werden",
        )

    csrf_token = issue_token()
    principal = await repository.rotate_active_session_csrf(
        token_hash,
        csrf_token_hash=csrf_token.digest,
        now=_now(request),
        idle_timeout=request.app.state.session_idle_timeout,
    )
    if principal is None:
        return _authentication_failed()

    response = Response(status_code=204)
    response.headers["X-CSRF-Token"] = csrf_token.plaintext
    return response


@router.delete("/session", status_code=204)
async def delete_session(request: Request) -> Response:
    response = Response(status_code=204)
    repository = _repository(request)
    token_hash = _session_digest(request)
    if repository is None or token_hash is None:
        clear_session_cookie(response)
        return response

    now = _now(request)
    principal = await repository.find_active_session(token_hash, now=now)
    if principal is None:
        clear_session_cookie(response)
        return response

    allowed_origin = request.app.state.allowed_origin
    if allowed_origin is None or request.headers.get("origin") != allowed_origin:
        return problem_response(
            status=403,
            code="request_verification_failed",
            title="Anfrage konnte nicht verifiziert werden",
        )

    csrf_token = request.headers.get("x-csrf-token")
    if csrf_token is None:
        return problem_response(
            status=403,
            code="request_verification_failed",
            title="Anfrage konnte nicht verifiziert werden",
        )

    try:
        csrf_matches = hmac.compare_digest(
            digest_token(csrf_token),
            principal.csrf_token_hash,
        )
    except ValueError:
        csrf_matches = False

    if not csrf_matches:
        return problem_response(
            status=403,
            code="request_verification_failed",
            title="Anfrage konnte nicht verifiziert werden",
        )

    await repository.revoke_session(
        token_hash,
        now=now,
        reason="user_logout",
    )
    clear_session_cookie(response)
    return response


def utc_now() -> datetime:
    return datetime.now(UTC)


DEFAULT_SESSION_IDLE_TIMEOUT = timedelta(minutes=30)
