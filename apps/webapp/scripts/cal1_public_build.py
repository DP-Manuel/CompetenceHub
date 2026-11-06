"""Compile only the existing CAL-0.1 component's isolated local entry."""
import os
from pathlib import Path
import subprocess

WEBSITE = Path(__file__).resolve().parents[2] / "website"
PUBLIC_BUILD = WEBSITE / ".tmp/cal1-public"


def build_public_calendar():
    node = WEBSITE.parents[1] / "tools/node-v22.16.0-win-x64/node.exe"
    environment = {**os.environ, "ASTRO_TELEMETRY_DISABLED": "1"}
    subprocess.run([str(node), "node_modules/astro/astro.js", "build", "--config",
                    "astro.cal1-demo.config.mjs"], cwd=WEBSITE, env=environment, check=True)
    if not (PUBLIC_BUILD / "index.html").is_file():
        raise RuntimeError("Local CAL-0.1 build missing; no fallback dataset")
    return PUBLIC_BUILD
