from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Optional

from app.db.session import get_db
from app.schemas.payment import WebhookRequest, WebhookResponse
from app.db.utils.payment import WebhookService
from app.core.config import WEBHOOK_SECRET_KEY

router = APIRouter(prefix="/webhooks")
logger = logging.getLogger(__name__)


@router.post(
    "/payment",
    response_model=WebhookResponse,
    summary="Process payment webhook",
    description="""
    Process incoming webhook from payment system.

    This endpoint validates the signature, checks for duplicate transactions,
    creates accounts if needed, and updates user balances.

    **Security Note:** Requires valid SHA256 signature verification.
    """,
    responses={
        400: {
            "description": "Invalid request data or signature",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid signature"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error processing webhook"
                    }
                }
            }
        }
    }
)
async def process_payment_webhook(
        request: Request,
        webhook_data: WebhookRequest,
        db: AsyncSession = Depends(get_db),
        x_forwarded_for: Optional[str] = Header(None),
        user_agent: Optional[str] = Header(None)
) -> WebhookResponse:
    """
    Process payment webhook from external payment system.

    Args:
        request: FastAPI request object
        webhook_data: Validated webhook payload
        db: Database session for transaction processing
        x_forwarded_for: Client IP address from header (for logging)
        user_agent: User agent from header (for logging)

    Returns:
        WebhookResponse: Processing result with status and details

    Raises:
        HTTPException: 400 for invalid requests, 500 for processing errors
    """
    client_ip = x_forwarded_for or request.client.host
    logger.info(
        f"Received webhook from {client_ip} - "
        f"Transaction: {webhook_data.transaction_id}, "
        f"Amount: {webhook_data.amount}, "
        f"User-Agent: {user_agent}"
    )

    try:
        rout_response = await WebhookService.process_webhook(
            db=db,
            payload=webhook_data.model_dump(),
            secret_key=WEBHOOK_SECRET_KEY
        )

        logger.info(
            f"Webhook processed successfully - "
            f"Transaction: {rout_response.transaction_id}, "
            f"Account: {rout_response.account_id}"
        )

        return rout_response

    except ValueError as e:
        logger.warning(f"Webhook validation failed: {e} - Transaction: {webhook_data.transaction_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error(
            f"Webhook processing error: {e} - "
            f"Transaction: {webhook_data.transaction_id}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )
