"""Incremental, local source inventory. No import, publication or network.

The CLI is deliberately confined to the explicitly authorized 20261030 folder.
Raw filenames/extractions/reconciliation stay in ignored private local artifacts.
The baseline lists previously processed bytes, not inferred filesystem history.
"""

import argparse
from collections import Counter
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
from xml.etree import ElementTree
from zipfile import ZipFile, BadZipFile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Quellen/20261030"
OUTPUT = ROOT / ".tmp/source-ingestion-20261102"
BASELINE = {
    "Konzept_Schwabauer.pdf": "04805b6e6b96313e68f285d01c922d9342bd692ce4ec2cce68b9b124191f4620"
}
BASELINE_PATH = ROOT / "scripts/coach-source-20261030-baseline.json"
MAX_BYTES = 32 * 1024 * 1024
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def no_links(path):
    for ancestor in (path, *path.parents):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            continue
        if (
            stat.S_ISLNK(info.st_mode)
            or getattr(info, "st_file_attributes", 0)
            & stat.FILE_ATTRIBUTE_REPARSE_POINT
        ):
            raise ValueError("linked source/output forbidden")


def diff_inventory(records, baseline):
    seen = set()
    result = []
    for record in records:
        row = dict(record)
        name = row["relative_path"]
        if name in seen:
            raise ValueError("duplicate source path")
        seen.add(name)
        previous = baseline.get(name)
        row["previously_processed"] = previous is not None
        row["change"] = (
            "NEW"
            if previous is None
            else "UNCHANGED" if previous == row["sha256"] else "MODIFIED"
        )
        result.append(row)
    return {
        "files": sorted(result, key=lambda r: r["relative_path"]),
        "removed": sorted(set(baseline) - seen),
    }


def docx_text(path):
    with ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > 2000 or sum(e.file_size for e in entries) > 4 * MAX_BYTES:
            raise ValueError("oversized DOCX archive")
        if any(e.flag_bits & 1 for e in entries):
            raise ValueError("encrypted DOCX unsupported")
        if len({e.filename for e in entries}) != len(entries):
            raise ValueError("duplicate DOCX entries")
        if archive.testzip() is not None:
            raise ValueError("DOCX CRC failure")
        info = archive.getinfo("word/document.xml")
        if info.file_size > MAX_BYTES:
            raise ValueError("DOCX XML too large")
        body = archive.read(info)
    if b"<!DOCTYPE" in body or b"<!ENTITY" in body:
        raise ValueError("XML declarations forbidden")
    root = ElementTree.fromstring(body)
    # Keep document order including table paragraphs; no external links or macros.
    return "\n".join(
        "".join(n.text or "" for n in p.iter(W + "t")) for p in root.iter(W + "p")
    )


def technical_check(path, extension):
    try:
        if extension == ".docx":
            text = docx_text(path)
            return bool(text.strip()), "DOCX_XML", None
        if extension == ".pdf":
            # Metadata check only for unchanged PDFs; never interpret their text again.
            result = subprocess.run(
                ["pdfinfo", str(path)], capture_output=True, timeout=30, check=False
            )
            return result.returncode == 0, "PDF_STRUCTURE", None
        return False, "UNSUPPORTED_REVIEW_REQUIRED", "UNSUPPORTED_TYPE"
    except (
        OSError,
        ValueError,
        BadZipFile,
        KeyError,
        ElementTree.ParseError,
        subprocess.SubprocessError,
    ):
        return False, "UNREADABLE", "TECHNICAL_REVIEW_REQUIRED"


