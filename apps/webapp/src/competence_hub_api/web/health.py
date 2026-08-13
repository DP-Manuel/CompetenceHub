from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def readiness(request: Request) -> JSONResponse:
    if request.app.state.readiness_probe():
        return JSONResponse({"status": "ready"})

    return JSONResponse(
        status_code=503,
        content={
            "type": "about:blank",
            "title": "Service nicht bereit",
            "status": 503,
            "code": "service_not_ready",
        },
        media_type="application/problem+json",
    )
