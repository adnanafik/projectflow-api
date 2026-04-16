"""User management endpoints."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import ErrorResponse, MessageResponse
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
async def create_user(
    data: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Create a new user."""
    try:
        user = await user_service.create_user(db, data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(e)},
        )


@router.get("", response_model=UserListResponse)
async def list_users(db: AsyncSession = Depends(get_db)) -> UserListResponse:
    """List all users."""
    users = await user_service.list_users(db)
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users]
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_user(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get a user by ID."""
    user = await user_service.get_user(db, user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"User with id '{user_id}' not found"},
        )
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
async def update_user(
    user_id: uuid.UUID, data: UserUpdate, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Update a user."""
    try:
        user = await user_service.update_user(db, user_id, data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": error_msg},
            )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": error_msg},
        )


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    responses={404: {"model": ErrorResponse}},
)
async def delete_user(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Delete a user."""
    try:
        await user_service.delete_user(db, user_id)
        return MessageResponse(message="User deleted successfully")
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(e)},
        )


@router.get(
    "/{user_id}/tasks",
    response_model=List[dict],
    responses={404: {"model": ErrorResponse}},
)
async def get_user_tasks(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list:
    """Get all tasks assigned to a user."""
    user = await user_service.get_user(db, user_id)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"User with id '{user_id}' not found"},
        )
    # TODO: returns empty until Phase 4
    return []
