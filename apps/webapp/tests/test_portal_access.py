from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pyotp
import pytest
from httpx import ASGITransport, AsyncClient

from competence_hub_api.auth.admission import INTERNAL_ADMISSION, PORTAL_ADMISSION
from competence_hub_api.auth.login_repository import LoginAccount
from competence_hub_api.auth.login_service import LoginService
from competence_hub_api.auth.mfa_repository import MfaChallenge
from competence_hub_api.auth.mfa_service import MfaService
from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.main import create_app
from competence_hub_api.portal.calendar import CalendarService
from competence_hub_api.portal.companies import CompanyService
from competence_hub_api.security.passwords import PasswordPolicy, PasswordService
from competence_hub_api.security.secret_encryption import SecretCipher
from competence_hub_api.security.tokens import digest_token
from scripts.browser_acceptance_app import (
    COACH_EMAIL, SYNTHETIC_IDENTITIES, InMemoryCalendarRepository, InMemoryCompanyRepository,
)

ORIGIN = "https://portal.example.invalid"
ACCESS = "/api/v1/portal/access"
PASSWORD = "Synthetic-access-passphrase-2026!"
SECRET = "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP"
NOW = datetime(2026, 10, 22, 9, 0, tzinfo=UTC)


@pytest.fixture
def anyio_backend():
    return "asyncio"


class AuthStore:
    """Local persistence double; LoginService, MfaService and HTTP handlers are real."""

    def __init__(self, roles):
        self.roles = roles
        self.active = True
        self.user_id = SYNTHETIC_IDENTITIES[COACH_EMAIL][0]
        self.passwords = PasswordService(PasswordPolicy(frozenset()))
        self.password_hash = self.passwords.hash(PASSWORD)
        self.cipher = SecretCipher({"test": b"t" * 32}, "test")
        self.encrypted = self.cipher.encrypt(SECRET, subject_id=str(self.user_id)).envelope
        self.enrolled = True
        self.last_step = None
        self.challenge = None
        self.challenge_values = None
        self.sessions = {}
        self.recovery = ()
        self.failures = 0

    async def find_login_account(self, email):
        if email != COACH_EMAIL:
            return None
        return LoginAccount(self.user_id, self.password_hash, self.active, self.roles, self.enrolled)

    async def find_login_rate_limit(self, *args, **kwargs):
        return None

    async def record_failed_login(self, *args, **kwargs):
        self.failures += 1
        return None

    async def create_login_challenge(self, **values):
        self.challenge_values = values
        self.challenge = MfaChallenge(
            challenge_id=uuid4(), user_id=self.user_id, email=COACH_EMAIL,
            state=values["state"], csrf_token_hash=values["csrf_token_hash"],
            encrypted_totp_secret=self.encrypted, totp_key_version="test",
            totp_enabled_at=NOW if self.enrolled else None,
            last_accepted_time_step=self.last_step,
        )

    async def find_active_challenge(self, token_hash, *, now):
        values = self.challenge_values
        if (self.challenge is None or values is None
                or values["token_hash"] != token_hash or values["expires_at"] <= now
                or not PORTAL_ADMISSION.allows(active=self.active, roles=self.roles)):
            return None
        return replace(self.challenge, last_accepted_time_step=self.last_step)

    async def find_mfa_rate_limit(self, *args, **kwargs):
        return None

    async def record_failed_mfa(self, **kwargs):
        self.failures += 1
        return None

    async def save_pending_totp(self, **values):
        if self.enrolled or self.challenge is None:
            return False
        self.encrypted = values["encrypted_secret"]
        self.challenge = replace(self.challenge, encrypted_totp_secret=self.encrypted)
        return True

    def finish(self, values):
        if (self.challenge is None or self.challenge.challenge_id != values["challenge_id"]
                or self.challenge_values["expires_at"] <= values["now"]
                or not PORTAL_ADMISSION.allows(active=self.active, roles=self.roles)):
            return False
        session = values["session"]
        self.sessions[session.token_hash] = SessionPrincipal(
            uuid4(), self.user_id, "Synthetic access", self.roles, values["now"],
            session.idle_expires_at, session.absolute_expires_at, session.csrf_token_hash,
        )
        self.challenge = None
        return True

    async def complete_totp(self, **values):
        step = values["accepted_time_step"]
        if self.last_step is not None and step <= self.last_step:
            return False
        if not self.finish(values):
            return False
        self.last_step = step
        if values["enrollment"]:
            self.enrolled = True
            self.recovery = values["recovery_codes"]
        return True

    async def complete_recovery(self, **values):
        match = next((record for record in self.recovery if record in values["candidate_digests"]), None)
        if match is None or not self.finish(values):
            return False
        self.recovery = tuple(record for record in self.recovery if record != match)
        return True


