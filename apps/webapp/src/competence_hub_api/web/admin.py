import hmac
from typing import Literal

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from competence_hub_api.auth.account_lifecycle import (
    AccountLifecycleService,
    IdempotencyConflictError,
    InvitationConflictError,
    LifecycleQueued,
    LifecycleRateLimited,
)
from competence_hub_api.auth.login_service import normalize_email
from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token
from competence_hub_api.web.problems import problem_response

router = APIRouter(prefix="/api/v1/admin", tags=["administration"])
MAX_ADMIN_REQUEST_BYTES = 32 * 1024


class InvitationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=254)
    display_name: str = Field(min_length=1, max_length=200)
    role_codes: tuple[Literal["internal"], ...] = Field(min_length=1, max_length=1)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = normalize_email(value)
        if (
            "@" not in normalized
            or normalized.startswith("@")
            or normalized.endswith("@")
            or any(character.isspace() for character in normalized)
        ):
            raise ValueError("invalid email")
        return normalized


def _authentication_failed() -> Response:
    return problem_response(
        status=401,
        code="authentication_failed",
        title="Authentifizierung erforderlich",
    )


async def _read_invitation_request(request: Request) -> InvitationRequest | None:
    content_type = request.headers.get("content-type", "")
    if content_type.split(";", 1)[0].strip().casefold() != "application/json":
        return None
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_ADMIN_REQUEST_BYTES:
                return None
        except ValueError:
            return None
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > MAX_ADMIN_REQUEST_BYTES:
            return None
        body.extend(chunk)
    try:
        return InvitationRequest.model_validate_json(bytes(body))
    except ValidationError:
        return None


async def _admin_principal(request: Request) -> SessionPrincipal | Response:
    repository = request.app.state.session_repository
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if repository is None or token is None:
        return _authentication_failed()
    try:
        token_hash = digest_token(token)
    except ValueError:
        return _authentication_failed()
    principal = await repository.refresh_active_session(
        token_hash,
        now=request.app.state.clock(),
        idle_timeout=request.app.state.session_idle_timeout,
    )
    if principal is None:
        return _authentication_failed()
    if "admin" not in principal.roles:
        return problem_response(
            status=403,
            code="authorization_failed",
            title="Berechtigung nicht vorhanden",
        )
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
    return principal


@router.post("/users/invitations")
async def issue_user_invitation(request: Request) -> Response:
    service: AccountLifecycleService | None = request.app.state.account_lifecycle_service
    if service is None:
        return problem_response(
            status=503,
            code="authentication_unavailable",
            title="Anfrage derzeit nicht verfuegbar",
        )
    principal = await _admin_principal(request)
    if isinstance(principal, Response):
        return principal
    payload = await _read_invitation_request(request)
    idempotency_key = request.headers.get("idempotency-key", "")
    if payload is None or not idempotency_key:
        return problem_response(
            status=400,
            code="invalid_request",
            title="Anfrage ist ungueltig",
        )
    peer_ip = request.client.host if request.client is not None else "unavailable"
    try:
        outcome = await service.issue_invitation(
            actor=principal,
            email=payload.email,
            display_name=payload.display_name,
            role_codes=payload.role_codes,
            idempotency_key=idempotency_key,
            client_ip=peer_ip,
            now=request.app.state.clock(),
        )
    except ValueError:
        return problem_response(
            status=400,
            code="invalid_request",
            title="Anfrage ist ungueltig",
        )
    except IdempotencyConflictError:
        return problem_response(
            status=409,
            code="idempotency_conflict",
            title="Anfrage steht im Konflikt mit einer vorherigen Anfrage",
        )
    except InvitationConflictError:
        return problem_response(
            status=409,
            code="account_conflict",
            title="Einladung konnte nicht erstellt werden",
        )
    if isinstance(outcome, LifecycleRateLimited):
        response = problem_response(
            status=429,
            code="rate_limit_exceeded",
            title="Anfrage voruebergehend nicht moeglich",
        )
        response.headers["Retry-After"] = str(outcome.retry_after_seconds)
        return response
    if not isinstance(outcome, LifecycleQueued) or outcome.recipient_user_id is None:
        return problem_response(
            status=403,
            code="authorization_failed",
            title="Berechtigung nicht vorhanden",
        )
    response = JSONResponse(
        status_code=202,
        content={
            "status": "accepted",
            "user_id": str(outcome.recipient_user_id),
        },
    )
    if outcome.replayed:
        response.headers["Idempotent-Replay"] = "true"
    return response
