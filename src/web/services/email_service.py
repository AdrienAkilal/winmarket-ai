"""Minimal SMTP admin-notification service.

If SMTP_HOST/SMTP_FROM_EMAIL are not configured, every function here is a
safe no-op: the underlying data (registration, contact request) is always
persisted by the caller first — only the notification email is skipped,
and that fact is logged, never raised as an error to the end user.
SMTP_PASSWORD is never logged or included in any message body.
"""
from __future__ import annotations

import smtplib
from email.message import EmailMessage

from src.core import config
from src.core.logger import get_agent_logger

logger = get_agent_logger("web_email")


def _smtp_configured() -> bool:
    return bool(config.SMTP_HOST and config.SMTP_FROM_EMAIL)


def send_admin_notification(subject: str, body: str) -> bool:
    """Returns True if actually sent, False if skipped or failed. Never raises."""
    if not config.ADMIN_NOTIFICATION_EMAIL:
        logger.warning("ADMIN_NOTIFICATION_EMAIL non configuré — notification ignorée (%s)", subject)
        return False
    if not _smtp_configured():
        logger.warning("SMTP non configuré — notification non envoyée (%s)", subject)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config.SMTP_FROM_EMAIL
    message["To"] = config.ADMIN_NOTIFICATION_EMAIL
    message.set_content(body)

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10) as server:
            server.starttls()
            if config.SMTP_USERNAME:
                server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.send_message(message)
        logger.info("Admin notification sent: %s", subject)
        return True
    except Exception:
        logger.exception("Failed to send admin notification: %s", subject)
        return False


def notify_new_starter_registration(user) -> bool:
    return send_admin_notification(
        subject=f"[WinMarket AI] Nouvelle inscription Starter — {user.email}",
        body=(
            "Nouveau compte Starter en attente de validation.\n\n"
            f"Nom : {user.full_name}\n"
            f"Email : {user.email}\n"
            f"Société : {user.company or '-'}\n\n"
            f"Activer : python scripts/activate_user.py {user.email}\n"
            f"Refuser : python scripts/reject_user.py {user.email}"
        ),
    )


def notify_new_contact_request(contact_request) -> bool:
    plan_label = (contact_request.plan or "?").capitalize()
    full_name = f"{contact_request.first_name or ''} {contact_request.last_name or ''}".strip() or "-"
    return send_admin_notification(
        subject=f"[WinMarket AI] Nouvelle demande de contact ({plan_label}) — {contact_request.email}",
        body=(
            "Nouvelle demande de contact.\n\n"
            f"Offre : {plan_label}\n"
            f"Nom : {full_name}\n"
            f"Email : {contact_request.email}\n"
            f"Société : {contact_request.company or '-'}\n"
            f"Fonction : {contact_request.job_title or '-'}\n"
            f"Nombre d'utilisateurs : {contact_request.employee_count or '-'}\n\n"
            f"Message :\n{contact_request.message or '-'}"
        ),
    )