class SessionView:
    def __init__(self, store, policy):
        self.store = store
        self.policy = policy

    async def find_active_session(self, token_hash, *, now):
        principal = self.store.sessions.get(token_hash)
        if (principal is None or principal.idle_expires_at <= now
                or principal.absolute_expires_at <= now
                or not self.policy.allows(active=self.store.active, roles=self.store.roles)):
            return None
        return replace(principal, roles=tuple(sorted(set(self.store.roles) & self.policy.roles)))

    async def refresh_active_session(self, token_hash, *, now, idle_timeout):
        principal = await self.find_active_session(token_hash, now=now)
        if principal is not None:
            principal = replace(principal, idle_expires_at=min(now + idle_timeout, principal.absolute_expires_at))
            self.store.sessions[token_hash] = principal
        return principal

    async def rotate_active_session_csrf(self, token_hash, *, csrf_token_hash, now, idle_timeout):
        principal = await self.refresh_active_session(token_hash, now=now, idle_timeout=idle_timeout)
        if principal is not None:
            principal = replace(principal, csrf_token_hash=csrf_token_hash)
            self.store.sessions[token_hash] = principal
        return principal

    async def revoke_session(self, token_hash, **kwargs):
        self.store.sessions.pop(token_hash, None)


def access_app(roles):
    store = AuthStore(roles)
    clock = [NOW]
    internal = SessionView(store, INTERNAL_ADMISSION)
    portal = SessionView(store, PORTAL_ADMISSION)
    def login_service(policy):
        return LoginService(store, store.passwords, dummy_password_hash=store.password_hash,
                            rate_limit_hmac_key=b"l" * 32, admission_policy=policy)
    mfa = MfaService(store, store.cipher, recovery_hmac_keys={"test": b"r" * 32},
                     recovery_active_key_version="test", rate_limit_hmac_key=b"l" * 32,
                     session_idle_timeout=timedelta(minutes=30))
    app = create_app(
        session_repository=internal, calendar_session_repository=portal,
        portal_session_repository=portal, portal_login_service=login_service(PORTAL_ADMISSION),
        portal_mfa_service=mfa, login_service=login_service(INTERNAL_ADMISSION),
        calendar_service=CalendarService(InMemoryCalendarRepository()),
        company_service=CompanyService(InMemoryCompanyRepository()),
        account_lifecycle_service=ForbiddenLifecycle(),
        allowed_origin=ORIGIN, clock=lambda: clock[0],
    )
    return app, store, clock


class ForbiddenLifecycle:
    async def issue_invitation(self, **values):
        raise AssertionError("Calendar-only principal reached admin mutation service")


async def first_factor(client):
    return await client.post(f"{ACCESS}/login", headers={"Origin": ORIGIN},
                             json={"email": COACH_EMAIL, "password": PASSWORD})


async def verify(client, csrf, code):
    return await client.post(f"{ACCESS}/mfa/totp/verify", json={"code": code},
                             headers={"Origin": ORIGIN, "X-CSRF-Token": csrf})


