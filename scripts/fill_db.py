import asyncio
import hashlib
import os

from dotenv import load_dotenv
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from alembic.config import Config
from alembic import command

from app.core.config import WEBHOOK_SECRET_KEY, PROJECT_ROOT, DATABASE_URL
from app.db.models import Payment, User, UserRole, Account
from app.core.security import get_password_hash, verify_password
from app.db.session import engine, Base, AsyncSessionLocal


def create_signature(payload: dict, secret_key: str):
    signature_data = ''.join([
        str(payload['account_id']),
        str(payload['amount']),
        str(payload['transaction_id']),
        str(payload['user_id']),
        secret_key
    ])

    return hashlib.sha256(signature_data.encode()).hexdigest()


async def fill_test_db(session: AsyncSession):
    users_data = [
        {
            "full_name": "Test User",
            "email": "test_user@example.com",
            "hashed_password": get_password_hash("test_user_password"),
        },
        {
            "full_name": "Test User1",
            "email": "test_user1@example.com",
            "hashed_password": get_password_hash("test_user1_password"),
        },
        {
            "full_name": "Test Admin",
            "email": "test_admin@example.com",
            "hashed_password": get_password_hash("test_admin_password"),
            "role": UserRole.ADMIN,
        },
    ]
    await_users = await session.execute(insert(User).returning(User.id), users_data)
    user_ids = await_users.scalars().all()

    accounts_data = [
        {"id": 1, "user_id": user_ids[0], "balance": 100.50},
        {"id": 2, "user_id": user_ids[0], "balance": 200.59},
    ]
    await session.execute(insert(Account), accounts_data)
    # account = Account(user_id=user_ids[0], id=1)
    # session.add(account)

    payments_data = [
        {
            "account_id": 1,
            "amount": 100.50,
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
            "user_id": user_ids[0],
            # "signature": "89bb7bf3bf31631c656bbca64fa9c44a67fa7d644dd7d84acc406265252e10f6",
        },
        {
            "account_id": 2,
            "amount": 200.59,
            "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132d",
            "user_id": user_ids[0],
            # "signature": "1c97e5c22817248cdefcb8a84581c3a8892282befa2aa7ede92b8a4519c2291a",
        },
    ]
    await session.execute(insert(Payment), payments_data)


async def create_test_data(session: AsyncSession):
    try:
        await fill_test_db(session)
    except Exception as exc:
        print(f"\n❌ Exception has occurred while test data was creating: {exc}")
        raise

    print("\n✅ Test data created")
    print("🧑🏻 Test User:\n\tEmail: test_user@example.com\n\tPassword: test_user_password\n\tRole: User")
    print("\n👑 Test Admin:\n\tEmail: test_admin@example.com\n\tPassword: test_admin_password\n\tRole: Admin")
    print("\n💰 Test account with balance 0.00 created for Test User")


async def init_db_with_test_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            await create_test_data(session)


def run_init_migrations():
    alembic_ini_path = PROJECT_ROOT / "alembic.ini"
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    asyncio.run(init_db_with_test_data())
