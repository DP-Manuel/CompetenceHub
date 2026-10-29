"""Read-only semantic spot-check of CURRENT public Preview, not an import gate.

Run from any directory with python -B scripts/coach3b_preview_parity.py --verify.
Only the frozen snapshot and review map are read locally; HTTP is GET-only.
HTML stays in memory. No Portal imports, DB, auth, UUIDs, writes or publication.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE_URL = "https://dp-manuel.github.io/CompetenceHub/"
SNAPSHOT_SHA256 = "e3feda67b2bdb681b080e2336d82fd9c9eb39128735f2955c47773fed5e743a9"
REVIEW_MAP_SHA256 = "19c8c1cc0a8c1688729dd3ebcfeab7076fe032dd9bed684d9ace4cee16ebb497"
ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / ".tmp/coach3b-canonical-inputs-2026-10-29.json"
REVIEW_MAP = ROOT / "scripts/coach3b-review-map.json"
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
FROZEN_COUNTS = {
    "profile_status_200": 9,
    "profile_names": 9,
    "public_qualifications": 30,
    "old_offering_titles": 25,
    "asset_sha256": 8,
    "index_routes": 9,
    "index_topic_links": 22,
}


def sha256(body):
    return hashlib.sha256(body).hexdigest()


def normalize(text):
    return " ".join(unicodedata.normalize("NFC", text).split())


class FetchFailure(ValueError):
    """A sanitized transport or URL-boundary failure."""


def checked_url(url):
    """Reject alternate authorities, encoded traversal and paths outside Preview."""
    parts = urlsplit(url)
    if (
        parts.scheme != "https"
        or parts.netloc != "dp-manuel.github.io"
        or not parts.path.startswith("/CompetenceHub/")
        or parts.query
        or parts.fragment
        or any(c in url for c in ("%", "\\"))
        or any(ord(c) <= 32 or ord(c) >= 127 for c in url)
        or any(segment in {".", ".."} for segment in parts.path.split("/"))
    ):
        raise FetchFailure("outside fixed public Preview boundary")
    return url


def public_url(reference):
    return checked_url(urljoin(BASE_URL, reference))


class PreviewRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        checked_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


@dataclass(frozen=True)
class Response:
    status: int
    url: str
    body: bytes


def validate_response(url, response):
    checked_url(response.url)
    if response.url.rstrip("/") != url.rstrip("/"):
        raise FetchFailure("unexpected final response URL")
    if len(response.body) > MAX_RESPONSE_BYTES:
        raise FetchFailure("response exceeds memory limit")
    return response


def fetch_public(url):
    """Unauthenticated GET only; validate redirect targets before following them."""
    checked_url(url)
    opener = build_opener(PreviewRedirectHandler())
    request = Request(url, headers={"User-Agent": "CompetenceHub-readonly-parity/1"})
    try:
        with opener.open(request, timeout=25) as response:
            # Check the final URL before consuming any body, including with custom openers.
            validate_response(url, Response(response.status, response.url, b""))
            return validate_response(
                url,
                Response(
                    response.status, response.url, response.read(MAX_RESPONSE_BYTES + 1)
                ),
            )
    except HTTPError as error:
        try:
            return validate_response(url, Response(error.code, error.url, b""))
        finally:
            error.close()
    except (OSError, URLError) as error:
        raise FetchFailure("public GET failed") from error


class PreviewHTML(HTMLParser):
    """Extract rendered text and article-local href/topic associations, not scripts."""

    VOID = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
    BLOCK = {
        "article",
        "aside",
        "blockquote",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }
    EXCLUDED = {"head", "script", "style", "template", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.cards = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        hidden = (
            (self.stack and self.stack[-1][1])
            or tag in self.EXCLUDED
            or "hidden" in attrs
            or attrs.get("aria-hidden", "").lower() == "true"
        )
        card = self.stack[-1][2] if self.stack else None
        if not hidden:
            if tag in self.BLOCK:
                self.parts.append(" ")
            if tag == "article" and (
                "data-topics" in attrs
                or "data-preview-coach" in attrs
                or "coach-card" in attrs.get("class", "").split()
            ):
                card = {"topics": attrs.get("data-topics", "").split(), "hrefs": []}
                self.cards.append(card)
            if tag == "a" and card is not None and attrs.get("href"):
                card["hrefs"].append(attrs["href"])
        if tag not in self.VOID:
            self.stack.append((tag, bool(hidden), card))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                if not self.stack[index][1] and tag in self.BLOCK:
                    self.parts.append(" ")
                del self.stack[index:]
                break

    def handle_data(self, data):
        if not self.stack or not self.stack[-1][1]:
            self.parts.append(data)

    @property
    def text(self):
        return normalize("".join(self.parts))


def parse_html(body):
    parser = PreviewHTML()
    parser.feed(body.decode("utf-8-sig", errors="strict"))
    parser.close()
    return parser


def expected_records(canonical, review):
    """Only explicit classification selects public qualifications; no inference."""
    if (
        canonical.get("mode") != "READ_ONLY_CANONICAL_NO_DB"
        or review.get("scope") != "PREPARATION_ONLY_NO_DATABASE_OR_PUBLICATION"
        or review.get("source_snapshot_sha256") != SNAPSHOT_SHA256
    ):
        raise ValueError("invalid input scope or snapshot binding")
    records = []
    slugs = set()
    kinds_allowed = {
        "qualification",
        "role_descriptor",
        "background",
        "competency",
        "languages",
        "format_description",
    }
    for coach in canonical["coaches"]:
        path = coach["profile_path"]
        slug = path.strip("/").split("/")[-1]
        if path != f"/coaches/{slug}/" or slug in slugs:
            raise ValueError("invalid or duplicate canonical route")
        slugs.add(slug)
        kinds = review["coaches"][slug]["credential_kinds"]
        if len(kinds) != len(coach["credentials"]) or not set(kinds) <= kinds_allowed:
            raise ValueError("invalid credential classification")
        qualifications = [
            label
            for label, kind in zip(coach["credentials"], kinds)
            if kind == "qualification"
        ]
        titles = [offer["title"] for offer in coach["offerings"]]
        if any(
            not normalize(label) for label in [coach["name"], *qualifications, *titles]
        ):
            raise ValueError("empty canonical text")
        topics = coach["topics"]
        if len(topics) != len(set(topics)):
            raise ValueError("duplicate canonical topic")
        asset = coach["asset"]
        if asset and (
            len(asset["sha256"]) != 64
            or any(c not in "0123456789abcdef" for c in asset["sha256"])
        ):
            raise ValueError("invalid asset hash")
        records.append(
            {
                "url": public_url(path.lstrip("/")),
                "name": coach["name"],
                "qualifications": qualifications,
                "titles": titles,
                "topics": topics,
                "asset_url": public_url(asset["reference"]) if asset else None,
                "asset_hash": asset["sha256"] if asset else None,
            }
        )
    if not records or slugs != set(review["coaches"]):
        raise ValueError("review coach set changed")
    return records


def verify(canonical, review, fetch=fetch_public):
    """Inject a bytes-only GET helper for pure synthetic tests. Never write evidence."""
    records = expected_records(canonical, review)
    expected = {
        "profile_status_200": len(records),
        "profile_names": len(records),
        "public_qualifications": sum(len(r["qualifications"]) for r in records),
        "old_offering_titles": sum(len(r["titles"]) for r in records),
        "asset_sha256": sum(r["asset_url"] is not None for r in records),
        "index_routes": len(records),
        "index_topic_links": sum(len(r["topics"]) for r in records),
    }
    matched = Counter()
    gaps = Counter()
    observations = []

    def get(url, kind):
        try:
            response = validate_response(checked_url(url), fetch(url))
        except (FetchFailure, OSError, URLError):
            gaps[kind + "_fetch_or_url"] += 1
            return None
        observations.append([url, response.status, sha256(response.body)])
        if response.status != 200:
            gaps[kind + "_http_status"] += 1
            return None
        return response

    def html(response, kind):
        if response is None:
            return None
        try:
            return parse_html(response.body)
        except (UnicodeError, ValueError):
            gaps[kind + "_html"] += 1
            return None

    index_url = public_url("coaches/")
    index = html(get(index_url, "index"), "index")
    by_route = {}
    if index is not None:
        if len(index.cards) != len(records):
            gaps["index_card_count"] += 1
        for card in index.cards:
            routes = set()
            for href in card["hrefs"]:
                try:
                    target = checked_url(urljoin(index_url, href)).rstrip("/")
                except (ValueError, FetchFailure):
                    gaps["index_anchor_boundary"] += 1
                    continue
                routes.add(target)
            if len(routes) != 1:
                gaps["index_card_route"] += 1
                continue
            route = routes.pop()
            by_route.setdefault(route, []).append(card["topics"])
        if set(by_route) - {r["url"].rstrip("/") for r in records}:
            gaps["index_unexpected_route"] += 1

    for record in records:
        response = get(record["url"], "profile")
        if response is not None:
            matched["profile_status_200"] += 1
        profile = html(response, "profile")
        if profile is not None:
            for key, labels in (
                ("profile_names", [record["name"]]),
                ("public_qualifications", record["qualifications"]),
                ("old_offering_titles", record["titles"]),
            ):
                matched[key] += sum(
                    normalize(label) in profile.text for label in labels
                )
        if record["asset_url"]:
            asset = get(record["asset_url"], "asset")
            if asset is not None and sha256(asset.body) == record["asset_hash"]:
                matched["asset_sha256"] += 1
        cards = by_route.get(record["url"].rstrip("/"), [])
        if len(cards) == 1:
            matched["index_routes"] += 1
            topics = cards[0]
            matched["index_topic_links"] += len(set(topics) & set(record["topics"]))
            if Counter(topics) != Counter(record["topics"]):
                gaps["index_topic_assignment"] += 1
    for key, count in expected.items():
        if matched[key] != count:
            gaps[key] += count - matched[key]
    return {
        "status": "FAIL" if gaps else "PASS",
        "counts": {
            key: {"matched": matched[key], "expected": count}
            for key, count in expected.items()
        },
        "gaps": dict(sorted(gaps.items())),
        # These are approved dry-run deltas, never CURRENT live expectations.
        "excluded_new_formats": sum(
            len(f["formats"]) for f in review.get("new_offering_families", [])
        ),
        "responses_observed": len(observations),
        "response_manifest_sha256": sha256(
            json.dumps(observations, separators=(",", ":")).encode("utf-8")
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument(
        "--verify",
        action="store_true",
        required=True,
        help="GET-only check of the fixed public Preview",
    )
    parser.parse_args(argv)
    try:
        snapshot_bytes = SNAPSHOT.read_bytes()
        if sha256(snapshot_bytes) != SNAPSHOT_SHA256:
            raise ValueError("frozen snapshot hash mismatch")
        review_bytes = REVIEW_MAP.read_bytes()
        if sha256(review_bytes) != REVIEW_MAP_SHA256:
            raise ValueError("frozen review map hash mismatch")
        canonical, review = json.loads(snapshot_bytes), json.loads(review_bytes)
        # Fail before network access if classification/count expectations have drifted.
        records = expected_records(canonical, review)
        counts = {
            "profile_status_200": len(records),
            "profile_names": len(records),
            "public_qualifications": sum(len(r["qualifications"]) for r in records),
            "old_offering_titles": sum(len(r["titles"]) for r in records),
            "asset_sha256": sum(r["asset_url"] is not None for r in records),
            "index_routes": len(records),
            "index_topic_links": sum(len(r["topics"]) for r in records),
        }
        if counts != FROZEN_COUNTS:
            raise ValueError("frozen expected counts changed")
        result = verify(canonical, review)
        result["snapshot_sha256"] = SNAPSHOT_SHA256
        result["review_map_sha256"] = sha256(review_bytes)
    except (OSError, ValueError, KeyError, TypeError):
        result = {"status": "FAIL", "gaps": {"input_or_verification_error": 1}}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
