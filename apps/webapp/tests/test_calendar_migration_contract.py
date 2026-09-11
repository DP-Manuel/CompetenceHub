from pathlib import Path


DATABASE_ROOT = Path(__file__).parents[1] / "database"
MIGRATION = DATABASE_ROOT / "migrations" / "0005_calendar_availability_and_review.sql"
SMOKE = DATABASE_ROOT / "verification" / "0005_calendar_availability_and_review_smoke.sql"


def test_calendar_migration_contains_approved_schema_and_bounds() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")

    assert "CREATE TABLE competence_hub.calendar_offers" in sql
    assert "CREATE TABLE competence_hub.calendar_offer_revisions" in sql
    assert "CREATE TABLE competence_hub.calendar_review_decisions" in sql
    assert "VALUES ('calendar_reviewer', 'Kalenderpruefung')" in sql
    assert "format_code IN ('online', 'praesenz', 'hybrid')" in sql
    assert "time_zone text NOT NULL DEFAULT 'Europe/Berlin'" in sql
    assert "char_length(time_zone) <= 64" in sql
    assert "capacity BETWEEN 1 AND 500" in sql
    assert "review_threshold BETWEEN 1 AND capacity" in sql
    assert "char_length(title) <= 160" in sql
    assert "char_length(summary) <= 1200" in sql
    assert "char_length(public_location) <= 200" in sql
    assert "char_length(price_display_text) <= 200" in sql
    assert "char_length(note) <= 1000" in sql
    assert "calendar_review_decisions_revision_uq UNIQUE (revision_id)" in sql


def test_calendar_migration_keeps_runtime_role_non_destructive() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")

    assert "GRANT SELECT, INSERT, UPDATE\n    ON competence_hub.calendar_offers" in sql
    assert "GRANT SELECT, INSERT, UPDATE\n    ON competence_hub.calendar_offer_revisions" in sql
    assert "GRANT SELECT, INSERT\n    ON competence_hub.calendar_review_decisions" in sql
    assert "GRANT SELECT, INSERT, UPDATE, DELETE" not in sql
    assert "ON DELETE CASCADE" not in sql
    assert "review_threshold\n    IS 'Internal review threshold; never expose" in sql


def test_calendar_smoke_is_synthetic_and_rollback_only() -> None:
    sql = SMOKE.read_text(encoding="utf-8")

    assert sql.startswith("\\set ON_ERROR_STOP on\n\nBEGIN;")
    assert "example.invalid" in sql
    assert "Overlapping drafts were not retained" in sql
    assert "Runtime role has forbidden Calendar mutation rights" in sql
    assert sql.rstrip().endswith("ROLLBACK;")
