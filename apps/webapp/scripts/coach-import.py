"""Controlled bundled-fixture operator. No file-backed APPLY and no HTTP endpoint."""

import argparse
import asyncio
from dataclasses import asdict
from datetime import UTC, datetime
import json
import os

from sqlalchemy.ext.asyncio import create_async_engine

from coach_import_fixture import ACTOR, fixture
from competence_hub_api.portal.coach_import import validate_records
from competence_hub_api.portal.postgres_coach_import import (
    ImportSnapshot,
    PostgresCoachImporter,
    local_import_url,
    plan_records,
    technical_run,
)


async def run(args):
    records, contract, catalogue, assets = fixture()
    if args.mode == "apply" and not (args.local_database and args.synthetic_apply):
        return {"result": "CONFLICT", "issues": [{"code": "SYNTHETIC_SCOPE_REQUIRED"}]}
    if args.mode == "validate" or not args.local_database:
        validated = validate_records(
            records, contract, catalogue, assets, now=datetime.now(UTC)
        )
        if args.mode == "validate":
            return {
                "result": "CONFLICT" if validated.issues else "PASS",
                "validated": len(validated.records),
                "issues": [asdict(i) for i in validated.issues],
                "business_mutations": 0,
            }
        return {
            "snapshot": "EMPTY_SYNTHETIC_MODEL_NOT_DATABASE",
            **plan_records(validated, ImportSnapshot()).report(),
        }
    raw = os.environ.get("COMPETENCE_HUB_COACH_IMPORT_LOCAL_DATABASE_URL", "")
    local_import_url(raw)
    engine = create_async_engine(raw, hide_parameters=True)
    try:
        importer = PostgresCoachImporter(engine)
        if args.mode == "dry-run":
            return await importer.dry_run(records, contract, assets)
        return await importer.apply_synthetic(records, contract, assets, actor=ACTOR)
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode", nargs="?", choices=("validate", "dry-run", "apply"), default="validate"
    )
    parser.add_argument("--local-database", action="store_true")
    parser.add_argument("--synthetic-apply", action="store_true")
    args = parser.parse_args()
    started = datetime.now(UTC)
    try:
        result = asyncio.run(run(args))
    except Exception:
        # Exception strings may include URLs, SQL parameters or source payloads.
        result = {"result": "CONFLICT", "issues": [{"code": "LOCAL_OPERATOR_FAILURE"}]}
    print(json.dumps(technical_run(args.mode, result, started=started), sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
