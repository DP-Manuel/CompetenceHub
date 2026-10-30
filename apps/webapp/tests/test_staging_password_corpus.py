"""Pinned public negative-corpus preparation, no user password or network calls."""

import hashlib
import importlib.util
import io
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "public_password_corpus", ROOT / "deploy/scripts/prepare-staging-password-corpus.py"
)
corpus = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = corpus
spec.loader.exec_module(corpus)


def test_normalization_matches_existing_password_service_without_trimming():
    from competence_hub_api.security.passwords import PasswordPolicy, PasswordService

    lines = [f"synthetic-public-negative-{i}" for i in range(90000)]
    lines += ["Stra\u00dfe", "STRASSE", " leading-space", "trailing-space "]
    result, count, distinct = corpus.fingerprints(
        ("\r\n".join(lines) + "\r\n").encode()
    )
    values = result.decode().splitlines()
    assert count == 90004 and distinct == 90003
    assert values == sorted(set(values))
    service = PasswordService(PasswordPolicy(frozenset(values)))
    for value in ("strasse", "STRASSE", " leading-space", "trailing-space "):
        assert hashlib.sha256(value.casefold().encode()).hexdigest() in values
        with pytest.raises(ValueError):
            service.hash(value)
    assert hashlib.sha256(b"leading-space").hexdigest() not in values


@pytest.mark.parametrize(
    "raw",
    [b"0\n", b"\n" * 95000, b"placeholder\n" * 95000],
    ids=["too-small", "empty", "repeated-placeholder"],
)
def test_small_or_duplicate_placeholder_corpus_is_rejected(raw):
    with pytest.raises(ValueError):
        corpus.fingerprints(raw)


def test_public_download_checks_exact_url_status_size_and_sha(monkeypatch):
    data = b"synthetic public negative corpus"

    class Response(io.BytesIO):
        status = 200
        url = corpus.BASE + corpus.SOURCE

    response = Response(data)

    class Opener:
        def open(self, request, timeout):
            assert request.full_url == corpus.BASE + corpus.SOURCE and timeout == 30
            return response

    monkeypatch.setattr(corpus, "build_opener", lambda handler: Opener())
    assert corpus.download(corpus.SOURCE, hashlib.sha256(data).hexdigest()) == data
    for attribute, value in (("url", "https://other.invalid"), ("status", 302)):
        response = Response(data)
        setattr(response, attribute, value)
        with pytest.raises(ValueError):
            corpus.download(corpus.SOURCE, hashlib.sha256(data).hexdigest())
    response = Response(data)
    with pytest.raises(ValueError):
        corpus.download(corpus.SOURCE, "0" * 64)
    response = Response(b"x" * (2 * 1024 * 1024 + 1))
    with pytest.raises(ValueError):
        corpus.download(corpus.SOURCE, hashlib.sha256(response.getvalue()).hexdigest())


def test_pinned_source_refuses_redirects():
    with pytest.raises(ValueError, match="must not redirect"):
        corpus.NoRedirect().redirect_request(
            None, None, 301, "moved", {}, "https://other.invalid"
        )


def test_output_cannot_replace_existing_files_or_use_repository_or_ancestor(
    tmp_path, monkeypatch
):
    repo = tmp_path / "repository"
    repo.mkdir()
    monkeypatch.setattr(corpus, "ROOT", repo)
    existing = tmp_path / "already-present"
    existing.mkdir()
    for path in (existing, repo, repo / "new-file", tmp_path, Path("relative")):
        with pytest.raises(ValueError):
            corpus.protected_destination(path)


def test_no_user_password_input_or_submission_path_exists():
    source = (ROOT / "deploy/scripts/prepare-staging-password-corpus.py").read_text()
    assert "getpass" not in source and "Read-Host" not in source
    assert "casefold" in source and 'open("xb")' in source
    assert "HTTPRedirectHandler" in source and "User-Agent" in source
    assert "not all breached passwords or a live check" in source
