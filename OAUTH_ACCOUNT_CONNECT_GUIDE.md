# Drive Fusion OAuth Account Connection Guide

## Purpose

Drive Fusion supports live Google OAuth account connection and post-login Drive sync so users can pull real quota and file metadata into the unified dashboard. The repository documents this flow using `GET /auth/login?user_id=<account_id>`, `GET /auth/callback`, and `POST /api/accounts/{account_id}/sync`. [page:1]

This guide explains that flow step by step for end users and maintainers.

## What this guide covers

This guide covers how to:
- add an account in Drive Fusion,
- start Google sign-in for that account,
- complete the consent screen,
- return to Drive Fusion successfully,
- run the sync endpoint,
- verify that the account now shows live quota and indexed files. [page:1]

## Prerequisites

Before you start, make sure the following are already done:

1. The repository has been cloned locally. [page:1]
2. A Python virtual environment has been created and activated. [page:1]
3. Dependencies from `requirements.txt` are installed. [page:1]
4. `.env.example` has been copied to `.env` and Google OAuth variables have been filled in. [page:1]
5. The Google Drive API is enabled in your Google Cloud project. [web:66]
6. The OAuth consent screen is configured. [web:61][web:67]
7. If the app is still in testing mode, the Google account you want to sign in with has been added as a test user. [web:65]

## Step 1 — Start Drive Fusion locally

From the repository root, start the app with the same Python environment where your dependencies are installed. The repository documents `uvicorn drive_fusion.api.app:app --reload` as the GUI launch command. [page:1]

Recommended command:

```bash
python -m uvicorn drive_fusion.api.app:app --reload
```

Then open the dashboard in your browser:

```text
http://127.0.0.1:8000/
```

If you get `ModuleNotFoundError: No module named 'fastapi'`, you are probably running Uvicorn outside your virtual environment. The repo’s installation instructions require creating a virtual environment, activating it, and installing `requirements.txt` first. [page:1]

## Step 2 — Add or confirm an account in Drive Fusion

The login route requires the id of an account that already exists in Drive Fusion. The repository states that `/auth/login?user_id=` must use the id of an account already added through the CLI or GUI. [page:1]

You can create or inspect accounts in two ways.

### Option A — Use the CLI

List existing accounts:

```bash
python -m drive_fusion.cli accounts
```

Add a new account if needed:

```bash
python -m drive_fusion.cli connect "Work" work@example.com --total-gb 25
```

The CLI output includes the account id, which is the value you need for the login URL. The repository documents `drive_fusion.cli` as the command-line interface entry point and includes `accounts` and `connect` commands in the README. [page:1]

### Option B — Use the GUI

Open the dashboard and add an account using the connected accounts form. The repository says the GUI includes a connected accounts table and a form to add new accounts. [page:1]

After adding the account, note the generated account id. That id is required in the OAuth login URL. [page:1]

## Step 3 — Get the exact account id

Before starting Google sign-in, identify the exact `account_id`. This is usually a value such as:

```text
acct-primary
```

or

```text
acct-work
```

Do not use the label or email unless the app explicitly says those are the same value. The login flow uses the actual account id in the query string. [page:1]

## Step 4 — Start the Google OAuth flow

Open the following URL in your browser, replacing `<account_id>` with the real account id from Drive Fusion. The repository documents `GET /auth/login` as the route that starts the Google OAuth flow for `?user_id=`. [page:1]

Example:

```text
http://127.0.0.1:8000/auth/login?user_id=acct-work
```

What happens next:
1. Drive Fusion starts the Google OAuth flow. [page:1]
2. Google shows the account-selection and consent screen. [page:1]
3. You select the Google account you want to connect.
4. You review and approve the permissions requested by Drive Fusion.
5. Google redirects you back to Drive Fusion at `/auth/callback`. [page:1]

## Step 5 — Complete the Google consent screen

During sign-in, Google will show a consent screen that identifies the app and the data access being requested. Google documents this as part of the OAuth consent flow configured under the Google Auth platform. [web:61][web:67]

What to do:
- Choose the intended Google account.
- Review the requested permissions.
- Click Continue or Allow.
- Wait for Google to redirect you back to the app.

If the app is in testing mode and your email is not listed as a test user, Google may block access. Google’s OAuth setup requires test users for apps that are not yet fully published. [web:65]

## Step 6 — Return through `/auth/callback`

After you approve access, Google redirects back to Drive Fusion’s callback route. The repository documents `GET /auth/callback` as the Google OAuth redirect target. [page:1]

A successful callback usually means:
- Drive Fusion exchanged the OAuth code for tokens,
- the tokens were stored for that account,
- the account is now authenticated for Drive API actions. [page:1]

If the browser returns to the app without an error, proceed to the sync step.

## Step 7 — Sync live quota and files for that account