def load_baseline(path=BASELINE_PATH):
    no_links(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("scope") != "PROCESSED_SOURCE_BYTES_NOT_PUBLICATION_APPROVAL":
        raise ValueError("processed-byte baseline required")
    result = {}
    for row in value["files"]:
        name = row["relative_path"]
        if (
            name in result
            or not name
            or "\\" in name
            or ":" in name
            or any(p in {".", ".."} for p in name.split("/"))
            or name.startswith("/")
            or not re.fullmatch(r"[a-f0-9]{64}", row["sha256"])
        ):
            raise ValueError("invalid baseline entry")
        result[name] = row["sha256"]
    return result


def inventory(source=SOURCE, baseline=None):
    baseline = load_baseline() if baseline is None else baseline
    no_links(source)
    source = source.resolve(strict=True)
    records = []

    def files(directory):
        for path in sorted(directory.iterdir()):
            no_links(path)
            if path.is_dir():
                yield from files(path)
            elif path.is_file():
                yield path

    for path in files(source):
        no_links(path)
        if not path.is_file():
            continue
        if not path.resolve().is_relative_to(source):
            raise ValueError("source escaped authorized folder")
        ext = path.suffix.lower()
        # Unknown/credential-like types are never opened merely for inventory.
        if ext not in {".pdf", ".docx"} or path.stat().st_size > MAX_BYTES:
            raise ValueError(
                "unsupported/oversized source: metadata-only review required"
            )
        info = path.stat()
        body = path.read_bytes()
        if len(body) != info.st_size:
            raise ValueError("source changed during inventory")
        if baseline.get(path.relative_to(source).as_posix()) == digest(body):
            readable, method, issue = True, "KNOWN_PROCESSED_HASH_MATCH", None
        else:
            readable, method, issue = technical_check(path, ext)
        records.append(
            {
                "relative_path": path.relative_to(source).as_posix(),
                "type": ext[1:],
                "bytes": len(body),
                "modified_utc": datetime.fromtimestamp(info.st_mtime, UTC).isoformat(),
                "sha256": digest(body),
                "technically_readable": readable,
                "technical_check": method,
                "technical_issue": issue,
            }
        )
    return {
        "schema": 1,
        "scope": "PRIVATE_INCREMENTAL_INVENTORY_NO_IMPORT_OR_PUBLICATION",
        "baseline_kind": "DOCUMENTED_PROCESSED_BYTES_NOT_FOLDER_CREATION_HISTORY",
        **diff_inventory(records, baseline),
    }


def extract_changed(source, report, output):
    no_links(output)
    output.mkdir(parents=True, exist_ok=True)
    for index, row in enumerate(report["files"], 1):
        if row["change"] == "UNCHANGED" or not row["technically_readable"]:
            continue
        path = source / row["relative_path"]
        no_links(path)
        if digest(path.read_bytes()) != row["sha256"]:
            raise ValueError("source changed before extraction")
        if row["type"] == "docx":
            text = docx_text(path)
        else:
            result = subprocess.run(
                ["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
                capture_output=True,
                timeout=60,
                check=True,
            )
            text = result.stdout.decode("utf-8")
        if digest(path.read_bytes()) != row["sha256"]:
            raise ValueError("source changed during extraction")
        target = output / f"source-{index:02d}.txt"
        with target.open("x", encoding="utf-8") as stream:
            stream.write(text)
        row["private_extraction"] = target.name
        row["extraction_sha256"] = digest(text.encode("utf-8"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract-new", action="store_true")
    parser.add_argument("--run-name", default="20261102")
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,60}", args.run_name):
        raise ValueError("safe run name required")
    output = ROOT / (".tmp/source-ingestion-" + args.run_name)
    no_links(output)
    if args.verify_existing:
        if args.extract_new:
            raise ValueError("verification never re-extracts sources")
        no_links(output / "inventory.json")
        old = json.loads((output / "inventory.json").read_text(encoding="utf-8"))
        current = inventory()
        old_bytes = {r["relative_path"]: r["sha256"] for r in old["files"]}
        current_bytes = {r["relative_path"]: r["sha256"] for r in current["files"]}
        if current_bytes != old_bytes:
            raise ValueError("current source byte inventory changed")
        print(
            json.dumps(
                {
                    "status": "CURRENT_BYTES_VERIFIED_NO_REINTERPRETATION",
                    "files": len(current_bytes),
                    "processed_baseline_changes": dict(
                        Counter(r["change"] for r in current["files"])
                    ),
                }
            )
        )
        return
    if output.exists():
        raise ValueError("private run directory exists; preserve previous evidence")
    report = inventory()
    output.mkdir(parents=True)
    if args.extract_new:
        extract_changed(SOURCE, report, output / "extracted")
    (output / "inventory.json").write_bytes(encoded(report))
    print(
        json.dumps(
            {
                "files": len(report["files"]),
                "changes": dict(Counter(r["change"] for r in report["files"])),
                "unreadable": sum(
                    not r["technically_readable"] for r in report["files"]
                ),
                "removed": len(report["removed"]),
                "inventory_sha256": digest(encoded(report)),
                "scope": "LOCAL_PRIVATE_NO_IMPORT",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
