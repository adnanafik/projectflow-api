"""User business logic."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """Create a new user. Raises ValueError if email already exists."""
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise ValueError(f"User with email '{data.email}' already exists")

    user = User(
        id=uuid.uuid4(),
        name=data.name,
        email=data.email,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Get a user by ID. Returns None if not found."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email. Returns None if not found."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession) -> List[User]:
    """List all users."""
    result = await db.execute(select(User).order_by(User.created_at))
    return list(result.scalars().all())


async def update_user(
    db: AsyncSession, user_id: uuid.UUID, data: UserUpdate
) -> User:
    """Update a user. Raises ValueError if not found or email taken."""
    user = await get_user(db, user_id)
    if not user:
        raise ValueError(f"User with id '{user_id}' not found")

    if data.email is not None and data.email != user.email:
        existing = await get_user_by_email(db, data.email)
        if existing:
            raise ValueError(f"User with email '{data.email}' already exists")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """Delete a user. Returns True if deleted, raises ValueError if not found."""
    user = await get_user(db, user_id)
    if not user:
        raise ValueError(f"User with id '{user_id}' not found")

    await db.delete(user)
    await db.commit()
    return True
