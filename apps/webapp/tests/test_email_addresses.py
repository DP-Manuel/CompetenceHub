import pytest

from competence_hub_api.security.email_addresses import is_single_email_address


@pytest.mark.parametrize(
    "value",
    [
        "person@example.invalid",
        "first.last+portal@example.invalid",
    ],
)
def test_single_email_address_accepts_plain_mailboxes(value: str) -> None:
    assert is_single_email_address(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "",
        "not-an-email",
        "person@example.invalid,attacker@example.invalid",
        "Person <person@example.invalid>",
        "person@example.invalid\r\nBcc: attacker@example.invalid",
        "person @example.invalid",
    ],
)
def test_single_email_address_rejects_lists_names_and_header_injection(
    value: str,
) -> None:
    assert is_single_email_address(value) is False
