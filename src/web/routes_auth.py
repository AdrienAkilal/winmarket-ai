"""Authentication routes: /login, /register, /logout.

Thin on purpose — validation and persistence live in src/web/auth/service.py
and the repositories; this module only wires HTTP (forms, cookies, CSRF,
redirects) to that logic.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.core.logger import get_agent_logger
from src.web.auth import service as auth_service
from src.web.auth.session_cookie import clear_user_session, set_user_session
from src.web.database.repositories import users as users_repo
from src.web.database.session import get_db
from src.web.security.csrf import attach_csrf_cookie, get_or_create_csrf_token, require_csrf
from src.web.security.rate_limit import is_rate_limited, record_attempt, reset as reset_rate_limit
from src.web.templating import templates

router = APIRouter()
logger = get_agent_logger("web_auth")


def _safe_next(next_url: str | None) -> str:
    """Only ever redirect to a relative, in-app path — never an open redirect."""
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return next_url
    return "/app"


# ─── Login ──────────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next: str = "/app", blocked: str = ""):
    token, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, "login.html", {
        "csrf_token": token,
        "next": _safe_next(next),
        "error": "Votre compte est temporairement bloqué." if blocked else None,
    })
    if is_new:
        attach_csrf_cookie(resp, token)
    return resp


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/app"),
    csrf_token: str = Form(...),
):
    require_csrf(request, csrf_token)
    next_url = _safe_next(next)

    client_host = request.client.host if request.client else "unknown"
    rate_key = f"{(email or '').strip().lower()}:{client_host}"

    def render_error(message: str):
        token, is_new = get_or_create_csrf_token(request)
        resp = templates.TemplateResponse(request, "login.html", {
            "csrf_token": token, "next": next_url, "error": message, "email": email,
        })
        if is_new:
            attach_csrf_cookie(resp, token)
        return resp

    if is_rate_limited(rate_key):
        logger.warning("Login rate-limited")
        return render_error("Trop de tentatives. Réessayez dans une minute.")

    user = auth_service.authenticate(db, email=email, password=password)
    if user is None:
        record_attempt(rate_key)
        return render_error("Email ou mot de passe incorrect.")

    if user.status in ("rejected", "disabled"):
        # Deliberately the same generic message — no account-status leak.
        record_attempt(rate_key)
        return render_error("Email ou mot de passe incorrect.")

    reset_rate_limit(rate_key)
    users_repo.record_login(db, user)
    db.commit()

    redirect_url = "/account/pending" if user.status == "pending" else next_url
    resp = RedirectResponse(url=redirect_url, status_code=303)
    set_user_session(resp, user.id)
    return resp


# ─── Register ───────────────────────────────────────────────────────────────

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    token, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, "register.html", {"csrf_token": token, "error": None})
    if is_new:
        attach_csrf_cookie(resp, token)
    return resp


@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    db: Session = Depends(get_db),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    company: str = Form(""),
    job_title: str = Form(""),
    phone: str = Form(""),
    password: str = Form(...),
    password_confirm: str = Form(...),
    accept_terms: str = Form(""),
    csrf_token: str = Form(...),
):
    require_csrf(request, csrf_token)

    def render_error(message: str):
        token, is_new = get_or_create_csrf_token(request)
        resp = templates.TemplateResponse(request, "register.html", {
            "csrf_token": token, "error": message,
            "first_name": first_name, "last_name": last_name, "email": email,
            "company": company, "job_title": job_title, "phone": phone,
        })
        if is_new:
            attach_csrf_cookie(resp, token)
        return resp

    if not accept_terms:
        return render_error("Vous devez accepter les conditions d'utilisation et la politique de confidentialité.")

    try:
        user = auth_service.register_starter_user(
            db, email=email, password=password, password_confirm=password_confirm,
            first_name=first_name, last_name=last_name,
            company=company, job_title=job_title, phone=phone,
        )
        db.commit()
    except auth_service.RegistrationError as exc:
        db.rollback()
        return render_error(str(exc))

    logger.info("New starter registration user_id=%s", user.id)
    try:
        from src.web.services.email_service import notify_new_starter_registration
        notify_new_starter_registration(user)
    except Exception:
        logger.exception("Failed to send new-registration admin notification")

    resp = RedirectResponse(url="/account/pending", status_code=303)
    set_user_session(resp, user.id)
    return resp


# ─── Logout ─────────────────────────────────────────────────────────────────

@router.post("/logout")
def logout_submit(request: Request, csrf_token: str = Form(...)):
    require_csrf(request, csrf_token)
    resp = RedirectResponse(url="/", status_code=303)
    clear_user_session(resp)
    return resp
