"""One local native PostgreSQL Calendar demo or acceptance; no external target."""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from uuid import uuid4
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import uvicorn
from scripts.browser_acceptance_app import create_loopback_certificate
from scripts.cal1_demo_app import attach_demo_views
from scripts.cal1_public_build import build_public_calendar
from scripts.local_calendar_postgres import LocalCalendarPostgres
from scripts.native_calendar_fixture import NativeCalendarFixture


class LocalPilotFixture(NativeCalendarFixture):
    def __init__(self):
        super().__init__(local_container_rehearsal=True)
        self.password = "Synthetic-Portal-2026!"
        for key in self.roles:
            suffix = {"coach_two": "coach-empty", "contact": "company"}.get(key, key)
            self.emails[key] = f"synthetic.{suffix}@example.invalid"

    def app(self, port):
        return attach_demo_views(super().app(port), native=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance", action="store_true")
    parser.add_argument("--integrated-acceptance", action="store_true")
    parser.add_argument("--onboarding-acceptance", action="store_true")
    parser.add_argument("--port", type=int, default=8447)
    parser.add_argument("--browser-executable", type=Path,
        default=Path(os.environ["LOCALAPPDATA"]) / "ms-playwright/chromium-1228/chrome-win64/chrome.exe")
    options = parser.parse_args()
    if options.onboarding_acceptance:
        options.integrated_acceptance=True
    if options.integrated_acceptance:
        options.acceptance = True
    if not 1024 <= options.port <= 65535:
        parser.error("invalid loopback port")
    if options.acceptance and not options.browser_executable.is_file():
        parser.error("Existing local Chromium executable required; no browser download")
    build_public_calendar()
    evidence = ROOT.parents[1] / ("release-artifacts/integrated-pilot-20261109" if options.integrated_acceptance else "release-artifacts/cal1-pilot-20261106")
    if options.onboarding_acceptance:
        evidence=ROOT.parents[1]/'release-artifacts/onboarding-v1-20261110'/uuid4().hex
    evidence.mkdir(parents=True, exist_ok=True)
    report_file = evidence / ("report.json" if options.acceptance else "demo-status.json")
    report = {"scope": "OWNED_LOCAL_POSTGRES_SYNTHETIC_ONLY", "status": "RUNNING"}
    previous = {key: os.environ.get(key) for key in ("TEMP", "TMP")}
    previous_temp = tempfile.tempdir
    database = None
    try:
        with tempfile.TemporaryDirectory(prefix="owned-", dir=evidence) as temp:
            for key in previous:
                os.environ[key] = temp
            tempfile.tempdir = None
            database = LocalCalendarPostgres()
            with database:
                report["postgres_version"] = database.command("exec", database.container, "postgres", "--version").stdout.strip()
                fixture = LocalPilotFixture()
                fixture.prepare()
                try:
                    if options.acceptance:
                        from scripts.cal1_pilot_acceptance import run
                        if options.onboarding_acceptance:
                            from scripts.onboarding_acceptance import run as onboarding_acceptance
                            onboarding_acceptance(fixture,options,report,evidence)
                        elif options.integrated_acceptance:
                            from scripts.pilot_release_acceptance import run as release_acceptance
                            release_acceptance(fixture, options, report, evidence)
                        run(fixture, database, options, report, evidence)
                    else:
                        cert, key = create_loopback_certificate(Path(temp))
                        print(f"LOCAL_POSTGRES_DEMO: https://127.0.0.1:{options.port}/demo/public/", flush=True)
                        print("Synthetic accounts only. Native MFA setup uses an authenticator app. No personal passwords. Ctrl+C removes this owned fixture.", flush=True)
                        uvicorn.run(fixture.app(options.port), host="127.0.0.1", port=options.port,
                            ssl_certfile=str(cert), ssl_keyfile=str(key), access_log=False, log_level="warning")
                finally:
                    fixture.cleanup()
                    report["zero_residue"] = fixture.cleanup_pass
                if options.acceptance:
                    report["zero_residue"] = False
                    result = subprocess.run([sys.executable,"-m","pytest","tests/test_staging_calendar_integration.py",
                        "tests/test_staging_calendar_api_integration.py","-q","-o","addopts="],cwd=ROOT,
                        capture_output=True,text=True,encoding="utf8",timeout=300)
                    if result.returncode:
                        raise RuntimeError("Native PostgreSQL API regression incomplete; no external fallback")
                    summary = re.search(r"\d+ passed[^\r\n]*",result.stdout)
                    report["native_api_regression"] = summary.group(0) if summary else "PASS"
                    print("Native PostgreSQL API: " + report["native_api_regression"],flush=True)
                    counts=fixture.database(fixture.counts)
                    report["zero_residue"] = not any(counts.values())
                    if not report["zero_residue"]:
                        raise RuntimeError("Native API regression left synthetic rows")
            report["container_removed"] = database.removed
            report["owned_volume_removed"] = database.volume_removed
        report.update(status="PASS" if options.acceptance else "STOPPED", temporary_context_removed=not Path(temp).exists())
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf8")
        status = "PASS" if options.acceptance else "STOPPED"
        print(f"LOCAL_CAL1={status} POSTGRES_REMOVED=PASS ZERO_RESIDUE=PASS TEMP_CLEANUP=PASS")
    except BaseException as failure:
        categories = {
            'strict mode violation':'AMBIGUOUS_BROWSER_SELECTOR',
            'Target page, context or browser has been closed':'BROWSER_CLOSED',
            'Element is not attached':'DETACHED_BROWSER_TARGET',
            'Execution context was destroyed':'BROWSER_NAVIGATION_RACE',
        }
        report.update(status="INCOMPLETE", failure_type=type(failure).__name__,
            failure_category=next((value for key,value in categories.items() if key in str(failure)), 'OTHER'),
            container_removed=bool(database and database.removed),
            owned_volume_removed=bool(database and database.volume_removed),
            failure_locations=[{"file":Path(frame.filename).name,"line":frame.lineno}
                for frame in traceback.extract_tb(failure.__traceback__) if "site-packages" not in frame.filename])
        report_file.write_text(json.dumps(report, indent=2), encoding="utf8")
        print("LOCAL_CAL1=STOP TYPE=" + type(failure).__name__ + " NO_EXTERNAL_FALLBACK")
        raise SystemExit(1) from None
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        tempfile.tempdir = previous_temp


if __name__ == "__main__":
    main()
