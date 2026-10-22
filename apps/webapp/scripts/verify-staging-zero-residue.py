"""Read-only postflight using process configuration; never changes rows."""
import json
from pathlib import Path

from sqlalchemy import text
from native_calendar_fixture import NativeCalendarFixture


def main():
    fixture = NativeCalendarFixture()
    async def verify(connection):
        counts = await fixture.counts(connection)
        listen = await connection.scalar(text("SHOW listen_addresses"))
        versions = (await connection.execute(text("SELECT version FROM competence_hub.schema_migrations ORDER BY version"))).scalars().all()
        owners = (await connection.execute(text("SELECT tableowner,count(*) FROM pg_tables WHERE schemaname='competence_hub' GROUP BY tableowner"))).all()
        return {"counts": counts, "listen_addresses": listen, "migrations": versions,
                "owners": {row[0]: row[1] for row in owners}}
    report = fixture.database(verify)
    report["status"] = "PASS" if (not any(report["counts"].values()) and report["listen_addresses"] == "localhost"
        and report["migrations"] == ["0001", "0002", "0003", "0004", "0005", "0006"]
        and report["owners"] == {"competence_hub_owner": 27}) else "FAIL"
    target = Path(__file__).resolve().parents[3] / "release-artifacts/cal1-native-ui-20261022/postflight.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