@pytest.mark.anyio
@pytest.mark.parametrize("roles", [("coach",), ("calendar_reviewer",), ("coach", "calendar_reviewer"), ("admin",), ("internal",)])
async def test_mfa_backed_portal_admission_resume_logout_without_role_escalation(roles):
    app, store, clock = access_app(roles)
    async with AsyncClient(transport=ASGITransport(app=app), base_url=ORIGIN) as client:
        challenge = await first_factor(client)
        assert challenge.status_code == 202
        assert challenge.json()["state"] == "mfa_required"
        assert (await client.get(f"{ACCESS}/session")).status_code == 401
        assert not store.sessions
        csrf = challenge.json()["csrf_token"]
        invalid = await verify(client, csrf, "invalid")
        assert invalid.status_code == 401 and not store.sessions
        done = await verify(client, csrf, pyotp.TOTP(SECRET).at(clock[0].timestamp()))
        assert done.status_code == 204
        assert "Secure" in done.headers["set-cookie"] and "HttpOnly" in done.headers["set-cookie"]
        session_token = client.cookies.get("__Host-competence_hub_session")
        session = await client.get(f"{ACCESS}/session")
        assert session.status_code == 200
        assert session.headers["cache-control"] == "no-store"
        assert set(session.json()["user"]["roles"]) == set(roles)
        assert (await client.get(f"{ACCESS}/session")).json()["user"] == session.json()["user"]
        if not set(roles) & INTERNAL_ADMISSION.roles:
            assert (await client.get("/api/v1/auth/session")).status_code == 401
            for path in ("/api/v1/portal/companies", "/api/v1/portal/companies/00000000-0000-4000-8000-000000000001/contacts", "/api/v1/admin/users/invitations"):
                denied = await client.post(path, json={}, headers={"Origin": ORIGIN, "X-CSRF-Token": done.headers["x-csrf-token"]})
                assert denied.status_code == 401
            caps = await client.get("/api/v1/portal/calendar/capabilities")
            assert caps.json()["can_manage_own_offers"] == ("coach" in roles)
            assert caps.json()["can_review_offers"] == ("calendar_reviewer" in roles)
            if roles == ("coach",):
                assert (await client.get("/api/v1/portal/calendar/review-queue")).status_code == 403
                assert (await client.get(f"/api/v1/portal/calendar/offers/{uuid4()}")).status_code == 404
            if roles == ("calendar_reviewer",):
                draft = {
                    "topic_id": str(InMemoryCalendarRepository.TOPIC.id),
                    "title": "Synthetic scope test", "summary": None,
                    "starts_at": (NOW + timedelta(days=20)).isoformat(),
                    "ends_at": (NOW + timedelta(days=20, hours=2)).isoformat(),
                    "time_zone": "Europe/Berlin", "format": "online",
                    "public_location": None, "capacity": 10, "review_threshold": 5,
                    "decision_deadline": (NOW + timedelta(days=15)).isoformat(),
                    "price_display_text": "Synthetic",
                }
                denied = await client.post(
                    "/api/v1/portal/calendar/offers",
                    json={"client_request_id": str(uuid4()), "draft": draft},
                    headers={"Origin": ORIGIN, "X-CSRF-Token": done.headers["x-csrf-token"]},
                )
                assert denied.status_code == 403
        elif roles == ("internal",):
            assert (await client.get("/api/v1/portal/calendar/capabilities")).status_code == 403
        old_csrf = done.headers["x-csrf-token"]
        rotated = await client.post(f"{ACCESS}/session/csrf", headers={"Origin": ORIGIN})
        assert rotated.status_code == 204
        assert rotated.headers["x-csrf-token"] != old_csrf
        stale = await client.delete(f"{ACCESS}/session", headers={"Origin": ORIGIN, "X-CSRF-Token": old_csrf})
        assert stale.status_code == 403
        logout = await client.delete(f"{ACCESS}/session", headers={"Origin": ORIGIN, "X-CSRF-Token": rotated.headers["x-csrf-token"]})
        assert logout.status_code == 204 and not store.sessions
        client.cookies.set("__Host-competence_hub_session", session_token)
        assert (await client.get(f"{ACCESS}/session")).status_code == 401
        again = await first_factor(client)
        assert (await verify(client, again.json()["csrf_token"], pyotp.TOTP(SECRET).at(clock[0].timestamp()))).status_code == 401
        clock[0] += timedelta(seconds=30)
        assert (await verify(client, again.json()["csrf_token"], pyotp.TOTP(SECRET).at(clock[0].timestamp()))).status_code == 204
        store.roles = ()
        assert (await client.get(f"{ACCESS}/session")).status_code == 401
        assert (await client.get("/api/v1/portal/calendar/capabilities")).status_code == 401


