from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "CEMO - Controle de Insumos")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database' / 'cemo.db'}")
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
INITIAL_ADMIN_EMAIL = os.getenv("INITIAL_ADMIN_EMAIL", "admin@cemo.local")
INITIAL_ADMIN_PASSWORD = os.getenv("INITIAL_ADMIN_PASSWORD", "Admin@123")

CRITICAL_COVERAGE_DAYS = int(os.getenv("CRITICAL_COVERAGE_DAYS", "15"))
WARNING_COVERAGE_DAYS = int(os.getenv("WARNING_COVERAGE_DAYS", "30"))
PROCESS_STALE_DAYS = int(os.getenv("PROCESS_STALE_DAYS", "20"))
EXPIRY_ALERT_DAYS = int(os.getenv("EXPIRY_ALERT_DAYS", "30"))

