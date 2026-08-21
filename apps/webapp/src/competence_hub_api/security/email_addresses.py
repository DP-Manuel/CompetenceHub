from email.headerregistry import Address


def is_single_email_address(value: str) -> bool:
    if not value or len(value) > 254 or any(character.isspace() for character in value):
        return False
    try:
        address = Address(addr_spec=value)
    except (IndexError, ValueError):
        return False
    return bool(address.username and address.domain) and address.addr_spec == value
