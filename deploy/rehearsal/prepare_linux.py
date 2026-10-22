"""Local disposable Ubuntu validation; not a VPS installation tool."""
import email.parser
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import traceback
import urllib.request
import venv
import zipfile

ROOT = Path("/work")


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Local preparation command failed: " + Path(args[0]).name)
    return result.stdout


def main():
    if not Path("/.dockerenv").exists() or not (ROOT / "LOCAL_REHEARSAL_ONLY").exists():
        raise RuntimeError("Refusing execution outside the owned local container")
    package = ROOT / "release.zip"
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    if digest != sys.argv[1]:
        raise ValueError("Release checksum mismatch")
    bundle = ROOT / "bundle"
    with zipfile.ZipFile(package) as archive:
        manifest = json.loads(archive.read("MANIFEST.json").decode("utf-8-sig"))
        if manifest["dirty"] or manifest["deployment_authorized"]:
            raise ValueError("Unexpected release authority or dirty source")
        files = {row["path"]: row for row in manifest["files"]}
        if set(archive.namelist()) != set(files) | {"MANIFEST.json"}:
            raise ValueError("Archive differs from its exact inventory")
        for name in archive.namelist():
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name or any(p.startswith(".") for p in path.parts):
                raise ValueError("Unsafe release entry")
            data = archive.read(name)
            if name in files and (len(data) != files[name]["bytes"] or hashlib.sha256(data).hexdigest() != files[name]["sha256"]):
                raise ValueError("Inventory checksum mismatch")
            target = bundle / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    print("PASS | Exact release inventory and checksums", flush=True)
    tools = ROOT / "build-venv"
    venv.create(tools, with_pip=True)
    pip = str(tools / "bin/python")
    run(pip, "-m", "pip", "--isolated", "install", "--index-url", "https://pypi.org/simple", "--only-binary=:all:", "-r", str(bundle / "requirements-build.lock"))
    wheels = ROOT / "wheelhouse"
    wheels.mkdir()
    run(pip, "-m", "pip", "--isolated", "download", "--index-url", "https://pypi.org/simple", "--only-binary=:all:", "-r", str(bundle / "requirements-production.lock"), "--dest", str(wheels))
    pins = {}
    for line in (bundle / "requirements-production.lock").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, version = line.split("==")
            pins[re.sub(r"[-_.]+", "-", name).lower()] = version
    inventory, seen, requirements = [], set(), []
    for wheel in sorted(wheels.glob("*.whl")):
        with zipfile.ZipFile(wheel) as archive:
            metadata = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
            package_metadata = email.parser.BytesParser().parsebytes(archive.read(metadata))
        name = re.sub(r"[-_.]+", "-", package_metadata["Name"]).lower()
        version = package_metadata["Version"]
        if name in seen or pins.get(name) != version:
            raise ValueError("Unpinned or duplicate runtime dependency")
        seen.add(name)
        sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{version}/json", timeout=30) as response:
            upstream = json.load(response)
        if not any(row["filename"] == wheel.name and row["digests"]["sha256"] == sha for row in upstream["urls"]):
            raise ValueError("Wheel does not match published PyPI checksum")
        inventory.append({"name": name, "version": version, "file": wheel.name, "sha256": sha,
                          "pypi_vulnerabilities": [item["id"] for item in upstream.get("vulnerabilities", [])]})
        requirements.append(f"{name}=={version} --hash=sha256:{sha}")
    if seen != set(pins):
        raise ValueError("Runtime wheelhouse is incomplete")
    (wheels / "requirements-linux-x86_64-py312.hashes").write_text("\n".join(requirements) + "\n")
    (wheels / "INVENTORY.json").write_text(json.dumps({"source": "https://pypi.org/simple", "runtime": "Ubuntu 24.04 x86_64 Python 3.12", "files": inventory}, indent=2))
    if any(row["pypi_vulnerabilities"] for row in inventory):
        raise RuntimeError("Published dependency advisories require review before the local install")
    print("PASS | Exact Linux wheels, published hashes and PyPI advisory snapshot", flush=True)
    target = Path("/opt/competence-hub/releases/local-rehearsal")
    target.mkdir(parents=True)
    runtime = target / "venv"
    venv.create(runtime, with_pip=True)
    python = str(runtime / "bin/python")
    run(python, "-m", "pip", "--isolated", "install", "--no-index", "--only-binary=:all:", "--require-hashes", "--find-links", str(wheels), "-r", str(wheels / "requirements-linux-x86_64-py312.hashes"))
    wheel = next((bundle / "packages").glob("*.whl"))
    run(python, "-m", "pip", "--isolated", "install", "--no-index", "--no-deps", str(wheel))
    run(python, "-m", "pip", "check")
    (target.parent.parent / "current").symlink_to(target, target_is_directory=True)
    report = {"release_sha256": digest, "commit": manifest["commit"], "runtime_dependencies": len(inventory),
              "python": run(python, "--version").strip(), "nginx": run("dpkg-query", "-W", "-f=${Version}", "nginx"),
              "systemd": run("dpkg-query", "-W", "-f=${Version}", "systemd"), "source": "PyPI exact binary wheels, offline hash-verified install",
              "vps_changed": False, "deployment_authorized": False}
    (ROOT / "package-result.json").write_text(json.dumps(report, indent=2))
    print("PASS | Fresh Linux venv, offline runtime install and pip check", flush=True)
    print("LOCAL_PACKAGE_PREPARATION=PASS", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Never print driver/SQL exception strings or locals.
        (ROOT / "preparation-failure.json").write_text(json.dumps({
            "failure_type": type(error).__name__,
            "frames": [{"function": frame.name, "line": frame.lineno} for frame in traceback.extract_tb(error.__traceback__)
                       if Path(frame.filename).name == Path(__file__).name]
        }, indent=2))
        print("LOCAL_PREPARATION_FAIL " + type(error).__name__, flush=True)
        raise SystemExit(1)
