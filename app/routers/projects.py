"""Project management endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import ErrorResponse, MessageResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.schemas.task import TaskListResponse, TaskResponse
from app.services import project_service, task_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}},
)
async def create_project(
    data: ProjectCreate, db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Create a new project."""
    try:
        project = await project_service.create_project(db, data)
        return ProjectResponse.model_validate(project)
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(e)},
        )


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    """List all non-archived projects."""
    projects = await project_service.list_projects(db)
    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects]
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_project(
    project_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Get a project by ID."""
    project = await project_service.get_project(db, project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Project with id '{project_id}' not found"},
        )
    return ProjectResponse.model_validate(project)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    responses={404: {"model": ErrorResponse}},
)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Update a project."""
    try:
        project = await project_service.update_project(db, project_id, data)
        return ProjectResponse.model_validate(project)
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(e)},
        )


@router.delete(
    "/{project_id}",
    response_model=MessageResponse,
    responses={404: {"model": ErrorResponse}},
)
async def delete_project(
    project_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Soft-delete a project (set status to archived)."""
    try:
        await project_service.delete_project(db, project_id)
        return MessageResponse(message="Project archived successfully")
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(e)},
        )


@router.get(
    "/{project_id}/tasks",
    response_model=TaskListResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_project_tasks(
    project_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> TaskListResponse:
    """Get all tasks in a project."""
    project = await project_service.get_project(db, project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Project with id '{project_id}' not found"},
        )
    tasks = await task_service.list_tasks_by_project(db, project_id)
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks]
    )
