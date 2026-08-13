from fastapi import Response

LOGIN_COOKIE_NAME = "__Host-competence_hub_login"
SESSION_COOKIE_NAME = "__Host-competence_hub_session"


def set_login_cookie(response: Response, token: str, max_age: int = 300) -> None:
    _set_secure_cookie(response, LOGIN_COOKIE_NAME, token, max_age)


def set_session_cookie(
    response: Response,
    token: str,
    max_age: int = 8 * 60 * 60,
) -> None:
    _set_secure_cookie(response, SESSION_COOKIE_NAME, token, max_age)


def clear_login_cookie(response: Response) -> None:
    _clear_secure_cookie(response, LOGIN_COOKIE_NAME)


def clear_session_cookie(response: Response) -> None:
    _clear_secure_cookie(response, SESSION_COOKIE_NAME)


def _set_secure_cookie(
    response: Response,
    name: str,
    token: str,
    max_age: int,
) -> None:
    if not token:
        raise ValueError("cookie token must not be empty")
    if max_age <= 0:
        raise ValueError("cookie max_age must be positive")

    response.set_cookie(
        key=name,
        value=token,
        max_age=max_age,
        secure=True,
        httponly=True,
        samesite="lax",
        path="/",
    )


def _clear_secure_cookie(response: Response, name: str) -> None:
    response.delete_cookie(
        key=name,
        secure=True,
        httponly=True,
        samesite="lax",
        path="/",
    )
