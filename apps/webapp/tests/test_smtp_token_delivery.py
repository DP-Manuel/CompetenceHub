from datetime import UTC, datetime
from uuid import UUID

import pytest

from competence_hub_api.auth.smtp_token_delivery import SmtpTokenMessageAdapter
from competence_hub_api.auth.token_delivery import TokenDeliveryError


def adapter() -> SmtpTokenMessageAdapter:
    return SmtpTokenMessageAdapter(
        host="smtp.example.invalid",
        port=587,
        tls_mode="starttls",
        username="synthetic-user",
        password="synthetic-password",
        sender="portal@example.invalid",
        reply_to="support@example.invalid",
        account_action_base_url="https://portal.example.invalid/portal/",
    )


@pytest.mark.parametrize(
    ("purpose", "action"),
    [
        ("invitation", "einladung"),
        ("password_reset", "passwort-zuruecksetzen"),
    ],
)
def test_message_uses_fragment_link_and_expected_headers(purpose: str, action: str) -> None:
    message = adapter()._message(  # noqa: SLF001
        purpose=purpose,  # type: ignore[arg-type]
        recipient_email="recipient@example.invalid",
        token="synthetic token/+",
        expires_at=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
    )

    body = message.get_content()
    assert message["To"] == "recipient@example.invalid"
    assert message["From"] == "portal@example.invalid"
    assert message["Reply-To"] == "support@example.invalid"
    assert (
        f"https://portal.example.invalid/portal/#/{action}?token="
        "synthetic%20token%2F%2B"
    ) in body
    assert "synthetic token/+" not in str(message.items())


@pytest.mark.anyio
async def test_adapter_maps_transport_failure_to_generic_delivery_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    smtp_adapter = adapter()

    def fail(_message) -> None:
        raise OSError("synthetic transport failure")

    monkeypatch.setattr(smtp_adapter, "_send", fail)

    with pytest.raises(TokenDeliveryError, match="SMTP delivery failed"):
        await smtp_adapter.deliver(
            delivery_id=UUID("00000000-0000-0000-0000-000000000001"),
            purpose="invitation",
            recipient_email="recipient@example.invalid",
            token="synthetic-token",
            expires_at=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
        )


@pytest.mark.anyio
async def test_adapter_rejects_multiple_recipients_before_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    smtp_adapter = adapter()
    transport_called = False

    def record_transport(_message) -> None:
        nonlocal transport_called
        transport_called = True

    monkeypatch.setattr(smtp_adapter, "_send", record_transport)

    with pytest.raises(TokenDeliveryError, match="SMTP delivery failed"):
        await smtp_adapter.deliver(
            delivery_id=UUID("00000000-0000-0000-0000-000000000001"),
            purpose="invitation",
            recipient_email="first@example.invalid,second@example.invalid",
            token="synthetic-token",
            expires_at=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
        )

    assert transport_called is False
