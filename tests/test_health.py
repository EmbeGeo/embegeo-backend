import pytest
from httpx import AsyncClient



@pytest.mark.asyncio
async def test_health_check_ok(client: AsyncClient):
    """
    Test that the health check endpoint returns an OK status when all dependencies are healthy.
    Note: This test assumes DB and Redis are reachable during test execution.
    In a real scenario, you might mock these dependencies.
    """
    response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["data"]["database"] == "connected"
    assert response.json()["data"]["redis"] == "connected"
    assert "timestamp" in response.json()["data"]


@pytest.mark.asyncio
async def test_health_check_service_unavailable(client: AsyncClient, mocker):
    """
    Test that the health check endpoint returns 503 if a dependency is down.
    Mocks database connection failure.
    """
    # Mocking a database connection error
    mocker.patch(
        "app.database.connection.async_engine.connect",
        side_effect=Exception("Mock DB connection error"),
    )

    response = await client.get("/api/health")

    assert response.status_code == 503
    assert response.json()["status"] == "error"
    assert "database" in response.json()["data"]
    assert "redis" in response.json()["data"]
    assert "timestamp" in response.json()["data"]
    assert "error" in response.json()["data"]["database"]  # Check for error message
