"""Explicitly pinned accepted TLS rollover; historical receipts stay immutable."""
from pathlib import Path
import json
import os
import re

# Filled only from a successful independently checked operating receipt.
ACCEPTED_RUN = ''
RECEIPT_SHA = ''
CA_SHA = ''
LEAF_SHA = ''


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
