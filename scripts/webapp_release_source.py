"""Export only reviewed Webapp release inputs, never recursively copy a worktree."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

DEPLOY_FILES = frozenset({
    "deploy/README.md",
    "deploy/nginx/competence-hub-app.conf.example",
    "deploy/nginx/competence-hub-acme-http.conf.example",
    "deploy/postgresql/backup.conf.example",
    *[f"deploy/systemd/{name}.example" for name in (
        "competence-hub-api.service", "competence-hub-token-worker.service",
        "competence-hub-token-worker.timer", "competence-hub-postgres-backup.service",
        "competence-hub-postgres-backup.timer", "competence-hub-postgres-backup-monitor.service",
        "competence-hub-postgres-backup-monitor.timer")],
    *[f"deploy/scripts/{name}" for name in (
        "competence-hub-postgres-backup", "competence-hub-postgres-backup-monitor",
        "competence-hub-postgres-restore-check", "competence-hub-backup-notification-render")],
})
DOC_FILES = frozenset({
    "docs/architecture/coach-registry-contract-v0.1.md",
    "docs/architecture/coach-import-contract-v0.1.md",
    "docs/operations/cryptography-maintenance-2026-10-23.md",
    "docs/architecture/webapp-release-rehearsal-runbook.md",
    "docs/architecture/postgresql-backup-restore-runbook.md",
    "docs/architecture/calendar-cal1-technical-design-v0.1.md",
    "docs/architecture/calendar-cal1-api-contract-v0.1.md",
    "docs/architecture/webapp-dependency-assessment-2026-10-22.md",
    "docs/operations/cal1-production-readiness-2026-10-22.md",
    "docs/operations/cal1-linux-proxy-readiness-2026-10-22.md",
})


def destination(path):
    parts = PurePosixPath(path).parts
    if (not parts or PurePosixPath(path).is_absolute() or "\\" in path
            or any(part in {".", ".."} or part.startswith(".") for part in parts)):
        return None
    base = "apps/webapp/"
    if path in {base + "pyproject.toml"}:
        return "package-source/pyproject.toml"
    if path in {base + "requirements-production.lock", base + "requirements-build.lock"}:
        return "bundle/" + path.removeprefix(base)
    source = base + "src/competence_hub_api/"
    if path.startswith(source):
        relative = path.removeprefix(source)
        if (PurePosixPath(relative).suffix == ".py" or
                re.fullmatch(r"portal_ui/[a-z0-9_-]+\.(html|css|js)", relative)):
            return "package-source/src/competence_hub_api/" + relative
    if (path in {base + "database/README.md", base + "database/bootstrap-staging.sql"}
            or re.fullmatch(base + r"database/(migrations|verification)/000[1-8]_[a-z0-9_]+\.sql", path)):
        return "bundle/" + path.removeprefix(base)
    if path in DEPLOY_FILES or path in DOC_FILES:
        return "bundle/" + path
    return None


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout


def stage(repo, commit, build_root, *, working_tree=False):
    repo, build_root = Path(repo).resolve(), Path(build_root).resolve()
    resolved = git(repo, "rev-parse", "--verify", commit + "^{commit}").decode().strip()
    epoch = int(git(repo, "show", "-s", "--format=%ct", resolved))
    entries = []
    for record in git(repo, "ls-tree", "-rz", resolved).split(b"\0"):
        if not record:
            continue
        metadata, name = record.split(b"\t", 1)
        path = name.decode("utf-8")
        target = destination(path)
        if target is None:
            continue
        if metadata.split()[0] not in {b"100644", b"100755"}:
            raise ValueError("Release inputs must be regular Git files")
        entries.append((path, target))
    required = DEPLOY_FILES | DOC_FILES | {
        "apps/webapp/pyproject.toml", "apps/webapp/requirements-production.lock",
        "apps/webapp/requirements-build.lock", "apps/webapp/src/competence_hub_api/runtime.py",
        "apps/webapp/src/competence_hub_api/portal_ui/index.html",
    }
    if not required <= {path for path, _ in entries}:
        raise ValueError("Required release contract file is absent from selected commit")
    if build_root.exists() and any(build_root.iterdir()):
        raise ValueError("Release staging destination must be empty")
    inventory = []
    for path, target in sorted(entries):
        if working_tree:
            source = repo / path
            for node in (source, *source.parents):
                if node == repo:
                    break
                info = os.lstat(node)
                if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                    raise ValueError("Working-tree release input is a link/reparse point")
            data = source.read_bytes()
        else:
            data = git(repo, "show", f"{resolved}:{path}")
        output = build_root / target
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        inventory.append({"source": path, "destination": target,
                          "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    report = {"commit": resolved, "source_date_epoch": epoch,
              "source_mode": "working-tree-development" if working_tree else "committed-git-export",
              "deployment_authorized": False, "files": inventory}
    (build_root / "bundle/SOURCE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--build-root", required=True)
    parser.add_argument("--working-tree", action="store_true")
    args = parser.parse_args()
    report = stage(args.repo, args.commit, args.build_root, working_tree=args.working_tree)
    print(json.dumps({"commit": report["commit"], "files": len(report["files"]), "source_mode": report["source_mode"]}))
