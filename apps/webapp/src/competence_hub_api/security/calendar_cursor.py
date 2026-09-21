import base64
from datetime import UTC, datetime
import hashlib
import hmac
import json
from uuid import UUID


class CalendarCursorCodec:
    def __init__(self, key: bytes) -> None:
        if len(key) < 32:
            raise ValueError("calendar cursor key must contain at least 256 bits")
        self._key = key

    def encode(self, starts_at: datetime, offer_id: UUID) -> str:
        if starts_at.tzinfo is None or starts_at.utcoffset() is None:
            raise ValueError("cursor timestamp must be timezone-aware")
        payload = json.dumps(
            {
                "offer_id": str(offer_id),
                "starts_at": starts_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        signature = hmac.new(self._key, payload, hashlib.sha256).digest()
        return f"{_encode(payload)}.{_encode(signature)}"

    def decode(self, token: str) -> tuple[datetime, UUID]:
        if not token or len(token) > 1024 or token.count(".") != 1:
            raise ValueError("invalid calendar cursor")
        payload_token, signature_token = token.split(".")
        try:
            payload = _decode(payload_token)
            signature = _decode(signature_token)
            expected = hmac.new(self._key, payload, hashlib.sha256).digest()
            if not hmac.compare_digest(signature, expected):
                raise ValueError("invalid calendar cursor")
            value = json.loads(payload.decode("ascii"))
            if not isinstance(value, dict) or set(value) != {"offer_id", "starts_at"}:
                raise ValueError("invalid calendar cursor")
            starts_at = datetime.fromisoformat(value["starts_at"].replace("Z", "+00:00"))
            offer_id = UUID(value["offer_id"])
            if starts_at.tzinfo is None or starts_at.utcoffset() is None:
                raise ValueError("invalid calendar cursor")
        except (ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid calendar cursor") from exc
        return starts_at, offer_id


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.b64decode(value + padding, altchars=b"-_", validate=True)
