"""Personal (per-user) analysis history — the V3 read path for /app/historique.

PostgreSQL is now the source of truth for the FastAPI SaaS UI. The legacy
`src/web/historique_service.py` (global JSON file) is untouched and keeps
serving the independent Streamlit UI — this module never reads or writes
that file.

Records are formatted into the exact same dict shape the existing history
template/JS already expect (titre, client, secteur, decision, score,
budget, techs, date, resultat, job_id), so no frontend change was needed
beyond swapping the data source.
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from src.web.database.models import Analysis
from src.web.database.repositories import analyses as analyses_repo


def _format_record(analysis: Analysis) -> dict:
    # Migrated legacy rows with no real job_id get a synthetic
    # "legacy:..." key purely for dedup (see scripts/migrate_history_to_postgresql.py)
    # — never expose that as an openable link.
    job_id = analysis.job_id if analysis.job_id and not analysis.job_id.startswith("legacy:") else None
    return {
        "ao_id": analysis.job_id or str(analysis.id),
        "titre": analysis.title or "",
        "client": analysis.client_name or "",
        "secteur": analysis.sector or "Non renseigne",
        "decision": analysis.decision or "",
        "score": float(analysis.score) if analysis.score is not None else 0,
        "budget": analysis.budget,
        "techs": analysis.technologies or [],
        "date": analysis.created_at.strftime("%d/%m/%Y %H:%M"),
        "resultat": "en attente",
        "job_id": job_id,
    }


def list_for_user(db: Session, user_id: uuid.UUID) -> list[dict]:
    return [_format_record(a) for a in analyses_repo.list_for_user(db, user_id)]


def sidebar_stats(db: Session, user_id: uuid.UUID) -> dict:
    records = list_for_user(db, user_id)
    return {
        "total": len(records),
        "go": sum(1 for r in records if r["decision"] == "GO"),
        "reserve": sum(1 for r in records if "RESERVE" in (r["decision"] or "").upper()),
        "nogo": sum(1 for r in records if r["decision"] == "NO-GO"),
    }
