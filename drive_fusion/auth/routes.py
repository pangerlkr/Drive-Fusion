"""FastAPI routes for the Google OAuth login flow.

Exposes:
    GET /auth/login     -> redirects the user to Google's consent screen
    GET /auth/callback  -> handles the OAuth redirect, exchanges the code
                            for credentials, and stores them for the user
    POST /auth/logout    -> deletes stored credentials for the user

Wire this router into your app with:
    app.include_router(router)
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from .google_oauth import exchange_code_for_credentials, get_authorization_url
from .token_store import delete_credentials, save_credentials

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory map of OAuth state -> user id, used to correlate the callback
# with the user who initiated the flow. Replace with a session/DB-backed
# store for multi-instance deployments.
_pending_states: dict[str, str] = {}


@router.get("/login")
def login(user_id: str) -> RedirectResponse:
    auth_url, state = get_authorization_url()
    _pending_states[state] = user_id
    return RedirectResponse(auth_url)


@router.get("/callback")
def callback(request: Request) -> dict:
    params = request.query_params
    code = params.get("code")
    state = params.get("state")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")

    user_id = _pending_states.pop(state, None)
    if not user_id:
        raise HTTPException(status_code=400, detail="Unknown or expired state")

    creds = exchange_code_for_credentials(code=code, state=state)
    save_credentials(user_id, creds)
    return {"status": "connected", "user_id": user_id}


@router.post("/logout")
def logout(user_id: str) -> dict:
    delete_credentials(user_id)
    return {"status": "disconnected", "user_id": user_id}
