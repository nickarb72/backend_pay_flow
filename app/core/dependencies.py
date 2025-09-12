from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def validate_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Validate JWT token and extract standardized payload data.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(**payload)

    except (JWTError, ValidationError) as e:
        raise credentials_exception from e


async def get_current_user(
        token_data: TokenData = Depends(validate_token),
        db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from validated token data.

    Args:
        token_data: standardized payload data
        db: Database session

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: 401 if user not found
    """
    from sqlalchemy import select

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found",
        headers={"WWW-Authenticate": "Bearer"},
    )

    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def require_admin(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin role for access.

    Args:
        current_user: The current authenticated user

    Returns:
        User: The user if admin

    Raises:
        HTTPException: 403 if not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )

    return current_user
