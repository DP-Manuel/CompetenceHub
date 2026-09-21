import re


MAX_PUBLIC_PROFILE_PATH_LENGTH = 200
_PUBLIC_PROFILE_PATH = re.compile(
    r"/coaches/[a-z0-9]+(?:-[a-z0-9]+)*/",
    flags=re.ASCII,
)


def validate_public_profile_path(value: str | None) -> str | None:
    """Validate an explicit mapping to an approved public Coach profile."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("invalid public_profile_path")
    if len(value) > MAX_PUBLIC_PROFILE_PATH_LENGTH or not _PUBLIC_PROFILE_PATH.fullmatch(
        value
    ):
        raise ValueError("invalid public_profile_path")
    return value
