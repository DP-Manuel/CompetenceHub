from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from ipaddress import ip_address
from pathlib import Path
from uuid import UUID, uuid4

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import uvicorn

from competence_hub_api.auth.login_service import LoginAccepted, LoginRejected
from competence_hub_api.auth.mfa_service import (
    MfaRejected,
    MfaSessionCreated,
    TotpEnrollmentCreated,
)
from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.main import create_app
from competence_hub_api.portal.companies import (
    CompanyContactRecord,
    CompanyDetail,
    CompanyRecord,
    CompanyRepository,
    CompanyService,
    CompanySummary,
    NewCompanyContact,
)
from competence_hub_api.security.tokens import digest_token

HOST = "127.0.0.1"
DEFAULT_PORT = 8443
INTERNAL_EMAIL = "synthetic.internal@example.invalid"
ENROLLMENT_EMAIL = "synthetic.enrollment@example.invalid"
SYNTHETIC_PASSWORD = "Synthetic-Portal-2026!"
TOTP_CODE = "123456"
RECOVERY_CODE = "AAAA-BBBB-CCCC-DDDD"
RECOVERY_CODES = (
    RECOVERY_CODE,
    "EEEE-FFFF-GGGG-HHHH",
    "IIII-JJJJ-KKKK-LLLL",
    "MMMM-NNNN-OOOO-PPPP",
    "QQQQ-RRRR-SSSS-TTTT",
    "UUUU-VVVV-WWWW-XXXX",
    "2222-3333-4444-5555",
    "6666-7777-8888-9999",
    "ABCD-EFGH-IJKL-MNOP",
    "QRST-UVWX-YZ23-4567",
)
SESSION_TOKEN = "synthetic-browser-session-token"
SESSION_CSRF = "synthetic-browser-session-csrf"
USER_ID = UUID("00000000-0000-4000-8000-000000000901")


def utc_now() -> datetime:
    return datetime.now(UTC)


class SyntheticSessionRepository:
    def __init__(self) -> None:
        self._active = False
        self._csrf_token_hash = digest_token(SESSION_CSRF)

    def activate(self) -> None:
        self._active = True
        self._csrf_token_hash = digest_token(SESSION_CSRF)

    def _principal(self, now: datetime) -> SessionPrincipal | None:
        if not self._active:
            return None
        return SessionPrincipal(
            session_id=UUID("00000000-0000-4000-8000-000000000902"),
            user_id=USER_ID,
            display_name="Synthetic Internal User",
            roles=("internal",),
            authenticated_at=now - timedelta(minutes=2),
            idle_expires_at=now + timedelta(minutes=30),
            absolute_expires_at=now + timedelta(hours=8),
            csrf_token_hash=self._csrf_token_hash,
        )

    async def refresh_active_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
        idle_timeout: timedelta,
    ) -> SessionPrincipal | None:
        del idle_timeout
        if token_hash != digest_token(SESSION_TOKEN):
            return None
        return self._principal(now)

    async def find_active_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
    ) -> SessionPrincipal | None:
        if token_hash != digest_token(SESSION_TOKEN):
            return None
        return self._principal(now)

    async def rotate_active_session_csrf(
        self,
        token_hash: bytes,
        *,
        csrf_token_hash: bytes,
        now: datetime,
        idle_timeout: timedelta,
    ) -> SessionPrincipal | None:
        del idle_timeout
        if token_hash != digest_token(SESSION_TOKEN) or not self._active:
            return None
        self._csrf_token_hash = csrf_token_hash
        return self._principal(now)

    async def revoke_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
        reason: str,
    ) -> None:
        del now, reason
        if token_hash == digest_token(SESSION_TOKEN):
            self._active = False


class SyntheticLoginService:
    async def authenticate(
        self,
        *,
        normalized_email: str,
        password: str,
        client_ip: str,
        now: datetime,
    ):
        del client_ip, now
        if password != SYNTHETIC_PASSWORD:
            return LoginRejected()
        states = {
            INTERNAL_EMAIL: "mfa_required",
            ENROLLMENT_EMAIL: "mfa_enrollment_required",
        }
        state = states.get(normalized_email)
        if state is None:
            return LoginRejected()
        suffix = "enrollment" if normalized_email == ENROLLMENT_EMAIL else "internal"
        return LoginAccepted(
            state=state,
            login_token=f"synthetic-browser-login-{suffix}",
            csrf_token=f"synthetic-browser-login-csrf-{suffix}",
        )


class SyntheticMfaService:
    def __init__(self, sessions: SyntheticSessionRepository) -> None:
        self._sessions = sessions

    @staticmethod
    def _valid_challenge(login_token: str, csrf_token: str) -> bool:
        suffix = "enrollment" if login_token.endswith("enrollment") else "internal"
        return (
            login_token == f"synthetic-browser-login-{suffix}"
            and csrf_token == f"synthetic-browser-login-csrf-{suffix}"
        )

    def _session(self) -> MfaSessionCreated:
        self._sessions.activate()
        return MfaSessionCreated(
            session_token=SESSION_TOKEN,
            csrf_token=SESSION_CSRF,
        )

    async def start_totp_enrollment(
        self,
        *,
        login_token: str,
        csrf_token: str,
        now: datetime,
    ):
        del now
        if not login_token.endswith("enrollment") or not self._valid_challenge(
            login_token, csrf_token
        ):
            return MfaRejected()
        return TotpEnrollmentCreated(
            "otpauth://totp/CompetenceHub:synthetic.enrollment@example.invalid"
            "?secret=JBSWY3DPEHPK3PXP&issuer=CompetenceHub"
        )

    async def confirm_totp_enrollment(self, **values):
        if (
            values["code"] != TOTP_CODE
            or not values["login_token"].endswith("enrollment")
            or not self._valid_challenge(
                values["login_token"], values["csrf_token"]
            )
        ):
            return MfaRejected()
        outcome = self._session()
        return replace(
            outcome,
            recovery_codes=RECOVERY_CODES,
        )

    async def verify_totp(self, **values):
        if values["code"] != TOTP_CODE or not self._valid_challenge(
            values["login_token"], values["csrf_token"]
        ):
            return MfaRejected()
        return self._session()

    async def verify_recovery_code(self, **values):
        if values["code"] != RECOVERY_CODE or not self._valid_challenge(
            values["login_token"], values["csrf_token"]
        ):
            return MfaRejected()
        return self._session()


