"""JSON API — thin routes that only validate input and call existing services.

No scoring, RAG, LLM or business logic lives in this file: every route
either delegates to src/web/jobs.py (which itself only orchestrates the
existing src/agents, src/rag and src/livrables modules) or to a repository
class that already existed before this migration (CapacityRepository,
LocalRAGManager).

V3: every route below is gated behind an authenticated, active Starter
user (require_active_starter_user) except /api/contact, which anonymous
prospects use. Analysis-scoped routes additionally verify ownership —
a user can only ever see their own jobs/downloads.
"""
from __future__ import annotations

import csv
import io
import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from src.core.capacity_repository import CapacityPlan, CapacityRepository
from src.core.logger import get_agent_logger
from src.web import examples_service, jobs, knowledge_service
from src.web.auth.dependencies import require_active_starter_user
from src.web.database.models import User
from src.web.database.repositories import contacts as contacts_repo
from src.web.database.session import get_db
from src.web.pipeline_singleton import get_pipeline
from src.web.security.csrf import require_csrf
from src.web.services import history_service
from src.web.services.email_service import notify_new_contact_request

router = APIRouter(prefix="/api")
logger = get_agent_logger("web_api")

ALLOWED_UPLOAD_SUFFIXES = {".pdf", ".txt", ".md", ".docx"}


@router.get("/examples")
def api_list_examples(current_user: User = Depends(require_active_starter_user)):
    return {"examples": examples_service.list_examples()}


@router.get("/examples/{example_id}")
def api_read_example(example_id: str, current_user: User = Depends(require_active_starter_user)):
    text = examples_service.read_example(example_id)
    if text is None:
        raise HTTPException(404, "Exemple introuvable.")
    return {"id": example_id, "text": text}


@router.post("/analyze")
async def api_analyze(
    mode: str = Form(...),
    example_id: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_active_starter_user),
):
    if mode == "stock":
        if not example_id:
            raise HTTPException(400, "Aucun exemple sélectionné.")
        content = examples_service.read_example(example_id)
        if content is None:
            raise HTTPException(404, "Exemple introuvable.")
        source_label = f"Exemple : {example_id.replace('_', ' ')}"

    elif mode == "upload":
        if file is None or not file.filename:
            raise HTTPException(400, "Aucun fichier fourni.")
        suffix = Path(file.filename).suffix.lower()
        if suffix not in ALLOWED_UPLOAD_SUFFIXES:
            raise HTTPException(400, "Format non supporté. Formats acceptés : PDF, DOCX, TXT, MD.")
        raw = await file.read()
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(raw)
                tmp_path = tmp.name
            from src.agents.ao_extractor import read_document
            content = read_document(tmp_path)
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        source_label = f"Fichier : {file.filename}"

    elif mode == "paste":
        if not text or not text.strip():
            raise HTTPException(400, "Le texte de l'appel d'offres est vide.")
        content = text
        source_label = "Texte collé"

    else:
        raise HTTPException(400, "Mode de source invalide.")

    job = jobs.create_job(source_label=source_label, user_id=current_user.id)
    jobs.start_analysis(job, content)
    return {"job_id": job.id}


@router.get("/analyze/{job_id}/status")
def api_analyze_status(job_id: str, current_user: User = Depends(require_active_starter_user)):
    job = jobs.get_job(job_id)
    if job is None or job.user_id != current_user.id:
        raise HTTPException(404, "Analyse introuvable.")
    return {
        "job_id": job.id,
        "status": job.status,
        "step_index": job.step_index,
        "step_label": job.step_label,
        "message": job.message,
        "total_steps": len(jobs.STEPS),
        "error": job.error,
        "redirect_url": f"/app/resultats/{job.id}" if job.status == "done" else None,
    }


@router.get("/download/{job_id}/{kind}")
def api_download(job_id: str, kind: str, current_user: User = Depends(require_active_starter_user)):
    if kind not in ("pdf", "docx"):
        raise HTTPException(400, "Type de document invalide.")
    job = jobs.get_job(job_id)
    if job is None or job.user_id != current_user.id or not job.files.get(kind):
        raise HTTPException(404, "Document introuvable.")
    path = Path(job.files[kind])
    if not path.exists():
        raise HTTPException(404, "Le fichier n'existe plus sur le serveur.")
    media_type = "application/pdf" if kind == "pdf" else (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    return FileResponse(path, media_type=media_type, filename=path.name)


@router.get("/history/export.csv")
def api_export_history_csv(
    current_user: User = Depends(require_active_starter_user),
    db: Session = Depends(get_db),
):
    records = history_service.list_for_user(db, current_user.id)
    buffer = io.StringIO()
    fieldnames = ["ao_id", "titre", "client", "secteur", "decision", "score", "budget", "techs", "date", "resultat"]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in records:
        row = dict(row)
        row["techs"] = ", ".join(row.get("techs", []) or [])
        writer.writerow(row)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=historique_ao.csv"},
    )


