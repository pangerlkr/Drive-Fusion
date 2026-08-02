# Drive Fusion

Drive Fusion is a web UI based project for users who manage multiple Google accounts and want one operational workspace for Google Drive. The product does not combine Google storage quotas at the platform level; instead, it provides a federated layer that connects several authorized accounts, aggregates visibility, and makes browsing, searching, reporting, and transfer planning easier in one interface.[1][2]

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

## Deployment

Drive Fusion targets a split deployment: a static/Jinja2 frontend and a FastAPI backend API, with persistent storage for state and OAuth tokens.

### Frontend (Netlify)

- Build/publish the `templates/` and `static/` assets, or migrate to a React build, and deploy the output directory to Netlify.
- Configure Netlify environment variables to point API calls at the deployed backend URL (Render).
- Set up a `_redirects` or `netlify.toml` rewrite so frontend routes proxy `/api/*` and `/auth/*` calls to the Render backend.

### Backend (Render)

- Deploy `drive_fusion.api.app:app` as a Render Web Service running `uvicorn drive_fusion.api.app:app --host 0.0.0.0 --port $PORT`.
- Set required environment variables in the Render dashboard: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` (pointing at the Render URL's `/auth/callback`), `TOKEN_STORE_DIR`, and `DATABASE_URL` (a PostgreSQL connection string; defaults to a local SQLite file if unset).
- Register the Render callback URL in the Google Cloud Console OAuth client's authorized redirect URIs.
- Provision a managed PostgreSQL database and set `DATABASE_URL` accordingly (falls back to a local SQLite file if unset), and use a persistent disk for `TOKEN_STORE_DIR` so accounts, files, jobs, and tokens survive restarts and deploys.

### Hardening checklist before public deployment

- Done: state (accounts, files, jobs) is persisted via SQLAlchemy in `drive_fusion/core/db.py` (SQLite by default, PostgreSQL via `DATABASE_URL`), with automatic one-time migration from the legacy `data/state.json` on first run.
- Done: transfer jobs run asynchronously on a background thread (`DriveFusionService._run_transfer_job_async`) so large copy jobs don't block requests. A dedicated worker/queue (Celery/RQ) is still recommended for horizontal scaling.
- Add rate limiting and structured logging/telemetry around OAuth and sync endpoints.
- Review CORS, cookie, and session settings for the production domain.
