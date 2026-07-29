# Running Drive Fusion

This repository contains a functional prototype: a shared Python core, a Typer CLI, and a FastAPI-powered GUI, with live Google OAuth and Drive API integration.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your Google OAuth credentials:

```bash
cp .env.example .env
```

Required variables: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `TOKEN_STORE_DIR`. Create OAuth credentials in the Google Cloud Console with the Drive API enabled and the redirect URI registered.

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

- Click **Connect** next to an account to start the Google OAuth flow (`/auth/login?user_id=<account_id>`).
- Click **Sync** on an account, or **Sync all accounts**, to pull live quota and file metadata from Google Drive.

## Authentication flow

- `GET /auth/login?user_id=<id>` — redirects to Google's OAuth consent screen.
- `GET /auth/callback` — handles the OAuth redirect, exchanges the code for tokens, and stores credentials via `drive_fusion/auth/token_store.py`.
- `GET /auth/logout?user_id=<id>` — clears stored credentials for that account.
- Credentials are stored locally (encrypted-at-rest token store under `TOKEN_STORE_DIR`) for development use only; use a managed secret store in production.

## API endpoints

- `GET /api/health`
- `GET /api/accounts`, `POST /api/accounts`
- `GET /api/files`
- `GET /api/quota`
- `GET /api/jobs`, `POST /api/jobs`
- `POST /api/accounts/{account_id}/sync` — pull live quota + files for one account
- `POST /api/sync` — sync every connected account
- `GET /auth/login`, `GET /auth/callback`, `GET /auth/logout`

## Notes

Account and file state is stored in local JSON state (`data/state.json`). Quota and file metadata are populated from the live Google Drive API once an account completes the OAuth flow; unauthenticated accounts return a clear error when synced. The next planned phase replaces simulated transfer jobs with real Drive API copy/move operations and background job execution.
