"""Background analysis jobs for the FastAPI UI.

This module intentionally re-implements the exact same call sequence the
Streamlit UI (src/ui/app.py) uses — it does not call AOPipeline.run_text()
because the Streamlit UI itself doesn't either: it calls each pipeline step
individually so it can report real progress to the user. We mirror that
here, in a background thread, so the browser can poll real step-by-step
status instead of blocking on one long HTTP request. No business logic is
changed — same classes, same order, same parameters.
"""
from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.core.config import DATA_DIR
from src.core.content_security import ContentSecurityError
from src.core.models import AOContext, ScoringResult
from src.web.historique_service import append_to_historique
from src.web.pipeline_singleton import get_pipeline

STEPS = [
    "Sécurité et préparation",
    "Lecture intelligente",
    "Recherche client",
    "Analyse sémantique",
    "Scoring enrichi",
    "Disponibilité équipe",
    "Génération documents",
]

ANALYSES_DIR = DATA_DIR / "historique" / "analyses"


@dataclass
class Job:
    id: str
    user_id: Optional[uuid.UUID] = None
    status: str = "running"  # running | done | error
    step_index: int = 0
    step_label: str = STEPS[0]
    message: str = "Initialisation..."
    error: Optional[str] = None
    source_label: str = ""
    ao: Optional[AOContext] = None
    result: Optional[ScoringResult] = None
    files: dict = field(default_factory=dict)
    history_record: Optional[dict] = None
    analysis_id: Optional[uuid.UUID] = None
    created_at: float = field(default_factory=time.time)


_JOBS: dict[str, Job] = {}
_LOCK = threading.Lock()


def create_job(source_label: str = "", user_id: Optional[uuid.UUID] = None) -> Job:
    job = Job(id=uuid.uuid4().hex[:12], user_id=user_id, source_label=source_label)
    with _LOCK:
        _JOBS[job.id] = job
    return job


def get_job(job_id: str) -> Optional[Job]:
    with _LOCK:
        job = _JOBS.get(job_id)
    if job is not None:
        return job
    return _load_persisted(job_id)


def start_analysis(job: Job, text: str) -> None:
    thread = threading.Thread(target=_run_analysis, args=(job, text), daemon=True)
    thread.start()


def _run_analysis(job: Job, text: str) -> None:
    pipeline = get_pipeline()

    def progress(step_idx: int, msg: str) -> None:
        job.step_index = step_idx
        job.step_label = STEPS[step_idx]
        job.message = msg

    try:
        try:
            pipeline.security.validate(text)
        except ContentSecurityError as exc:
            job.status = "error"
            job.error = exc.user_message
            return
        text = pipeline.preparer.prepare(text).text

        progress(0, "Lecture du document...")
        from src.agents.ao_extractor import AOExtractor
        from src.agents.llm_client import ClaudeClient
        llm = ClaudeClient()
        ao = AOExtractor().extract(text)

        progress(1, f"Lecture intelligente du document — {ao.titre[:60]}")
        from src.agents.company_enrichment import CompanyEnrichmentAgent
        progress(2, f"Recherche d'informations sur le client : {ao.client}")
        company = CompanyEnrichmentAgent().enrich(ao.client)

        progress(3, "Analyse sémantique de vos références internes...")
        query = " ".join([ao.titre] + ao.technologies_demandees + ao.certifications_obligatoires)
        evidences = pipeline.rag.search(query, top_k=8)
        evidences, rag_synthesis = pipeline.rag.semantic_rerank(ao.texte_source, evidences, llm)

        progress(4, "Calcul et enrichissement du score de réussite...")
        from src.agents.capacity_analyzer import CapacityAnalyzer
        capacity = CapacityAnalyzer().analyze(ao)
        from src.agents.scoring_engine import ScoringEngine
        result = ScoringEngine().score(ao, company, evidences, capacity)
        result.rag_synthesis = rag_synthesis
        result = pipeline.scoring.enrich_with_llm(ao, result, llm)

        progress(5, "Évaluation de la disponibilité de l'équipe...")
        ai_content = pipeline.generator._generate_ai_content(ao, result, llm)
        result.ai_content = ai_content

        progress(6, "Génération de vos documents de réponse sur mesure...")
        from src.livrables.document_generator import DocumentGenerator
        dg = DocumentGenerator()
        files = {
            "pdf": str(dg.generate_pdf(ao, result)),
            "docx": str(dg.generate_docx(ao, result)),
        }

        job.ao = ao
        job.result = result
        job.files = files
        # Legacy global JSON history — kept during the V3 transition so the
        # independent Streamlit UI keeps working unchanged (double-write).
        job.history_record = append_to_historique(ao, result, job_id=job.id)
        _persist(job)
        _persist_to_database(job)  # best-effort; never blocks a successful analysis
        job.status = "done"
    except Exception as exc:  # noqa: BLE001 — surfaced to the user as a clean error card
        job.status = "error"
        job.error = f"Une erreur inattendue est survenue pendant l'analyse : {exc}"


