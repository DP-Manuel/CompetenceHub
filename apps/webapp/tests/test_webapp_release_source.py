import importlib.util
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("release_source", ROOT / "scripts/webapp_release_source.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


@pytest.mark.parametrize("path", [
    ".env", "deploy/.env.production", "deploy/private.key", "deploy/website/sftp-target.example.json",
    "Quellen/coach.docx", "apps/webapp/tests/test_runtime.py", "apps/webapp/scripts/native_calendar_fixture.py",
    "apps/webapp/src/competence_hub_api/.env", "apps/webapp/src/competence_hub_api/__pycache__/a.pyc",
    "apps/webapp/src/competence_hub_api/portal_ui/backup.zip", "../deploy/README.md",
    "/deploy/README.md", "deploy/../deploy/README.md", "deploy\\README.md",
    "apps/webapp/database/real-database.dump", "apps/webapp/database/verification/fixtures.sql",
])
def test_release_denylist_is_not_a_recursive_copy(path):
    assert release.destination(path) is None


@pytest.mark.parametrize("path", [
    "apps/webapp/src/competence_hub_api/auth/admission.py",
    "apps/webapp/src/competence_hub_api/portal_ui/app.js",
    "apps/webapp/database/migrations/0006_coach_public_profile_path.sql",
    "docs/operations/cal1-production-readiness-2026-10-22.md",
    "docs/operations/cal1-linux-proxy-readiness-2026-10-22.md",
    "deploy/nginx/competence-hub-acme-http.conf.example",
])
def test_release_preserves_actual_runtime_and_current_contract(path):
    assert release.destination(path)


def command(repo, *args, input=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=input, check=True, capture_output=True).stdout


@pytest.fixture
def repository(tmp_path):
    command(tmp_path, "init", "-q")
    required = release.DEPLOY_FILES | release.DOC_FILES | {
        "apps/webapp/pyproject.toml", "apps/webapp/requirements-production.lock",
        "apps/webapp/requirements-build.lock", "apps/webapp/src/competence_hub_api/runtime.py",
        "apps/webapp/src/competence_hub_api/portal_ui/index.html",
    }
    for path in required:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"reviewed\n")
    command(tmp_path, "add", ".")
    command(tmp_path, "-c", "user.name=ReleaseTest", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture")
    return tmp_path


def test_export_uses_git_bytes_and_ignores_dirty_and_untracked_material(repository, tmp_path_factory):
    original = repository / "apps/webapp/src/competence_hub_api/runtime.py"
    original.write_bytes(b"not committed\n")
    (repository / ".env").write_bytes(b"synthetic excluded sentinel\n")
    first = tmp_path_factory.mktemp("export-a")
    second = tmp_path_factory.mktemp("export-b")
    a = release.stage(repository, "HEAD", first)
    b = release.stage(repository, "HEAD", second)
    assert a == b
    assert a["deployment_authorized"] is False
    assert a["source_mode"] == "committed-git-export"
    assert (first / "package-source/src/competence_hub_api/runtime.py").read_bytes() == b"reviewed\n"
    assert not any(".env" in row["source"] for row in a["files"])


def test_selected_git_symlink_is_rejected_without_reading_target(repository, tmp_path_factory):
    blob = command(repository, "hash-object", "-w", "--stdin", input=b"/excluded/private.key").decode().strip()
    command(repository, "update-index", "--cacheinfo", f"120000,{blob},apps/webapp/src/competence_hub_api/runtime.py")
    command(repository, "-c", "user.name=ReleaseTest", "-c", "user.email=test@example.invalid", "commit", "-qm", "link")
    with pytest.raises(ValueError, match="regular Git files"):
        release.stage(repository, "HEAD", tmp_path_factory.mktemp("export-link"))


def test_incomplete_commit_cannot_build_release(repository, tmp_path_factory):
    command(repository, "rm", "-q", "apps/webapp/requirements-build.lock")
    command(repository, "-c", "user.name=ReleaseTest", "-c", "user.email=test@example.invalid", "commit", "-qm", "missing")
    with pytest.raises(ValueError, match="Required release contract"):
        release.stage(repository, "HEAD", tmp_path_factory.mktemp("export-missing"))


def test_templates_preserve_proxy_and_service_boundaries():
    unit = (ROOT / "deploy/systemd/competence-hub-api.service.example").read_text()
    nginx = (ROOT / "deploy/nginx/competence-hub-app.conf.example").read_text()
    assert "--host 127.0.0.1" in unit
    assert "--forwarded-allow-ips=127.0.0.1" in unit
    assert "StartLimitIntervalSec=60" in unit and "StartLimitBurst=5" in unit
    assert "--no-access-log" in unit and "StandardOutput=journal" in unit
    assert "proxy_set_header X-Forwarded-For $remote_addr;" in nginx
    assert "proxy_set_header X-Forwarded-Proto https;" in nginx
    assert "proxy_set_header Host __APP_HOSTNAME__;" in nginx
    assert "client_max_body_size 32k;" in nginx
    assert "proxy_add_x_forwarded_for" not in nginx
    assert "includeSubDomains" not in nginx and "preload" not in nginx
