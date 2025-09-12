from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import re
from uuid import UUID
from datetime import datetime


class WebhookBase(BaseModel):
    """Base schema for webhook payload validation."""
    transaction_id: UUID = Field(..., description="Unique transaction ID from payment system")
    user_id: int = Field(..., gt=0, description="User ID in our system")
    account_id: int = Field(..., gt=0, description="Account ID in our system")
    amount: float = Field(..., gt=0, description="Payment amount (must be positive)")


class WebhookRequest(WebhookBase):
    """Webhook schema for receiving from external system."""
    signature: str = Field(..., min_length=64, max_length=64, description="SHA256 signature for verification")

    class Config:
        json_schema_extra  = {
            "example": {
                "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
                "user_id": 1,
                "account_id": 1,
                "amount": 100.50,
                "signature": "89bb7bf3bf31631c656bbca64fa9c44a67fa7d644dd7d84acc406265252e10f6"
            }
        }

    @field_validator('signature')
    def validate_signature_format(cls, v):
        """Validate that signature is a valid SHA256 hex string."""
        if not re.match(r'^[a-f0-9]{64}$', v):
            raise ValueError('Signature must be a valid SHA256 hex string')
        return v


class WebhookResponse(WebhookBase):
    """Response schema for webhook processing result."""
    created_at: datetime = Field(..., description="Timestamp of when the record was created")
    message: Optional[str] = Field(None, description="Additional information")

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
                "user_id": 10,
                "account_id": 1,
                "amount": 100.50,
                "created_at": "2025-09-08T12:00:28.375614Z",
                "message": "Payment processed successfully"
            }
        }


class PaymentResponse(WebhookBase):
    """Response schema for getting user's payment."""
    created_at: datetime = Field(..., description="Timestamp of when the record was created")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
                "user_id": 10,
                "account_id": 1,
                "amount": 100.50,
                "created_at": "2025-09-08T12:00:28.375614Z",
            }
        }


class PaymentListResponse(BaseModel):
    """Response schema for successful getting list of authorized user's payments."""

    payments: List[PaymentResponse] = Field(default_factory=list)
