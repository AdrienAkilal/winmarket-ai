from src.agents.capacity_analyzer import CapacityAnalyzer
from src.core.capacity_repository import CapacityPlan, CapacityRepository, DEFAULT_POLES
from src.core.models import AOContext


def test_loads_existing_legacy_capacity_document(tmp_path):
    path = tmp_path / "capacity.md"
    path.write_text(
        "# Capacité\nLa charge consolidée est actuellement estimée à 73 %.\n"
        "Software Engineering : 31 % de capacité disponible.\n"
        "Nombre de projets en cours : 6.\n",
        encoding="utf-8",
    )
    plan = CapacityRepository(path).load()
    assert plan.charge_globale_pct == 73
    assert plan.nombre_projets_en_cours == 6
    assert plan.capacites_par_pole["Software Engineering"] == 31


def test_save_updates_markdown_and_round_trips(tmp_path):
    path = tmp_path / "capacity.md"
    path.write_text(
        "# Capacité\n\n## Délais réalistes par type de projet\n- MVP : 10 semaines.\n",
        encoding="utf-8",
    )
    repository = CapacityRepository(path)
    repository.save(CapacityPlan(
        charge_globale_pct=64,
        nombre_projets_en_cours=3,
        projets_en_cours=["Portail client", "Projet Data"],
        capacites_par_pole={**DEFAULT_POLES, "Data & IA": 42},
    ))
    saved = path.read_text(encoding="utf-8")
    loaded = repository.load()
    assert "CAPACITY_DATA_START" in saved
    assert "## Délais réalistes par type de projet" in saved
    assert loaded.charge_globale_pct == 64
    assert loaded.nombre_projets_en_cours == 3
    assert loaded.projets_en_cours == ["Portail client", "Projet Data"]
    assert loaded.capacites_par_pole["Data & IA"] == 42


def test_capacity_analyzer_uses_repository_values():
    class Repository:
        def load(self):
            return CapacityPlan(charge_globale_pct=55, nombre_projets_en_cours=4)

    result = CapacityAnalyzer(Repository()).analyze(AOContext(
        titre="Portail client", technologies_demandees=["Python"],
    ))
    assert result.charge_actuelle_pct == 55
    assert result.capacite_restante_pct == 45
    assert "4 projet(s) en cours" in result.commentaire
