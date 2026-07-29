"""FastAPI backend and dashboard for Drive Fusion."""
import os

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from drive_fusion.core.service import DriveFusionService
from drive_fusion.auth.routes import router as auth_router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

app = FastAPI(title="Drive Fusion")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

service = DriveFusionService()
app.include_router(auth_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/accounts")
def api_accounts():
    return service.list_accounts()


@app.post("/api/accounts")
def api_add_account(name: str = Form(...), email: str = Form(...), total_gb: float = Form(15.0)):
    return service.add_account(name, email, total_gb)


@app.get("/api/files")
def api_files(q: str | None = None):
    return service.list_files(q)


@app.get("/api/quota")
def api_quota():
    return service.usage_summary()


@app.get("/api/jobs")
def api_jobs():
    return service.list_jobs()


@app.post("/api/jobs")
def api_create_job(
    source_account: str = Form(...),
    target_account: str = Form(...),
    file_ids: str = Form(...),
    note: str = Form(""),
):
    ids = [f.strip() for f in file_ids.split(",") if f.strip()]
    return service.create_transfer_job(source_account, target_account, ids, note or None)


@app.post("/api/jobs/{job_id}/retry")
def api_retry_job(job_id: str):
    """Retry only the failed files from a previous transfer job."""
    try:
        return service.retry_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/api/accounts/{account_id}/sync")
def api_sync_account(account_id: str):
    """Pull live quota and file metadata from Google Drive for one account."""
    try:
        return service.sync_account(account_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/sync")
def api_sync_all():
    """Sync every connected account from the live Google Drive API."""
    return service.sync_all_accounts()


@app.get("/")
def dashboard(request: Request):
    context = {
        "request": request,
        "summary": service.usage_summary(),
        "accounts": service.list_accounts(),
        "files": service.list_files(),
        "jobs": service.list_jobs(),
    }
    return templates.TemplateResponse("dashboard.html", context)


@app.post("/ui/accounts")
def ui_add_account(name: str = Form(...), email: str = Form(...), total_gb: float = Form(15.0)):
    service.add_account(name, email, total_gb)
    return RedirectResponse(url="/", status_code=303)


@app.post("/ui/jobs")
def ui_create_job(
    source_account: str = Form(...),
    target_account: str = Form(...),
    file_ids: str = Form(...),
    note: str = Form(""),
):
    ids = [f.strip() for f in file_ids.split(",") if f.strip()]
    service.create_transfer_job(source_account, target_account, ids, note or None)
    return RedirectResponse(url="/", status_code=303)


@app.post("/ui/jobs/{job_id}/retry")
def ui_retry_job(job_id: str):
    try:
        service.retry_job(job_id)
    except ValueError:
        pass
    return RedirectResponse(url="/", status_code=303)


@app.post("/ui/accounts/{account_id}/sync")
def ui_sync_account(account_id: str):
    try:
        service.sync_account(account_id)
    except ValueError:
        pass
    return RedirectResponse(url="/", status_code=303)


@app.post("/ui/sync")
def ui_sync_all():
    """Sync every connected account and return to the dashboard."""
    service.sync_all_accounts()
    return RedirectResponse(url="/", status_code=303)
