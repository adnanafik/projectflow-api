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
    """POST /tasks accepts due_date and returns it in the response."""
    due = date.today() + timedelta(days=7)
    response = await client.post(
        "/tasks",
        json={
            "title": "Task with due date",
            "project_id": str(test_project.id),
            "due_date": due.isoformat(),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Task with due date"
    assert data["due_date"] == due.isoformat()


@pytest.mark.asyncio
async def test_create_task_without_due_date_defaults_to_null(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks without due_date returns null due_date."""
    response = await client.post(
        "/tasks",
        json={
            "title": "No due date",
            "project_id": str(test_project.id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["due_date"] is None


@pytest.mark.asyncio
async def test_create_task_with_explicit_null_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks with explicit null due_date is accepted."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Null due date",
            "project_id": str(test_project.id),
            "due_date": None,
        },
    )
    assert response.status_code == 201
    assert response.json()["due_date"] is None


@pytest.mark.asyncio
async def test_create_task_with_past_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks accepts a past due date (no validation rule)."""
    past = date.today() - timedelta(days=30)
    response = await client.post(
        "/tasks",
        json={
            "title": "Overdue Task",
            "project_id": str(test_project.id),
            "due_date": past.isoformat(),
        },
    )
    assert response.status_code == 201
    assert response.json()["due_date"] == past.isoformat()


@pytest.mark.asyncio
async def test_create_task_with_invalid_due_date_format_returns_422(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks with non-date string for due_date returns 422."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Bad date",
            "project_id": str(test_project.id),
            "due_date": "not-a-date",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_with_invalid_due_date_type_returns_422(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks with non-string type for due_date returns 422."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Bad date type",
            "project_id": str(test_project.id),
            "due_date": 12345,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_task_returns_due_date(
    client: AsyncClient, test_task: Task
) -> None:
    """GET /tasks/{id} includes due_date field."""
    response = await client.get(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    data = response.json()
    assert "due_date" in data


@pytest.mark.asyncio
async def test_list_tasks_returns_due_date(
    client: AsyncClient, test_task: Task
) -> None:
    """GET /tasks includes due_date field in listed tasks."""
    response = await client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) == 1
    assert "due_date" in tasks[0]


@pytest.mark.asyncio
async def test_update_task_set_due_date(
    client: AsyncClient, test_task: Task
) -> None:
    """PUT /tasks/{id} can set a due_date on an existing task."""
    due = date.today() + timedelta(days=14)
    response = await client.put(
        f"/tasks/{test_task.id}",
        json={"due_date": due.isoformat()},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["due_date"] == due.isoformat()
    assert data["title"] == test_task.title  # unchanged


@pytest.mark.asyncio
async def test_update_task_change_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """PUT /tasks/{id} can change an existing due_date."""
    initial = date.today() + timedelta(days=3)
    create_response = await client.post(
        "/tasks",
        json={
            "title": "Reschedule me",
            "project_id": str(test_project.id),
            "due_date": initial.isoformat(),
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    new_due = date.today() + timedelta(days=10)
    update_response = await client.put(
        f"/tasks/{task_id}",
        json={"due_date": new_due.isoformat()},
    )
    assert update_response.status_code == 200
    assert update_response.json()["due_date"] == new_due.isoformat()


@pytest.mark.asyncio
async def test_update_task_clear_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """PUT /tasks/{id} can clear the due_date by setting it to null."""
    due = date.today() + timedelta(days=5)
    create_response = await client.post(
        "/tasks",
        json={
            "title": "Clear me",
            "project_id": str(test_project.id),
            "due_date": due.isoformat(),
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    update_response = await client.put(
        f"/tasks/{task_id}",
        json={"due_date": None},
    )
    assert update_response.status_code == 200
    assert update_response.json()["due_date"] is None


@pytest.mark.asyncio
async def test_update_task_preserves_due_date_when_not_provided(
    client: AsyncClient, test_project: Project
) -> None:
    """PUT /tasks/{id} without due_date in payload preserves existing due_date."""
    due = date.today() + timedelta(days=5)
    create_response = await client.post(
        "/tasks",
        json={
            "title": "Keep date",
            "project_id": str(test_project.id),
            "due_date": due.isoformat(),
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    update_response = await client.put(
        f"/tasks/{task_id}",
        json={"title": "Renamed"},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Renamed"
    assert data["due_date"] == due.isoformat()


@pytest.mark.asyncio
async def test_update_task_with_invalid_due_date_returns_422(
    client: AsyncClient, test_task: Task
) -> None:
    """PUT /tasks/{id} with invalid due_date format returns 422."""
    response = await client.put(
        f"/tasks/{test_task.id}",
        json={"due_date": "31/12/2024"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_task_due_date_not_found_returns_404(
    client: AsyncClient,
) -> None:
    """PUT /tasks/{id} with unknown ID returns 404 even when updating due_date."""
    response = await client.put(
        f"/tasks/{uuid.uuid4()}",
        json={"due_date": date.today().isoformat()},
    )
    assert response.status_code == 404
