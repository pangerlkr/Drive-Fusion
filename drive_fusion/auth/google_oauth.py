"""Google OAuth 2.0 flow helpers for connecting Drive accounts.

Requires environment variables (see .env.example):
  GOOGLE_CLIENT_ID
  GOOGLE_CLIENT_SECRET
  GOOGLE_REDIRECT_URI

Credentials come from a Google Cloud OAuth client that you create yourself
at https://console.cloud.google.com/apis/credentials
"""
import os
from typing import Optional

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]


def _client_config() -> dict:
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/auth/callback")
    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }


def is_configured() -> bool:
    """True once real Google OAuth credentials are present in the environment."""
    return bool(os.environ.get("GOOGLE_CLIENT_ID")) and bool(os.environ.get("GOOGLE_CLIENT_SECRET"))


def build_flow(state: Optional[str] = None) -> Flow:
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/auth/callback")
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, state=state)
    flow.redirect_uri = redirect_uri
    return flow


def get_authorization_url() -> tuple[str, str]:
    flow = build_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return auth_url, state


def exchange_code_for_credentials(code: str, state: str) -> Credentials:
    flow = build_flow(state=state)
    flow.fetch_token(code=code)
    return flow.credentials


def credentials_to_dict(creds: Credentials) -> dict:
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }
