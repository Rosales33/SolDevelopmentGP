FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# Copy lockfiles first for caching
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# Create venv + install deps from lock (reproducible)
RUN uv sync --frozen

# Copy application code
COPY app /app/app

# Copy entrypoint and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

#the “main executable” the container always runs
ENTRYPOINT ["/app/entrypoint.sh"] 

#the default arguments to the entrypoint, can be overridden at runtime
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 



