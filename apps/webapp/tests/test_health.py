import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.main import create_app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_liveness_is_available_but_not_cacheable() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="https://test.invalid",
    ) as client:
        response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"


@pytest.mark.anyio
async def test_readiness_is_honest_until_dependencies_are_connected() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="https://test.invalid",
    ) as client:
        response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "service_not_ready"


@pytest.mark.anyio
async def test_readiness_can_be_supplied_by_the_runtime_adapter() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app(readiness_probe=lambda: True)),
        base_url="https://test.invalid",
    ) as client:
        response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