@pytest.mark.anyio
@pytest.mark.parametrize("roles,active", [((), True), (("company_contact",), True), (("coach",), False), (("calendar_reviewer",), False)])
async def test_portal_access_denies_unadmitted_or_disabled_accounts(roles, active):
    app, store, _ = access_app(roles)
    store.active = active
    async with AsyncClient(transport=ASGITransport(app=app), base_url=ORIGIN) as client:
        response = await first_factor(client)
        assert response.status_code == 401
        assert response.json()["code"] == "authentication_failed"
        assert not store.sessions and store.challenge is None


@pytest.mark.anyio
@pytest.mark.parametrize("roles", [("coach",), ("calendar_reviewer",)])
async def test_calendar_mfa_expiry_state_origin_and_role_recheck(roles):
    app, store, clock = access_app(roles)
    async with AsyncClient(transport=ASGITransport(app=app), base_url=ORIGIN) as client:
        challenge = await first_factor(client)
        csrf = challenge.json()["csrf_token"]
        wrong_state = await client.post(f"{ACCESS}/mfa/totp/enrollment/confirm", json={"code": pyotp.TOTP(SECRET).at(clock[0].timestamp())}, headers={"Origin": ORIGIN, "X-CSRF-Token": csrf})
        assert wrong_state.status_code == 401
        wrong_origin = await client.post(f"{ACCESS}/mfa/totp/verify", json={"code": "123456"}, headers={"Origin": "https://other.example.invalid", "X-CSRF-Token": csrf})
        assert wrong_origin.status_code == 403
        clock[0] += timedelta(minutes=6)
        assert (await verify(client, csrf, pyotp.TOTP(SECRET).at(clock[0].timestamp()))).status_code == 401
        challenge = await first_factor(client)
        store.roles = ()
        assert (await verify(client, challenge.json()["csrf_token"], pyotp.TOTP(SECRET).at(clock[0].timestamp()))).status_code == 401
        assert not store.sessions


@pytest.mark.anyio
async def test_portal_access_defaults_fail_closed_without_runtime_services():
    async with AsyncClient(transport=ASGITransport(app=create_app()), base_url=ORIGIN) as client:
        assert (await first_factor(client)).status_code == 503
        assert (await client.get(f"{ACCESS}/session")).status_code == 401


@pytest.mark.anyio
@pytest.mark.parametrize("roles", [("coach",), ("calendar_reviewer",)])
async def test_calendar_mfa_enrollment_recovery_and_session_expiry(roles):
    app, store, clock = access_app(roles)
    store.enrolled = False
    async with AsyncClient(transport=ASGITransport(app=app), base_url=ORIGIN) as client:
        challenge = await first_factor(client)
        headers = {"Origin": ORIGIN, "X-CSRF-Token": challenge.json()["csrf_token"]}
        assert challenge.json()["state"] == "mfa_enrollment_required"
        assert (await verify(client, challenge.json()["csrf_token"], pyotp.TOTP(SECRET).at(clock[0].timestamp()))).status_code == 401
        enrollment = await client.post(f"{ACCESS}/mfa/totp/enrollment", headers=headers)
        totp = pyotp.parse_uri(enrollment.json()["provisioning_uri"])
        completed = await client.post(f"{ACCESS}/mfa/totp/enrollment/confirm", headers=headers, json={"code": totp.at(clock[0].timestamp())})
        assert completed.status_code == 200 and store.enrolled
        recovery = completed.json()["recovery_codes"][0]
        assert len(store.sessions) == 1
        clock[0] += timedelta(minutes=31)
        assert (await client.get(f"{ACCESS}/session")).status_code == 401
        challenge = await first_factor(client)
        headers["X-CSRF-Token"] = challenge.json()["csrf_token"]
        recovered = await client.post(f"{ACCESS}/mfa/recovery/verify", headers=headers, json={"code": recovery})
        assert recovered.status_code == 204
        assert (await client.get(f"{ACCESS}/session")).status_code == 200
        challenge = await first_factor(client)
        headers["X-CSRF-Token"] = challenge.json()["csrf_token"]
        assert (await client.post(f"{ACCESS}/mfa/recovery/verify", headers=headers, json={"code": recovery})).status_code == 401
        store.active = False
        assert (await client.get(f"{ACCESS}/session")).status_code == 401
