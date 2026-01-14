# Backend Migration Plan: Postgres to SQLite

## 1. Context and Objective
The goal is to migrate the backend persistence layer from PostgreSQL to SQLite. This is intended for "Dev mode" simplicity.
**Note**: No data migration is required. We will start with a fresh database.
**Target**: `docs/plans/backend/infra/postgres_to_sqlite.md`

## 2. Dependency Updates
We need to swap the Postgres async driver for a SQLite async driver.

### TO-DOs:
- [ ] Edit `backend/requirements.txt`:
    - Remove `asyncpg`
    - Remove `psycopg2-binary`
    - Add `aiosqlite>=0.19.0`
- [ ] Re-install dependencies in the virtual environment:
    ```bash
    pip install -r backend/requirements.txt
    ```

## 3. Configuration & Code Changes
Update the application configuration to point to a SQLite database file and ensure Alembic handles SQLite's limitations (e.g., lack of strong `ALTER TABLE` support) using batch mode.

### TO-DOs:
- [ ] Edit `backend/app/core/config.py`:
    - Change default `DATABASE_URL` from:
      `postgresql+asyncpg://postgres:postgres@localhost:5432/langgraph_demo`
      to:
      `sqlite+aiosqlite:///./langgraph_demo.db`
- [ ] Edit `backend/alembic/env.py`:
    - Update driver stripping logic (Line 16):
      Change `replace("+asyncpg", "")` to `replace("+aiosqlite", "")` (or remove generic driver parts).
    - Enable **Batch Mode** for SQLite migrations:
      - In `run_migrations_offline()`: Add `render_as_batch=True` to `context.configure(...)`.
      - In `run_migrations_online()`: Add `render_as_batch=True` to `context.configure(...)`.
- [ ] Edit `backend/app/db/database.py` (SQLite-safe engine):
        - Add `connect_args={"check_same_thread": False}` to `create_async_engine(...)`.
        - Consider `poolclass=StaticPool` if running in-memory; keep default pool for on-disk `langgraph_demo.db`.
        - Set SQLite pragmas on connect:
                - `PRAGMA foreign_keys=ON` (enforce FK constraints).
                - Optional: `PRAGMA journal_mode=WAL` for fewer lock errors during dev.

## 4. Database Schema Migration (Reset)
Since strict data migration is not required, we will reset the migration history.

### TO-DOs:
- [ ] Delete all existing migration scripts in `backend/alembic/versions/` (delete the `.py` files).
- [ ] Generate a fresh initial migration for SQLite:
    ```bash
    cd backend
    alembic revision --autogenerate -m "Initial SQLite migration"
    ```
- [ ] Apply the migration:
    ```bash
    alembic upgrade head
    ```

## 5. Infrastructure (Docker)
Remove the Postgres container and clean up the Compose file.

### TO-DOs:
- [ ] Edit `docker-compose.yml`:
    - Remove the `postgres` service entirely.
    - Remove the `postgres_data` volume from the `volumes` section.
    - Update `backend` service:
        - Remove `depends_on` block (was depending on `postgres`).
        - Remove or update `DATABASE_URL` environment variable. If removed, it will default to the value in `config.py` (`sqlite+aiosqlite:///./langgraph_demo.db`).
        - **Verify Persistence**: The `backend` service mounts `./backend:/app`. The DB file `./langgraph_demo.db` will be constructed inside `/app`, which maps to `d:\work\LangGraph-E2E-Demo\backend\langgraph_demo.db` on the host. This ensures data persistence across restarts.

## 6. Verification
- [ ] Run the backend locally: `uvicorn app.main:app --reload`
- [ ] Verify `langgraph_demo.db` is created.
- [ ] Test a simple API endpoint (e.g., health check or creating a conversation) to ensure DB writes work.
- [ ] Confirm FK enforcement is active (e.g., attempt to insert a `messages` row with a non-existent `conversation_id` should fail).
- [ ] Confirm timestamp fields remain in UTC and serialize as expected (SQLite stores as text).
- [ ] Confirm JSON columns round-trip (stored as text) and code paths do not rely on Postgres JSON operators.
