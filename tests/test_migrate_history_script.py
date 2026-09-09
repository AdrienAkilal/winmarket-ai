"""V3 SaaS — scripts/migrate_history_to_postgresql.py.

Covers checklist item 12 (migration historique). Runs against a temporary
historique_ao.json — never against the real project data — via
monkeypatched module paths.
"""
import json
import sys

from tests.conftest import make_active_starter_user


def _patch_history_paths(monkeypatch, tmp_path):
    import scripts.migrate_history_to_postgresql as migrate

    hist_dir = tmp_path / "historique"
    hist_dir.mkdir()
    hist_file = hist_dir / "historique_ao.json"
    analyses_dir = hist_dir / "analyses"
    analyses_dir.mkdir()
    backup_root = hist_dir / "_migration_backups"

    monkeypatch.setattr(migrate, "HIST_FILE", hist_file)
    monkeypatch.setattr(migrate, "ANALYSES_DIR", analyses_dir)
    monkeypatch.setattr(migrate, "BACKUP_ROOT", backup_root)
    return migrate, hist_file, analyses_dir, backup_root


def _run_migration(monkeypatch, migrate, owner_email: str) -> None:
    monkeypatch.setattr(sys, "argv", ["migrate_history_to_postgresql.py", owner_email])
    migrate.main()


def test_migration_creates_one_analysis_per_record_and_backs_up(db, tmp_path, monkeypatch, test_db):
    migrate, hist_file, analyses_dir, backup_root = _patch_history_paths(monkeypatch, tmp_path)

    owner = make_active_starter_user(db, "owner@example.com")
    records = [
        {"titre": "AO 1", "client": "Client 1", "decision": "GO", "score": 90, "date": "01/01/2026 10:00"},
        {"ao_id": "AO_X", "titre": "AO 2", "client": "Client 2", "decision": "NO-GO", "score": 40,
         "date": "02/01/2026 10:00", "job_id": "jobdetail1"},
    ]
    hist_file.write_text(json.dumps(records), encoding="utf-8")
    (analyses_dir / "jobdetail1.json").write_text(json.dumps({
        "id": "jobdetail1", "ao": {"titre": "AO 2 detail"}, "result": {"decision": "NO-GO"},
    }), encoding="utf-8")

    _run_migration(monkeypatch, migrate, "owner@example.com")

    from src.web.database.repositories import analyses as analyses_repo
    rows = analyses_repo.list_for_user(db, owner.id)
    assert len(rows) == 2
    assert backup_root.exists()
    assert any(backup_root.iterdir())

    detailed = next(r for r in rows if r.job_id == "jobdetail1")
    assert detailed.result_data.get("ao", {}).get("titre") == "AO 2 detail"


def test_migration_is_idempotent(db, tmp_path, monkeypatch, test_db):
    migrate, hist_file, analyses_dir, backup_root = _patch_history_paths(monkeypatch, tmp_path)
    owner = make_active_starter_user(db, "owner2@example.com")

    hist_file.write_text(json.dumps([
        {"titre": "AO only once", "client": "Client", "decision": "GO", "score": 80, "date": "03/01/2026 10:00"},
    ]), encoding="utf-8")

    _run_migration(monkeypatch, migrate, "owner2@example.com")
    _run_migration(monkeypatch, migrate, "owner2@example.com")  # re-run — must not duplicate

    from src.web.database.repositories import analyses as analyses_repo
    matching = [r for r in analyses_repo.list_for_user(db, owner.id) if r.title == "AO only once"]
    assert len(matching) == 1


def test_migration_fails_clearly_when_owner_missing(tmp_path, monkeypatch, test_db):
    migrate, hist_file, analyses_dir, backup_root = _patch_history_paths(monkeypatch, tmp_path)
    hist_file.write_text(json.dumps([{"titre": "AO", "date": "01/01/2026 10:00"}]), encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["migrate_history_to_postgresql.py", "doesnotexist@example.com"])
    try:
        migrate.main()
        raised = False
    except SystemExit:
        raised = True
    assert raised
