# Drive Fusion

Drive Fusion is a workspace for users who manage multiple Google accounts and want one operational layer for Google Drive. It does not combine Google storage quotas at the platform level; instead, it provides a federated layer that connects several authorized accounts, aggregates visibility, and makes browsing, searching, reporting, and transfer planning easier in one interface.[1][2]

The project now ships as a **functional prototype** with three working pieces:

- A shared Python core (`drive_fusion/core`)
- A command-line interface (`drive_fusion/cli.py`)
- A FastAPI-powered web GUI (`drive_fusion/api`, `templates/`, `static/`)

Both the CLI and the GUI call the same core service, so behavior stays consistent across interfaces.

## Problem statement

Each Google Account includes up to 15 GB of storage shared across Gmail, Google Drive, and Google Photos, which means users often end up splitting content across multiple accounts when they outgrow a single free allocation.[2] Google Drive API based apps can authenticate users with OAuth and work with file metadata, listing, and transfers, which makes a unified management layer technically feasible.[1][3]

## Product goal

The goal is to create a professional workspace that lets a user connect multiple Google accounts, inspect quota usage, index files across those accounts, and run user-approved transfer workflows without constant account switching.[1][2]

## Core concept

| Layer | Role | Notes |
|---|---|---|
| Account connector | Connect multiple Google accounts | Uses OAuth per account and stores token references securely.[1][3] |
| Quota monitor | Track used and free storage | Reads usage metadata and presents both per-account and aggregate views.[2] |
| Unified index | Search files across accounts | Normalizes metadata into one searchable catalog.[1][4] |
| Transfer engine | Copy files between accounts | Runs queued jobs with retry and progress handling. |
| Export center | Produce reports | Generates CSV and Markdown workspace reports. |

## Functional scope

### Included

- Connect two or more Google accounts with explicit OAuth consent.[1][3]
- View capacity and usage for each connected account.[2]
- Aggregate visible storage metrics into one dashboard total while preserving per-account ownership boundaries.[2]
- Search files across all connected accounts.
- Queue copy and organization jobs between accounts.
- Export workspace reports and transfer logs.

### Not included

- Changing how Google allocates quota to a single account.[2]
- Bypassing Google storage policies or terms.
- Silent account linking without user authorization.[1][3]

## Repository structure

```
drive-fusion/
├── README.md
├── RUNNING.md
├── CONTRIBUTING.md
├── SECURITY.md
├── requirements.txt
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── src/
│   └── drive-fusion.html      # original static concept prototype
├── drive_fusion/
│   ├── __init__.py
│   ├── models.py              # Pydantic data models
│   ├── cli.py                 # Typer CLI entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── store.py           # JSON-backed state (prototype persistence)
│   │   └── service.py         # Shared service layer used by CLI and API
│   └── api/
│       ├── __init__.py
│       └── app.py             # FastAPI app + dashboard routes
├── templates/
│   └── dashboard.html         # GUI dashboard template
├── static/
│   └── style.css              # GUI styling
└── data/
    └── state.json             # generated at first run
```

## Getting started

### 1. Clone and set up a virtual environment

```bash
git clone https://github.com/pangerlkr/Drive-Fusion
cd Drive-Fusion
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Use the CLI

```bash
# List connected accounts
python -m drive_fusion.cli accounts

# Show aggregate quota usage
python -m drive_fusion.cli quota

# Search the unified file index
python -m drive_fusion.cli search "security"

# Register a new account
python -m drive_fusion.cli connect "Work" work@example.com --total-gb 25

# Queue a transfer job (file ids are comma separated)
python -m drive_fusion.cli transfer acct-primary acct-archive file-001,file-002 --note "Archive run"

# Export a Markdown workspace report
python -m drive_fusion.cli report --output output/workspace-report.md
```

Run `python -m drive_fusion.cli --help` to see all commands, and `--help` after any command for its options.

### 3. Use the GUI

```bash
uvicorn drive_fusion.api.app:app --reload
```

Then open `http://127.0.0.1:8000/` to see:

- An overview panel with used/free storage and utilization across all accounts
- A connected accounts table with a form to add new accounts
- A transfer queue table with a form to queue new jobs
- A unified file index across all connected accounts

### 4. API reference

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/accounts` | List accounts |
| POST | `/api/accounts` | Add an account |
| GET | `/api/files` | List/search files (`?q=term`) |
| GET | `/api/quota` | Aggregate quota summary |
| GET | `/api/jobs` | List transfer jobs |
| POST | `/api/jobs` | Create a transfer job |

See `RUNNING.md` for the same instructions in a quick-reference format.

## Suggested stack

| Area | Recommendation |
|---|---|
| Frontend | FastAPI + Jinja2 dashboard now; React migration later |
| Backend | FastAPI for OAuth callbacks, indexing, and job orchestration |
| Queue | Celery, RQ, or a lightweight async worker |
| Database | PostgreSQL or SQLite during prototype stage (currently JSON file) |
| Cache | Redis for token/session and background job state |
| Storage | Local encrypted token store or managed secret store |
| Deployment | Netlify for frontend, Render for backend API |

## Development phases

| Phase | Focus | Status |
|---|---|---|
| Phase 1 | Product prototype | Done — static web UI and documentation |
| Phase 2 | Functional core, CLI, GUI | Done — shared service layer, Typer CLI, FastAPI dashboard |
| Phase 3 | Authentication | Next — live Google OAuth multi-account connection flow |
| Phase 4 | Live indexing | Planned — real Drive API metadata sync and quota reads |
| Phase 5 | Transfer workflows | Planned — real copy jobs, retries, progress tracking |
| Phase 6 | Hardening | Planned — security review, deployment, telemetry |

## Next milestone: live Google integration

The current prototype uses local JSON state (`data/state.json`) to simulate accounts, files, and jobs so the CLI and GUI are fully usable today. The next milestone replaces that with:

- Google Cloud OAuth client setup
- `/auth/login` and `/auth/callback` routes in the FastAPI app
- Secure token storage per account
- Real quota and file metadata sync via the Google Drive API

## Contributing

See `CONTRIBUTING.md` for guidelines. See `SECURITY.md` for the security policy.
