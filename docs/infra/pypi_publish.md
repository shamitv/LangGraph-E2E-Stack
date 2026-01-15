# How to Package and Publish to PyPI

This guide shows how to build and publish the backend package.

## 1. Build UI assets (optional for packaging)
Run the UI bundling script from the repo root:

- PowerShell (Windows):
  - `./build_ui.ps1`
- Bash (macOS/Linux):
  - `./build_ui.sh`

## 2. Build the package
From the repo root:
1. `cd backend`
2. `python -m build`

Artifacts will be created in `backend/dist/`.

## 3. Publish to PyPI
From `backend/`, run:

```
twine upload \
  --repository pypi \
  --username __token__ \
  --password $PYPI_TOKEN \
  dist/*
```

### Notes
- Set `PYPI_TOKEN` in your environment before running the command.
- Use TestPyPI by replacing `--repository pypi` with `--repository testpypi` and configuring `.pypirc` if needed.
