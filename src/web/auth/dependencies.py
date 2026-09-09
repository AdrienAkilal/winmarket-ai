"""Central access-control logic.

Two flavors are provided, matching the two kinds of routes in this app:

- For `/api/*` JSON routes: FastAPI dependencies (`require_authenticated_user`,
  `require_active_starter_user`) that raise a generic HTTPException.
- For `/app/*` HTML page routes: `resolve_app_access()`, called explicitly at
  the top of each route, which returns either the User or a ready-to-return
  RedirectResponse (to /login?next=..., or /account/pending) — pages don't
  want a raw JSON 401/403, they want a redirect.

Every check re-reads status from PostgreSQL on every request — the session
cookie only carries a user_id pointer, never the authority.
"""
from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.web.auth.session_cookie import get_session_user_id
from src.web.database.models import User
from src.web.database.repositories import subscriptions as subscriptions_repo
from src.web.database.repositories import users as users_repo
from src.web.database.session import get_db


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Best-effort lookup — returns None for anonymous or invalid sessions."""
    raw_user_id = get_session_user_id(request)
    if not raw_user_id:
        return None
    try:
        user_id = uuid.UUID(raw_user_id)
    except ValueError:
        return None
    return users_repo.get_by_id(db, user_id)


def require_authenticated_user(user: User | None = Depends(get_current_user)) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentification requise.")
    return user


def user_has_active_starter_subscription(db: Session, user: User | None) -> bool:
    """Shared predicate — used by the API gate, the page gate, and the
    landing/header template context (to decide which CTAs to show)."""
    if user is None or user.status != "active":
        return False
    subscription = subscriptions_repo.get_latest_for_user(db, user.id)
    return bool(subscription and subscription.plan == "starter" and subscription.status == "active")


def require_active_starter_user(
    user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> User:
    """The gate every /api/* route that touches user data must depend on."""
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte non actif.")
    if not user_has_active_starter_subscription(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Abonnement Starter actif requis.")
    return user


def resolve_app_access(request: Request, db: Session) -> tuple[User | None, RedirectResponse | None]:
    """For HTML page routes. Usage:

        user, redirect = resolve_app_access(request, db)
        if redirect:
            return redirect
    """
    user = get_current_user(request, db)
    if user is None:
        return None, RedirectResponse(f"/login?next={request.url.path}", status_code=303)
    if user.status == "pending":
        return None, RedirectResponse("/account/pending", status_code=303)
    if user.status in ("rejected", "disabled"):
        return None, RedirectResponse("/login?blocked=1", status_code=303)

    if not user_has_active_starter_subscription(db, user):
        return None, RedirectResponse("/account/pending", status_code=303)

    return user, None
