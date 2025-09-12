from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    """Response schema for getting user's account."""
    id: int = Field(..., example=10)
    user_id: int = Field(..., example=100)
    balance: float = Field(..., example=1000.67)
    created_at: datetime = Field(..., example="2025-09-08T12:00:28.375614Z")
    updated_at: Optional[datetime] = Field(None, example="2025-09-08T12:00:28.375614Z")

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    """Response schema for successful getting list of authorized user's accounts."""

    accounts: List[AccountResponse] = Field(default_factory=list)