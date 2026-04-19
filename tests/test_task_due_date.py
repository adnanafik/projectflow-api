"""Tests for the task due date feature.

Requirements under test:
- Tasks must support a due date field.
- Users must be able to set a due date when creating a task.
- Users must be able to edit the due date of an existing task.

Clarifications:
- Due date is optional (with default null/None) on creation.
- Date-only (no time-of-day).
- Overdue handling is visual-only (no state change enforced by backend).
"""

import uuid

import pytest
from httpx import AsyncClient

from app.models.project import Project
from app.models.task import Task


@pytest.mark.asyncio
async def test_create_task_with_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """A due date can be assigned to a task at creation."""
    payload = {
        "title": "Task with due date",
        "description": "Has a due date",
        "project_id": str(test_project.id),
        "due_date": "2025-12-31",
    }
    response = await client.post("/tasks", json=payload)
    assert response.status_code == 201, response.text
    body = response.json()
    assert "due_date" in body, "Response must include due_date field"
    assert body["due_date"] == "2025-12-31"


@pytest.mark.asyncio
async def test_create_task_without_due_date_is_allowed(
    client: AsyncClient, test_project: Project
) -> None:
    """Due date is optional on creation; omission yields null."""
    payload = {
        "title": "Task without due date",
        "project_id": str(test_project.id),
    }
    response = await client.post("/tasks", json=payload)
    assert response.status_code == 201, response.text
    body = response.json()
    assert "due_date" in body, "Response must include due_date field"
    assert body["due_date"] is None


@pytest.mark.asyncio
async def test_get_task_displays_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """The due date is displayed on the task when retrieved."""
    create_payload = {
        "title": "Display due date",
        "project_id": str(test_project.id),
        "due_date": "2026-01-15",
    }
    create_resp = await client.post("/tasks", json=create_payload)
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["due_date"] == "2026-01-15"


@pytest.mark.asyncio
async def test_list_tasks_includes_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """Tasks listed via the list endpoint include their due_date."""
    payload = {
        "title": "Listed task",
        "project_id": str(test_project.id),
        "due_date": "2025-06-01",
    }
    create_resp = await client.post("/tasks", json=payload)
    assert create_resp.status_code == 201

    list_resp = await client.get("/tasks")
    assert list_resp.status_code == 200
    tasks = list_resp.json()["tasks"]
    assert len(tasks) >= 1
    for t in tasks:
        assert "due_date" in t, "Each task in list must include due_date"
    matching = [t for t in tasks if t["title"] == "Listed task"]
    assert len(matching) == 1
    assert matching[0]["due_date"] == "2025-06-01"


@pytest.mark.asyncio
async def test_update_task_set_due_date(
    client: AsyncClient, test_task: Task
) -> None:
    """Users can set a due date on an existing task via update."""
    response = await client.put(
        f"/tasks/{test_task.id}", json={"due_date": "2025-11-20"}
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["due_date"] == "2025-11-20"


@pytest.mark.asyncio
async def test_update_task_change_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """Users can modify the due date of an existing task."""
    create_resp = await client.post(
        "/tasks",
        json={
            "title": "Change due date",
            "project_id": str(test_project.id),
            "due_date": "2025-01-01",
        },
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/tasks/{task_id}", json={"due_date": "2025-09-09"}
    )
    assert update_resp.status_code == 200, update_resp.text
    assert update_resp.json()["due_date"] == "2025-09-09"

    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["due_date"] == "2025-09-09"


@pytest.mark.asyncio
async def test_update_task_remove_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """Users can remove the due date by setting it to null."""
    create_resp = await client.post(
        "/tasks",
        json={
            "title": "Remove due date",
            "project_id": str(test_project.id),
            "due_date": "2025-05-05",
        },
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]
    assert create_resp.json()["due_date"] == "2025-05-05"

    update_resp = await client.put(
        f"/tasks/{task_id}", json={"due_date": None}
    )
    assert update_resp.status_code == 200, update_resp.text
    assert update_resp.json()["due_date"] is None

    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["due_date"] is None


@pytest.mark.asyncio
async def test_create_task_rejects_datetime_string_for_due_date(
    client: AsyncClient, test_project: Project
) -> None:
    """Due date is date-only; full ISO datetime strings must not be accepted as-is.

    The stored/returned value must be a pure date (YYYY-MM-DD), not a datetime.
    """
    payload = {
        "title": "Datetime rejection",
        "project_id": str(test_project.id),
        "due_date": "2025-12-31T23:59:59",
    }
    response = await client.post("/tasks", json=payload)
    # Either the API rejects the datetime string, or it coerces to a date-only value.
    if response.status_code == 201:
        body = response.json()
        assert body["due_date"] == "2025-12-31", (
            "due_date must be date-only (YYYY-MM-DD), not a datetime"
        )
    else:
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_invalid_due_date_format_rejected(
    client: AsyncClient, test_project: Project
) -> None:
    """Non-date strings for due_date should be rejected."""
    payload = {
        "title": "Bad date",
        "project_id": str(test_project.id),
        "due_date": "not-a-date",
    }
    response = await client.post("/tasks", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_past_due_date_does_not_change_status(
    client: AsyncClient, test_project: Project
) -> None:
    """Overdue handling is visual-only: backend does not mutate task status."""
    payload = {
        "title": "Overdue task",
        "project_id": str(test_project.id),
        "due_date": "2000-01-01",
    }
    create_resp = await client.post("/tasks", json=payload)
    assert create_resp.status_code == 201
    body = create_resp.json()
    # Status should remain the default 'todo' regardless of overdue due_date.
    assert body["status"] == "todo"
    assert body["due_date"] == "2000-01-01"

    task_id = body["id"]
    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "todo"
