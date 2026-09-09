"""Activate a pending Starter account.

In a single transaction:
    users.status = active
    subscriptions.status = active
    subscriptions.started_at = now()
Rolls back entirely if anything fails.

Usage:
    python scripts/activate_user.py email@example.com
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.web.database.repositories import subscriptions as subscriptions_repo
from src.web.database.repositories import users as users_repo
from src.web.database.session import session_scope


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage : python scripts/activate_user.py email@example.com")
        raise SystemExit(1)
    email = sys.argv[1].strip().lower()
    plan_label = None

    with session_scope() as db:
        user = users_repo.get_by_email(db, email)
        if user is None:
            print(f"Aucun utilisateur avec l'email {email}")
            raise SystemExit(1)

        subscription = subscriptions_repo.get_latest_for_user(db, user.id)
        if subscription is None:
            print(f"Aucun abonnement trouvé pour {email}")
            raise SystemExit(1)

        users_repo.set_status(db, user, "active")
        subscriptions_repo.activate(db, subscription)
        plan_label = subscription.plan
        # session_scope() commits here on success, rolls back on exception —
        # the whole activation is one atomic transaction.

    print(f"Compte activé : {email} (plan={plan_label})")


if __name__ == "__main__":
    main()
