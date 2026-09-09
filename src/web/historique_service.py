"""Historique persistence — ported unchanged from src/ui/app.py.

Same file (data/historique/historique_ao.json), same record schema. The
Streamlit UI and the FastAPI UI both read/write this file so history stays
consistent whichever interface produced it.
"""
import json
from datetime import datetime

from src.core.config import DATA_DIR
from src.core.models import AOContext, ScoringResult

HIST_FILE = DATA_DIR / "historique" / "historique_ao.json"


def load_historique() -> list:
    HIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    if HIST_FILE.exists():
        try:
            return json.loads(HIST_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_historique(records: list) -> None:
    HIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    HIST_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def append_to_historique(ao: AOContext, result: ScoringResult, job_id: str | None = None) -> dict:
    records = load_historique()
    record = {
        "ao_id": datetime.now().strftime("AO_%Y%m%d_%H%M%S"),
        "titre": ao.titre,
        "client": ao.client,
        "secteur": ao.secteur or "Non renseigne",
        "decision": result.decision,
        "score": result.score_global,
        "budget": ao.budget_estime,
        "techs": ao.technologies_demandees[:4],
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "resultat": "en attente",
    }
    if job_id:
        # Additive field only — links a history row back to its full stored
        # analysis so the new UI can offer to reopen it. The Streamlit UI
        # simply ignores unknown keys, so this does not break it.
        record["job_id"] = job_id
    records.append(record)
    save_historique(records)
    return record
