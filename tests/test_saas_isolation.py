"""V3 SaaS — per-user history isolation.

Covers checklist items 9-11: historique filtré par user_id, analyse A
invisible pour utilisateur B, sauvegarde nouvelle analyse.
"""
import re

from tests.conftest import make_active_starter_user


def _csrf_from(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match
    return match.group(1)


def _login(client, email, password="Sup3rSecret!"):
    r = client.get("/login")
    csrf = _csrf_from(r.text)
    return client.post("/login", data={"email": email, "password": password, "next": "/app", "csrf_token": csrf})


def test_new_analysis_persisted_with_user_id(db):
    from src.web.database.repositories import analyses as analyses_repo

    user = make_active_starter_user(db, "owner@example.com")
    analysis = analyses_repo.create_analysis(
        db, user_id=user.id, job_id="job-owner-1", title="AO Owner",
        client_name="Client X", score=88.5, decision="GO",
        result_data={"ao": {}, "result": {}},
    )
    db.commit()

    assert analysis.user_id == user.id
    assert analysis.job_id == "job-owner-1"
    assert analysis.decision == "GO"


def test_history_service_filters_by_user(db):
    from src.web.database.repositories import analyses as analyses_repo
    from src.web.services import history_service

    user_a = make_active_starter_user(db, "a@example.com")
    user_b = make_active_starter_user(db, "b@example.com")

    analyses_repo.create_analysis(db, user_id=user_a.id, job_id="jobA", title="AO de A", decision="GO", result_data={})
    analyses_repo.create_analysis(db, user_id=user_b.id, job_id="jobB", title="AO de B", decision="NO-GO", result_data={})
    db.commit()

    history_a = history_service.list_for_user(db, user_a.id)
    history_b = history_service.list_for_user(db, user_b.id)

    assert [r["titre"] for r in history_a] == ["AO de A"]
    assert [r["titre"] for r in history_b] == ["AO de B"]


def test_analysis_ownership_check_blocks_other_user(db):
    from src.web.database.repositories import analyses as analyses_repo

    user_a = make_active_starter_user(db, "owner2@example.com")
    user_b = make_active_starter_user(db, "intruder@example.com")

    analysis = analyses_repo.create_analysis(
        db, user_id=user_a.id, job_id="secret-job", title="Confidentiel", result_data={},
    )
    db.commit()

    assert analyses_repo.get_by_id_for_user(db, analysis.id, user_a.id) is not None
    assert analyses_repo.get_by_id_for_user(db, analysis.id, user_b.id) is None


def test_history_page_shows_only_own_analyses(client, db):
    from src.web.database.repositories import analyses as analyses_repo

    user_a = make_active_starter_user(db, "histA@example.com")
    user_b = make_active_starter_user(db, "histB@example.com")
    analyses_repo.create_analysis(db, user_id=user_a.id, job_id="hist-jobA", title="Titre unique A", result_data={})
    analyses_repo.create_analysis(db, user_id=user_b.id, job_id="hist-jobB", title="Titre unique B", result_data={})
    db.commit()

    _login(client, "histA@example.com")
    r = client.get("/app/historique")
    assert "Titre unique A" in r.text
    assert "Titre unique B" not in r.text


def test_job_status_endpoint_hides_other_users_jobs(client, db):
    """/api/analyze/{job_id}/status must 404 for a job that isn't the
    caller's, exactly like a job that doesn't exist — see routes_api.py."""
    from src.web import jobs

    user_a = make_active_starter_user(db, "jobownerA@example.com")
    user_b = make_active_starter_user(db, "jobownerB@example.com")
    job = jobs.create_job(source_label="test", user_id=user_a.id)

    _login(client, "jobownerB@example.com")
    r = client.get(f"/api/analyze/{job.id}/status")
    assert r.status_code == 404

    _login(client, "jobownerA@example.com")
    r2 = client.get(f"/api/analyze/{job.id}/status")
    assert r2.status_code == 200
