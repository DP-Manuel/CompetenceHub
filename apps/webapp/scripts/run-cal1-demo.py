"""Single-terminal synthetic HTTPS demo; Ctrl+C removes owned temporary TLS files."""
import argparse
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import uvicorn

from scripts.browser_acceptance_app import HOST, create_loopback_certificate
from scripts.cal1_demo_app import create_demo_app
from scripts.cal1_public_build import build_public_calendar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8446)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    build_public_calendar()
    with tempfile.TemporaryDirectory(prefix="competence-hub-local-cal-demo-") as folder:
        cert, key = create_loopback_certificate(Path(folder))
        print(f"SYNTHETIC LOCAL DEMO: https://{HOST}:{args.port}/demo/", flush=True)
        print(f"LOCAL CAL-0.1: https://{HOST}:{args.port}/demo/public/", flush=True)
        print("No DB, VPS, GPG, real accounts or email. Ctrl+C stops and discards demo state.", flush=True)
        uvicorn.run(create_demo_app(args.port), host=HOST, port=args.port,
                    ssl_certfile=str(cert), ssl_keyfile=str(key), access_log=False, log_level="warning")
    print("DEMO_STOPPED TEMPORARY_TLS_REMOVED=PASS IN_MEMORY_DATA_DISCARDED=PASS")


if __name__ == "__main__":
    main()
