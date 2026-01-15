# Plan: Package Backend for PyPI

## 1. Goal
Package the `healthcare_agent` backend code into a distributable Python library (`sdist` and `wheel`) that can be published to PyPI.
Critically, the package must:
1.  **Include** all necessary code (`backend/agent_demo_framework`).
2.  **Include** required data files (`backend/agent_demo_framework/data/mock_db`, `backend/agent_demo_framework/data/policies`) so the agent works out-of-the-box.
3.  **Exclude** development artifacts (`node_modules`, `venv`, `tests`, `docs`).
4.  **Install** cleanly via `pip install agentorchestra-stack`.

## 2. Directory Restructuring
Current structure relies on a repo-root `data/` folder. This is not portable. We will move data inside the package.

### 2.1 Move Data
*   **Source**: `d:\work\LangGraph-E2E-Demo\data`
*   **Destination**: `d:\work\LangGraph-E2E-Demo\backend\agent_demo_framework\data`
*   **Action**: Move `mock_db` and `policies` directories into `backend/agent_demo_framework/data`.

### 2.2 Update Configuration
Refactor `backend/agent_demo_framework/core/config.py` to resolve `DATA_DIR` relative to the package installation:

```python
# OLD
DATA_DIR = os.path.join(..., "data")

# NEW
import agent_demo_framework
PACKAGE_ROOT = os.path.dirname(os.path.abspath(agent_demo_framework.__file__))
DATA_DIR = os.path.join(PACKAGE_ROOT, "data")
```

### 2.3 Data Move Impact
Track and update all code paths that reference repo-level `data/`:
*   Update tools that load mock DB / policy files.
*   Update any tests, scripts, or docs that reference repo-level paths.
*   Validate the CLI still resolves data in an installed environment.

### 2.4 Choose Proper Package Path
Decide whether to keep `backend/agent_demo_framework` as the package root or adopt a `src/` layout.
*   **Option A (keep)**: package root is `backend/agent_demo_framework`.
*   **Option B (src)**: move code to `backend/src/app` to avoid accidental imports from repo root.
Document the choice and update packaging config accordingly.

### 2.5 Choose Proper Name
Confirm the distribution name and import name:
*   **Distribution name**: `agentorchestra-stack` (pip install name).
*   **Import package**: `agent_demo_framework`.

Assume a full rename from `app` → `agent_demo_framework` across the codebase:
*   Update all imports.
*   Update entry points.
*   Update config paths.
*   Update any internal references to the package root.

## 3. Packaging Configuration
We will use modern `pyproject.toml` (PEP 621) located in `backend/`.

### 3.1 `backend/pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "agentorchestra-stack"
version = "0.1.0"
description = "A LangGraph-based Healthcare Care Coordinator Agent"
readme = "README.md"
authors = [
  { name = "Your Name", email = "your.email@example.com" },
]
license = "MIT"
classifiers = [
  "Programming Language :: Python :: 3",
  "Operating System :: OS Independent",
]
requires-python = ">=3.9"
dependencies = [
    "fastapi>=0.128.0",
    "uvicorn[standard]>=0.40.0",
    "langgraph>=0.2.0",
    "langchain>=0.3.0",
    "langchain-openai>=0.2.1",
    "pydantic>=2.12.0",
    "pydantic-settings>=2.12.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.18.0",
    "aiosqlite>=0.19.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.28.0",
    "aiohttp>=3.9.0",
    "python-multipart>=0.0.9",
    "tzdata>=2024.1",
]

[project.urls]
Homepage = "https://github.com/shamitv/LangGraph-E2E-Demo"
Repository = "https://github.com/shamitv/LangGraph-E2E-Demo"
Issues = "https://github.com/shamitv/LangGraph-E2E-Demo/issues"

[project.scripts]
# NOTE: cmdline/ is now inside backend/agent_demo_framework/.
healthcare-agent = "agent_demo_framework.cmdline.healthcare_agent_cli:main"

