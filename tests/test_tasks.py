"""Tests for task management endpoints."""

import uuid

import pytest
from httpx import AsyncClient

from app.models.project import Project
from app.models.task import Task
from app.models.user import User


@pytest.mark.asyncio
async def test_create_task_with_assignee_success(
    client: AsyncClient, test_project: Project, test_user: User
) -> None:
    """POST /tasks creates a task with assignee and returns 201."""
    response = await client.post(
        "/tasks",
        json={
            "title": "New Task",
            "description": "A new task",
            "project_id": str(test_project.id),
            "assignee_id": str(test_user.id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["description"] == "A new task"
    assert data["status"] == "todo"
    assert data["priority"] == "medium"
    assert data["project_id"] == str(test_project.id)
    assert data["assignee_id"] == str(test_user.id)
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_task_without_assignee_success(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks creates a task without assignee and returns 201."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Unassigned Task",
            "project_id": str(test_project.id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Unassigned Task"
    assert data["assignee_id"] is None


@pytest.mark.asyncio
async def test_create_task_invalid_project_returns_404(
    client: AsyncClient,
) -> None:
    """POST /tasks with non-existent project returns 404."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Orphan Task",
            "project_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_task_invalid_assignee_returns_404(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks with non-existent assignee returns 404."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Bad Assignee Task",
            "project_id": str(test_project.id),
            "assignee_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_task_missing_fields_returns_422(
    client: AsyncClient,
) -> None:
    """POST /tasks without required fields returns 422."""
    response = await client.post("/tasks", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_tasks_empty(client: AsyncClient) -> None:
    """GET /tasks with no tasks returns empty list."""
    response = await client.get("/tasks")
    assert response.status_code == 200
    assert response.json()["tasks"] == []


@pytest.mark.asyncio
async def test_list_tasks_with_records(
    client: AsyncClient, test_task: Task
) -> None:
    """GET /tasks returns all tasks."""
    response = await client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["id"] == str(test_task.id)


@pytest.mark.asyncio
async def test_get_task_success(
    client: AsyncClient, test_task: Task
) -> None:
    """GET /tasks/{id} returns the task."""
    response = await client.get(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_task.id)
    assert data["title"] == test_task.title


@pytest.mark.asyncio
async def test_get_task_not_found_returns_404(
    client: AsyncClient,
) -> None:
    """GET /tasks/{id} with unknown ID returns 404."""
    response = await client.get(f"/tasks/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task_success(
    client: AsyncClient, test_task: Task
) -> None:
    """PUT /tasks/{id} updates and returns the task."""
    response = await client.put(
        f"/tasks/{test_task.id}",
        json={"title": "Updated Task"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"


@pytest.mark.asyncio
async def test_update_task_not_found_returns_404(
    client: AsyncClient,
) -> None:
    """PUT /tasks/{id} with unknown ID returns 404."""
    response = await client.put(
        f"/tasks/{uuid.uuid4()}",
        json={"title": "Ghost"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task_partial(
    client: AsyncClient, test_task: Task
) -> None:
    """PUT /tasks/{id} with partial data only updates provided fields."""
    response = await client.put(
        f"/tasks/{test_task.id}",
        json={"status": "in_progress"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["title"] == test_task.title  # unchanged


@pytest.mark.asyncio
async def test_delete_task_success(
    client: AsyncClient, test_task: Task
) -> None:
    """DELETE /tasks/{id} deletes the task and returns message."""
    response = await client.delete(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()

    # Verify task is gone
    get_response = await client.get(f"/tasks/{test_task.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_not_found_returns_404(
    client: AsyncClient,
) -> None:
    """DELETE /tasks/{id} with unknown ID returns 404."""
    response = await client.delete(f"/tasks/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_project_tasks(
    client: AsyncClient, test_project: Project, test_task: Task
) -> None:
    """GET /projects/{id}/tasks returns tasks for the project."""
    response = await client.get(f"/projects/{test_project.id}/tasks")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["id"] == str(test_task.id)


@pytest.mark.asyncio
async def test_get_user_tasks(
    client: AsyncClient, test_user: User, test_task: Task
) -> None:
    """GET /users/{id}/tasks returns tasks assigned to the user."""
    response = await client.get(f"/users/{test_user.id}/tasks")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["id"] == str(test_task.id)
