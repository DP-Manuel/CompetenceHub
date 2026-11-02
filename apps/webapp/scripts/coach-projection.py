"""COACH-4 local synthetic generator and public-only review CLI. No DB/HTTP."""

import argparse
import json
from pathlib import Path

from competence_hub_api.portal.coach_projection import (
    checked_local_path,
    generate_projection,
    projection_diff,
    projection_parity,
    read_projection,
    review_markdown,
    write_projection,
)
from scripts.coach_projection_fixture import (
    ASSET_REFERENCE,
    PORTRAIT,
    synthetic_registry,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("synthetic")
    generate.add_argument(
        "--environment", choices=("preview", "production"), required=True
    )
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--assets", type=Path, required=True)
    for command in ("diff", "parity"):
        compare = commands.add_parser(command)
        compare.add_argument("--current", type=Path, required=True)
        compare.add_argument("--candidate", type=Path, required=True)
        compare.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    local_root = Path(__file__).resolve().parents[3] / ".tmp/coach4"
    args.output = checked_local_path(args.output, root=local_root)
    if args.command == "synthetic":
        args.assets = checked_local_path(args.assets, root=local_root)
        if args.output.exists():
            raise ValueError("output exists; choose a new candidate path")
        asset = args.assets / ASSET_REFERENCE
        checked_local_path(asset, root=local_root)
        asset.parent.mkdir(parents=True, exist_ok=True)
        if asset.exists():
            if asset.read_bytes() != PORTRAIT:
                raise ValueError("synthetic asset collision")
        else:
            with asset.open("xb") as stream:
                stream.write(PORTRAIT)
        value = generate_projection(synthetic_registry(), args.environment)
        digest = write_projection(value, args.output, asset_root=args.assets)
        print(
            json.dumps(
                {
                    "status": "SYNTHETIC_ONLY",
                    "coaches": len(value["coaches"]),
                    "sha256": digest,
                }
            )
        )
    else:
        a, b = read_projection(args.current), read_projection(args.candidate)
        report = (
            projection_diff(a, b) if args.command == "diff" else projection_parity(a, b)
        )
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(
                review_markdown(report)
                if args.command == "diff"
                else json.dumps(report, ensure_ascii=False, indent=2) + "\n"
            )
        print(
            "PROJECTION_REVIEW=READY"
            if args.command == "diff"
            else "PROJECTION_PARITY=" + report["status"]
        )
        return 0 if args.command == "diff" or report["status"] == "PASS" else 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError):
        raise SystemExit(
            "COACH_PROJECTION=FAIL INVALID_LOCAL_INPUT_OR_OUTPUT"
        ) from None