def _persist(job: Job) -> None:
    ANALYSES_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": job.id,
        "user_id": str(job.user_id) if job.user_id else None,
        "created_at": job.created_at,
        "source_label": job.source_label,
        "ao": job.ao.model_dump() if job.ao else None,
        "result": job.result.model_dump() if job.result else None,
        "files": job.files,
    }
    (ANALYSES_DIR / f"{job.id}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _persist_to_database(job: Job) -> None:
    """PostgreSQL is the SaaS source of truth (V3) — this mirrors the JSON
    write above without depending on it. Failure here is logged, never
    raised: a user must still get their result even if the database is
    briefly unavailable.
    """
    if job.user_id is None:
        return
    try:
        from src.core.logger import get_agent_logger
        from src.web.database.repositories import analyses as analyses_repo
        from src.web.database.session import session_scope

        logger = get_agent_logger("web_jobs")
        result_data = {
            "id": job.id,
            "created_at": job.created_at,
            "source_label": job.source_label,
            "ao": job.ao.model_dump() if job.ao else None,
            "result": job.result.model_dump() if job.result else None,
            "files": job.files,
        }
        with session_scope() as db:
            analysis = analyses_repo.create_analysis(
                db,
                user_id=job.user_id,
                job_id=job.id,
                title=job.ao.titre if job.ao else None,
                client_name=job.ao.client if job.ao else None,
                sector=job.ao.secteur if job.ao else None,
                score=job.result.score_global if job.result else None,
                decision=job.result.decision if job.result else None,
                budget=job.ao.budget_estime if job.ao else None,
                technologies=(job.ao.technologies_demandees[:4] if job.ao else None),
                result_data=result_data,
            )
            job.analysis_id = analysis.id

            from src.web.storage.service import get_storage_service
            storage = get_storage_service()
            for kind, path_str in job.files.items():
                path = Path(path_str)
                if not path.exists():
                    continue
                analyses_repo.add_document(
                    db,
                    analysis_id=analysis.id,
                    user_id=job.user_id,
                    filename=path.name,
                    original_filename=path.name,
                    storage_path=storage.save(path),
                    mime_type=("application/pdf" if kind == "pdf" else
                               "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                    file_size=path.stat().st_size,
                )
    except Exception:
        from src.core.logger import get_agent_logger
        get_agent_logger("web_jobs").exception("Failed to persist analysis to PostgreSQL job_id=%s", job.id)


def _load_persisted(job_id: str) -> Optional[Job]:
    path = ANALYSES_DIR / f"{job_id}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not data.get("ao") or not data.get("result"):
        return None
    raw_user_id = data.get("user_id")
    job = Job(
        id=data["id"],
        user_id=uuid.UUID(raw_user_id) if raw_user_id else None,
        status="done",
        step_index=len(STEPS) - 1,
        step_label=STEPS[-1],
        message="Analyse terminée.",
        source_label=data.get("source_label", ""),
        ao=AOContext(**data["ao"]),
        result=ScoringResult(**data["result"]),
        files=data.get("files", {}),
        created_at=data.get("created_at", time.time()),
    )
    with _LOCK:
        _JOBS[job.id] = job
    return job
