# Running Drive Fusion

This repository now contains a functional prototype: a shared Python core, a Typer CLI, and a FastAPI-powered GUI.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## CLI usage

```bash
python -m drive_fusion.cli accounts
python -m drive_fusion.cli quota
python -m drive_fusion.cli search "security"
python -m drive_fusion.cli connect "Work" work@example.com --total-gb 25
python -m drive_fusion.cli transfer acct-primary acct-archive file-001,file-002 --note "Archive run"
python -m drive_fusion.cli report --output output/workspace-report.md
```

## GUI usage

```bash
uvicorn drive_fusion.api.app:app --reload
```

Then open http://127.0.0.1:8000/ for the dashboard.

## API endpoints

- GET /api/health
- GET /api/accounts, POST /api/accounts
- GET /api/files
- GET /api/quota
- GET /api/jobs, POST /api/jobs

## Notes

This prototype uses local JSON state in `data/state.json` in place of live Google OAuth and Drive API integration. That integration is the next planned phase.
