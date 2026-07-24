"""Data models for Drive Fusion."""
from pydantic import BaseModel
from typing import Optional


class Account(BaseModel):
    id: str
    name: str
    email: str
    used_gb: float = 0.0
    total_gb: float = 15.0


class DriveFile(BaseModel):
    id: str
    name: str
    account_id: str
    size_mb: float = 0.0
    mime_type: str = "application/octet-stream"


class TransferJob(BaseModel):
    id: str
    source_account: str
    target_account: str
    file_ids: list[str]
    note: Optional[str] = None
    status: str = "queued"
