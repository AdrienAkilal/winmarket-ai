"""Account pages: /account, /account/pending, /forgot-password, /reset-password.

Password reset is deliberately minimal for V3 (see PASSWORD RESET note
below) — registration, login, session and history isolation are the
priority; sending the actual reset email is not wired up yet.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.logger import get_agent_logger
from src.web.auth import service as auth_service
from src.web.auth.dependencies import get_current_user
from src.web.database.models import PasswordResetToken, User
from src.web.database.repositories import subscriptions as subscriptions_repo
from src.web.database.repositories import users as users_repo
from src.web.database.session import get_db
from src.web.security.csrf import attach_csrf_cookie, get_or_create_csrf_token, require_csrf
from src.web.templating import templates

router = APIRouter()
logger = get_agent_logger("web_account")


@router.get("/account", response_class=HTMLResponse)
def account_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user is None:
        return RedirectResponse("/login?next=/account", status_code=303)

    subscription = subscriptions_repo.get_latest_for_user(db, user.id)
    token, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, "account.html", {
        "user": user, "subscription": subscription, "csrf_token": token, "saved": False,
    })
    if is_new:
        attach_csrf_cookie(resp, token)
    return resp


@router.post("/account", response_class=HTMLResponse)
def account_update(
    request: Request,
    db: Session = Depends(get_db),
    first_name: str = Form(...),
    last_name: str = Form(...),
    company: str = Form(""),
    job_title: str = Form(""),
    phone: str = Form(""),
    csrf_token: str = Form(...),
):
    require_csrf(request, csrf_token)
    user = get_current_user(request, db)
    if user is None:
        return RedirectResponse("/login?next=/account", status_code=303)

    user.first_name = first_name.strip() or user.first_name
    user.last_name = last_name.strip() or user.last_name
    user.company = company.strip() or None
    user.job_title = job_title.strip() or None
    user.phone = phone.strip() or None
    db.commit()

    subscription = subscriptions_repo.get_latest_for_user(db, user.id)
    token, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, "account.html", {
        "user": user, "subscription": subscription, "csrf_token": token, "saved": True,
    })
    if is_new:
        attach_csrf_cookie(resp, token)
    return resp


@router.get("/account/pending", response_class=HTMLResponse)
def account_pending_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    token, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, "account_pending.html", {"user": user, "csrf_token": token})
    if is_new:
        attach_csrf_cookie(resp, token)
    return resp


# ─── Password reset ─────────────────────────────────────────────────────────
# PASSWORD RESET STATUS: the structure (table, token generation, hashed
# storage, expiry, single-use) is implemented and functional end-to-end
# EXCEPT the actual email delivery, which is intentionally deferred until
# after the core SaaS flow (register/login/session/history isolation) is
# validated — see src/web/services/email_service.py. Today, the reset link
# is only logged server-side, never emailed to the user.

@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    token, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, "forgot_password.html", {"csrf_token": token, "submitted": False})
    if is_new:
        attach_csrf_cookie(resp, token)
    return resp


@router.post("/forgot-password", response_class=HTMLResponse)
def forgot_password_submit(request: Request, db: Session = Depends(get_db), email: str = Form(...), csrf_token: str = Form(...)):
    require_csrf(request, csrf_token)
    user = users_repo.get_by_email(db, email)
    if user is not None:
        raw_token = secrets.token_urlsafe(32)
        reset_row = PasswordResetToken(
            user_id=user.id,
            token_hash=auth_service.hash_password(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.add(reset_row)
        db.commit()
        # TODO(email): send `raw_token` via src/web/services/email_service.py
        # once SMTP is wired up. For now we only log that a reset was issued.
        logger.info("Password reset token issued user_id=%s (email delivery not yet implemented)", user.id)
    # Always the same response — do not reveal whether the email exists.
    token, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, "forgot_password.html", {"csrf_token": token, "submitted": True})
    if is_new:
        attach_csrf_cookie(resp, token)
    return resp


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request, token: str = ""):
    csrf, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, "reset_password.html", {
        "csrf_token": csrf, "reset_token": token, "error": None, "done": False,
    })
    if is_new:
        attach_csrf_cookie(resp, csrf)
    return resp


@router.post("/reset-password", response_class=HTMLResponse)
def reset_password_submit(
    request: Request,
    db: Session = Depends(get_db),
    reset_token: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    csrf_token: str = Form(...),
):
    require_csrf(request, csrf_token)

    def render_error(message: str):
        csrf, is_new = get_or_create_csrf_token(request)
        resp = templates.TemplateResponse(request, "reset_password.html", {
            "csrf_token": csrf, "reset_token": reset_token, "error": message, "done": False,
        })
        if is_new:
            attach_csrf_cookie(resp, csrf)
        return resp

    if password != password_confirm:
        return render_error("Les mots de passe ne correspondent pas.")
    strength_error = auth_service.password_strength_error(password)
    if strength_error:
        return render_error(strength_error)

    now = datetime.now(timezone.utc)
    candidates = db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
    ).scalars().all()

    matched: PasswordResetToken | None = None
    for candidate in candidates:
        if auth_service.verify_password(reset_token, candidate.token_hash):
            matched = candidate
            break

    if matched is None:
        return render_error("Ce lien de réinitialisation est invalide ou a expiré.")

    user = users_repo.get_by_id(db, matched.user_id)
    if user is None:
        return render_error("Ce lien de réinitialisation est invalide ou a expiré.")

    user.password_hash = auth_service.hash_password(password)
    matched.used_at = now
    db.commit()

    csrf, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, "reset_password.html", {
        "csrf_token": csrf, "reset_token": "", "error": None, "done": True,
    })
    if is_new:
        attach_csrf_cookie(resp, csrf)
    return resp
