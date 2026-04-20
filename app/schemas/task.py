"""Task request/response schemas."""

import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    project_id: uuid.UUID
    assignee_id: Optional[uuid.UUID] = None
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = Field(None, min_length=1, max_length=20)
    priority: Optional[str] = Field(None, min_length=1, max_length=20)
    assignee_id: Optional[uuid.UUID] = None
    due_date: Optional[date] = None


class TaskResponse(BaseModel):
    """Schema for task response data."""

    id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    project_id: uuid.UUID
    assignee_id: Optional[uuid.UUID]
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Schema for a list of tasks."""

    tasks: List[TaskResponse]
