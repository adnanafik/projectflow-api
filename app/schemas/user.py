"""User request/response schemas."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    name: str = Field(..., min_length=1, max_length=100)
    # TODO: Validate that email is a proper email format using Pydantic's EmailStr.
    # Install pydantic[email] and replace the email field type.
    email: str = Field(..., min_length=1, max_length=255)


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=1, max_length=255)


class UserResponse(BaseModel):
    """Schema for user response data."""

    id: uuid.UUID
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Schema for a list of users."""

    users: List[UserResponse]
