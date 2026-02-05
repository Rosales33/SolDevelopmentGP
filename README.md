# Chinook API (FastAPI + MySQL + Docker)

Learning project: a **FastAPI** backend connected to a **MySQL 8** database preloaded with the **Chinook** sample dataset.

This repo includes:
- A containerized FastAPI backend
- A containerized MySQL database
- Automatic DB readiness waiting on startup
- Chinook SQL seed script

---

## 1) Clone the repository

    git clone https://github.com/Rosales33/SolDevelopmentGP.git
    cd SolDevelopmentGP

---

## 2) Requirements

You need:
- **Docker Desktop** installed
- Docker Desktop **running**

Check Docker is working:

    docker --version
    docker compose version

---

## 3) Run the project (Docker Compose)

From the repo root:

    docker compose up --build

This will:
- Build and start the `api` container (FastAPI)
- Pull and start the `db` container (MySQL)
- Import the Chinook dataset on first run
- Start the API only after the DB is ready

---

## 4) Test endpoints

- Health check: http://localhost:8000/health
- Swagger docs: http://localhost:8000/docs
- ReDoc docs: http://localhost:8000/redoc

Test with curl:

    curl http://localhost:8000/health

Expected response:

    {"status":"ok"}

---

## 5) Common issues

### Port 3306 already in use
If you already have MySQL running locally, port `3306` may be taken.

Fix: edit `docker-compose.yml` and change:

    ports:
      - "3306:3306"

to:

    ports:
      - "3307:3306"

This does **not** affect the API connection (containers still talk to MySQL using `db:3306`).

---

## 6) Reset the database (re-import Chinook)

MySQL data is persisted in a Docker volume.
To wipe everything and re-seed from scratch:

    docker compose down -v
    docker compose up --build

---

## 7) Project structure

    .
    ├── app/
    │   ├── main.py              # FastAPI app
    │   ├── db.py                # SQLAlchemy engine/session
    │   ├── wait_for_db.py       # Wait until MySQL is ready before starting API
    │   └── routers/
    │       └── health.py        # GET /health
    ├── scripts/
    │   └── chinook-mysql.sql    # Chinook MySQL seed script
    ├── Dockerfile               # API image build
    ├── docker-compose.yml       # API + DB orchestration
    ├── .env                     # Environment variables (learning project)
    ├── pyproject.toml           # Python dependencies (uv-managed)
    └── uv.lock                  # Dependency lockfile (uv)

---

## 8) Stop containers

Press `Ctrl + C` in the terminal where Compose is running, then:

    docker compose down
