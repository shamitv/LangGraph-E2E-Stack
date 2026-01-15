# Plan: Package Backend for PyPI

## 1. Goal
Package the `healthcare_agent` backend code into a distributable Python library (`sdist` and `wheel`) that can be published to PyPI.
Critically, the package must:
1.  **Include** all necessary code (`backend/app`).
2.  **Include** required data files (`data/mock_db`, `data/policies`) so the agent works out-of-the-box.
3.  **Exclude** development artifacts (`node_modules`, `venv`, `tests`, `docs`).
4.  **Install** cleanly via `pip install langgraph-healthcare-agent`.

## 2. Directory Restructuring
Current structure relies on a repo-root `data/` folder. This is not portable. We will move data inside the package.

### 2.1 Move Data
*   **Source**: `d:\work\LangGraph-E2E-Demo\data`
*   **Destination**: `d:\work\LangGraph-E2E-Demo\backend\app\data`
*   **Action**: Move `mock_db` and `policies` directories into `backend/app/data`.

### 2.2 Update Configuration
Refactor `backend/app/core/config.py` to resolve `DATA_DIR` relative to the package installation:

```python
# OLD
DATA_DIR = os.path.join(..., "data")

# NEW
import app
PACKAGE_ROOT = os.path.dirname(os.path.abspath(app.__file__))
DATA_DIR = os.path.join(PACKAGE_ROOT, "data")
```

## 3. Packaging Configuration
We will use modern `pyproject.toml` (PEP 621) located in `backend/`.

### 3.1 `backend/pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "langgraph-healthcare-agent"
version = "0.1.0"
description = "A LangGraph-based Healthcare Care Coordinator Agent"
readme = "README.md"
authors = [
  { name = "Your Name", email = "your.email@example.com" },
]
license = { text = "MIT" }
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
requires-python = ">=3.9"
dependencies = [
    "langgraph>=0.0.10",
    "langchain-openai>=0.0.5",
    "pydantic>=2.0",
    "python-dotenv>=1.0.0",
    "pydantic-settings>=2.0.0"
]

[project.scripts]
healthcare-agent = "app.cmdline.healthcare_agent_cli:main"

[tool.setuptools]
packages = ["app"]
```

### 3.2 `backend/MANIFEST.in`
Explicitly control non-code file inclusion.
```text
include app/data/mock_db/*.json
include app/data/policies/*.md
include app/data/policies/README.md
global-exclude __pycache__
global-exclude *.py[cod]
global-exclude .env
global-exclude venv
global-exclude node_modules
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

## 6. Execution Steps (Checklist)
1. [ ] **Backup**: Ensure repo is committed.
2. [ ] **Refactor Data**: Move `data/` to `backend/app/data/`.
3. [ ] **Update Config**: Modify `config.py` path logic.
4. [ ] **Create Configs**: Write `pyproject.toml` and `MANIFEST.in`.
5. [ ] **Build**: Run builder.
6. [ ] **Verify**: Inspect archive contents.
