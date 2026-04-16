"""Tests for user management endpoints."""

import uuid

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient) -> None:
    """POST /users creates a user and returns 201."""
    response = await client.post(
        "/users",
        json={"name": "Alice", "email": "alice@example.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email_returns_409(
    client: AsyncClient, test_user: User
) -> None:
    """POST /users with duplicate email returns 409."""
    response = await client.post(
        "/users",
        json={"name": "Duplicate", "email": test_user.email},
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_user_missing_required_fields_returns_422(
    client: AsyncClient,
) -> None:
    """POST /users without required fields returns 422."""
    response = await client.post("/users", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_user_success(client: AsyncClient, test_user: User) -> None:
    """GET /users/{id} returns the user."""
    response = await client.get(f"/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["name"] == test_user.name


@pytest.mark.asyncio
async def test_get_user_not_found_returns_404(client: AsyncClient) -> None:
    """GET /users/{id} with unknown ID returns 404."""
    response = await client.get(f"/users/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_users_empty(client: AsyncClient) -> None:
    """GET /users with no users returns empty list."""
    response = await client.get("/users")
    assert response.status_code == 200
    assert response.json()["users"] == []


@pytest.mark.asyncio
async def test_list_users_with_records(
    client: AsyncClient, test_user: User
) -> None:
    """GET /users returns all users."""
    response = await client.get("/users")
    assert response.status_code == 200
    users = response.json()["users"]
    assert len(users) == 1
    assert users[0]["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_update_user_success(
    client: AsyncClient, test_user: User
) -> None:
    """PUT /users/{id} updates and returns the user."""
    response = await client.put(
        f"/users/{test_user.id}",
        json={"name": "Updated Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_user_not_found_returns_404(client: AsyncClient) -> None:
    """PUT /users/{id} with unknown ID returns 404."""
    response = await client.put(
        f"/users/{uuid.uuid4()}",
        json={"name": "Ghost"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user_duplicate_email_returns_409(
    client: AsyncClient, test_user: User
) -> None:
    """PUT /users/{id} with taken email returns 409."""
    # Create a second user
    await client.post(
        "/users",
        json={"name": "Other", "email": "other@example.com"},
    )
    # Try to update test_user's email to the second user's email
    response = await client.put(
        f"/users/{test_user.id}",
        json={"email": "other@example.com"},
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_user_success(
    client: AsyncClient, test_user: User
) -> None:
    """DELETE /users/{id} deletes the user and returns message."""
    response = await client.delete(f"/users/{test_user.id}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()

    # Verify user is gone
    get_response = await client.get(f"/users/{test_user.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_not_found_returns_404(client: AsyncClient) -> None:
    """DELETE /users/{id} with unknown ID returns 404."""
    response = await client.delete(f"/users/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_tasks_returns_empty_list(
    client: AsyncClient, test_user: User
) -> None:
    """GET /users/{id}/tasks returns empty list when no tasks assigned."""
    response = await client.get(f"/users/{test_user.id}/tasks")
    assert response.status_code == 200
    assert response.json()["tasks"] == []
