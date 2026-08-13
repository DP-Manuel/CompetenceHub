from collections.abc import Callable

from fastapi import FastAPI

from competence_hub_api.web.health import router as health_router
from competence_hub_api.web.middleware import SecurityHeadersMiddleware

ReadinessProbe = Callable[[], bool]


def create_app(readiness_probe: ReadinessProbe | None = None) -> FastAPI:
    app = FastAPI(
        title="Competence Hub API",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.readiness_probe = readiness_probe or (lambda: False)
    app.add_middleware(SecurityHeadersMiddleware)
    app.include_router(health_router)
    return app


app = create_app()
