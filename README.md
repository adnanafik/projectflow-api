# ProjectFlow API

A project and task management REST API built with FastAPI and SQLite.

## Features
- Health check endpoint
- Database with async SQLAlchemy and Alembic migrations
- CI pipeline with GitHub Actions

## Coming Soon
- User management (CRUD)
- Project management with soft deletes
- Task management with status transitions and assignment
- Pagination, due dates, and project statistics

## Setup

Prerequisites: Python 3.10+, Git

1. Clone the repo
   ```bash
   git clone <repo-url>
   cd projectflow-api
   ```

2. Create virtual environment
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Configure environment
   ```bash
   cp .env.example .env
   ```

5. Run migrations and start server
   ```bash
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

Visit http://localhost:8000/docs for the API explorer.

## Run with Docker

```bash
docker compose up -d
```

Visit http://localhost:9000/docs. The SQLite database persists in the `api_data` Docker volume; migrations run automatically on container start.

## Running Tests

```bash
pytest tests/ -v --cov=app
```

## API Documentation

Interactive docs available at `/docs` when the server is running.

## Architecture

See CLAUDE.md for full architecture documentation and the reasoning behind every decision.
