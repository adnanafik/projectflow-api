"""Common response schemas shared across endpoints."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str


class MessageResponse(BaseModel):
    """Standard message response body."""

    message: str
