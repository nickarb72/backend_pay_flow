from fastapi import APIRouter

from app.api.endpoints import auth, users, admin, payments

main_router = APIRouter()
main_router.include_router(users.router, tags=["users"])
main_router.include_router(admin.router, tags=["admin"])
main_router.include_router(payments.router, tags=["webhooks"])
main_router.include_router(auth.router, tags=["authentication"])
