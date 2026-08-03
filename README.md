# Drive Fusion

[![License](https://img.shields.io/github/license/pangerlkr/Drive-Fusion)](LICENSE) [![Stars](https://img.shields.io/github/stars/pangerlkr/Drive-Fusion?style=social)](https://github.com/pangerlkr/Drive-Fusion/stargazers) [![Docker Image](https://img.shields.io/github/actions/workflow/status/pangerlkr/Drive-Fusion/docker-publish.yml?label=docker%20build)](https://github.com/pangerlkr/Drive-Fusion/actions) [![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

## Sponsored by GitAds

<p align="center">
  <a href="https://docs.gitads.dev/">
    <img
      src="https://gitads.dev/assets/images/sponsor/camos/camo-3.png"
      alt="Sponsored by GitAds"
      width="360"
    />
  </a>
</p>

<p align="center">
  <em>
    Drive Fusion advances under the patronage of
    <strong>
      <a href="https://docs.gitads.dev/docs/getting-started/publishers">
        GitAds
      </a>
    </strong>,
    ensuring that cloud storage drives remain open, secure, and free.
  </em>
</p>

## About

**Drive Fusion** is an open-source **Google Drive storage aggregator and multi-account manager**. It unifies multiple Google Drive accounts into a single dashboard for file search, cross-account transfers, and real-time storage usage tracking — built with **Python, FastAPI, and SQLAlchemy**.

> Keywords: google drive manager, multi-account google drive, cloud storage aggregator, google drive api, fastapi dashboard, self-hosted storage manager, open source drive tool

⭐ If you find this project useful, please star the repo and consider [contributing](CONTRIBUTING.md) — forks and pull requests are welcome!

Drive Fusion is a workspace for users who manage multiple Google accounts and want one operational layer for Google Drive. It does not combine Google storage quotas at the platform level; instead, it provides a federated layer that connects several authorized accounts, aggregates visibility, and makes browsing, searching, reporting, and transfer planning easier in one interface.[1][2]

The project now ships as a **functional prototype** with live Google OAuth and Drive API integration:

- A shared Python core (`drive_fusion/core`)
- A Google OAuth integration package (`drive_fusion/auth`)
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
- Sync live quota and file metadata from the Google Drive API for connected accounts.

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
├── .env.example
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── src/
│   └── drive-fusion.html   # original static concept prototype
├── drive_fusion/
│   ├── __init__.py
│   ├── models.py           # Pydantic data models
│   ├── cli.py              # Typer CLI entry point
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── google_oauth.py # OAuth flow helpers (build_flow, auth URL, token exchange)
│   │   ├── token_store.py  # Per-user OAuth token persistence
│   │   └── routes.py       # /auth/login, /auth/callback, /auth/logout
│   ├── core/
│   │   ├── __init__.py
        ├── db.py             # SQLAlchemy models + init_db/load_state/save_state
│   │   ├── service.py      # Shared service layer used by CLI and API
│   │   └── drive_client.py # Google Drive API v3 wrapper (quota, file listing)
│   └── api/
│       ├── __init__.py
│       └── app.py          # FastAPI app + dashboard + auth + sync routes
├── templates/
│   └── dashboard.html      # GUI dashboard template
├── static/
│   └── style.css           # GUI styling
├── .tokens/                # generated OAuth token JSON files (gitignored)
└── data/
    └── state.json          # generated at first run
```

## Getting started

### 1. Clone and set up a virtual environment

```bash
git clone https://github.com/pangerlkr/Drive-Fusion
cd Drive-Fusion
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Google OAuth

Copy `.env.example` to `.env` and fill in credentials from a Google Cloud OAuth client (create one at https://console.cloud.google.com/apis/credentials):

```bash
cp .env.example .env
# then edit .env with your GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
```

Never commit your real `.env` file — it's already covered by `.gitignore`, along with the `.tokens/` directory where per-account credentials are stored.

### 3. Use the CLI

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

### 4. Use the GUI

```bash
uvicorn drive_fusion.api.app:app --reload
```

Then open `http://127.0.0.1:8000/` to see:

- An overview panel with used/free storage and utilization across all accounts
- A connected accounts table with a form to add new accounts
- A transfer queue table with a form to queue new jobs
- A unified file index across all connected accounts

To connect a real Google account, visit `/auth/login?user_id=<account_id>` (using the id of an account already added via the CLI/GUI) and complete the Google consent screen. Once connected, sync that account's live quota and files with `POST /api/accounts/{account_id}/sync`.

### 5. API reference

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/accounts` | List accounts |
| POST | `/api/accounts` | Add an account |
| GET | `/api/files` | List/search files (`?q=term`) |
| GET | `/api/quota` | Aggregate quota summary |
| GET | `/api/jobs` | List transfer jobs |
| POST | `/api/jobs` | Create a transfer job |
| GET | `/auth/login` | Start Google OAuth flow for `?user_id=` |
| GET | `/auth/callback` | Google OAuth redirect target |
| POST | `/auth/logout` | Disconnect a user's stored Google credentials |
| POST | `/api/accounts/{account_id}/sync` | Pull live quota + files for one account |
| POST | `/api/sync` | Sync all connected accounts |

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
| Phase 3 | Authentication | Done — live Google OAuth multi-account connection flow (`drive_fusion/auth`) |
| Phase 4 | Live indexing | Done — real Drive API metadata sync and quota reads via `drive_client.py` and `/api/.../sync` |
| Phase 5 | Transfer workflows | Done — real Drive API copy jobs via `drive_client.copy_file_between_accounts`, per-file status, retry endpoint |
| Phase 6 | Hardening | In progress — CORS configured and transfers run async; security review, DB migration, and deployment still open |

## Next milestone: hardening and deployment

Accounts can be connected with live Google OAuth, quota/file metadata can be synced from the real Drive API, and transfer jobs copy files for real between connected accounts (with per-file status, error surfacing, and a retry endpoint for failed files). The next milestone focuses on:

- Done: transfer jobs run on a background thread so large transfers don't block the request; a dedicated worker/queue (Celery/RQ) is still recommended for horizontal scaling
- Moving state from a local JSON file to PostgreSQL or SQLite
- Security review of the token store and OAuth flow ahead of any public deployment
- Deployment to Netlify (frontend) and Render (backend API)

## Contributing

See `CONTRIBUTING.md` for guidelines. See `SECURITY.md` for the security policy.
