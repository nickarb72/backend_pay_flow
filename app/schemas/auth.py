from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Schema for successful authentication response containing JWT token."""
    access_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Schema for JWT token payload data."""
    sub: str = Field(..., description="Subject (user ID)", example="123")
    exp: datetime = Field(..., description="Expiration time")
    iat: datetime = Field(..., description="Issued at time")
    role: str = Field(..., description="User role", example="user")

    class Config:
        extra = "forbid"


class UserLogin(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "your_secure_password_123"
            }
        }
