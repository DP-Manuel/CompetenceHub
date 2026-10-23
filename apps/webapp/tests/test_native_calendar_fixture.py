import pytest
from datetime import UTC, datetime, timedelta

from scripts.native_calendar_fixture import staging_urls, public_query_window
from competence_hub_api.portal.calendar import validate_public_calendar_window


@pytest.mark.parametrize("delay", [timedelta(milliseconds=101), timedelta(seconds=30)])
def test_native_public_query_remains_valid_when_database_clock_advances(delay):
    sampled = datetime(2026, 10, 23, 10, tzinfo=UTC)
    with pytest.raises(ValueError):
        validate_public_calendar_window(from_at=sampled, to_at=sampled + timedelta(days=80), now=sampled + delay)
    window = public_query_window(sampled)
    validate_public_calendar_window(from_at=datetime.fromisoformat(window["from"]), to_at=datetime.fromisoformat(window["to"]), now=sampled + delay)


def urls():
    return {
        "COMPETENCE_HUB_TEST_APP_DATABASE_URL": "postgresql+asyncpg://competence_hub_app:synthetic@127.0.0.1:55432/competence_hub_staging",
        "COMPETENCE_HUB_TEST_MIGRATOR_DATABASE_URL": "postgresql+asyncpg://competence_hub_migrator:synthetic@127.0.0.1:55432/competence_hub_staging",
    }


def test_native_fixture_accepts_only_explicit_matching_staging_process_urls():
    values = urls()
    assert staging_urls(values) == tuple(values.values())


@pytest.mark.parametrize("change", [
    ("127.0.0.1", "217.160.255.86"),
    ("competence_hub_staging", "competence_hub_production"),
    ("competence_hub_app", "postgres"),
    ("postgresql+asyncpg", "postgresql"),
    (":synthetic@", "@"),
    ("/competence_hub_staging", "/competence_hub_staging?ssl=require"),
    (":55432/", ":55433/"),
])
def test_native_fixture_rejects_wrong_host_database_role_driver_password_options_or_tunnel(change):
    values = urls()
    name = "COMPETENCE_HUB_TEST_APP_DATABASE_URL"
    values[name] = values[name].replace(*change)
    with pytest.raises(ValueError):
        staging_urls(values)


def test_native_fixture_never_falls_back_to_secret_files_or_default_credentials():
    with pytest.raises(ValueError):
        staging_urls({})
