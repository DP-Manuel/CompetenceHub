"""Local synthetic export only; no DB URL, config, source ingestion or apply."""

import argparse
import json
from pathlib import Path

from competence_hub_api.portal.coach_export import (
    RegistrySnapshot,
    export_registry,
    write_export,
)
from competence_hub_api.portal.coach_projection import checked_local_path
from scripts.coach_projection_fixture import synthetic_registry


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("internal", "preview", "production"), required=True
    )
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--assets", type=Path, required=True)
    args = parser.parse_args(argv)
    allowed = Path(__file__).resolve().parents[3] / ".tmp/coach4"
    output = checked_local_path(args.output_root, root=allowed)
    assets = checked_local_path(args.assets, root=allowed)
    snapshot = RegistrySnapshot.capture(synthetic_registry())
    value = export_registry(snapshot, args.mode, asset_root=assets)
    manifest = write_export(
        value,
        mode=args.mode,
        source_identifier="synthetic-coach4-v1",
        output_root=output,
    )
    print(json.dumps({"status": "SYNTHETIC_ONLY", **manifest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PermissionError, LookupError):
        raise SystemExit(
            "COACH_EXPORT=FAIL INVALID_LOCAL_SNAPSHOT_ASSET_OR_OUTPUT"
        ) from None
