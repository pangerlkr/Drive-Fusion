"""SQLAlchemy-backed persistence for Drive Fusion.

Replaces the prototype's local JSON state file (data/state.json) with a
real database (SQLite by default, PostgreSQL in production via DATABASE_URL).
On first run, if the database is empty and a legacy data/state.json file
exists, its contents are migrated in automatically so existing local
development setups keep their data.
"""
import json
import os
from typing import Any, Optional

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

LEGACY_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
)
LEGACY_STATE_FILE = os.path.join(LEGACY_DATA_DIR, "state.json")

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{LEGACY_DATA_DIR}/drive_fusion.db")

# Render/Heroku-style URLs sometimes use postgres:// which SQLAlchemy 2.x
# no longer accepts directly.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

os.makedirs(LEGACY_DATA_DIR, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class AccountModel(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    used_gb = Column(Float, default=0.0)
    total_gb = Column(Float, default=15.0)


class FileModel(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    size_mb = Column(Float, default=0.0)
    mime_type = Column(String, default="")


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    source_account = Column(String, nullable=False)
    target_account = Column(String, nullable=False)
    file_ids_json = Column(Text, default="[]")
    note = Column(String, nullable=True)
    status = Column(String, default="pending")
    results_json = Column(Text, default="[]")


def init_db() -> None:
    """Create tables if they don't exist, then migrate legacy JSON state
    into the database on first run (only if the accounts table is empty).
    """
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        has_accounts = session.query(AccountModel).first() is not None
        if not has_accounts and os.path.exists(LEGACY_STATE_FILE):
            _migrate_legacy_json(session)


def _migrate_legacy_json(session: Session) -> None:
    with open(LEGACY_STATE_FILE, "r", encoding="utf-8") as fh:
        legacy = json.load(fh)
    for account in legacy.get("accounts", []):
        session.merge(
            AccountModel(
                id=account["id"],
                name=account["name"],
                email=account["email"],
                used_gb=account.get("used_gb", 0.0),
                total_gb=account.get("total_gb", 15.0),
            )
        )
    for file in legacy.get("files", []):
        session.merge(
            FileModel(
                id=file["id"],
                name=file["name"],
                account_id=file["account_id"],
                size_mb=file.get("size_mb", 0.0),
                mime_type=file.get("mime_type", ""),
            )
        )
    for job in legacy.get("jobs", []):
        session.merge(
            JobModel(
                id=job["id"],
                source_account=job["source_account"],
                target_account=job["target_account"],
                file_ids_json=json.dumps(job.get("file_ids", [])),
                note=job.get("note"),
                status=job.get("status", "pending"),
                results_json=json.dumps(job.get("results", [])),
            )
        )
    session.commit()


def load_state() -> dict[str, Any]:
    """Load all rows and shape them into the same dict structure the rest
    of the app (service.py) already expects, to minimize call-site changes.
    """
    init_db()
    with SessionLocal() as session:
        accounts = [
            {
                "id": a.id,
                "name": a.name,
                "email": a.email,
                "used_gb": a.used_gb,
                "total_gb": a.total_gb,
            }
            for a in session.query(AccountModel).all()
        ]
        files = [
            {
                "id": f.id,
                "name": f.name,
                "account_id": f.account_id,
                "size_mb": f.size_mb,
                "mime_type": f.mime_type,
            }
            for f in session.query(FileModel).all()
        ]
        jobs = [
            {
                "id": j.id,
                "source_account": j.source_account,
                "target_account": j.target_account,
                "file_ids": json.loads(j.file_ids_json or "[]"),
                "note": j.note,
                "status": j.status,
                "results": json.loads(j.results_json or "[]"),
            }
            for j in session.query(JobModel).all()
        ]
    return {"accounts": accounts, "files": files, "jobs": jobs}


def save_state(state: dict[str, Any]) -> None:
    """Persist the full in-memory state dict back to the database.

    This mirrors the JSON store's replace-everything semantics so
    service.py doesn't need structural changes: each call re-syncs all
    accounts/files/jobs from the given state.
    """
    with SessionLocal() as session:
        session.query(AccountModel).delete()
        session.query(FileModel).delete()
        session.query(JobModel).delete()
        for account in state.get("accounts", []):
            session.add(
                AccountModel(
                    id=account["id"],
                    name=account["name"],
                    email=account["email"],
                    used_gb=account.get("used_gb", 0.0),
                    total_gb=account.get("total_gb", 15.0),
                )
            )
        for file in state.get("files", []):
            session.add(
                FileModel(
                    id=file["id"],
                    name=file["name"],
                    account_id=file["account_id"],
                    size_mb=file.get("size_mb", 0.0),
                    mime_type=file.get("mime_type", ""),
                )
            )
        for job in state.get("jobs", []):
            session.add(
                JobModel(
                    id=job["id"],
                    source_account=job["source_account"],
                    target_account=job["target_account"],
                    file_ids_json=json.dumps(job.get("file_ids", [])),
                    note=job.get("note"),
                    status=job.get("status", "pending"),
                    results_json=json.dumps(job.get("results", [])),
                )
            )
        session.commit()

