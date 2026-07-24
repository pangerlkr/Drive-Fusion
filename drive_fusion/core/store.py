"""Simple JSON-backed persistence for the prototype."""
import json
import os
from typing import Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
STATE_FILE = os.path.join(DATA_DIR, "state.json")

DEFAULT_STATE: dict[str, Any] = {
    "accounts": [
        {"id": "acct-primary", "name": "Primary", "email": "primary@example.com", "used_gb": 9.5, "total_gb": 15.0},
        {"id": "acct-archive", "name": "Archive", "email": "archive@example.com", "used_gb": 3.2, "total_gb": 15.0},
    ],
    "files": [
        {"id": "file-001", "name": "security-audit.pdf", "account_id": "acct-primary", "size_mb": 4.2, "mime_type": "application/pdf"},
        {"id": "file-002", "name": "portfolio-notes.docx", "account_id": "acct-primary", "size_mb": 1.1, "mime_type": "application/msword"},
        {"id": "file-003", "name": "backup-2026.zip", "account_id": "acct-archive", "size_mb": 512.0, "mime_type": "application/zip"},
    ],
    "jobs": [],
}


def _ensure_state_file() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w", encoding="utf-8") as fh:
            json.dump(DEFAULT_STATE, fh, indent=2)


def load_state() -> dict[str, Any]:
    _ensure_state_file()
    with open(STATE_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_state(state: dict[str, Any]) -> None:
    _ensure_state_file()
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)
