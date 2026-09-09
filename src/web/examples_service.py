"""Access to the bundled example AO files (data/ao_examples/*.txt).

Mirrors the "Appels d'offres en stock" source mode from the Streamlit UI.
"""
from src.core.config import DATA_DIR

EXAMPLES_DIR = DATA_DIR / "ao_examples"


def list_examples() -> list[dict]:
    if not EXAMPLES_DIR.exists():
        return []
    return [
        {"id": p.stem, "label": p.stem.replace("_", " ")}
        for p in sorted(EXAMPLES_DIR.glob("*.txt"))
    ]


def read_example(example_id: str) -> str | None:
    path = (EXAMPLES_DIR / f"{example_id}.txt").resolve()
    if not path.is_file() or EXAMPLES_DIR.resolve() not in path.parents:
        return None
    return path.read_text(encoding="utf-8")