class InMemoryCompanyRepository(CompanyRepository):
    def __init__(self) -> None:
        self._companies: dict[UUID, CompanyRecord] = {}
        self._contacts: dict[UUID, CompanyContactRecord] = {}

    async def create_company(
        self,
        *,
        actor_user_id: UUID,
        name: str,
        industry: str | None,
        status: str,
        internal_notes: str | None,
        initial_contact: NewCompanyContact,
        now: datetime,
    ) -> CompanyDetail:
        del actor_user_id
        company_id = uuid4()
        company = CompanyRecord(
            id=company_id,
            name=name,
            industry=industry,
            status=status,
            internal_notes=internal_notes,
            created_at=now,
            updated_at=now,
        )
        contact = self._new_contact(company_id, initial_contact, now)
        self._companies[company_id] = company
        self._contacts[contact.id] = contact
        return CompanyDetail(company, (contact,))

    async def list_companies(
        self,
        *,
        query: str | None,
        limit: int,
    ) -> tuple[CompanySummary, ...]:
        records = sorted(self._companies.values(), key=lambda item: item.name.casefold())
        if query:
            needle = query.casefold()
            records = [item for item in records if needle in item.name.casefold()]
        return tuple(
            CompanySummary(
                id=item.id,
                name=item.name,
                industry=item.industry,
                status=item.status,
                updated_at=item.updated_at,
            )
            for item in records[:limit]
        )

    async def get_company(self, company_id: UUID) -> CompanyDetail | None:
        company = self._companies.get(company_id)
        if company is None:
            return None
        contacts = tuple(
            item for item in self._contacts.values() if item.company_id == company_id
        )
        return CompanyDetail(company, contacts)

    async def update_company(
        self,
        *,
        actor_user_id: UUID,
        company_id: UUID,
        changes: Mapping[str, str | None],
        now: datetime,
    ) -> CompanyRecord | None:
        del actor_user_id
        company = self._companies.get(company_id)
        if company is None:
            return None
        updated = replace(company, **changes, updated_at=now)
        self._companies[company_id] = updated
        return updated

    async def add_contact(
        self,
        *,
        actor_user_id: UUID,
        company_id: UUID,
        contact: NewCompanyContact,
        now: datetime,
    ) -> CompanyContactRecord | None:
        del actor_user_id
        if company_id not in self._companies:
            return None
        created = self._new_contact(company_id, contact, now)
        self._contacts[created.id] = created
        return created

    async def update_contact(
        self,
        *,
        actor_user_id: UUID,
        company_id: UUID,
        contact_id: UUID,
        changes: Mapping[str, str | None],
        now: datetime,
    ) -> CompanyContactRecord | None:
        del actor_user_id
        contact = self._contacts.get(contact_id)
        if contact is None or contact.company_id != company_id:
            return None
        updated = replace(contact, **changes, updated_at=now)
        self._contacts[contact_id] = updated
        return updated

    @staticmethod
    def _new_contact(
        company_id: UUID,
        contact: NewCompanyContact,
        now: datetime,
    ) -> CompanyContactRecord:
        return CompanyContactRecord(
            id=uuid4(),
            company_id=company_id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
            job_function=contact.job_function,
            created_at=now,
            updated_at=now,
        )


def create_acceptance_app(port: int = DEFAULT_PORT):
    sessions = SyntheticSessionRepository()
    return create_app(
        readiness_probe=_ready,
        session_repository=sessions,
        login_service=SyntheticLoginService(),
        mfa_service=SyntheticMfaService(sessions),
        company_service=CompanyService(InMemoryCompanyRepository()),
        allowed_origin=f"https://{HOST}:{port}",
        clock=utc_now,
    )


async def _ready() -> bool:
    return True


def create_loopback_certificate(directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "Competence Hub synthetic loopback")]
    )
    now = utc_now()
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName(
                [x509.IPAddress(ip_address(HOST)), x509.DNSName("localhost")]
            ),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )
    key_path = directory / "loopback-key.pem"
    certificate_path = directory / "loopback-certificate.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    certificate_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    return certificate_path, key_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the synthetic, loopback-only Competence Hub browser fixture."
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--certificate-directory", type=Path, required=True)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    certificate_path, key_path = create_loopback_certificate(
        args.certificate_directory
    )
    uvicorn.run(
        create_acceptance_app(args.port),
        host=HOST,
        port=args.port,
        ssl_certfile=str(certificate_path),
        ssl_keyfile=str(key_path),
        log_level="warning",
        access_log=False,
    )


if __name__ == "__main__":
    main()
