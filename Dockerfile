FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# Instala dependencias del proyecto (resolviendo con uv)
RUN uv pip install --system fastapi uvicorn sqlalchemy pymysql python-dotenv cryptography

COPY app /app/app

EXPOSE 8000
CMD ["sh", "-c", "python -m app.wait_for_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]



