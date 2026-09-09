"""Signed, HttpOnly session cookie.

Deliberately minimal: the cookie carries only `user_id` (as a signed,
timestamped token — itsdangerous, keyed by SESSION_SECRET). Every protected
access re-reads the user (and their subscription) from PostgreSQL, so a
user disabled in the database is blocked immediately even if their cookie
is still valid — the cookie is just a pointer, never the source of truth.
"""
from __future__ import annotations

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from fastapi import Request, Response

from src.core import config

_SALT = "wm-auth-session-v1"


def _serializer() -> URLSafeTimedSerializer:
    if not config.SESSION_SECRET:
        raise RuntimeError(
            "SESSION_SECRET n'est pas configuré. Renseigne-le dans .env (voir .env.example)."
        )
    return URLSafeTimedSerializer(config.SESSION_SECRET, salt=_SALT)


def set_user_session(response: Response, user_id) -> None:
    token = _serializer().dumps(str(user_id))
    response.set_cookie(
        key=config.SESSION_COOKIE_NAME,
        value=token,
        max_age=config.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        secure=(config.APP_ENV == "production"),
        path="/",
    )


def get_session_user_id(request: Request) -> str | None:
    raw = request.cookies.get(config.SESSION_COOKIE_NAME)
    if not raw:
        return None
    try:
        return _serializer().loads(raw, max_age=config.SESSION_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None


def clear_user_session(response: Response) -> None:
    response.delete_cookie(config.SESSION_COOKIE_NAME, path="/")
