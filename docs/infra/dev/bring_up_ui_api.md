# Development guide: bring up UI and API

This doc explains how to run the backend (FastAPI) and frontend (Vite/React) together during local development so you can try the chat UI against the SQLite-backed API.

## 1. Environment prerequisites
- Python 3.11+ in a virtual environment. The repository already ships with `venv/`; activate it with:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- Node.js 18+ (to run the Vite/React frontend). Use `nvm`, `fnm`, or your package manager of choice.
- Environment variables (optional if you rely on defaults):
  - `OPENAI_API_KEY`: Add to `backend/.env` if you want the LangGraph agent to call OpenAI; leave empty for the demo fallback.
  - `VITE_API_URL`: The frontend already defaults to `http://localhost:8000/api/v1`, but you can override it in `frontend/.env` if you need a different host/port.

## 2. Backend setup & run
1. From the repo root, install/update Python dependencies:
   ```powershell
   .\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
   ```
2. The backend is configured to use SQLite (`sqlite+aiosqlite:///./langgraph_demo.db`). The file is created under `backend/` after you start the app; it is ignored via `.gitignore`.
3. Start the backend from its directory so the package import paths resolve correctly:
   ```powershell
   cd backend
   ..\venv\Scripts\uvicorn.exe app.main:app --reload
   ```
   - The server watches `backend/`, listens on `http://127.0.0.1:8000`, and automatically reloads when you change Python files.
   - The SQLite engine already sets `PRAGMA foreign_keys=ON` and `journal_mode=WAL`, so FK constraints are enforced.
4. While the server is running, use another terminal to hit the health or chat endpoint (e.g., `http POST http://127.0.0.1:8000/api/v1/chat ...`). Successful requests write into `langgraph_demo.db`.

## 3. Frontend setup & run
1. From the `frontend/` folder, install Node dependencies if you have not already:
   ```powershell
   cd frontend
   npm install
   ```
2. Start the Vite dev server (it proxies to the backend on `http://localhost:8000`):
   ```powershell
   npm run dev -- --host
   ```
   - The UI launches at `http://localhost:5173`; it expects the backend at `http://localhost:8000/api/v1`.
   - The React stack watches `frontend/src`, so edits trigger hot reloads.
3. Use the chat interface or send requests to `/api/v1/chat` to confirm the SQLite backend handles them.

## 4. Running both concurrently
1. Run the backend (step 2) in one terminal so the API stays up.
2. In a second terminal, run the frontend (step 3) so you can interact with the UI.
3. The frontend `VITE_API_URL` defaults to `http://localhost:8000/api/v1`; no additional overrides are needed unless you change the backend port.
4. The backend logs show SQL statements (SQLAlchemy `echo=True`), so you can verify inserts/queries by watching the console.

## 5. Verification reminders
- The migration plan still lists the following checks; once you manually test them, mark them done:
  - Hit `/api/v1/chat` and ensure SQLite writes/reads work (i.e., the frontend works end-to-end).
  - Confirm FK enforcement by creating data that would violate `messages.conversation_id`.
  - Ensure timestamps stay UTC and JSON payloads round-trip even though SQLite stores them as text.
- After the app is running, `langgraph_demo.db` appears inside `backend/`—delete or reset it if you need to recreate the schema.

## 6. Optional: Docker-compose sanity run
`docker-compose.yml` now only builds the backend and frontend services and relies on the SQLite URL that is baked into `backend/app/core/config.py`. If you prefer Docker, run:
```powershell
docker-compose up --build
```
The frontend (`http://localhost:3000`) proxies to the backend (`http://localhost:8000`), and the SQLite file lives inside the backend container at `/app/langgraph_demo.db` (mirrored to your host via the `./backend:/app` volume).

## 7. Quick troubleshooting
- `ModuleNotFoundError: No module named 'app'`: start Uvicorn from `backend/` so the `app` package is on `sys.path`.
- LangChain import errors are resolved via `langchain.messages`/`langchain_core.messages`; do not revert those edits.
- SQLite fails with `database is locked`? The engine already uses WAL mode, but restart the backend and delete `langgraph_demo.db` if a previous run hung.

Keep this document updated if the dev workflow changes; it mirrors the checklist inside `docs/plans/backend/infra/postgres_to_sqlite.md`.