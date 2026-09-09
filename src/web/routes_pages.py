"""HTML page routes — server-rendered Jinja2 templates.

Every route here only gathers data from existing services and renders a
template; no scoring, RAG, LLM or extraction logic is implemented here.

V3: every /app/* route is gated by resolve_app_access() (auth + active
Starter subscription check, re-verified against PostgreSQL on every
request). Personal history/results come from PostgreSQL via
src/web/services/history_service.py; the legacy global JSON historique
(src/web/historique_service.py) is no longer read here — it stays in
place only for the independent Streamlit UI.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.web import examples_service, jobs, knowledge_service
from src.web.auth.dependencies import resolve_app_access
from src.web.database.session import get_db
from src.web.pipeline_singleton import get_pipeline
from src.web.security.csrf import attach_csrf_cookie, get_or_create_csrf_token
from src.web.services import history_service
from src.web.templating import templates

router = APIRouter()


def _render(request: Request, template_name: str, context: dict, status_code: int = 200):
    """Every /app/* page needs a CSRF token (sidebar logout form) — resolve
    it here so each route doesn't repeat the same lines. Reuses the
    existing cookie's token when valid (see get_or_create_csrf_token) so
    that having several /app/* pages open at once doesn't invalidate each
    other's forms."""
    token, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, template_name, {**context, "csrf_token": token}, status_code=status_code)
    if is_new:
        attach_csrf_cookie(resp, token)
    return resp


@router.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(request, "landing.html", {})


@router.get("/pricing", response_class=HTMLResponse)
def pricing(request: Request):
    return templates.TemplateResponse(request, "pricing.html", {})


@router.get("/contact", response_class=HTMLResponse)
def contact(request: Request, plan: str = ""):
    token, is_new = get_or_create_csrf_token(request)
    resp = templates.TemplateResponse(request, "contact.html", {"default_plan": plan, "csrf_token": token})
    if is_new:
        attach_csrf_cookie(resp, token)
    return resp


@router.get("/app")
def app_root():
    return RedirectResponse(url="/app/analyser")


@router.get("/app/analyser", response_class=HTMLResponse)
def app_analyser(request: Request, db: Session = Depends(get_db)):
    user, redirect = resolve_app_access(request, db)
    if redirect:
        return redirect
    return _render(request, "app_analyze.html", {
        "active_nav": "analyser",
        "user": user,
        "sidebar_stats": history_service.sidebar_stats(db, user.id),
        "examples": examples_service.list_examples(),
        "steps": jobs.STEPS,
    })


@router.get("/app/resultats/{job_id}", response_class=HTMLResponse)
def app_resultats(request: Request, job_id: str, db: Session = Depends(get_db)):
    user, redirect = resolve_app_access(request, db)
    if redirect:
        return redirect

    ctx_base = {"active_nav": "analyser", "user": user, "sidebar_stats": history_service.sidebar_stats(db, user.id)}
    job = jobs.get_job(job_id)

    # Ownership check: a job that exists but belongs to someone else must
    # look exactly like a job that doesn't exist — never leak its presence.
    if job is None or job.user_id != user.id:
        return _render(request, "app_error.html", {
            **ctx_base,
            "title": "Analyse introuvable",
            "heading": "Cette analyse n'existe pas ou plus.",
            "message": "Le lien utilisé est invalide, ou le résultat a été supprimé du serveur.",
        }, status_code=404)

    if job.status == "error":
        return _render(request, "app_error.html", {
            **ctx_base,
            "title": "Échec de l'analyse",
            "heading": "L'analyse n'a pas pu être finalisée.",
            "message": job.error or "Erreur inconnue.",
        })

    if job.status == "running":
        return _render(request, "app_result_pending.html", {
            **ctx_base,
            "job": job,
            "steps": jobs.STEPS,
        })

    history_recent = history_service.list_for_user(db, user.id)[:10]
    return _render(request, "app_result.html", {
        **ctx_base,
        "job_id": job.id,
        "ao": job.ao,
        "result": job.result,
        "files": job.files,
        "history_recent": history_recent,
    })


@router.get("/app/historique", response_class=HTMLResponse)
def app_historique(request: Request, db: Session = Depends(get_db)):
    user, redirect = resolve_app_access(request, db)
    if redirect:
        return redirect
    return _render(request, "app_history.html", {
        "active_nav": "historique",
        "user": user,
        "sidebar_stats": history_service.sidebar_stats(db, user.id),
        "history": history_service.list_for_user(db, user.id),
    })


@router.get("/app/base-connaissances", response_class=HTMLResponse)
def app_base_connaissances(request: Request, db: Session = Depends(get_db)):
    user, redirect = resolve_app_access(request, db)
    if redirect:
        return redirect
    pipeline = get_pipeline()
    return _render(request, "app_knowledge.html", {
        "active_nav": "connaissances",
        "user": user,
        "sidebar_stats": history_service.sidebar_stats(db, user.id),
        "knowledge": knowledge_service.knowledge_summary(pipeline.rag),
    })
