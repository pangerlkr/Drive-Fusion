"""Core service layer shared by CLI and API."""
import uuid
from typing import Optional

from drive_fusion.core.store import load_state, save_state


class DriveFusionService:
    def __init__(self):
        self.state = load_state()

    def _persist(self):
        save_state(self.state)

    def list_accounts(self):
        return self.state["accounts"]

    def add_account(self, name: str, email: str, total_gb: float = 15.0):
        account = {
            "id": f"acct-{uuid.uuid4().hex[:8]}",
            "name": name,
            "email": email,
            "used_gb": 0.0,
            "total_gb": total_gb,
        }
        self.state["accounts"].append(account)
        self._persist()
        return account

    def list_files(self, query: Optional[str] = None):
        files = self.state["files"]
        if query:
            q = query.lower()
            files = [f for f in files if q in f["name"].lower()]
        return files

    def usage_summary(self):
        accounts = self.state["accounts"]
        used = sum(a["used_gb"] for a in accounts)
        total = sum(a["total_gb"] for a in accounts)
        free = total - used
        utilization = round((used / total) * 100, 1) if total else 0.0
        return {
            "used_gb": round(used, 2),
            "total_gb": round(total, 2),
            "free_gb": round(free, 2),
            "utilization_pct": utilization,
            "account_count": len(accounts),
        }

    def list_jobs(self):
        return self.state["jobs"]

    def create_transfer_job(self, source_account: str, target_account: str, file_ids: list[str], note: Optional[str] = None):
        job = {
            "id": f"job-{uuid.uuid4().hex[:8]}",
            "source_account": source_account,
            "target_account": target_account,
            "file_ids": file_ids,
            "note": note,
            "status": "completed",
        }
        self.state["jobs"].append(job)
        self._persist()
        return job

    def export_report(self) -> str:
        summary = self.usage_summary()
        lines = ["# Drive Fusion Workspace Report", ""]
        lines.append(f"- Total accounts: {summary['account_count']}")
        lines.append(f"- Used: {summary['used_gb']} GB")
        lines.append(f"- Free: {summary['free_gb']} GB")
        lines.append(f"- Utilization: {summary['utilization_pct']}%")
        lines.append("")
        lines.append("## Accounts")
        for a in self.state["accounts"]:
            lines.append(f"- {a['name']} ({a['email']}): {a['used_gb']}/{a['total_gb']} GB")
        lines.append("")
        lines.append("## Jobs")
        for j in self.state["jobs"]:
            lines.append(f"- {j['id']}: {j['source_account']} -> {j['target_account']} [{j['status']}]")
        return "\n".join(lines)
