"""Tests for the health check endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient) -> None:
    """GET /health returns a 200 status code."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_status_ok(client: AsyncClient) -> None:
    """GET /health returns a response body of {\"status\": \"ok\"}."""
    response = await client.get("/health")
    assert response.json() == {"status": "ok"}
