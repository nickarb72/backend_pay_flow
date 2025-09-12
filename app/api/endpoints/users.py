from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import User, Account, Payment
from app.schemas import UserResponse, AccountResponse, PaymentListResponse, PaymentResponse
from app.schemas.account import AccountListResponse

UNAUTHORIZED_RESPONSE = {
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Not authenticated"
                }
            }
        }
    }
}

router = APIRouter(prefix="/users")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user information",
    description="Retrieve information about the currently authenticated user",
    responses=UNAUTHORIZED_RESPONSE,
    response_model_exclude_none=True
)
async def read_users_me(
        current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user data.

    Args:
        current_user: The currently authenticated user from JWT token

    Returns:
        UserResponse: User data without sensitive information
    """
    return UserResponse.model_validate(current_user)


@router.get(
    "/accounts",
    response_model=AccountListResponse,
    summary="Get list of current user's accounts",
    description="Retrieve accounts with their balances of the currently authenticated user",
    responses=UNAUTHORIZED_RESPONSE,
    response_model_exclude_none=True
)
async def ger_users_accounts(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> AccountListResponse:
    """
    Get list of current user's accounts.

    Args:
        current_user: The currently authenticated user from JWT token
        db: Database session

    Returns:
        AccountListResponse: List of current user's accounts
    """
    await_accounts = await db.execute(select(Account).where(Account.user_id == current_user.id))
    accounts = await_accounts.scalars().all()

    account_responses = [AccountResponse.model_validate(account) for account in accounts]

    return AccountListResponse(accounts=account_responses)


@router.get(
    "/payments",
    response_model=PaymentListResponse,
    summary="Get list of current user's payments",
    description="Retrieve payments of the currently authenticated user",
    responses=UNAUTHORIZED_RESPONSE,
    response_model_exclude_none=True
)
async def ger_users_payments(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> PaymentListResponse:
    """
    Get list of current user's payments.

    Args:
        current_user: The currently authenticated user from JWT token
        db: Database session

    Returns:
        PaymentListResponse: List of current user's payments
    """
    await_payments = await db.execute(select(Payment).where(Payment.user_id == current_user.id))
    payments = await_payments.scalars().all()

    payment_responses = [PaymentResponse.model_validate(payment) for payment in payments]

    return PaymentListResponse(payments=payment_responses)
