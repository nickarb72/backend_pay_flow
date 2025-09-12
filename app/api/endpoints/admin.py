from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.core.dependencies import require_admin
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UsersListResponse,
    AccountResponse,
    UserWithAccountsResponse,
)
from app.db.utils.user import UserService

PROHIBITED_RESPONSE = {
    403: {
        "description": "Prohibited",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Admin access required"
                }
            }
        }
    }
}
NOT_FOUND_RESPONSE = {
    404: {
        "description": "Not found",
        "content": {
            "application/json": {
                "example": {
                    "detail": "User not found"
                }
            }
        }
    }
}

router = APIRouter(prefix="/admin/users")


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user account. Admin only.",
    responses={
        400: {"description": "User already exists or invalid data"},
        **PROHIBITED_RESPONSE
    },
    response_model_exclude_none=True
)
async def create_user(
        user_data: UserCreate,
        admin: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Create a new user.

    Args:
        user_data: User creation data
        admin: Authenticated admin user
        db: Database session

    Returns:
        UserResponse: Created user data

    Raises:
        HTTPException: 400 if user already exists
    """
    try:
        user = await UserService.create_user(db, user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user data by ID. Admin only.",
    responses={
        400: {"description": "Invalid data"},
        **NOT_FOUND_RESPONSE,
        **PROHIBITED_RESPONSE
    },
    response_model_exclude_none=True
)
async def update_user(
        user_id: int,
        update_data: UserUpdate,
        admin: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update user data.

    Args:
        user_id: ID of the user to update
        update_data: Data to update
        admin: Authenticated admin user
        db: Database session

    Returns:
        UserResponse: Updated user data

    Raises:
        HTTPException: 404 if user not found
    """
    try:
        user = await UserService.update_user(db, user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        return UserResponse.model_validate(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete user by ID. Admin only.",
    responses={
        204: {"description": "User deleted successfully"},
        **NOT_FOUND_RESPONSE,
        **PROHIBITED_RESPONSE
    }
)
async def delete_user(
        user_id: int,
        admin: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """
    Delete user by ID.

    Args:
        user_id: ID of the user to delete
        admin: Authenticated admin user
        db: Database session

    Raises:
        HTTPException: 404 if user not found
    """
    try:
        deleted = await UserService.delete_user(db, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )


@router.get(
    "",
    response_model=UsersListResponse,
    summary="Get list of all users with accounts",
    description="Retrieve list of all users with accounts with pagination. Admin only.",
    responses=PROHIBITED_RESPONSE,
    response_model_exclude_none=True
)
async def get_users_with_accounts(
        admin: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
) -> UsersListResponse:
    """
    Get list of all users with accounts.

    Args:
        admin: Authenticated admin user
        db: Database session

    Returns:
        UsersListResponse: List of all users with pagination
    """
    user_data = await UserService.get_all_users_with_accounts(db)

    user_responses = []
    for data in user_data.values():
        user = data["user"]
        accounts = data["accounts"]

        account_responses = [AccountResponse.model_validate(account) for account in accounts]

        user_response = UserResponse.model_validate(user)

        user_with_accounts = UserWithAccountsResponse(
            **user_response.model_dump(),
            accounts=account_responses
        )
        user_responses.append(user_with_accounts)

    return UsersListResponse(users=user_responses, total_count=len(user_responses))
