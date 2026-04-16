# CLAUDE.md — ProjectFlow API

## Purpose
ProjectFlow is a project and task management REST API
built with FastAPI and SQLite. It serves as the target
codebase for the Feature Agent course — an AI coding
agent that reads this codebase, implements GitHub
issues, and raises PRs to be reviewed and merged by
a human.

This codebase is intentionally realistic — proper
layered architecture, real migrations, real CI, and
deliberate feature gaps that the agent will implement
as course exercises.

## Build Prompt
This repository was built using the following prompt
with Claude CLI. Update this section when requirements
change and re-run to iterate.

---
See claude.md for the full build prompt.
---

## Tech Stack
  Python:      3.10+
  Framework:   FastAPI
  Database:    SQLite via async SQLAlchemy 2.0
  Migrations:  Alembic
  Testing:     pytest + httpx (async)
  CI:          GitHub Actions
  Config:      pydantic-settings

## Architecture
  app/main.py          FastAPI app, router registration
  app/config.py        settings via pydantic-settings
  app/database.py      async SQLAlchemy engine and session
  app/models/          SQLAlchemy ORM models
  app/schemas/         Pydantic request/response schemas
  app/routers/         FastAPI route handlers (HTTP only)
  app/services/        Business logic (never in routers)
  app/migrations/      Alembic migration versions
  tests/               pytest test suite

## Architecture Decisions

### Why service layer separate from routers
Business logic lives in app/services/ not in routers.
Routers handle HTTP only — parse request, call service,
return response. The agent always knows where to put
business logic and follows this pattern when adding
features.

### Why Alembic for migrations
Every feature that touches the database needs a
migration. Raw CREATE TABLE does not work for
production schema changes. When the agent adds a
new field it must generate an Alembic migration.

### Why SQLite
Zero setup for students. SQLAlchemy abstracts the
database — swapping to PostgreSQL requires changing
one line in database.py. Not the point of this course.

### Why async SQLAlchemy
Matches FastAPI's async model. All database calls
use async/await. Tests use an async test client.

### Soft deletes on projects
Projects are never hard deleted. status field is set
to "archived". Tasks in archived projects still exist
and are queryable. This is realistic behavior.

## For the AI Agent (feature-agent)
When the agent reads this codebase to implement a
GitHub issue it should:
  1. Read app/main.py to understand route structure
  2. Read app/models/ to understand data models
  3. Read app/schemas/ to understand request/response
  4. Read app/services/ to understand business logic
  5. Read tests/conftest.py to understand fixtures
  6. Follow ALL existing patterns exactly
  7. Never put business logic in routers
  8. Always add an Alembic migration for model changes
  9. Always add tests matching existing test style
  10. Never change unrelated code

## Phase Build Plan

### Phase 1 — Foundation [ ]
  PR: "feat: project scaffold, database, and CI setup"
  Goal: working project structure, database connection,
        health check, CI pipeline, base test fixtures

### Phase 2 — Users [ ]
  PR: "feat: user management endpoints"
  Goal: full CRUD for users with tests

### Phase 3 — Projects [ ]
  PR: "feat: project management endpoints"
  Goal: full CRUD for projects with tests

### Phase 4 — Tasks [ ]
  PR: "feat: task management endpoints"
  Goal: full CRUD for tasks, assignment, status with tests

### Phase 5 — Polish and course exercises [ ]
  PR: "chore: documentation, TODO markers, course issues"
  Goal: deliberate gaps, GitHub issues, final docs

Mark each phase [DONE] after PR is merged.
Update Architecture Decisions section as you build.
