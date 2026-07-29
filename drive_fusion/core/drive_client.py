"""Thin wrapper around the Google Drive API v3 for live metadata sync.

Given valid OAuth Credentials for a connected account, this module can
fetch storage quota (About.get) and list file metadata (Files.list),
normalizing results into the shapes used by DriveFusionService/state.
"""
from typing import Any, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

BYTES_PER_GB = 1024 ** 3


def _drive_service(creds: Credentials):
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def fetch_quota(creds: Credentials) -> dict[str, float]:
    """Return used/total storage in GB for the account behind `creds`."""
    service = _drive_service(creds)
    about = service.about().get(fields="storageQuota").execute()
    quota = about.get("storageQuota", {})
    used_bytes = float(quota.get("usage", 0))
    total_bytes = quota.get("limit")
    total_gb = float(total_bytes) / BYTES_PER_GB if total_bytes else 15.0
    return {
        "used_gb": round(used_bytes / BYTES_PER_GB, 2),
        "total_gb": round(total_gb, 2),
    }


def fetch_files(
    creds: Credentials,
    account_id: str,
    query: Optional[str] = None,
    page_size: int = 100,
) -> list[dict[str, Any]]:
    """List file metadata for the account behind `creds`.

    Results are normalized to the DriveFile shape used elsewhere in the
    app: id, name, account_id, size_mb, mime_type.
    """
    service = _drive_service(creds)
    q = None
    if query:
        safe_query = query.replace("'", "\\'")
        q = f"name contains '{safe_query}' and trashed = false"
    else:
        q = "trashed = false"

    files: list[dict[str, Any]] = []
    page_token = None
    while True:
        response = (
            service.files()
            .list(
                q=q,
                pageSize=page_size,
                fields="nextPageToken, files(id, name, size, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )
        for f in response.get("files", []):
            size_bytes = float(f.get("size", 0) or 0)
            files.append(
                {
                    "id": f["id"],
                    "name": f["name"],
                    "account_id": account_id,
                    "size_mb": round(size_bytes / (1024 ** 2), 2),
                    "mime_type": f.get("mimeType", "application/octet-stream"),
                }
            )
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return files


def is_reachable(creds: Credentials) -> bool:
    """Quick connectivity/permission check for a connected account."""
    try:
        _drive_service(creds).about().get(fields="user").execute()
        return True
    except HttpError:
        return False
