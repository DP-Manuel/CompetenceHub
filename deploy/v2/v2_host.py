"""Read-only V1.2 preservation checks and offline installation into a fresh V2 venv."""

import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile

from v2_package import (
    BASELINE, HASH_LOCK, add_package_arguments, json_bytes, json_read, matches, require, sha, verify,
    rejection_code,
)


V1_API, V1_PROXY, *_ = BASELINE["services"]
V2_SERVICES = ("competence-hub-v2-api.service", "competence-hub-v2-proxy.service")
V1_EXEC = "/opt/competence-hub-pilot/releases/5a555e9a9aae/venv/bin/uvicorn"
V1_DROPS = tuple(f"/etc/systemd/system/{V1_API}.d/{name}" for name in
                 ("20-v1-runtime.conf", "22-v11-runtime.conf", "24-v12-runtime.conf"))
V1_PROXY_FRAGMENT = Path("/etc/systemd/system") / V1_PROXY
V1_PROXY_FRAGMENT_SHA = "bf4f56169ef745cd50c22a70788c5615cd58cd083b1336ad8aaacab0967d151f"
V2_LISTENERS = {"127.0.0.1:8002", "127.0.0.1:8444"}
V2_RUNTIME = Path("/opt/competence-hub-v2/runtime")


def command(*args, **kwargs):
    result = subprocess.run(args, capture_output=True, text=True, timeout=180, **kwargs)
    require(result.returncode == 0, "LOCAL_COMMAND_FAILED")
    return result.stdout


def properties(unit, *names):
    output = command("/usr/bin/systemctl", "show", unit, *["--property=" + name for name in names])
    return dict(line.split("=", 1) for line in output.splitlines())


def inventory():
    services = {}
    for name in BASELINE["services"]:
        row = properties(name, "ActiveState", "InvocationID")
        require(row.get("ActiveState") == "active" and matches(r"[0-9a-f]{32}", row.get("InvocationID"))
                and row["InvocationID"] != "0" * 32, "SIX_REFERENCE_SERVICES_REQUIRED")
        services[name] = row["InvocationID"]
    runtime = properties(V1_API, "ExecStart", "DropInPaths")
    require(f"path={V1_EXEC} ;" in runtime["ExecStart"]
            and "--host 127.0.0.1 --port 8001" in runtime["ExecStart"]
            and tuple(runtime["DropInPaths"].split()) == V1_DROPS, "EXACT_V12_FALLBACK_REQUIRED")
    proxy = properties(V1_PROXY, "FragmentPath", "DropInPaths")
    require(proxy == {"FragmentPath": str(V1_PROXY_FRAGMENT), "DropInPaths": ""}
            and not V1_PROXY_FRAGMENT.is_symlink() and sha(V1_PROXY_FRAGMENT.read_bytes()) == V1_PROXY_FRAGMENT_SHA,
            "ACCEPTED_PROXY_UNIT_REQUIRED")
    listeners = {line.split()[3] for line in command("/usr/bin/ss", "-ltnH").splitlines()}
    for port in ("8001", "8443", "5432"):
        found = {address for address in listeners if address.endswith(":" + port)}
        allowed = {f"127.0.0.1:{port}"} | ({"[::1]:5432"} if port == "5432" else set())
        require(f"127.0.0.1:{port}" in found and found <= allowed, "REFERENCE_LOOPBACK_REQUIRED")
    # Compare all listeners while keeping unrelated addresses out of the receipt.
    others = sorted(address for address in listeners if not address.endswith((":8002", ":8444")))
    return {"six_invocation_ids": services, "reference_listeners_sha256": sha(json_bytes(others)),
            "v2_listeners": sorted(listeners - set(others))}


def host_check(args):
    manifest, _ = verify(args.archive, args.sha256, args.commit, args.source_evidence_sha256)
    current = inventory()
    scope = {"commit": args.commit, "archive_sha256": args.sha256,
             "source_evidence_sha256": args.source_evidence_sha256, "deployment_authorized": False}
    if args.phase == "before":
        require(not current["v2_listeners"] and args.before is None and args.before_sha256 is None,
                "FRESH_V2_PORTS_REQUIRED")
    else:
        require(args.before and args.before_sha256, "BOUND_BEFORE_RECEIPT_REQUIRED")
        data = args.before.read_bytes()
        require(sha(data) == args.before_sha256, "HOST_RECEIPT_SHA_MISMATCH")
        expected = {**current, **scope, "phase": "before", "v2_listeners": []}
        require(json_read(data) == expected, "V12_REFERENCE_HOST_CHANGED")
        active = args.phase == "active"
        require(set(current["v2_listeners"]) == (V2_LISTENERS if active else set()), "UNEXPECTED_V2_LISTENERS")
        for name in V2_SERVICES:
            state = properties(name, "ActiveState")["ActiveState"]
            require(state == "active" if active else state in {"inactive", "failed"}, "V2_SERVICE_STATE")
            if active:
                fragment = Path("/etc/systemd/system") / name
                require(properties(name, "FragmentPath", "DropInPaths") == {"FragmentPath": str(fragment), "DropInPaths": ""}
                        and not fragment.is_symlink()
                        and sha(fragment.read_bytes()) == manifest["files"][f"deploy/v2/{name}"]["sha256"],
                        "V2_UNIT_BYTES_CHANGED")
        if active:
            proxy = V2_RUNTIME.parent / "nginx.conf"
            require(not proxy.is_symlink() and sha(proxy.read_bytes()) == manifest["files"]["deploy/v2/nginx.conf"]["sha256"],
                    "V2_PROXY_BYTES_CHANGED")
    print(json_bytes({**current, **scope, "phase": args.phase}).decode(), end="")


