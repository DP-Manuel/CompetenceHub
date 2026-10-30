"""Prepare a versioned PUBLIC negative-password corpus, not user credentials.

Download only pinned public files, never submit an entered password anywhere.
Retain only normalized SHA-256 fingerprints plus license/provenance outside Git.
This static common-password list is not a comprehensive/live breach service.
"""

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
from urllib.request import HTTPRedirectHandler, Request, build_opener

COMMIT = "cb6d7645abf4a2c467bc80f84cf70bda3d60c2d6"
BASE = "https://raw.githubusercontent.com/danielmiessler/SecLists/" + COMMIT + "/"
SOURCE = "Passwords/Common-Credentials/100k-most-used-passwords-NCSC.txt"
SOURCE_SHA256 = "c2e5696882c603b76bb67a47ee970897e5a76fc4c3f5547abe3d0ca340c576e0"
LICENSE_SHA256 = "3dbdc93d5f8829de0941744841730a09c106d0732e5ae0e98ca1d77be7ded66c"
ROOT = Path(__file__).resolve().parents[2]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("pinned public source must not redirect")


def download(relative, expected):
    request = Request(
        BASE + relative,
        headers={"User-Agent": "CompetenceHub-public-corpus-preparation/1"},
    )
    with build_opener(NoRedirect()).open(request, timeout=30) as response:
        if response.url != BASE + relative or response.status != 200:
            raise ValueError("unexpected public corpus response")
        data = response.read(2 * 1024 * 1024 + 1)
    if len(data) > 2 * 1024 * 1024 or hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("pinned public corpus bytes changed")
    return data


def fingerprints(raw):
    # Same casefold+UTF-8+SHA256 semantics as the existing PasswordService.
    # Do not strip spaces: those are part of a password, not formatting.
    lines = raw.decode("utf-8").split("\n")
    values = [value.removesuffix("\r") for value in lines if value.removesuffix("\r")]
    if not 90000 <= len(values) <= 110000:
        raise ValueError("operational corpus is unexpectedly small/large")
    result = sorted(
        {
            hashlib.sha256(value.casefold().encode("utf-8")).hexdigest()
            for value in values
        }
    )
    if len(result) < 90000:
        raise ValueError("not enough distinct operational fingerprints")
    return ("\n".join(result) + "\n").encode("ascii"), len(values), len(result)


def protected_destination(path):
    original = Path(path)
    target = original.resolve()
    if (
        not original.is_absolute()
        or target == target.parent
        or target.is_relative_to(ROOT)
        or ROOT.is_relative_to(target)
        or target.exists()
    ):
        raise ValueError("new absolute outside-repository destination required")
    for parent in [original, *original.parents]:
        if parent.exists():
            info = parent.lstat()
            if (
                parent.is_symlink()
                or getattr(info, "st_file_attributes", 0)
                & stat.FILE_ATTRIBUTE_REPARSE_POINT
            ):
                raise ValueError(
                    "reparse points are not eligible for the corpus destination"
                )
    target.mkdir(mode=0o700, parents=True)
    if os.name == "nt":
        output = subprocess.check_output(
            ["whoami", "/user", "/fo", "csv", "/nh"], text=True
        )
        sid = next(csv.reader(io.StringIO(output)))[1]
        if not sid.startswith("S-1-"):
            raise ValueError("operator SID unavailable")
        subprocess.run(
            [
                "icacls",
                str(target),
                "/inheritance:r",
                "/grant:r",
                f"*{sid}:(OI)(CI)F",
                "*S-1-5-18:(OI)(CI)F",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    raw, license_data = download(SOURCE, SOURCE_SHA256), download(
        "LICENSE", LICENSE_SHA256
    )
    data, source_count, distinct = fingerprints(raw)
    destination = protected_destination(args.output_dir)
    output = destination / "compromised-password-fingerprints.sha256"
    metadata = {
        "schema": 1,
        "classification": "PUBLIC_NEGATIVE_PASSWORD_CORPUS_NOT_USER_CREDENTIALS",
        "source_url": BASE + SOURCE,
        "upstream_commit": COMMIT,
        "source_sha256": SOURCE_SHA256,
        "license": "MIT",
        "license_sha256": LICENSE_SHA256,
        "source_entries": source_count,
        "distinct_fingerprints": distinct,
        "normalization": "Python str.casefold + UTF-8 + SHA-256, no whitespace stripping",
        "fingerprints_sha256": hashlib.sha256(data).hexdigest(),
        "coverage": "Static common-password corpus, not all breached passwords or a live check",
    }
    for name, content in (
        (output.name, data),
        ("LICENSE-SecLists.txt", license_data),
        (
            "corpus-provenance.json",
            json.dumps(metadata, sort_keys=True, indent=2).encode(),
        ),
    ):
        with (destination / name).open("xb") as handle:
            handle.write(content)
    print(
        json.dumps(
            {"result": "PASS", "corpus_path": str(output), **metadata}, sort_keys=True
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
