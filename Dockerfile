FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# Copy lockfiles first for caching
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# Create a venv inside the container and install deps from the lock
RUN uv sync --frozen

# Copy application code
COPY app /app/app

EXPOSE 8000

# Use the venv created by uv (.venv) to run commands
CMD ["sh", "-c", ". .venv/bin/activate && python -m app.wait_for_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]




