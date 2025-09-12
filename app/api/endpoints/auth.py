from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import authenticate_user, create_access_token
from app.schemas import Token

router = APIRouter(prefix="/auth")


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user",
    description="""
    Authenticate user with email and password.

    Returns a JWT access token that should be included in the Authorization header
    of subsequent requests as: `Bearer {token}`
    """,
    responses={
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect email or password"
                    }
                }
            }
        }
    }
)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Args:
        form_data: OAuth2 password request form containing username (email) and password
        db: Database session

    Returns:
        Token: JWT access token and token type

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})

    return Token(access_token=access_token, token_type="bearer")
