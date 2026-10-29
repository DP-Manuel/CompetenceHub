"""Synthetic, DB-free tests: no real canonical input, network or public identities."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import socket
import sys
from urllib.request import Request

import pytest


def test_cli_rejects_changed_review_before_network(monkeypatch, capsys):
    payload = b'{"mode":"synthetic"}'
    monkeypatch.setattr(parity, "SNAPSHOT_SHA256", parity.sha256(payload))

    def read(path):
        return payload if path == parity.SNAPSHOT else b"{}"

    monkeypatch.setattr(Path, "read_bytes", read)
    assert parity.main(["--verify"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "FAIL"


ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "coach3b_preview_parity", ROOT / "scripts/coach3b_preview_parity.py"
)
parity = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = parity
spec.loader.exec_module(parity)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("pure tests must not access network")

    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)


def inputs():
    canonical = {
        "mode": "READ_ONLY_CANONICAL_NO_DB",
        "coaches": [
            {
                "profile_path": "/coaches/synthetic/",
                "name": "Synthetic Coach",
                "credentials": ["Synthetic degree", "Practice only"],
                "offerings": [{"title": "Old & public", "active": False}],
                "topics": ["topic-a", "topic-b"],
                "asset": {
                    "reference": "images/coaches/synthetic.webp",
                    "sha256": parity.sha256(b"synthetic asset"),
                },
            }
        ],
    }
    review = {
        "scope": "PREPARATION_ONLY_NO_DATABASE_OR_PUBLICATION",
        "source_snapshot_sha256": parity.SNAPSHOT_SHA256,
        "coaches": {"synthetic": {"credential_kinds": ["qualification", "background"]}},
        "new_offering_families": [{"formats": [{"label": "New unpublished"}]}],
    }
    pages = {
        parity.public_url(
            "coaches/"
        ): b'<article data-preview-coach data-topics="topic-b topic-a"><a href="/CompetenceHub/coaches/synthetic">Profile</a></article>',
        parity.public_url(
            "coaches/synthetic/"
        ): b"<main><h1>Synthetic <span>Coach</span></h1><ul><li>Synthetic&nbsp;degree</li></ul><p>Old &amp; public</p></main>",
        parity.public_url("images/coaches/synthetic.webp"): b"synthetic asset",
    }
    return canonical, review, pages


def run(canonical, review, pages):
    calls = []

    def fetch(url):
        calls.append(url)
        return parity.Response(200, url, pages[url])

    return parity.verify(canonical, review, fetch), calls


def test_parity_counts_classification_inactive_old_title_and_new_delta():
    canonical, review, pages = inputs()
    before = deepcopy((canonical, review, pages))
    result, calls = run(canonical, review, pages)
    assert result["status"] == "PASS"
    assert result["gaps"] == {}
    assert result["counts"]["public_qualifications"] == {"expected": 1, "matched": 1}
    assert result["counts"]["old_offering_titles"] == {"expected": 1, "matched": 1}
    assert result["counts"]["index_topic_links"] == {"expected": 2, "matched": 2}
    assert result["excluded_new_formats"] == 1
    assert result["responses_observed"] == len(calls) == 3
    assert (canonical, review, pages) == before
    assert run(canonical, review, pages)[0] == result


@pytest.mark.parametrize(
    "removed,gap",
    [
        (b"Synthetic <span>Coach</span>", "profile_names"),
        (b"Synthetic&nbsp;degree", "public_qualifications"),
        (b"Old &amp; public", "old_offering_titles"),
    ],
)
def test_missing_public_text_fails(removed, gap):
    canonical, review, pages = inputs()
    url = parity.public_url("coaches/synthetic/")
    pages[url] = pages[url].replace(removed, b"Missing")
    result, _ = run(canonical, review, pages)
    assert result["status"] == "FAIL"
    assert result["gaps"][gap] == 1


@pytest.mark.parametrize(
    "replacement,gap",
    [
        (
            b'<article data-topics="topic-a topic-b"><a href="/CompetenceHub/coaches/wrong">Profile</a></article>',
            "index_routes",
        ),
        (
            b'<article data-topics="topic-a"><a href="/CompetenceHub/coaches/synthetic">Profile</a></article>',
            "index_topic_links",
        ),
        (
            b'<article data-topics="topic-a topic-b extra"><a href="/CompetenceHub/coaches/synthetic">Profile</a></article>',
            "index_topic_assignment",
        ),
        (
            b'<article data-topics="topic-a topic-a topic-b"><a href="/CompetenceHub/coaches/synthetic">Profile</a></article>',
            "index_topic_assignment",
        ),
        (
            b'<article data-preview-coach><a href="/CompetenceHub/coaches/synthetic">Profile</a></article>',
            "index_topic_links",
        ),
        (
            b'<article data-topics="topic-a topic-b"><a href="https://other.example/CompetenceHub/coaches/synthetic">Profile</a></article>',
            "index_anchor_boundary",
        ),
    ],
)
def test_bad_index_route_or_topic_assignment_fails(replacement, gap):
    canonical, review, pages = inputs()
    pages[parity.public_url("coaches/")] = replacement
    result, _ = run(canonical, review, pages)
    assert result["status"] == "FAIL"
    assert result["gaps"][gap] > 0


def test_topic_assignment_is_per_profile_not_aggregate():
    canonical, review, pages = inputs()
    second = deepcopy(canonical["coaches"][0])
    second.update(profile_path="/coaches/second/", topics=["topic-c"], asset=None)
    canonical["coaches"].append(second)
    review["coaches"]["second"] = deepcopy(review["coaches"]["synthetic"])
    pages[parity.public_url("coaches/second/")] = pages[
        parity.public_url("coaches/synthetic/")
    ]
    pages[parity.public_url("coaches/")] = (
        b'<article data-topics="topic-c"><a href="/CompetenceHub/coaches/synthetic/">One</a></article><article data-topics="topic-a topic-b"><a href="/CompetenceHub/coaches/second/">Two</a></article>'
    )
    result, _ = run(canonical, review, pages)
    assert result["gaps"]["index_topic_assignment"] == 2
    assert result["counts"]["index_routes"]["matched"] == 2
    assert result["counts"]["index_topic_links"]["matched"] == 0


def test_duplicate_cards_do_not_supply_a_missing_route():
    canonical, review, pages = inputs()
    pages[parity.public_url("coaches/")] *= 2
    result, _ = run(canonical, review, pages)
    assert result["gaps"]["index_routes"] == 1
    assert result["gaps"]["index_card_count"] == 1


def test_changed_asset_bytes_fail():
    canonical, review, pages = inputs()
    pages[parity.public_url("images/coaches/synthetic.webp")] = b"changed"
    result, _ = run(canonical, review, pages)
    assert result["gaps"]["asset_sha256"] == 1


@pytest.mark.parametrize("tag", ["script", "style", "template", "noscript", "head"])
def test_nonpublic_html_text_cannot_satisfy_parity(tag):
    canonical, review, pages = inputs()
    pages[parity.public_url("coaches/synthetic/")] = (
        f"<{tag}>Synthetic Coach Synthetic degree Old &amp; public</{tag}>".encode()
    )
    result, _ = run(canonical, review, pages)
    assert result["gaps"]["profile_names"] == 1
    assert result["gaps"]["public_qualifications"] == 1
    assert result["gaps"]["old_offering_titles"] == 1


def test_normalization_entities_inline_boundaries_and_hidden_nodes():
    parser = parity.parse_html(
        b'<head><title>Ignore</title></head><div>Caf&#101;&#769; <b>&amp;</b>&nbsp;Tea</div><p>Next<span>word</span></p><p hidden>Hidden</p><div aria-hidden="true"><p>Also hidden</p></div><!-- comment -->'
    )
    assert parser.text == "Caf\u00e9 & Tea Nextword"


@pytest.mark.parametrize(
    "url",
    [
        "http://dp-manuel.github.io/CompetenceHub/coaches/",
        "https://other.example/CompetenceHub/coaches/",
        "https://dp-manuel.github.io/other/",
        "https://dp-manuel.github.io/CompetenceHub-evil/coaches/",
        "https://dp-manuel.github.io:443/CompetenceHub/coaches/",
        "https://user:password@dp-manuel.github.io/CompetenceHub/coaches/",
        "https://dp-manuel.github.io/CompetenceHub/../other/",
        "https://dp-manuel.github.io/CompetenceHub/%2e%2e/other/",
        "https://dp-manuel.github.io/CompetenceHub/coaches/?token=no",
        "https://dp-manuel.github.io/CompetenceHub/coaches/#fragment",
    ],
)
def test_unsafe_request_and_redirect_rejected_before_network(url):
    with pytest.raises(parity.FetchFailure):
        parity.fetch_public(url)
    handler = parity.PreviewRedirectHandler()
    with pytest.raises(parity.FetchFailure):
        handler.redirect_request(Request(parity.BASE_URL), None, 302, "Found", {}, url)


def test_https_same_base_redirect_is_allowed():
    request = Request(parity.public_url("coaches/synthetic"))
    target = parity.public_url("coaches/synthetic/")
    redirected = parity.PreviewRedirectHandler().redirect_request(
        request, None, 301, "Moved", {}, target
    )
    assert redirected.full_url == target
    assert redirected.get_method() == "GET"


@pytest.mark.parametrize(
    "final",
    [
        "https://other.example/CompetenceHub/coaches/synthetic/",
        parity.BASE_URL + "other/",
        "http://dp-manuel.github.io/CompetenceHub/coaches/synthetic/",
    ],
)
def test_injected_fetcher_cannot_bypass_final_url_validation(final):
    canonical, review, pages = inputs()
    result = parity.verify(
        canonical, review, lambda url: parity.Response(200, final, b"Synthetic Coach")
    )
    assert result["status"] == "FAIL"
    assert result["gaps"]["profile_fetch_or_url"] == 1


@pytest.mark.parametrize("status", [404, 503])
def test_http_failure_is_counted_not_treated_as_success(status):
    canonical, review, pages = inputs()
    result = parity.verify(
        canonical, review, lambda url: parity.Response(status, url, b"")
    )
    assert result["gaps"]["profile_http_status"] == 1
    assert result["counts"]["profile_status_200"]["matched"] == 0


def test_transport_failure_and_invalid_utf8_are_honest_gaps():
    canonical, review, pages = inputs()

    def failed(url):
        raise parity.FetchFailure("sanitized")

    result = parity.verify(canonical, review, failed)
    assert result["gaps"]["profile_fetch_or_url"] == 1
    pages[parity.public_url("coaches/synthetic/")] = b"\xff"
    result, _ = run(canonical, review, pages)
    assert result["gaps"]["profile_html"] == 1


@pytest.mark.parametrize("mutation", ["classification", "scope", "binding"])
def test_invalid_review_fails_before_fetch(mutation):
    canonical, review, pages = inputs()
    if mutation == "classification":
        review["coaches"]["synthetic"]["credential_kinds"] = []
    elif mutation == "scope":
        review["scope"] = "APPLY"
    else:
        review["source_snapshot_sha256"] = "0" * 64

    def forbidden(url):
        pytest.fail("invalid inputs must not fetch")

    with pytest.raises(ValueError):
        parity.verify(canonical, review, forbidden)


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--apply"],
        ["--verify", "--output", "dump.html"],
        ["--verify", "--base-url", "https://other.example/"],
    ],
)
def test_cli_requires_verify_and_has_no_mutation_or_server_override(args):
    with pytest.raises(SystemExit) as error:
        parity.main(args)
    assert error.value.code == 2


def test_cli_rejects_nonfrozen_bytes_without_reading_real_snapshot(monkeypatch, capsys):
    reads = []

    def read(path):
        reads.append(path)
        return b"synthetic nonfrozen bytes"

    monkeypatch.setattr(Path, "read_bytes", read)
    assert parity.main(["--verify"]) == 1
    assert reads == [parity.SNAPSHOT]
    assert json.loads(capsys.readouterr().out) == {
        "status": "FAIL",
        "gaps": {"input_or_verification_error": 1},
    }
