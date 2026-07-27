"""Simple per-user token storage for Google OAuth credentials.

Stores credentials as JSON on disk, keyed by user id. This is a minimal
implementation intended for local/dev use; swap for a database or secrets
manager in production.
"""
import json
import os
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials

from .google_oauth import SCOPES, credentials_to_dict

TOKEN_DIR = Path(os.environ.get("TOKEN_STORE_DIR", ".tokens"))


def _token_path(user_id: str) -> Path:
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = "".join(c for c in user_id if c.isalnum() or c in ("-", "_"))
    return TOKEN_DIR / f"{safe_id}.json"


def save_credentials(user_id: str, creds: Credentials) -> None:
    path = _token_path(user_id)
    with open(path, "w") as f:
        json.dump(credentials_to_dict(creds), f)


def load_credentials(user_id: str) -> Optional[Credentials]:
    path = _token_path(user_id)
    if not path.exists():
        return None
    with open(path, "r") as f:
        data = json.load(f)
    return Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes", SCOPES),
    )


def delete_credentials(user_id: str) -> None:
    path = _token_path(user_id)
    if path.exists():
        path.unlink()
