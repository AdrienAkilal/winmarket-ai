"""WinMarket AI — FastAPI web interface.

This is the new HTML/CSS/JS + FastAPI front door for WinMarket AI. It is a
thin presentation layer: every route delegates to the existing modules
under src/agents, src/rag, src/livrables and src/core, which are frozen —
no business rule is reimplemented here.

The legacy Streamlit interface (src/ui/app.py) keeps working unchanged and
can still be launched independently; see README.md.

Run with:
    uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.web.routes_account import router as account_router
from src.web.routes_api import router as api_router
from src.web.routes_auth import router as auth_router
from src.web.routes_pages import router as pages_router
from fastapi.staticfiles import StaticFiles
from src.web.templating import templates

app = FastAPI(title="WinMarket AI", docs_url="/api/docs", redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(HTTPException)
async def html_http_exception_handler(request: Request, exc: HTTPException):
    """/api/* keeps plain JSON (existing clients expect it); every other
    route renders a normal page instead of raw JSON like
    {"detail":"Method Not Allowed"} — this is what a user hit when an
    already-open page's stale CSRF token 403'd and a refresh replayed the
    POST as a GET against a POST-only route.
    """
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return templates.TemplateResponse(
        request, "error.html",
        {"status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
    )


@app.middleware("http")
async def inject_current_user_state(request: Request, call_next):
    """Makes request.state.current_user / is_active_starter available to
    every template (Jinja2Templates always exposes `request`) so public
    pages (landing, header) can show the right CTA without each route
    wiring the lookup manually. This is informational only — it never
    blocks a request; /app/* and /api/* routes enforce access themselves
    (src/web/auth/dependencies.py) regardless of what this sets.
    """
    request.state.current_user = None
    request.state.is_active_starter = False

    from src.web.database.session import is_database_configured
    if is_database_configured():
        try:
            from src.web.auth.dependencies import get_current_user, user_has_active_starter_subscription
            from src.web.database.session import session_scope

            with session_scope() as db:
                user = get_current_user(request, db)
                request.state.current_user = user
                request.state.is_active_starter = user_has_active_starter_subscription(db, user)
        except Exception:
            pass  # never let this best-effort lookup break page rendering

    return await call_next(request)


app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(account_router)
app.include_router(api_router)
