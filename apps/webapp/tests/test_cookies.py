from fastapi import Response

from competence_hub_api.security.cookies import (
    LOGIN_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    clear_session_cookie,
    set_login_cookie,
    set_session_cookie,
)


def test_session_cookie_has_host_only_security_attributes() -> None:
    response = Response()

    set_session_cookie(response, "synthetic-session-token")

    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{SESSION_COOKIE_NAME}=")
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=lax" in cookie
    assert "Path=/" in cookie
    assert "Domain=" not in cookie


def test_login_cookie_uses_short_default_lifetime() -> None:
    response = Response()

    set_login_cookie(response, "synthetic-login-token")

    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{LOGIN_COOKIE_NAME}=")
    assert "Max-Age=300" in cookie


def test_clearing_session_cookie_preserves_security_attributes() -> None:
    response = Response()

    clear_session_cookie(response)

    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{SESSION_COOKIE_NAME}=")
    assert "Max-Age=0" in cookie
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