def install(args):
    require(sys.platform == "linux" and sys.version_info[:2] == (3, 12) and platform.machine() == "x86_64"
            and platform.freedesktop_os_release().get("ID") == "ubuntu"
            and platform.freedesktop_os_release().get("VERSION_ID") == "24.04", "LINUX_RUNTIME_REQUIRED")
    require(args.runtime == V2_RUNTIME and os.geteuid() == 0
            and args.runtime.parent.resolve(strict=True) == args.runtime.parent
            and args.runtime.parent.stat().st_uid == 0 and not args.runtime.parent.stat().st_mode & 0o022
            and not args.runtime.exists() and not args.runtime.is_symlink(), "FRESH_OWNED_V2_RUNTIME_PATH_REQUIRED")
    old_umask = os.umask(0o022)
    try:
        install_verified(args)
    finally:
        os.umask(old_umask)


def install_verified(args):
    # The fresh directory remains inactive even if installation fails midway.
    with tempfile.TemporaryDirectory(prefix="competence-hub-v2-install-") as tmp:
        bundle = Path(tmp) / "verified"
        manifest, _ = verify(args.archive, args.sha256, args.commit, args.source_evidence_sha256, bundle)
        args.runtime.mkdir(mode=0o755)
        venv.create(args.runtime, with_pip=True)
        python = str(args.runtime.resolve() / "bin/python")
        env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "PIP_", "UV_"))}
        env["PIP_CONFIG_FILE"] = os.devnull
        env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
        pip = (python, "-I", "-m", "pip", "--disable-pip-version-check")
        offline = ("install", "--no-index", "--only-binary=:all:", "--no-cache-dir")
        command(*pip, *offline, "--require-hashes", "--find-links", str(bundle / "wheelhouse"),
                "-r", str(bundle / HASH_LOCK), env=env)
        command(*pip, *offline, "--no-deps", str(next((bundle / "packages").glob("*.whl"))), env=env)
        command(*pip, "check", env=env)
        command(python, "-I", "-c", "from competence_hub_api.runtime import create_runtime_app_from_environment",
                env=env)
        site_packages = args.runtime / "lib/python3.12/site-packages"
        for name, digest in manifest["runtime_source_sha256"].items():
            require(sha((site_packages / name).read_bytes()) == digest, "INSTALLED_WHEEL_SOURCE_MISMATCH")
        with (args.runtime / "V2-INSTALL.json").open("xb") as out:
            out.write(json_bytes({"commit": manifest["commit"], "archive_sha256": args.sha256,
                                  "installation": "offline", "deployment_authorized": False}))
    print("V2_OFFLINE_INSTALL=PASS; no service activation")


def linux_verify(args):
    require(Path("/.dockerenv").is_file() and sorted(p.name for p in Path("/sys/class/net").iterdir()) == ["lo"],
            "DISPOSABLE_NETWORK_NONE_CONTAINER_REQUIRED")
    V2_RUNTIME.parent.mkdir(mode=0o755, exist_ok=False)
    args.runtime = V2_RUNTIME
    install(args)
    with tempfile.TemporaryDirectory(prefix="competence-hub-v2-unit-check-") as tmp:
        bundle = Path(tmp) / "verified"
        verify(args.archive, args.sha256, args.commit, args.source_evidence_sha256, bundle)
        units = []
        for name in V2_SERVICES:
            target = Path(tmp) / name
            shutil.copyfile(bundle / "deploy/v2" / name, target)
            target.chmod(0o644)
            units.append(str(target))
        command("/usr/bin/systemd-analyze", "verify", *units)
    print("V2_LINUX_PACKAGE=PASS; offline install, installed source bytes and unit syntax; no service activation")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="command", required=True)
    check = modes.add_parser("host-check")
    add_package_arguments(check)
    check.add_argument("--phase", required=True, choices=("before", "active", "fallback"))
    check.add_argument("--before", type=Path)
    check.add_argument("--before-sha256")
    stage = modes.add_parser("offline-install")
    add_package_arguments(stage)
    stage.add_argument("--runtime", type=Path, required=True)
    probe = modes.add_parser("linux-verify")
    add_package_arguments(probe)
    args = parser.parse_args()
    {"host-check": host_check, "offline-install": install, "linux-verify": linux_verify}[args.command](args)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        print(f"V2_HOST=STOP ({rejection_code(error)}); no activation authorized", file=sys.stderr)
        sys.exit(1)
