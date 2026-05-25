from src.core.models import AOContext, CapacityResult

class CapacityAnalyzer:
    def analyze(self, ao: AOContext) -> CapacityResult:
        heavy = any(t.lower() in ["sap", "mainframe", "cobol", "blockchain"] for t in ao.technologies_demandees)
        many_techs = len(ao.technologies_demandees) >= 6
        charge = 82 + (8 if many_techs else 0) + (10 if heavy else 0)
        charge = min(charge, 99)
        remaining = 100 - charge
        ok = remaining >= 10 and not heavy
        return CapacityResult(
            charge_actuelle_pct=charge,
            capacite_restante_pct=remaining,
            equipe_disponible=ok,
            commentaire=("Capacité suffisante pour constituer une équipe projet." if ok else "Capacité sous tension ou compétence critique peu disponible.")
        )
