"""Shared pytest fixtures for the V3 SaaS test suite.

Uses an isolated, on-disk SQLite database per test (fast, no external
Postgres dependency required to run the suite) — the ORM models are
written to work identically against SQLite and PostgreSQL (see
src/web/database/models.py: portable Uuid type, JSONB.with_variant(JSON,
"sqlite")), so this exercises the real code paths, not a mock.
"""
import uuid

import pytest
from fastapi.testclient import TestClient

from src.core import config
from src.web.database import session as db_session_module
from src.web.database.models import Base


@pytest.fixture()
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / f"test_{uuid.uuid4().hex}.db"
    monkeypatch.setattr(config, "DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setattr(config, "SESSION_SECRET", "test-secret-not-for-production")
    monkeypatch.setattr(db_session_module, "_engine", None)
    monkeypatch.setattr(db_session_module, "_SessionLocal", None)

    engine = db_session_module.get_engine()
    Base.metadata.create_all(engine)
    yield engine

    engine.dispose()
    monkeypatch.setattr(db_session_module, "_engine", None)
    monkeypatch.setattr(db_session_module, "_SessionLocal", None)


@pytest.fixture()
def db(test_db):
    """A plain SQLAlchemy Session for repository-level tests."""
    session = db_session_module.get_session_factory()()
    yield session
    session.close()


@pytest.fixture()
def client(test_db):
    """FastAPI TestClient wired to the isolated test database."""
    import main
    with TestClient(main.app) as c:
        yield c


def make_active_starter_user(db, email: str, password: str = "Sup3rSecret!"):
    """Test helper: an already-active Starter user, ready to log in."""
    from src.web.auth import service as auth_service
    from src.web.database.repositories import subscriptions as subscriptions_repo
    from src.web.database.repositories import users as users_repo

    user = users_repo.create_user(
        db, email=email, password_hash=auth_service.hash_password(password),
        first_name="Test", last_name="User", status="active",
    )
    subscription = subscriptions_repo.create_subscription(db, user_id=user.id, plan="starter", status="pending")
    subscriptions_repo.activate(db, subscription)
    db.commit()
    return user
