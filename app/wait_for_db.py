import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

max_seconds = int(os.getenv("DB_WAIT_SECONDS", "90"))
deadline = time.time() + max_seconds

while True:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is ready")
        break
    except OperationalError:
        if time.time() > deadline:
            raise RuntimeError("Database not ready in time")
        print("⏳ Waiting for database...")
        time.sleep(2)
