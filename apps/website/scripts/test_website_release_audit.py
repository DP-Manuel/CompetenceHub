"""Offline checks for the public artifact comparison; never connect to SFTP."""
import hashlib
import importlib.util
from pathlib import Path
import zipfile

import pytest

spec = importlib.util.spec_from_file_location("release_audit", Path(__file__).with_name("audit-website-release.py"))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_exact_diff_preserves_each_old_and_new_digest():
    result = audit.difference({"same": b"a", "changed": b"b", "old": b"c"},
                              {"same": b"a", "changed": b"d", "new": b"e"})
    assert {key: [entry["path"] for entry in entries] for key, entries in result.items()} == {
        "added": ["new"], "changed": ["changed"], "removed": ["old"], "unchanged": ["same"],
    }
    assert result["changed"][0]["before_sha256"] == hashlib.sha256(b"b").hexdigest()
    assert result["changed"][0]["after_sha256"] == hashlib.sha256(b"d").hexdigest()


def test_archive_is_read_only_and_bound_to_digest(tmp_path):
    path = tmp_path / "site.zip"
    with zipfile.ZipFile(path, "w") as output:
        output.writestr("coaches/example/index.html", b"approved")
    original = path.read_bytes()
    assert audit.archive(path, hashlib.sha256(original).hexdigest()) == {"coaches/example/index.html": b"approved"}
    with pytest.raises(ValueError, match="Bound archive changed"):
        audit.archive(path, "0" * 64)
    assert path.read_bytes() == original


@pytest.mark.parametrize("name", ["../escape", "/absolute", "directory/"])
def test_invalid_archive_entry_is_rejected(tmp_path, name):
    path = tmp_path / "invalid.zip"
    with zipfile.ZipFile(path, "w") as output:
        output.writestr(name, b"")
    with pytest.raises(ValueError, match="Invalid release entry"):
        audit.archive(path)


def test_public_metadata_uses_html_parser():
    result = audit.Metadata()
    result.feed('<meta content="noindex, nofollow" name="robots"><link href="https://example.invalid/" rel="canonical"><a href="mailto:public@example.invalid">Kontakt</a>')
    assert result.meta["robots"] == "noindex, nofollow"
    assert result.canonical == ["https://example.invalid/"]
    assert result.links == ["mailto:public@example.invalid"]
