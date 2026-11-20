"""Offline verification and fresh extraction for the private V2 staging package."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import sys
import zipfile


TARGET = {
    "database": "competence_hub_v2_pilot", "host": "127.0.0.1", "port": 5432,
    "role": "competence_hub_app", "origin": "https://localhost:8447",
    "cal2_mode": "synthetic-pilot", "invitation_delivery_enabled": False,
}
FORMAT = "competence-hub-private-v2/2"
MIGRATIONS = tuple(f"database/migrations/{name}.sql" for name in (
    "0007_coach_registry", "0008_coach_import_ledger", "0009_coach_lossless_target",
    "0010_calendar_reservations", "0011_calendar_reservation_replies", "0012_customer_administration",
))
MIGRATION_HEAD = 6 + len(MIGRATIONS)
BASELINE = {
    "evidence_only": True,
    "v12_source": "5a555e9a9aaeecd03ccfa0645929b58d95801488",
    "v12_archive_sha256": "754322cd57ab0f121a85f1625c1681fd271ec9049fa5beda9024437e77bdea58",
    "v12_receipt_sha256": "0a034aae3d1e351f4a5a9868592beda933acbb580658b14863f4362014190a4e",
    "tls_receipt_sha256": "e6b80664b761c5223bdc561524f8b086e3d246684d8ec3aafd710ed11b22e36d",
    "tls_leaf_pem_sha256": "c37975978dc9fbf2836fadb8000bccd51a73c0c21e72d6708fe77fce73d72f87",
    "tls_ca_sha256": "4b1c2ddd2b46329531fb8966f0c9d6ff34edcf15bdc7a1f6b894cb8ec8448cae",
    "tls_leaf_not_after_utc": "2026-11-30T18:09:39Z",
    "source_database": "competence_hub_staging",
    "services": ["competence-hub-pilot-api.service", "competence-hub-pilot-proxy.service",
                 "dp-chatbot.service", "nginx.service", "fail2ban.service", "postgresql.service"],
}
RUNBOOK = "docs/operations/portal-v2-private-staging.md"
HELPERS = ("deploy/v2/v2_package.py", "deploy/v2/v2_clone.py", "deploy/v2/v2_host.py", RUNBOOK,
           "deploy/v2/competence-hub-v2-api.service", "deploy/v2/competence-hub-v2-proxy.service",
           "deploy/v2/nginx.conf")
INVENTORY = "wheelhouse/INVENTORY.json"
HASH_LOCK = "wheelhouse/requirements-linux-x86_64-py312.hashes"
VERSION_LOCK = "requirements-production.lock"
INVENTORY_SHA = "98e85f0832b2769408cabcaf531b875913cd775e7961e5c52cdfb2e37a8b609f"
HASH_LOCK_SHA = "d32ef256b106c808c82b81894b21b6d3aa4c1aee3d5eea651fe7da59f8d52fc0"
RUNTIME_PREFIX = "competence_hub_api/"
APP_WHEEL = r"packages/competence_hub_api-[a-z0-9.]+-py3-none-any\.whl"


def require(ok, code):
    if not ok:
        raise ValueError(code)


def rejection_code(error):
    detail = str(error)
    return detail if type(error) is ValueError and re.fullmatch(r"[A-Z][A-Z0-9_]{2,80}", detail) else type(error).__name__


def sha(data):
    return hashlib.sha256(data).hexdigest()


def matches(pattern, value):
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def sha_valid(value):
    return matches(r"[0-9a-f]{64}", value)


def commit_valid(value):
    return matches(r"[0-9a-f]{40}", value)


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("ascii")


def json_read(data):
    def pairs(items):
        result = dict(items)
        require(len(result) == len(items), "DUPLICATE_JSON_KEY")
        return result

    return json.loads(data, object_pairs_hook=pairs)


def wheelhouse_entries(read):
    inventory, lock = read(INVENTORY), read(HASH_LOCK)
    require(sha(inventory) == INVENTORY_SHA and sha(lock) == HASH_LOCK_SHA, "ACCEPTED_WHEELHOUSE_REQUIRED")
    pins = {}
    for line in read(VERSION_LOCK).decode("ascii").splitlines():
        if line.strip() and not line.startswith("#"):
            match = re.fullmatch(r"([a-zA-Z0-9_.-]+)==([0-9.]+)", line)
            require(match, "VERSION_LOCK_FORMAT")
            name = re.sub(r"[-_.]+", "-", match[1]).lower()
            require(name not in pins, "DUPLICATE_VERSION_PIN")
            pins[name] = match[2]
    rows = json_read(inventory)["files"]
    require(pins == {row["name"]: row["version"] for row in rows}
            and len(rows) == len(pins), "WHEELHOUSE_DOES_NOT_MATCH_SOURCE_LOCK")
    wheels = {}
    for row in rows:
        require(matches(r"[a-zA-Z0-9_.-]+\.whl", row["file"]) and not row["pypi_vulnerabilities"],
                "WHEELHOUSE_ENTRY")
        name = "wheelhouse/" + row["file"]
        require(sha(read(name)) == row["sha256"], "WHEELHOUSE_WHEEL_SHA")
        wheels[name] = row["sha256"]
    return set(wheels) | {INVENTORY, HASH_LOCK}


def archive_members(archive):
    names = set()
    for entry in archive.infolist():
        name = entry.filename
        require(matches(r"[a-zA-Z0-9_-][a-zA-Z0-9_.-]*(/[a-zA-Z0-9_-][a-zA-Z0-9_.-]*)*", name)
                and name not in names and not entry.is_dir()
                and stat.S_IFMT(entry.external_attr >> 16) in (0, stat.S_IFREG), "UNSAFE_ARCHIVE_ENTRY")
        names.add(name)
    require(len(names) == len({name.lower() for name in names}), "ARCHIVE_CASE_COLLISION")
    return names


def verify_wheel(wheel_bytes, runtime):
    with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as wheel:
        names = archive_members(wheel)
        actual = {name: sha(wheel.read(name)) for name in names if name.startswith(RUNTIME_PREFIX)}
        require(actual == runtime and RUNTIME_PREFIX + "portal_ui/index.html" in actual
                and RUNTIME_PREFIX + "runtime.py" in actual, "WHEEL_SOURCE_MISMATCH")
        metadata = names - actual.keys()
        require(metadata and all(matches(r"competence_hub_api-[a-z0-9.]+\.dist-info/[a-zA-Z0-9_.-]+", name)
                                 for name in metadata), "UNREVIEWED_WHEEL_MEMBER")
        require(any(b"COMPETENCE_HUB_CAL2_MODE" in wheel.read(name) for name in actual if name.endswith(".py")),
                "V2_OPT_IN_CONTRACT_MISSING")


def verify(path, expected_sha, commit, evidence_sha, extract_to=None):
    require(sha_valid(expected_sha) and commit_valid(commit) and sha_valid(evidence_sha), "EXACT_PINS_REQUIRED")
    # Verify and consume the same archive bytes, not a subsequent reopening of the pathname.
    data = path.read_bytes()
    require(sha(data) == expected_sha, "ARCHIVE_SHA_MISMATCH")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive_members(archive)
        manifest = json_read(archive.read("MANIFEST.json"))
        require(manifest["format"] == FORMAT and manifest["commit"] == commit
                and manifest["tested_source_evidence_sha256"] == evidence_sha
                and manifest["source_mode"] == "committed-git-export"
                and manifest["deployment_authorized"] is False and manifest["real_coach_import_authorized"] is False,
                "RELEASE_IDENTITY_OR_SCOPE")
        require(manifest["target"] == TARGET and manifest["baseline"] == BASELINE
                and manifest["required_migrations_before"] == [f"{i:04}" for i in range(1, 7)]
                and manifest["ordered_migrations"] == list(MIGRATIONS), "MIGRATION_OR_TARGET_CONTRACT")
        files = manifest["files"]
        require(members == set(files) | {"MANIFEST.json"} and "MANIFEST.json" not in files,
                "ARCHIVE_INVENTORY_MISMATCH")
        for name, row in files.items():
            payload = archive.read(name)
            require(row == {"sha256": sha(payload), "bytes": len(payload)}, "PACKAGE_FILE_MISMATCH")
        wheels = {name for name in files if matches(APP_WHEEL, name)}
        require(len(wheels) == 1 and set(files) == wheels | wheelhouse_entries(archive.read)
                | set(MIGRATIONS) | set(HELPERS) | {VERSION_LOCK}, "UNREVIEWED_PACKAGE_FILE")
        verify_wheel(archive.read(next(iter(wheels))), manifest["runtime_source_sha256"])
        migrations = [archive.read(name) for name in MIGRATIONS]
        if extract_to is not None:
            extract_to.mkdir(mode=0o700, exist_ok=False)
            for name in sorted(members):
                target = extract_to / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(archive.read(name))
    return manifest, migrations


def add_package_arguments(parser):
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--source-evidence-sha256", required=True)


def verify_arguments(args):
    return verify(args.archive, args.sha256, args.commit, args.source_evidence_sha256,
                  getattr(args, "extract_to", None))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_package_arguments(parser)
    parser.add_argument("--extract-to", type=Path, help="Fresh private directory; nothing is overwritten")
    verify_arguments(parser.parse_args())
    print("V2_PACKAGE=PASS; deployment_authorized=false")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(f"V2_PACKAGE=STOP ({rejection_code(error)}); no activation authorized", file=sys.stderr)
        sys.exit(1)
