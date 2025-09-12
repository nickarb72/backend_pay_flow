import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent.parent

load_dotenv()

WEBHOOK_SECRET_KEY = os.getenv("WEBHOOK_SECRET_KEY")

DATABASE_URL = os.getenv("DATABASE_URL")