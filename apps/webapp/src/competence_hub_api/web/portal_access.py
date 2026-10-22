from fastapi import APIRouter, Request, Response

from competence_hub_api.web.auth import (
    enrollment_response,
    login_response,
    logout_response,
    session_csrf_response,
    session_response,
    verify_mfa_response,
)

router = APIRouter(prefix="/api/v1/portal/access", tags=["portal-access"])


@router.post("/login")
async def login(request: Request) -> Response:
    return await login_response(request, request.app.state.portal_login_service)


@router.post("/mfa/totp/enrollment")
async def enroll(request: Request) -> Response:
    return await enrollment_response(request, request.app.state.portal_mfa_service)


@router.post("/mfa/totp/enrollment/confirm")
async def confirm(request: Request) -> Response:
    return await verify_mfa_response(
        request, request.app.state.portal_mfa_service, method="confirm_totp_enrollment"
    )


@router.post("/mfa/totp/verify")
async def verify(request: Request) -> Response:
    return await verify_mfa_response(
        request, request.app.state.portal_mfa_service, method="verify_totp"
    )


@router.post("/mfa/recovery/verify")
async def recover(request: Request) -> Response:
    return await verify_mfa_response(
        request, request.app.state.portal_mfa_service, method="verify_recovery_code"
    )


@router.get("/session")
async def session(request: Request) -> Response:
    return await session_response(request, request.app.state.portal_session_repository)


@router.post("/session/csrf", status_code=204)
async def csrf(request: Request) -> Response:
    return await session_csrf_response(request, request.app.state.portal_session_repository)


@router.delete("/session", status_code=204)
async def logout(request: Request) -> Response:
    return await logout_response(request, request.app.state.portal_session_repository)
