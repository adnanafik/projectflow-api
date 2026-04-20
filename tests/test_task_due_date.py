"""Tests for the task due date feature.

Requirement: Add a due date to tasks.
- Users should be able to set a due date when creating a task (optional).
- Users should be able to edit the due date of an existing task.
- Due dates should be stored and persisted with the task.
- Due dates are date-only (no time component).
- Due date field is optional.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.task import Task


@pytest.mark.asyncio
async def test_create_task_with_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """A due date can be supplied on task creation and is returned in the response."""
    payload = {
        "title": "Task with due date",
        "description": "Has a due date",
        "project_id": str(test_project.id),
        "due_date": "2025-12-31",
    }
    resp = await client.post("/tasks", json=payload)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "due_date" in body, "TaskResponse must include a due_date field"
    assert body["due_date"] == "2025-12-31"


@pytest.mark.asyncio
async def test_create_task_without_due_date_is_allowed(
    client: AsyncClient, test_project: Project
) -> None:
    """Due date is optional on creation."""
    payload = {
        "title": "Task without due date",
        "project_id": str(test_project.id),
    }
    resp = await client.post("/tasks", json=payload)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "due_date" in body, "TaskResponse must always include a due_date field"
    assert body["due_date"] is None


@pytest.mark.asyncio
async def test_create_task_with_null_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """Explicitly passing null as due_date is accepted."""
    payload = {
        "title": "Null due date",
        "project_id": str(test_project.id),
        "due_date": None,
    }
    resp = await client.post("/tasks", json=payload)
    assert resp.status_code == 201, resp.text
    assert resp.json()["due_date"] is None


@pytest.mark.asyncio
async def test_due_date_is_date_only_not_datetime(
    client: AsyncClient, test_project: Project
) -> None:
    """Due date is date-only; a full ISO datetime with time must be rejected."""
    payload = {
        "title": "Datetime due date",
        "project_id": str(test_project.id),
        "due_date": "2025-12-31T23:59:59",
    }
    resp = await client.post("/tasks", json=payload)
    assert resp.status_code == 422, (
        "Due date should be date-only; datetimes with time components "
        "must not be accepted."
    )


@pytest.mark.asyncio
async def test_create_task_invalid_due_date_format(
    client: AsyncClient, test_project: Project
) -> None:
    """Garbage due_date input is rejected with 422."""
    payload = {
        "title": "Bad date",
        "project_id": str(test_project.id),
        "due_date": "not-a-date",
    }
    resp = await client.post("/tasks", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_task_returns_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """The due date is persisted and returned when retrieving the task."""
    create_resp = await client.post(
        "/tasks",
        json={
            "title": "Persisted due date",
            "project_id": str(test_project.id),
            "due_date": "2026-01-15",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    task_id = create_resp.json()["id"]

    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["due_date"] == "2026-01-15"


@pytest.mark.asyncio
async def test_list_tasks_includes_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """Listed tasks include the due_date field."""
    await client.post(
        "/tasks",
        json={
            "title": "Listed task",
            "project_id": str(test_project.id),
            "due_date": "2027-03-10",
        },
    )
    resp = await client.get("/tasks")
    assert resp.status_code == 200
    tasks = resp.json()["tasks"]
    assert len(tasks) >= 1
    assert any(t.get("due_date") == "2027-03-10" for t in tasks)
    # All tasks expose a due_date key (even if None).
    for t in tasks:
        assert "due_date" in t


@pytest.mark.asyncio
async def test_update_task_set_due_date(
    client: AsyncClient, test_task: Task
) -> None:
    """Editing a task allows setting a due date on a task that had none."""
    resp = await client.put(
        f"/tasks/{test_task.id}",
        json={"due_date": "2025-08-20"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["due_date"] == "2025-08-20"

    # Persistence check via GET
    get_resp = await client.get(f"/tasks/{test_task.id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["due_date"] == "2025-08-20"


@pytest.mark.asyncio
async def test_update_task_change_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """Editing a task can change an existing due date."""
    create_resp = await client.post(
        "/tasks",
        json={
            "title": "To be updated",
            "project_id": str(test_project.id),
            "due_date": "2025-01-01",
        },
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/tasks/{task_id}",
        json={"due_date": "2025-06-30"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["due_date"] == "2025-06-30"

    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.json()["due_date"] == "2025-06-30"


@pytest.mark.asyncio
async def test_update_task_clear_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """Editing a task allows clearing the due date by passing null."""
    create_resp = await client.post(
        "/tasks",
        json={
            "title": "Clear me",
            "project_id": str(test_project.id),
            "due_date": "2025-05-05",
        },
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/tasks/{task_id}",
        json={"due_date": None},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["due_date"] is None

    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.json()["due_date"] is None


@pytest.mark.asyncio
async def test_update_task_without_touching_due_date_preserves_it(
    client: AsyncClient, test_project: Project
) -> None:
    """Partial updates that omit due_date must not erase it."""
    create_resp = await client.post(
        "/tasks",
        json={
            "title": "Preserve due date",
            "project_id": str(test_project.id),
            "due_date": "2025-09-09",
        },
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/tasks/{task_id}",
        json={"title": "New title only"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "New title only"
    assert update_resp.json()["due_date"] == "2025-09-09"

    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.json()["due_date"] == "2025-09-09"


@pytest.mark.asyncio
async def test_update_task_invalid_due_date_format(
    client: AsyncClient, test_task: Task
) -> None:
    """Invalid date strings are rejected during update."""
    resp = await client.put(
        f"/tasks/{test_task.id}",
        json={"due_date": "31-12-2025"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_task_due_date_rejects_datetime(
    client: AsyncClient, test_task: Task
) -> None:
    """Due date on update must be date-only."""
    resp = await client.put(
        f"/tasks/{test_task.id}",
        json={"due_date": "2025-12-31T10:00:00"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_due_date_persisted_in_database(
    client: AsyncClient, db_session: AsyncSession, test_project: Project
) -> None:
    """Verify the due date is actually stored in the database (not just echoed)."""
    resp = await client.post(
        "/tasks",
        json={
            "title": "DB persistence",
            "project_id": str(test_project.id),
            "due_date": "2030-07-04",
        },
    )
    assert resp.status_code == 201
    task_id = uuid.UUID(resp.json()["id"])

    task = await db_session.get(Task, task_id)
    assert task is not None
    assert hasattr(task, "due_date"), "Task model must have a due_date attribute"
    stored = task.due_date
    assert stored is not None
    # Accept either a date or a datetime-like with year/month/day matching.
    assert stored.year == 2030
    assert stored.month == 7
    assert stored.day == 4
