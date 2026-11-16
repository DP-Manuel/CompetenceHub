"""Explicitly pinned accepted TLS rollover; historical receipts stay immutable."""
from pathlib import Path
import json
import os
import re

# Filled only from a successful independently checked operating receipt.
ACCEPTED_RUN = 'f87c37d267614cce989ccbe5650214d9'
RECEIPT_SHA = 'e6b80664b761c5223bdc561524f8b086e3d246684d8ec3aafd710ed11b22e36d'
CA_SHA = '4b1c2ddd2b46329531fb8966f0c9d6ff34edcf15bdc7a1f6b894cb8ec8448cae'
LEAF_SHA = 'c37975978dc9fbf2836fadb8000bccd51a73c0c21e72d6708fe77fce73d72f87'


def bind_agent(bootstrap):
    if not ACCEPTED_RUN: return bootstrap
    if not re.fullmatch('[a-f0-9]{64}', LEAF_SHA): raise ValueError('ACCEPTED_TLS_LEAF_REQUIRED')
    return bootstrap.replace("u['serve'](", "u['LEAF_SHA']=" + repr(LEAF_SHA) + "\nu['serve'](")


def current_ca(root, original, require, sha):
    if not ACCEPTED_RUN: return original
    path = root / 'release-artifacts/pilot-tls' / (ACCEPTED_RUN + '.json')
    raw = path.read_bytes()
    require(sha(raw) == RECEIPT_SHA, 'ACCEPTED_TLS_RECEIPT_CHANGED')
    record = json.loads(raw)
    require(record['status'] == record['https'] == record['mfa_session'] == record['services'] == record['preservation'] == 'PASS'
            and record['certificate_sha256'] == LEAF_SHA and record['ca_sha256'] == CA_SHA
            and record['runtime'] == '5a555e9a9aae', 'ACCEPTED_TLS_ROLLOVER_REQUIRED')
    ca = Path(os.environ['LOCALAPPDATA']) / 'CompetenceHub/pilot-tls' / ACCEPTED_RUN / 'pilot-ca.pem'
    require(ca.is_file() and not ca.is_symlink() and sha(ca.read_bytes()) == CA_SHA, 'ACCEPTED_TLS_CA_REQUIRED')
    return ca