Connecting the account only completes OAuth. To actually pull live Google Drive data into Drive Fusion, the repository instructs you to call `POST /api/accounts/{account_id}/sync`. [page:1]

Example using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/acct-work/sync
```

Replace `acct-work` with the real account id.

What this sync does:
- requests live quota information from the Google Drive API,
- reads file metadata for the connected account,
- updates Drive Fusion’s per-account and aggregate views, 
- refreshes the unified index with the latest metadata. [page:1]

The repository explicitly describes this endpoint as “Pull live quota + files for one account.” [page:1]

## Step 8 — Verify that sync worked

Once the sync request finishes, confirm that Drive Fusion now reflects live data. The repository describes the dashboard as showing usage totals, connected accounts, transfer jobs, and a unified file index. [page:1]

Check any of the following:

### A. Dashboard verification

Refresh the GUI and confirm:
- quota values changed from placeholder values to live values,
- the account shows updated used/free storage,
- files from that account appear in the unified file index. [page:1]

### B. API verification

Use these endpoints:

```bash
curl http://127.0.0.1:8000/api/accounts
curl http://127.0.0.1:8000/api/quota
curl http://127.0.0.1:8000/api/files
```

The repository documents these endpoints in its API reference. [page:1]

### C. Sync-all verification

If multiple accounts are connected, you can also use the sync-all route documented in the repo:

```bash
curl -X POST http://127.0.0.1:8000/api/sync
```

This syncs all connected accounts instead of only one. [page:1]

## Full worked example

Here is the full flow from start to finish.

### 1. Start the app

```bash
python -m uvicorn drive_fusion.api.app:app --reload
```

### 2. List current accounts

```bash
python -m drive_fusion.cli accounts
```

### 3. Example CLI output

```json
[
  {
    "id": "acct-work",
    "label": "Work",
    "email": "work@example.com"
  }
]
```

### 4. Start login in browser

```text
http://127.0.0.1:8000/auth/login?user_id=acct-work
```

### 5. Complete Google sign-in and consent

You approve the app and Google redirects back to Drive Fusion. [page:1]

### 6. Sync the connected account

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/acct-work/sync
```

### 7. Check aggregate quota

```bash
curl http://127.0.0.1:8000/api/quota
```

### 8. Check indexed files

```bash
curl http://127.0.0.1:8000/api/files
```

At this point, the connected account should be fully visible in the Drive Fusion dashboard and APIs. [page:1]

## Common errors and how to fix them

### Error: `redirect_uri_mismatch`

Cause:
The redirect URI configured in Google Cloud does not exactly match the URI Drive Fusion is using.

Fix:
- Compare the redirect URI in `.env` with the OAuth client’s configured redirect URI.
- Match scheme, hostname, port, and path exactly.
- If the app uses `127.0.0.1`, do not register only `localhost`, and vice versa. Google’s OAuth client configuration requires exact redirect URI matches. [web:60]

### Error: access blocked or app not verified

Cause:
The OAuth app is in testing mode and the user is not listed as a test user.

Fix:
- Open the Google Auth platform settings.
- Add the user email as a test user.
- Retry the login flow. Google’s testing-mode OAuth flow requires authorized test users. [web:65]

### Error: OAuth succeeds but sync fails

Cause:
The Drive API may not be enabled, the scopes may be insufficient, or the token may not have the permissions the sync operation needs.

Fix:
- Confirm Google Drive API is enabled. [web:66]
- Confirm your scopes match what the app requests. Google documents `drive.metadata.readonly` as the metadata scope for viewing file metadata without file content access. [web:59][web:62][web:68]
- Reconnect the account after changing scopes.

### Error: wrong account connected

Cause:
The browser session may have selected a different signed-in Google account.

Fix:
- Sign out of the unintended Google account in the browser, or
- use an incognito/private window and sign in only with the intended account.

### Error: account added in app but login URL fails

Cause:
The `user_id` in the URL does not match a valid stored account id.

Fix:
- Run `python -m drive_fusion.cli accounts` again.
- Copy the exact `id` value.
- Retry the URL with that id. [page:1]

## Recommended README wording

The current README sentence can be expanded into clearer end-user instructions.

Suggested replacement:

1. Add an account in the CLI or GUI and note its `id`. [page:1]
2. Open `http://127.0.0.1:8000/auth/login?user_id=<account_id>` in your browser. [page:1]
3. Sign in to Google and approve the Drive Fusion consent screen. [page:1]
4. After you return to the app, sync the account:

```bash
curl -X POST http://127.0.0.1:8000/api/accounts/<account_id>/sync
```

5. Refresh the dashboard or call `/api/quota` and `/api/files` to verify that live quota and metadata were imported. [page:1]

## Maintainer note

This guide should be linked from `README.md`, `RUNNING.md`, and any future Settings or Setup page in the GUI. The repository already has a growing setup surface and live OAuth support, so a dedicated guide reduces onboarding friction and makes troubleshooting much easier. [page:1]
