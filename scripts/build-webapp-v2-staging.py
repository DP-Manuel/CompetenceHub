"""Build only from the explicitly attested, final tested Git commit. No network."""

import argparse
import importlib.metadata
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import tomllib
import zipfile

from webapp_release_source import destination

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "deploy/v2"))
from v2_package import (  # noqa: E402
    BASELINE, FORMAT, HASH_LOCK, HELPERS, INVENTORY, MIGRATIONS, TARGET, VERSION_LOCK,
    commit_valid, json_bytes, json_read, require, sha, sha_valid, verify,
    wheelhouse_entries,
)

WEBAPP = "apps/webapp/"
BUILDER_FILES = ("scripts/build-webapp-v2-staging.py", "scripts/webapp_release_source.py", "deploy/v2/v2_package.py")


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True,
                          env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_NO_REPLACE_OBJECTS": "1",
                               "GIT_ALLOW_PROTOCOL": ""}).stdout


def export(commit):
    require(commit_valid(commit) and git("rev-parse", "--verify", commit + "^{commit}").decode().strip() == commit,
            "FULL_EXISTING_COMMIT_REQUIRED")
    entries = {}
    builder = {}
    for line in git("ls-tree", "-rz", commit).split(b"\0"):
        if not line:
            continue
        metadata, filename = line.split(b"\t", 1)
        name = filename.decode("utf-8")
        target = destination(name)
        if name in BUILDER_FILES:
            builder[name] = metadata
        if target and target.startswith("package-source/"):
            exported = target
        elif name in HELPERS:
            exported = name
        elif name in {WEBAPP + path for path in (*MIGRATIONS, VERSION_LOCK, "requirements-build.lock")}:
            exported = name.removeprefix(WEBAPP)
        else:
            require(not name.startswith(WEBAPP + "src/competence_hub_api/"), "UNREVIEWED_RUNTIME_ASSET")
            continue
        mode, kind, oid = metadata.decode("ascii").split()
        require(kind == "blob" and mode in {"100644", "100755"}, "REGULAR_GIT_BLOB_REQUIRED")
        entries[exported] = git("cat-file", "blob", oid)
    require({*HELPERS, *MIGRATIONS, VERSION_LOCK, "requirements-build.lock", "package-source/pyproject.toml"}
            <= set(entries), "FINAL_COMMIT_RELEASE_INPUT_MISSING")
    require(set(builder) == set(BUILDER_FILES), "FINAL_COMMIT_BUILDER_MISSING")
    for name, metadata in builder.items():
        mode, kind, oid = metadata.decode("ascii").split()
        require(kind == "blob" and mode in {"100644", "100755"} and not (ROOT / name).is_symlink()
                and (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
                == git("cat-file", "blob", oid).replace(b"\r\n", b"\n"), "BUILDER_MUST_MATCH_TESTED_COMMIT")
    require(any(b"COMPETENCE_HUB_CAL2_MODE" in data for name, data in entries.items()
                if name.startswith("package-source/src/") and name.endswith(".py")), "V2_OPT_IN_CONTRACT_MISSING")
    return entries


def build(args):
    evidence = args.tested_source_receipt.read_bytes()
    receipt = json_read(evidence)
    require(sha_valid(args.source_evidence_sha256) and sha(evidence) == args.source_evidence_sha256
            and set(receipt) == {"commit", "result", "integration_report_sha256"}
            and receipt["commit"] == args.commit and receipt["result"] == "PASS"
            and sha_valid(receipt["integration_report_sha256"]), "TESTED_SOURCE_RECEIPT_REQUIRED")
    files = export(args.commit)
    locks = files.pop("requirements-build.lock").decode("ascii").splitlines()
    for line in locks:
        if line.strip() and not line.startswith("#"):
            name, version = line.split("==")
            require(importlib.metadata.version(name) == version, "PINNED_BUILD_TOOL_REQUIRED")

    def read_cached(name):
        if name == VERSION_LOCK:
            return files[name]
        source = args.wheelhouse / name.removeprefix("wheelhouse/")
        require(source.is_file() and not source.is_symlink(), "REGULAR_CACHED_WHEELHOUSE_FILE_REQUIRED")
        return files.setdefault(name, source.read_bytes())

    wheelhouse_entries(read_cached)
    require({INVENTORY, HASH_LOCK} <= files.keys(), "WHEELHOUSE_MISSING")
    epoch = int(git("show", "-s", "--format=%ct", args.commit))
    version = tomllib.loads(files["package-source/pyproject.toml"].decode("utf-8"))["project"]["version"]
    runtime = {}
    with tempfile.TemporaryDirectory(prefix="competence-hub-v2-build-") as directory:
        temp = Path(directory)
        for name in sorted(key for key in files if key.startswith("package-source/")):
            path = temp / name
            path.parent.mkdir(parents=True, exist_ok=True)
            data = files.pop(name)
            path.write_bytes(data)
            if name.startswith("package-source/src/"):
                runtime[name.removeprefix("package-source/src/")] = sha(data)
        wheel_dir = temp / "packages"
        env = {k: v for k, v in os.environ.items() if not k.startswith("PIP_")}
        env.update(PIP_CONFIG_FILE=os.devnull, SOURCE_DATE_EPOCH=str(epoch))
        subprocess.run([sys.executable, "-I", "-m", "pip", "--disable-pip-version-check", "wheel", "--no-index",
                        "--no-deps", "--no-build-isolation", "--wheel-dir", str(wheel_dir),
                        str(temp / "package-source")], check=True, env=env, cwd=temp, capture_output=True)
        wheels = list(wheel_dir.glob("*.whl"))
        require(len(wheels) == 1, "EXPECTED_SINGLE_APPLICATION_WHEEL")
        files["packages/" + wheels[0].name] = wheels[0].read_bytes()
        files["MANIFEST.json"] = json_bytes({
            "format": FORMAT, "commit": args.commit, "version": version,
            "source_mode": "committed-git-export", "source_date_epoch": epoch,
            "tested_source_evidence_sha256": args.source_evidence_sha256,
            "deployment_authorized": False, "real_coach_import_authorized": False,
            "target": TARGET, "baseline": BASELINE, "required_migrations_before": [f"{i:04}" for i in range(1, 7)],
            "ordered_migrations": MIGRATIONS, "runtime_source_sha256": runtime,
            "files": {name: {"sha256": sha(data), "bytes": len(data)} for name, data in files.items()},
        })
        archive = temp / "release.zip"
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
            for name, data in sorted(files.items()):
                member = zipfile.ZipInfo(name, time.gmtime(epoch)[:6])
                member.create_system = 3
                member.external_attr = 0o100644 << 16
                member.compress_type = zipfile.ZIP_DEFLATED
                output.writestr(member, data)
        artifact = archive.read_bytes()
        digest = sha(artifact)
        verify(archive, digest, args.commit, args.source_evidence_sha256)
        args.output_directory.mkdir(mode=0o700, exist_ok=False)
        filename = f"competence-hub-private-v2-{args.commit}.zip"
        (args.output_directory / filename).write_bytes(artifact)
        (args.output_directory / (filename + ".sha256")).write_text(f"{digest}  {filename}\n", encoding="ascii")
    print(f"V2_PACKAGE_BUILT={filename}\nSHA256={digest}\ndeployment_authorized=false")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tested-source-receipt", type=Path, required=True)
    parser.add_argument("--source-evidence-sha256", required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    build(parser.parse_args())


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError, importlib.metadata.PackageNotFoundError) as exc:
        code = str(exc) if type(exc) is ValueError and str(exc).isupper() else type(exc).__name__
        print(f"V2_BUILD_STOP={code}", file=sys.stderr)
        sys.exit(1)
