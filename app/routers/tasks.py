"""Task management endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import ErrorResponse, MessageResponse
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}},
)
async def create_task(
    data: TaskCreate, db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """Create a new task."""
    try:
        task = await task_service.create_task(db, data)
        return TaskResponse.model_validate(task)
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(e)},
        )


# TODO: Add skip (int, default 0) and limit (int, default 20) query parameters
# and pass them to the service layer.
# TODO: Add ability to filter tasks.
@router.get("", response_model=TaskListResponse)
async def list_tasks(
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    """List all tasks."""
    tasks = await task_service.list_tasks(db)
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks]
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_task(
    task_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """Get a task by ID."""
    task = await task_service.get_task(db, task_id)
    if not task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Task with id '{task_id}' not found"},
        )
    return TaskResponse.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update a task."""
    try:
        task = await task_service.update_task(db, task_id, data)
        return TaskResponse.model_validate(task)
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(e)},
        )


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
    responses={404: {"model": ErrorResponse}},
)
async def delete_task(
    task_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Delete a task."""
    try:
        await task_service.delete_task(db, task_id)
        return MessageResponse(message="Task deleted successfully")
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(e)},
        )