@router.get("/capacity")
def api_get_capacity(current_user: User = Depends(require_active_starter_user)):
    plan = CapacityRepository().load()
    return {
        "charge_globale_pct": plan.charge_globale_pct,
        "disponibilite_pct": max(0, 100 - plan.charge_globale_pct),
        "nombre_projets_en_cours": plan.nombre_projets_en_cours,
        "projets_en_cours": plan.projets_en_cours,
        "capacites_par_pole": plan.capacites_par_pole,
    }


@router.post("/capacity")
async def api_save_capacity(payload: dict, current_user: User = Depends(require_active_starter_user)):
    repository = CapacityRepository()
    plan = CapacityPlan(
        charge_globale_pct=int(payload.get("charge_globale_pct", 78)),
        nombre_projets_en_cours=int(payload.get("nombre_projets_en_cours", 0)),
        projets_en_cours=[str(x) for x in payload.get("projets_en_cours", [])],
        capacites_par_pole={k: int(v) for k, v in payload.get("capacites_par_pole", {}).items()},
    )
    repository.save(plan)
    get_pipeline().rag.load()
    return api_get_capacity(current_user)


@router.get("/knowledge")
def api_knowledge(current_user: User = Depends(require_active_starter_user)):
    pipeline = get_pipeline()
    return knowledge_service.knowledge_summary(pipeline.rag)


@router.post("/knowledge/reload")
def api_knowledge_reload(current_user: User = Depends(require_active_starter_user)):
    pipeline = get_pipeline()
    pipeline.rag.load()
    return knowledge_service.knowledge_summary(pipeline.rag)


@router.get("/knowledge/search")
def api_knowledge_search(q: str = "", current_user: User = Depends(require_active_starter_user)):
    if not q.strip():
        return {"query": q, "results": []}
    pipeline = get_pipeline()
    results = pipeline.rag.search(q, top_k=5)
    return {
        "query": q,
        "results": [
            {
                "source": ev.source,
                "score": ev.score,
                "relevance_pct": min(int(ev.score * 400), 100),
                "excerpt": ev.content[:800],
            }
            for ev in results
        ],
    }


@router.post("/contact")
async def api_contact(payload: dict, request: Request, db: Session = Depends(get_db)):
    """Business/Enterprise prospect requests — not a Starter signup (that's
    /register, which creates a real User + Subscription instead)."""
    require_csrf(request, payload.get("csrf_token"))

    first_name = (payload.get("first_name") or "").strip()
    last_name = (payload.get("last_name") or "").strip()
    email = (payload.get("email") or "").strip()
    company = (payload.get("company") or "").strip()
    job_title = (payload.get("job_title") or "").strip()
    plan = (payload.get("plan") or "").strip()
    message = (payload.get("message") or "").strip()
    raw_employee_count = (payload.get("employee_count") or "").strip() if isinstance(payload.get("employee_count"), str) else payload.get("employee_count")

    if not first_name or not last_name or not email or not message:
        raise HTTPException(400, "Merci de renseigner votre prénom, votre nom, votre email et votre message.")
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        raise HTTPException(400, "Adresse email invalide.")

    employee_count = None
    if raw_employee_count not in (None, ""):
        try:
            employee_count = int(raw_employee_count)
        except (TypeError, ValueError):
            raise HTTPException(400, "Nombre d'utilisateurs invalide.")

    contact_request = contacts_repo.create_contact_request(
        db,
        first_name=first_name,
        last_name=last_name,
        email=email,
        company=company or None,
        job_title=job_title or None,
        employee_count=employee_count,
        plan=plan or None,
        message=message,
    )
    db.commit()

    try:
        notify_new_contact_request(contact_request)
    except Exception:
        logger.exception("Failed to send contact-request admin notification")

    return {"status": "ok"}