[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]
include = ["agent_demo_framework", "agent_demo_framework.*"]
```

### 3.2 `backend/MANIFEST.in`
Explicitly control non-code file inclusion.

> **Note**: `agent_demo_framework/ui/dist` and `agent_demo_framework/ui/src` are created by the build step in §3.4.

```text
include agent_demo_framework/data/mock_db/*.json
include agent_demo_framework/data/policies/*.md
include agent_demo_framework/data/policies/README.md
recursive-include agent_demo_framework/ui/dist *
recursive-include agent_demo_framework/ui/src *
global-exclude __pycache__
global-exclude *.py[cod]
global-exclude .env
global-exclude venv
global-exclude node_modules
```

### 3.3 Data Inclusion
Ensure data files are included in **both** sdist and wheel:
*   `MANIFEST.in` covers sdist.
*   `include-package-data = true` (and/or `tool.setuptools.package-data`) covers wheels.
*   Verify that `agent_demo_framework/data/**` is present in the built wheel.

### 3.4 UI Bundling (src + wheel)
Bundle the built UI artifacts into the Python package so they appear in both sdist and wheel:
*   Build the frontend (e.g., `frontend/dist/`).
*   Copy or emit build output into a package path, e.g., `backend/agent_demo_framework/ui/`.
*   Ensure `MANIFEST.in` includes `app/ui/**`.
*   Ensure wheel includes UI files via `include-package-data = true` or `package-data` entries.
*   Add a build step (script or Make target) that builds UI **before** `python -m build`.

#### Concrete Build Step (build + copy source)
Create a repo-root script (or Make target) that:
1. Installs frontend deps (if needed).
2. Builds the UI.
3. Copies **built assets** and **UI source** into the package.

Example (PowerShell):
```powershell
# From repo root
Push-Location frontend
npm install
npm run build
Pop-Location

# Ensure package UI folders exist
New-Item -ItemType Directory -Force backend\agent_demo_framework\ui\dist | Out-Null
New-Item -ItemType Directory -Force backend\agent_demo_framework\ui\src | Out-Null

# Copy built UI assets
Copy-Item -Recurse -Force frontend\dist\* backend\agent_demo_framework\ui\dist\

# Copy UI source (for debugging / reference)
Copy-Item -Recurse -Force frontend\src\* backend\agent_demo_framework\ui\src\
```

Example (bash):
```bash
cd frontend
npm install
npm run build
cd ..

mkdir -p backend/agent_demo_framework/ui/dist backend/agent_demo_framework/ui/src
cp -R frontend/dist/* backend/agent_demo_framework/ui/dist/
cp -R frontend/src/* backend/agent_demo_framework/ui/src/
```

### 3.5 Dependencies
Validate runtime dependencies against `backend/requirements.txt` and actual imports:
*   Add missing runtime packages to `dependencies`.
*   Keep dev-only packages (linters, test frameworks) out of `dependencies`.
```

## 4. Build Process

### 4.1 Prerequisites
Install build tools in your `venv`:
```bash
pip install build twine
```

### 4.2 Building
Run from `backend/` directory:
```bash
cd backend
python -m build
```
This produces:
- `dist/langgraph_healthcare_agent-0.1.0.tar.gz` (Source)
- `dist/langgraph_healthcare_agent-0.1.0-py3-none-any.whl` (Binary)

### 4.3 Validation
Check the tarball content to ensure no unwanted files:
```bash
tar -tf dist/langgraph_healthcare_agent-0.1.0.tar.gz
```
*Verify specifically that `node_modules` and `venv` are ABSENT.*

## 5. Publishing
Upload to PyPI (or TestPyPI):
```bash
python -m twine upload dist/*
```

See [docs/infra/pypi_publish.md](../../infra/pypi_publish.md) for the full packaging and publishing guide.

## 6. Additional Considerations

### 6.1 Database Migrations
The `backend/alembic/` directory contains database migrations. Decide:
*   **Exclude** (recommended): Users run migrations separately; don't package.
*   **Include**: Add `alembic/` to package and document migration commands.

### 6.2 Versioning Strategy
Consider dynamic versioning via git tags:
```toml
[tool.setuptools.dynamic]
version = {attr = "agent_demo_framework.__version__"}
```
Or use `setuptools-scm` for automatic version from git tags.

### 6.3 CI/CD Publishing (Optional)
Add GitHub Actions workflow for automated PyPI publishing on release tags:
```yaml
# .github/workflows/publish.yml
on:
  release:
    types: [published]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install build twine
      - run: python -m build
        working-directory: backend
      - run: twine upload backend/dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

## 7. Execution Steps (Checklist)
1. [ ] **Backup**: Ensure repo is committed.
2. [x] **Refactor Data**: Move `data/` to `backend/agent_demo_framework/data/`.
3. [x] **Move CLI**: Move `backend/cmdline/` to `backend/agent_demo_framework/cmdline/`.
4. [x] **Update Config**: Modify `config.py` path logic.
5. [x] **Update Imports/Docs**: Fix any repo-level `data/` references.
6. [x] **Create Configs**: Write `pyproject.toml` and `MANIFEST.in`.
7. [x] **Validate Deps**: Reconcile `requirements.txt` with `dependencies`.
8. [ ] **Build UI & Copy**: Build UI and copy `dist/` + `src/` into `backend/agent_demo_framework/ui/`.
9. [ ] **Build**: Run `python -m build` from `backend/`.
10. [ ] **Verify**: Inspect archive contents (no `node_modules`, `venv`, etc.).
11. [ ] **Test Install**: `pip install dist/*.whl` in a fresh venv and run CLI.
