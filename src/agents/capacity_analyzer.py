from src.core.models import AOContext, CapacityResult
from src.core.capacity_repository import CapacityRepository

class CapacityAnalyzer:
    def __init__(self, repository: CapacityRepository | None = None):
        self.repository = repository or CapacityRepository()

    def analyze(self, ao: AOContext) -> CapacityResult:
        plan = self.repository.load()
        heavy = any(t.lower() in ["sap", "mainframe", "cobol", "blockchain"] for t in ao.technologies_demandees)
        many_techs = len(ao.technologies_demandees) >= 6
        charge = plan.charge_globale_pct + (8 if many_techs else 0) + (10 if heavy else 0)
        charge = min(charge, 99)
        remaining = 100 - charge
        ok = remaining >= 10 and not heavy
        return CapacityResult(
            charge_actuelle_pct=charge,
            capacite_restante_pct=remaining,
            equipe_disponible=ok,
            commentaire=(
                f"Capacité suffisante pour constituer une équipe projet ({plan.nombre_projets_en_cours} projet(s) en cours)."
                if ok else
                f"Capacité sous tension ou compétence critique peu disponible ({plan.nombre_projets_en_cours} projet(s) en cours)."
            )
        )
