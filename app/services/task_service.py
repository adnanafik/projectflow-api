"""Task business logic."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, data: TaskCreate) -> Task:
    """Create a new task. Raises ValueError if project or assignee not found."""
    result = await db.execute(select(Project).where(Project.id == data.project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError(f"Project with id '{data.project_id}' not found")

    if data.assignee_id is not None:
        result = await db.execute(select(User).where(User.id == data.assignee_id))
        assignee = result.scalar_one_or_none()
        if not assignee:
            raise ValueError(f"User with id '{data.assignee_id}' not found")

    task = Task(
        id=uuid.uuid4(),
        title=data.title,
        description=data.description,
        status="todo",
        priority="medium",
        project_id=data.project_id,
        assignee_id=data.assignee_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: uuid.UUID) -> Optional[Task]:
    """Get a task by ID. Returns None if not found."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


# TODO: Add pagination support — accept skip (default 0) and limit (default 20)
# query parameters. Return paginated results instead of all records.
# TODO: Add ability to filter tasks.
async def list_tasks(db: AsyncSession) -> List[Task]:
    """List all tasks."""
    result = await db.execute(select(Task).order_by(Task.created_at))
    return list(result.scalars().all())


async def list_tasks_by_project(
    db: AsyncSession, project_id: uuid.UUID
) -> List[Task]:
    """List all tasks for a given project."""
    result = await db.execute(
        select(Task)
        .where(Task.project_id == project_id)
        .order_by(Task.created_at)
    )
    return list(result.scalars().all())


async def list_tasks_by_assignee(
    db: AsyncSession, assignee_id: uuid.UUID
) -> List[Task]:
    """List all tasks assigned to a given user."""
    result = await db.execute(
        select(Task)
        .where(Task.assignee_id == assignee_id)
        .order_by(Task.created_at)
    )
    return list(result.scalars().all())


async def update_task(
    db: AsyncSession, task_id: uuid.UUID, data: TaskUpdate
) -> Task:
    """Update a task. Raises ValueError if not found or assignee not found."""
    task = await get_task(db, task_id)
    if not task:
        raise ValueError(f"Task with id '{task_id}' not found")

    update_data = data.model_dump(exclude_unset=True)

    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        result = await db.execute(
            select(User).where(User.id == update_data["assignee_id"])
        )
        assignee = result.scalar_one_or_none()
        if not assignee:
            raise ValueError(
                f"User with id '{update_data['assignee_id']}' not found"
            )

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: uuid.UUID) -> bool:
    """Delete a task. Raises ValueError if not found."""
    task = await get_task(db, task_id)
    if not task:
        raise ValueError(f"Task with id '{task_id}' not found")

    await db.delete(task)
    await db.commit()
    return True
