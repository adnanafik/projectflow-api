"""Tests for the health check endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_returns_200(client: AsyncClient) -> None:
    """GET /health returns 200 with status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_check_status_code(client: AsyncClient) -> None:
    """GET /health responds with HTTP status code 200."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check_response_body(client: AsyncClient) -> None:
    """GET /health response body equals {\"status\": \"ok\"}."""
    response = await client.get("/health")
    assert response.json() == {"status": "ok"}
