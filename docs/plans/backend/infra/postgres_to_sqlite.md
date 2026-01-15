# Backend Migration Plan: Postgres to SQLite

## 1. Context and Objective
The goal is to migrate the backend persistence layer from PostgreSQL to SQLite. This is intended for "Dev mode" simplicity.
**Note**: No data migration is required. We will start with a fresh database.
**Target**: `docs/plans/backend/infra/postgres_to_sqlite.md`

## 2. Dependency Updates
We need to swap the Postgres async driver for a SQLite async driver.
Status: Completed - dependencies now include `aiosqlite` and the `tzdata` bundle that provides `UTC` when running on Windows.

### TO-DOs:
- [x] Edit `backend/requirements.txt`:
    - Remove `asyncpg`
    - Remove `psycopg2-binary`
    - Add `aiosqlite>=0.19.0` and `tzdata==2024.1`
- [x] Re-install dependencies in the virtual environment:
    ```bash
    pip install -r backend/requirements.txt
    ```

## 3. Configuration & Code Changes
Update the application configuration to point to a SQLite database file and ensure Alembic handles SQLite's limitations (e.g., lack of strong `ALTER TABLE` support) using batch mode.
Status: Completed - config now points at `langgraph_demo.db`, Alembic renders batches, and the async engine sets SQLite pragmas.

### TO-DOs:
    - [x] Edit `backend/agent_demo_framework/core/config.py`:
          - Change default `DATABASE_URL` from PostgreSQL to `sqlite+aiosqlite:///./langgraph_demo.db`.   
      - [x] Edit `backend/alembic/env.py`:
          - Update driver stripping logic to drop `+aiosqlite` and resolve metadata via `Base.metadata`.  
          - Enable **Batch Mode** for both `run_migrations_offline()` and `run_migrations_online()`.      
    - [x] Edit `backend/agent_demo_framework/db/database.py` (SQLite-safe engine):
          - Pass `connect_args={"check_same_thread": False}` to `create_async_engine(...)`.
          - Leave the default pool for the on-disk file, but the hooks are ready for `StaticPool` if needed.                                                                                                            
          - Set SQLite pragmas on connect to turn on `foreign_keys` and prefer `journal_mode=WAL` for dev.
    - [x] Update `agent_demo_framework/api/chat.py`, `agent_demo_framework/agents/base_agent.py`, and `agent_demo_framework/agents/conversational_agent.py` to import messages via `langchain.messages`/`langchain_core.messages` so the server can start with `langchain==1.2.3`.

## 4. Database Schema Migration (Reset)
Since strict data migration is not required, we will reset the migration history.
Status: Completed - cleaned old migrations and generated/applied a fresh SQLite initial migration.

### TO-DOs:
- [x] Delete all existing migration scripts in `backend/alembic/versions/` (delete the `.py` files).
- [x] Generate a fresh initial migration for SQLite:
    ```bash
    cd backend
    alembic revision --autogenerate -m "Initial SQLite migration"
    ```
- [x] Apply the migration:
    ```bash
    alembic upgrade head
    ```

## 5. Infrastructure (Docker)
Remove the Postgres container and clean up the Compose file.
Status: Completed - `docker-compose.yml` now only brings up the backend + frontend, relying on the SQLite URL in config.

### TO-DOs:
- [x] Edit `docker-compose.yml`:
    - Remove the `postgres` service entirely.
    - Remove the `postgres_data` volume from the `volumes` section.
    - Update `backend` service:
        - Drop `depends_on` and the `DATABASE_URL` override so it relies on `config.py`'s SQLite URL.
        - **Verify Persistence**: The `backend` service mounts `./backend:/app`, creating `langgraph_demo.db` under the mapped directory.

## 6. Verification
- Status: Partial - the SQLite DB was created via Alembic, but runtime/endpoint verification still needs to run.
    - [x] Run the backend locally: `uvicorn agent_demo_framework.main:app --reload` (ran from the `backend/` directory after switching the message imports; server starts cleanly and awaits requests on `http://127.0.0.1:8000`).
    - [x] Verify `langgraph_demo.db` is created.
- [ ] Test a simple API endpoint (e.g., health check or creating a conversation) to ensure DB writes work.
- [ ] Confirm FK enforcement is active (e.g., attempt to insert a `messages` row with a non-existent `conversation_id` should fail).
- [ ] Confirm timestamp fields remain in UTC and serialize as expected (SQLite stores as text).
- [ ] Confirm JSON columns round-trip (stored as text) and code paths do not rely on Postgres JSON operators.

## 7. Follow-up Tasks
    - [x] Exercise the backend by running `uvicorn agent_demo_framework.main:app --reload`, hitting the chat endpoint, and verifying the SQLite file handles the operations.                                                                 
- [ ] Launch the Compose stack (`docker-compose up`), drive the frontend chat interface, and confirm the SQLite backend works without Postgres.
