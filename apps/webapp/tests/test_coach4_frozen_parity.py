from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

from scripts.coach_projection_fixture import synthetic_registry
from competence_hub_api.portal.coach_projection import generate_projection

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    spec = importlib.util.spec_from_file_location(
        "coach4_frozen_parity", ROOT / "scripts/coach4_frozen_parity.py"
    )
    parity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parity)
finally:
    sys.path.remove(str(ROOT / "scripts"))


def test_pure_synthetic_frozen_comparison_all_dimensions_and_unknown_production():
    registry = synthetic_registry()
    preview = generate_projection(registry, "preview")
    production = generate_projection(registry, "production")
    rows = []
    for c in registry:
        r = c.revisions[0]
        rows.append(
            {
                "content": r.content.model_dump(mode="json"),
                "topics": [
                    {"name": t.name, "categories": list(t.categories)} for t in r.topics
                ],
                **{
                    "projection_"
                    + env: next(
                        (
                            p
                            for p in value["coaches"]
                            if p["profile_path"] == r.content.profile_path
                        ),
                        None,
                    )
                    for env, value in (("preview", preview), ("production", production))
                },
            }
        )
    before = deepcopy(rows)
    for env, count in (("preview", 2), ("production", 1)):
        report, generated = parity.simulate_reviewed_rows(rows, env)
        assert report["status"] == "PASS"
        assert all(report["checks"].values())
        assert len(generated["coaches"]) == count
    assert rows == before
    rows[0]["projection_preview"]["short_intro"] = "Changed frozen public intro"
    assert parity.simulate_reviewed_rows(rows, "preview")[0]["status"] == "DIFFERENT"
