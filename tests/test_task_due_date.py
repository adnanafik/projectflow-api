"""Tests for task due_date field."""

import uuid
from datetime import date, timedelta

import pytest
from httpx import AsyncClient

from app.models.project import Project
from app.models.task import Task
from app.models.user import User


@pytest.mark.asyncio
async def test_create_task_with_due_date_success(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks creates a task with an explicit due_date."""
    due = (date.today() + timedelta(days=7)).isoformat()
    response = await client.post(
        "/tasks",
        json={
            "title": "Task With Due Date",
            "project_id": str(test_project.id),
            "due_date": due,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["due_date"] == due


@pytest.mark.asyncio
async def test_create_task_without_due_date_defaults_to_today(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks without due_date defaults due_date to today."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Task Default Due Date",
            "project_id": str(test_project.id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["due_date"] == date.today().isoformat()


@pytest.mark.asyncio
async def test_create_task_with_past_due_date_success(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks allows a past due_date."""
    past = (date.today() - timedelta(days=3)).isoformat()
    response = await client.post(
        "/tasks",
        json={
            "title": "Past Due Task",
            "project_id": str(test_project.id),
            "due_date": past,
        },
    )
    assert response.status_code == 201
    assert response.json()["due_date"] == past


@pytest.mark.asyncio
async def test_create_task_with_invalid_due_date_returns_422(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks with malformed due_date returns 422."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Bad Due Date",
            "project_id": str(test_project.id),
            "due_date": "not-a-date",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_with_null_due_date_defaults_to_today(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks with explicit null due_date defaults to today."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Null Due Date",
            "project_id": str(test_project.id),
            "due_date": None,
        },
    )
    assert response.status_code == 201
    assert response.json()["due_date"] == date.today().isoformat()


@pytest.mark.asyncio
async def test_get_task_includes_due_date(
    client: AsyncClient, test_task: Task
) -> None:
    """GET /tasks/{id} response contains a due_date field."""
    response = await client.get(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    data = response.json()
    assert "due_date" in data
    assert data["due_date"] is not None


@pytest.mark.asyncio
async def test_list_tasks_includes_due_date(
    client: AsyncClient, test_task: Task
) -> None:
    """GET /tasks response items include due_date."""
    response = await client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) == 1
    assert "due_date" in tasks[0]
    assert tasks[0]["due_date"] is not None


@pytest.mark.asyncio
async def test_update_task_due_date_success(
    client: AsyncClient, test_task: Task
) -> None:
    """PUT /tasks/{id} updates due_date."""
    new_due = (date.today() + timedelta(days=14)).isoformat()
    response = await client.put(
        f"/tasks/{test_task.id}",
        json={"due_date": new_due},
    )
    assert response.status_code == 200
    assert response.json()["due_date"] == new_due


@pytest.mark.asyncio
async def test_update_task_due_date_does_not_change_other_fields(
    client: AsyncClient, test_task: Task
) -> None:
    """PUT /tasks/{id} with only due_date leaves other fields unchanged."""
    new_due = (date.today() + timedelta(days=2)).isoformat()
    response = await client.put(
        f"/tasks/{test_task.id}",
        json={"due_date": new_due},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["due_date"] == new_due
    assert data["title"] == test_task.title
    assert data["status"] == test_task.status


@pytest.mark.asyncio
async def test_update_task_with_invalid_due_date_returns_422(
    client: AsyncClient, test_task: Task
) -> None:
    """PUT /tasks/{id} with malformed due_date returns 422."""
    response = await client.put(
        f"/tasks/{test_task.id}",
        json={"due_date": "2024-13-45"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_task_without_due_date_preserves_existing(
    client: AsyncClient, test_project: Project
) -> None:
    """PUT /tasks/{id} without due_date leaves existing due_date untouched."""
    original_due = (date.today() + timedelta(days=5)).isoformat()
    create_resp = await client.post(
        "/tasks",
        json={
            "title": "Keep Due Date",
            "project_id": str(test_project.id),
            "due_date": original_due,
        },
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/tasks/{task_id}",
        json={"title": "Renamed Task"},
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["title"] == "Renamed Task"
    assert data["due_date"] == original_due


@pytest.mark.asyncio
async def test_get_project_tasks_includes_due_date(
    client: AsyncClient, test_project: Project, test_task: Task
) -> None:
    """GET /projects/{id}/tasks items include due_date."""
    response = await client.get(f"/projects/{test_project.id}/tasks")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) == 1
    assert "due_date" in tasks[0]


@pytest.mark.asyncio
async def test_get_user_tasks_includes_due_date(
    client: AsyncClient, test_user: User, test_task: Task
) -> None:
    """GET /users/{id}/tasks items include due_date."""
    response = await client.get(f"/users/{test_user.id}/tasks")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) == 1
    assert "due_date" in tasks[0]


@pytest.mark.asyncio
async def test_create_task_preserves_due_date_on_retrieval(
    client: AsyncClient, test_project: Project
) -> None:
    """A task's due_date persists and is returned on subsequent GET."""
    due = (date.today() + timedelta(days=10)).isoformat()
    create_resp = await client.post(
        "/tasks",
        json={
            "title": "Persisted Due Date",
            "project_id": str(test_project.id),
            "due_date": due,
        },
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["due_date"] == due
