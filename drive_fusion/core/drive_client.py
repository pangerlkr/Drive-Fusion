"""Thin wrapper around the Google Drive API v3 for live metadata sync.

Given valid OAuth Credentials for a connected account, this module can
fetch storage quota (About.get), list file metadata (Files.list),
and perform real copy/move operations (Files.copy / Files.update),
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


def get_file_metadata(creds: Credentials, file_id: str) -> dict[str, Any]:
    """Fetch name/mimeType/parents for a single file, used before transfer."""
    service = _drive_service(creds)
    return (
        service.files()
        .get(fileId=file_id, fields="id, name, mimeType, parents")
        .execute()
    )


def copy_file_between_accounts(
    source_creds: Credentials,
    target_creds: Credentials,
    file_id: str,
) -> dict[str, Any]:
    """Copy a file owned by one Google account into another account's Drive.

    The Drive API cannot copy across accounts directly, so this downloads
    the file's bytes using the source account's credentials and re-uploads
    them as a new file using the target account's credentials. Returns the
    newly created file's metadata (id, name, size_mb, mime_type).
    """
    import io

    from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

    source_service = _drive_service(source_creds)
    target_service = _drive_service(target_creds)

    meta = (
        source_service.files()
        .get(fileId=file_id, fields="id, name, mimeType")
        .execute()
    )
    name = meta["name"]
    mime_type = meta.get("mimeType", "application/octet-stream")

    if mime_type.startswith("application/vnd.google-apps"):
        # Google Docs/Sheets/Slides must be exported, not downloaded raw.
        export_mime = "application/pdf"
        request = source_service.files().export_media(
            fileId=file_id, mimeType=export_mime
        )
        upload_mime = export_mime
        upload_name = f"{name}.pdf"
    else:
        request = source_service.files().get_media(fileId=file_id)
        upload_mime = mime_type
        upload_name = name

    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)

    media = MediaIoBaseUpload(buffer, mimetype=upload_mime, resumable=False)
    created = (
        target_service.files()
        .create(body={"name": upload_name}, media_body=media, fields="id, name, size, mimeType")
        .execute()
    )
    size_bytes = float(created.get("size", 0) or 0)
    return {
        "id": created["id"],
        "name": created["name"],
        "size_mb": round(size_bytes / (1024 ** 2), 2),
        "mime_type": created.get("mimeType", upload_mime),
    }
