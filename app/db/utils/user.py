from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional
import logging

from app.db.models import Account, User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


class UserService:
    """Service layer for user management operations."""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_users_with_accounts(db: AsyncSession, skip: int = 0, limit: int = 100) -> dict:
        """Get all users with accounts with pagination."""
        query = (
            select(User, Account)
            .outerjoin(Account,
                       User.id == Account.user_id)
            .order_by(User.id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        rows = result.all()

        user_data = defaultdict(lambda: {"user": None, "accounts": []})

        for row in rows:
            user, account = row
            if user_data[user.id]["user"] is None:
                user_data[user.id]["user"] = user
            if account:
                user_data[user.id]["accounts"].append(account)

        return user_data

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create new user."""
        existing_user = await UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")

        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role.value
        )

        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, update_data: UserUpdate) -> Optional[User]:
        """Update user data."""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)

        if "password" in update_dict:
            update_dict["hashed_password"] = get_password_hash(update_dict.pop("password"))

        if update_dict:
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_dict)
            )
            await db.flush()
            await db.refresh(user)

        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """Delete user by ID."""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        await db.execute(delete(User).where(User.id == user_id))
        # await db.flush()
        return True
