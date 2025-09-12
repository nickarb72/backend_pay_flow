from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

from app.schemas.account import AccountResponse


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100, description="User's full name")


class UserCreate(UserBase):
    """Schema for creating new user."""
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    role: UserRole = UserRole.USER

    class Config:
        json_schema_extra = {
            "example": {
                "email": "new_user@example.com",
                "full_name": "New User",
                "password": "SecurePassword123",
                "role": "USER"
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user data."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="User's full name")
    password: Optional[str] = Field(None, min_length=6, description="New password (optional)")
    role: Optional[UserRole] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "updated@example.com",
                "full_name": "Updated Name",
                "password": "NewPassword123",
                "role": "ADMIN",
            }
        }


class UserResponse(UserBase):
    """Schema for user response (without sensitive data)."""
    id: int
    role: UserRole
    created_at: datetime = Field(..., description="Timestamp of when the record was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of when the record was updated")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Smith",
                "id": 100,
                "role": "USER",
                "created_at": "2025-09-08T12:00:28.375614Z",
                "updated_at": "2025-09-10T12:00:28.375614Z",
            }
        }


class UserWithAccountsResponse(UserResponse):
    """Schema for user with his accounts."""
    accounts: List[AccountResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class UsersListResponse(BaseModel):
    """Schema for list of users with their accounts with pagination."""
    users: List[UserWithAccountsResponse] = Field(default_factory=list)
    total_count: int = Field(..., example=100)

    class Config:
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "John Smith",
                        "role": "USER",
                        "created_at": "2025-09-08T12:00:28.375614Z",
                        "updated_at": "2025-09-10T12:00:28.375614Z",
                        "accounts": [
                            {
                                "id": 1,
                                "user_id": 1,
                                "balance": 1000.67,
                                "created_at": "2025-09-08T12:00:28.375614Z",
                                "updated_at": "2025-09-10T12:00:28.375614Z"
                            },
                            {
                                "id": 2,
                                "user_id": 1,
                                "balance": 500.25,
                                "created_at": "2025-09-09T12:00:28.375614Z",
                                "updated_at": "2025-09-11T12:00:28.375614Z"
                            }
                        ]
                    }
                ],
                "total_count": 100
            }
        }
