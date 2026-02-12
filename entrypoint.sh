#!/bin/sh
set -e

# Wait until the DB is ready
/app/.venv/bin/python -m app.wait_for_db

# Start the API (exec makes uvicorn become PID 1)
exec /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
