import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.api import main_router
from app.db.session import engine
from scripts.fill_db import init_db_with_test_data, run_init_migrations

load_dotenv()

PORT = 8000


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("ENVIRONMENT") == "development":
        await asyncio.to_thread(run_init_migrations)

    yield

    await engine.dispose()


app = FastAPI(
    title="Payment System API",
    description="REST API for user authentication and payment management",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "authentication", "description": "Log in"},
        {"name": "users", "description": "Operations with users"},
        {"name": "admin", "description": "Operations admin access required"},
        {"name": "webhooks", "description": "Operations with payments"},
    ],
)

app.include_router(main_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)
