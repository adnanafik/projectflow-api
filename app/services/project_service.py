"""Project business logic."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


async def create_project(db: AsyncSession, data: ProjectCreate) -> Project:
    """Create a new project. Raises ValueError if owner not found."""
    result = await db.execute(select(User).where(User.id == data.owner_id))
    owner = result.scalar_one_or_none()
    if not owner:
        raise ValueError(f"User with id '{data.owner_id}' not found")

    project = Project(
        id=uuid.uuid4(),
        name=data.name,
        description=data.description,
        status="active",
        owner_id=data.owner_id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> Optional[Project]:
    """Get a project by ID. Returns None if not found."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def list_projects(db: AsyncSession) -> List[Project]:
    """List all non-archived projects."""
    result = await db.execute(
        select(Project)
        .where(Project.status != "archived")
        .order_by(Project.created_at)
    )
    return list(result.scalars().all())


async def update_project(
    db: AsyncSession, project_id: uuid.UUID, data: ProjectUpdate
) -> Project:
    """Update a project. Raises ValueError if not found."""
    project = await get_project(db, project_id)
    if not project:
        raise ValueError(f"Project with id '{project_id}' not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: uuid.UUID) -> bool:
    """Soft-delete a project by setting status to archived.
    Raises ValueError if not found.
    """
    project = await get_project(db, project_id)
    if not project:
        raise ValueError(f"Project with id '{project_id}' not found")

    project.status = "archived"
    await db.commit()
    await db.refresh(project)
    return True
