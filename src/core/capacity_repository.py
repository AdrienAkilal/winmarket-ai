"""Read and update the capacity plan stored in the RAG knowledge base."""
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Dict

from src.core.config import REG_DIR
from src.core.logger import get_agent_logger

logger = get_agent_logger("capacity_repository")
CAPACITY_FILE = REG_DIR / "ressources" / "capacite_charge_planification.md"
_START = "<!-- CAPACITY_DATA_START -->"
_END = "<!-- CAPACITY_DATA_END -->"
DEFAULT_POLES = {
    "Software Engineering": 22,
    "Data & IA": 15,
    "Cloud/DevOps": 12,
    "QA": 25,
    "Product Design": 30,
    "Chefferie de projet": 18,
}


@dataclass
class CapacityPlan:
    charge_globale_pct: int = 78
    nombre_projets_en_cours: int = 0
    projets_en_cours: list[str] = field(default_factory=list)
    capacites_par_pole: Dict[str, int] = field(default_factory=lambda: dict(DEFAULT_POLES))
    updated_at: str = ""


class CapacityRepository:
    def __init__(self, path: Path = CAPACITY_FILE):
        self.path = Path(path)

    def load(self) -> CapacityPlan:
        if not self.path.exists():
            return CapacityPlan()
        text = self.path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(re.escape(_START) + r"\s*(.*?)\s*" + re.escape(_END), text, re.S)
        if match:
            try:
                data = json.loads(match.group(1))
                return CapacityPlan(
                    charge_globale_pct=self._pct(data.get("charge_globale_pct", 78)),
                    nombre_projets_en_cours=max(0, int(data.get("nombre_projets_en_cours", 0))),
                    projets_en_cours=[str(item).strip() for item in data.get("projets_en_cours", []) if str(item).strip()],
                    capacites_par_pole={
                        pole: self._pct(data.get("capacites_par_pole", {}).get(pole, value))
                        for pole, value in DEFAULT_POLES.items()
                    },
                    updated_at=str(data.get("updated_at", "")),
                )
            except (ValueError, TypeError, json.JSONDecodeError):
                logger.warning("Invalid structured capacity block; using legacy parser")
        return self._load_legacy(text)

    def save(self, plan: CapacityPlan) -> None:
        plan.charge_globale_pct = self._pct(plan.charge_globale_pct)
        plan.nombre_projets_en_cours = max(0, int(plan.nombre_projets_en_cours))
        plan.projets_en_cours = [name.strip() for name in plan.projets_en_cours if name.strip()]
        plan.capacites_par_pole = {
            pole: self._pct(plan.capacites_par_pole.get(pole, default))
            for pole, default in DEFAULT_POLES.items()
        }
        plan.updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
        previous = self.path.read_text(encoding="utf-8", errors="ignore") if self.path.exists() else ""
        static_start = previous.find("## Délais réalistes par type de projet")
        static_content = previous[static_start:].strip() if static_start >= 0 else ""
        payload = json.dumps({
            "charge_globale_pct": plan.charge_globale_pct,
            "nombre_projets_en_cours": plan.nombre_projets_en_cours,
            "projets_en_cours": plan.projets_en_cours,
            "capacites_par_pole": plan.capacites_par_pole,
            "updated_at": plan.updated_at,
        }, ensure_ascii=False, indent=2)
        projects = "\n".join(f"- {name}" for name in plan.projets_en_cours) or "- Aucun projet détaillé."
        poles = "\n".join(f"{pole} : {value} % de capacité disponible." for pole, value in plan.capacites_par_pole.items())
        document = f"""# Capacité, charge et règles de planification

{_START}
{payload}
{_END}

## Charge globale
La charge consolidée de NovaSoft Conseil est actuellement estimée à {plan.charge_globale_pct} %.
Nombre de projets en cours : {plan.nombre_projets_en_cours}.

## Projets en cours
{projects}

## Capacité disponible par pôle
{poles}

{static_content}
"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(document.strip() + "\n", encoding="utf-8")
        logger.info("Capacity plan updated load_pct=%d active_projects=%d",
                    plan.charge_globale_pct, plan.nombre_projets_en_cours)

    @staticmethod
    def _pct(value) -> int:
        return max(0, min(100, int(value)))

    def _load_legacy(self, text: str) -> CapacityPlan:
        charge = re.search(r"charge consolidée[^\d]*(\d{1,3})\s*%", text, re.I)
        project_count = re.search(r"nombre de projets en cours\s*:\s*(\d+)", text, re.I)
        poles = dict(DEFAULT_POLES)
        for pole in poles:
            match = re.search(re.escape(pole) + r"\s*:\s*(\d{1,3})\s*%", text, re.I)
            if match:
                poles[pole] = self._pct(match.group(1))
        return CapacityPlan(
            charge_globale_pct=self._pct(charge.group(1) if charge else 78),
            nombre_projets_en_cours=int(project_count.group(1)) if project_count else 0,
            capacites_par_pole=poles,
        )
