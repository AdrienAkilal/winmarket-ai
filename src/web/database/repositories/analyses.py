"""Pure data-access functions for `analyses` and `analysis_documents`.

Callers (src/web/jobs.py) are responsible for turning AOContext/ScoringResult
into plain fields before calling create_analysis — this module has no
knowledge of the pipeline's business models, only of the SQL rows.
"""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.web.database.models import Analysis, AnalysisDocument


def create_analysis(
    db: Session,
    *,
    user_id: uuid.UUID,
    result_data: dict[str, Any],
    job_id: str | None = None,
    title: str | None = None,
    client_name: str | None = None,
    sector: str | None = None,
    score: float | None = None,
    decision: str | None = None,
    budget: str | None = None,
    technologies: list[str] | None = None,
    summary_data: dict[str, Any] | None = None,
) -> Analysis:
    analysis = Analysis(
        user_id=user_id,
        job_id=job_id,
        title=(title or "")[:500] or None,
        client_name=(client_name or "")[:255] or None,
        sector=(sector or "")[:100] or None,
        score=score,
        decision=(decision or "")[:30] or None,
        budget=(str(budget) if budget is not None else None),
        technologies=technologies or None,
        result_data=result_data,
        summary_data=summary_data,
    )
    db.add(analysis)
    db.flush()
    return analysis


def get_by_job_id(db: Session, job_id: str) -> Analysis | None:
    stmt = select(Analysis).where(Analysis.job_id == job_id)
    return db.execute(stmt).scalar_one_or_none()


def get_by_id_for_user(db: Session, analysis_id: uuid.UUID | str, user_id: uuid.UUID) -> Analysis | None:
    """Ownership-checked lookup — never returns another user's analysis."""
    stmt = select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def list_for_user(db: Session, user_id: uuid.UUID, limit: int = 200) -> list[Analysis]:
    stmt = (
        select(Analysis)
        .where(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


def add_document(
    db: Session,
    *,
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    filename: str | None,
    original_filename: str | None,
    storage_path: str,
    mime_type: str | None,
    file_size: int | None,
) -> AnalysisDocument:
    doc = AnalysisDocument(
        analysis_id=analysis_id,
        user_id=user_id,
        filename=filename,
        original_filename=original_filename,
        storage_path=storage_path,
        mime_type=mime_type,
        file_size=file_size,
    )
    db.add(doc)
    db.flush()
    return doc
