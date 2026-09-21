from pathlib import Path

import pytest

from competence_hub_api.portal.coach_profiles import validate_public_profile_path


DATABASE_ROOT = Path(__file__).parents[1] / "database"
MIGRATION = DATABASE_ROOT / "migrations" / "0006_coach_public_profile_path.sql"
SMOKE = DATABASE_ROOT / "verification" / "0006_coach_public_profile_path_smoke.sql"


@pytest.mark.parametrize(
    "value",
    [
        "https://example.invalid/coaches/test/",
        "//example.invalid/coaches/test/",
        "/coaches/../admin/",
        "/coaches/test/?x=1",
        "/coaches/test/#fragment",
        "/kontakt/",
        "",
        " /coaches/test/",
        "/coaches//test/",
        "/coaches/test%2fadmin/",
        "/coaches/test\\admin/",
        "/coaches/Test/",
        "/coaches/test",
    ],
)
def test_public_profile_path_rejects_unsafe_or_noncanonical_values(value: str) -> None:
    with pytest.raises(ValueError, match="public_profile_path"):
        validate_public_profile_path(value)


def test_public_profile_path_accepts_null_and_canonical_coach_path() -> None:
    assert validate_public_profile_path(None) is None
    assert (
        validate_public_profile_path("/coaches/christian-galvano/")
        == "/coaches/christian-galvano/"
    )


def test_public_profile_path_has_no_name_to_slug_fallback() -> None:
    with pytest.raises(ValueError):
        validate_public_profile_path("Christian Galvano")


def test_profile_path_migration_is_additive_unique_and_does_not_map_real_data() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")

    assert "ADD COLUMN public_profile_path text" in sql
    assert "char_length(public_profile_path) <= 200" in sql
    assert "^/coaches/[a-z0-9]+(-[a-z0-9]+)*/$" in sql
    assert "CREATE UNIQUE INDEX coaches_public_profile_path_uq" in sql
    assert "WHERE public_profile_path IS NOT NULL" in sql
    assert "UPDATE competence_hub.coaches" not in sql
    assert "INSERT INTO competence_hub.coaches" not in sql
    assert "VALUES ('0006', 'Explicit public Coach profile path mapping')" in sql


def test_profile_path_smoke_checks_duplicate_and_unsafe_paths_then_rolls_back() -> None:
    sql = SMOKE.read_text(encoding="utf-8")

    assert "Synthetic Duplicate" in sql
    assert "WHEN unique_violation" in sql
    assert "WHEN check_violation" in sql
    assert sql.rstrip().endswith("ROLLBACK;")
