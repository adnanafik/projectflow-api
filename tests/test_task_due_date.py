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
    """POST /tasks creates a task with due_date and returns 201."""
    due = date.today() + timedelta(days=7)
    response = await client.post(
        "/tasks",
        json={
            "title": "Task With Due Date",
            "project_id": str(test_project.id),
            "due_date": due.isoformat(),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Task With Due Date"
    assert data["due_date"] == due.isoformat()


@pytest.mark.asyncio
async def test_create_task_without_due_date_defaults_none(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks without due_date leaves it as null."""
    response = await client.post(
        "/tasks",
        json={
            "title": "No Due Date",
            "project_id": str(test_project.id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["due_date"] is None


@pytest.mark.asyncio
async def test_create_task_with_null_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks with explicit null due_date succeeds."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Null Due Date",
            "project_id": str(test_project.id),
            "due_date": None,
        },
    )
    assert response.status_code == 201
    assert response.json()["due_date"] is None


@pytest.mark.asyncio
async def test_create_task_with_invalid_due_date_returns_422(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks with malformed due_date returns 422."""
    response = await client.post(
        "/tasks",
        json={
            "title": "Bad Date",
            "project_id": str(test_project.id),
            "due_date": "not-a-date",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_with_past_due_date_allowed(
    client: AsyncClient, test_project: Project
) -> None:
    """POST /tasks accepts a past due_date (no business-rule restriction)."""
    past = date.today() - timedelta(days=30)
    response = await client.post(
        "/tasks",
        json={
            "title": "Past Due",
            "project_id": str(test_project.id),
            "due_date": past.isoformat(),
        },
    )
    assert response.status_code == 201
    assert response.json()["due_date"] == past.isoformat()


@pytest.mark.asyncio
async def test_get_task_includes_due_date(
    client: AsyncClient, test_task: Task
) -> None:
    """GET /tasks/{id} includes due_date in response."""
    response = await client.get(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    data = response.json()
    assert "due_date" in data


@pytest.mark.asyncio
async def test_list_tasks_includes_due_date(
    client: AsyncClient, test_task: Task
) -> None:
    """GET /tasks includes due_date in each task."""
    response = await client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) == 1
    assert "due_date" in tasks[0]


@pytest.mark.asyncio
async def test_update_task_set_due_date(
    client: AsyncClient, test_task: Task
) -> None:
    """PUT /tasks/{id} can set a due_date on a task."""
    due = date.today() + timedelta(days=14)
    response = await client.put(
        f"/tasks/{test_task.id}",
        json={"due_date": due.isoformat()},
    )
    assert response.status_code == 200
    assert response.json()["due_date"] == due.isoformat()


@pytest.mark.asyncio
async def test_update_task_change_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """PUT /tasks/{id} can change an existing due_date."""
    initial = date.today() + timedelta(days=3)
    create_response = await client.post(
        "/tasks",
        json={
            "title": "Changeable",
            "project_id": str(test_project.id),
            "due_date": initial.isoformat(),
        },
    )
    task_id = create_response.json()["id"]

    updated = date.today() + timedelta(days=10)
    response = await client.put(
        f"/tasks/{task_id}",
        json={"due_date": updated.isoformat()},
    )
    assert response.status_code == 200
    assert response.json()["due_date"] == updated.isoformat()


@pytest.mark.asyncio
async def test_update_task_clear_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """PUT /tasks/{id} can clear a due_date by setting null."""
    due = date.today() + timedelta(days=5)
    create_response = await client.post(
        "/tasks",
        json={
            "title": "Clearable",
            "project_id": str(test_project.id),
            "due_date": due.isoformat(),
        },
    )
    task_id = create_response.json()["id"]

    response = await client.put(
        f"/tasks/{task_id}",
        json={"due_date": None},
    )
    assert response.status_code == 200
    assert response.json()["due_date"] is None


@pytest.mark.asyncio
async def test_update_task_invalid_due_date_returns_422(
    client: AsyncClient, test_task: Task
) -> None:
    """PUT /tasks/{id} with invalid due_date returns 422."""
    response = await client.put(
        f"/tasks/{test_task.id}",
        json={"due_date": "2024-13-45"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_task_partial_preserves_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """PUT /tasks/{id} without due_date does not clear existing due_date."""
    due = date.today() + timedelta(days=8)
    create_response = await client.post(
        "/tasks",
        json={
            "title": "Preserve Due",
            "project_id": str(test_project.id),
            "due_date": due.isoformat(),
        },
    )
    task_id = create_response.json()["id"]

    response = await client.put(
        f"/tasks/{task_id}",
        json={"title": "Renamed"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Renamed"
    assert data["due_date"] == due.isoformat()
