from __future__ import annotations

import argparse
import secrets
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
from competence_hub_api.portal.calendar import (
    CalendarDraft,
    CalendarOfferDetail,
    CalendarOfferNotFoundError,
    CalendarOfferRecord,
    CalendarReviewDecision,
    CalendarRevisionRecord,
    CalendarService,
    CalendarTopic,
    CalendarTransitionConflictError,
    CalendarVersionConflictError,
    PublicCalendarOffer,
)
from competence_hub_api.security.tokens import digest_token

HOST = "127.0.0.1"
DEFAULT_PORT = 8443
INTERNAL_EMAIL = "synthetic.internal@example.invalid"
ENROLLMENT_EMAIL = "synthetic.enrollment@example.invalid"
COACH_EMAIL = "synthetic.coach@example.invalid"
EMPTY_COACH_EMAIL = "synthetic.coach-empty@example.invalid"
REVIEWER_EMAIL = "synthetic.reviewer@example.invalid"
ADMIN_EMAIL = "synthetic.admin@example.invalid"
COMPANY_CONTACT_EMAIL = "synthetic.company-contact@example.invalid"
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
USER_ID = UUID("00000000-0000-4000-8000-000000000901")

SYNTHETIC_IDENTITIES = {
    INTERNAL_EMAIL: (USER_ID, "Internal A", ("internal",)),
    ENROLLMENT_EMAIL: (USER_ID, "Enrollment A", ("internal",)),
    COACH_EMAIL: (
        UUID("00000000-0000-4000-8000-000000000911"),
        "Coach A",
        ("coach",),
    ),
    EMPTY_COACH_EMAIL: (
        UUID("00000000-0000-4000-8000-000000000912"),
        "Coach ohne Angebote",
        ("coach",),
    ),
    REVIEWER_EMAIL: (
        UUID("00000000-0000-4000-8000-000000000913"),
        "Reviewer A",
        ("calendar_reviewer",),
    ),
    ADMIN_EMAIL: (
        UUID("00000000-0000-4000-8000-000000000914"),
        "Admin A",
        ("admin",),
    ),
    COMPANY_CONTACT_EMAIL: (
        UUID("00000000-0000-4000-8000-000000000915"),
        "Firmenkontakt A",
        ("company_contact",),
    ),
}


def utc_now() -> datetime:
    return datetime.now(UTC)


class SyntheticSessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[bytes, tuple[str, bytes, UUID]] = {}

    def activate(self, identity_email: str) -> tuple[str, str]:
        session_token = secrets.token_urlsafe(32)
        csrf_token = secrets.token_urlsafe(32)
        self._sessions[digest_token(session_token)] = (
            identity_email,
            digest_token(csrf_token),
            uuid4(),
        )
        return session_token, csrf_token

    def _principal(
        self, token_hash: bytes, now: datetime
    ) -> SessionPrincipal | None:
        session = self._sessions.get(token_hash)
        if session is None:
            return None
        identity_email, csrf_token_hash, session_id = session
        user_id, display_name, roles = SYNTHETIC_IDENTITIES[identity_email]
        return SessionPrincipal(
            session_id=session_id,
            user_id=user_id,
            display_name=display_name,
            roles=roles,
            authenticated_at=now - timedelta(minutes=2),
            idle_expires_at=now + timedelta(minutes=30),
            absolute_expires_at=now + timedelta(hours=8),
            csrf_token_hash=csrf_token_hash,
        )

    async def refresh_active_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
        idle_timeout: timedelta,
    ) -> SessionPrincipal | None:
        del idle_timeout
        return self._principal(token_hash, now)

    async def find_active_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
    ) -> SessionPrincipal | None:
        return self._principal(token_hash, now)

    async def rotate_active_session_csrf(
        self,
        token_hash: bytes,
        *,
        csrf_token_hash: bytes,
        now: datetime,
        idle_timeout: timedelta,
    ) -> SessionPrincipal | None:
        del idle_timeout
        session = self._sessions.get(token_hash)
        if session is None:
            return None
        identity_email, _, session_id = session
        self._sessions[token_hash] = (identity_email, csrf_token_hash, session_id)
        return self._principal(token_hash, now)

    async def revoke_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
        reason: str,
    ) -> None:
        del now, reason
        self._sessions.pop(token_hash, None)


class SyntheticLoginService:
    def __init__(self) -> None:
        self._challenges: dict[str, tuple[str, str]] = {}

    def resolve_challenge(self, login_token: str, csrf_token: str) -> str | None:
        expected = self._challenges.get(login_token)
        if expected is None or expected[0] != csrf_token:
            return None
        return expected[1]

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
        if normalized_email not in SYNTHETIC_IDENTITIES:
            return LoginRejected()
        state = "mfa_enrollment_required" if normalized_email == ENROLLMENT_EMAIL else "mfa_required"
        suffix = normalized_email.split("@", 1)[0].replace(".", "-")
        login_token = f"synthetic-browser-login-{suffix}"
        csrf_token = f"synthetic-browser-login-csrf-{suffix}"
        self._challenges[login_token] = (csrf_token, normalized_email)
        return LoginAccepted(
            state=state,
            login_token=login_token,
            csrf_token=csrf_token,
        )


class SyntheticMfaService:
    def __init__(
        self,
        sessions: SyntheticSessionRepository,
        login_service: SyntheticLoginService,
    ) -> None:
        self._sessions = sessions
        self._login_service = login_service

    def _identity(self, login_token: str, csrf_token: str) -> str | None:
        return self._login_service.resolve_challenge(login_token, csrf_token)

    def _session(self, identity_email: str) -> MfaSessionCreated:
        session_token, csrf_token = self._sessions.activate(identity_email)
        return MfaSessionCreated(
            session_token=session_token,
            csrf_token=csrf_token,
        )

    async def start_totp_enrollment(
        self,
        *,
        login_token: str,
        csrf_token: str,
        now: datetime,
    ):
        del now
        if self._identity(login_token, csrf_token) != ENROLLMENT_EMAIL:
            return MfaRejected()
        return TotpEnrollmentCreated(
            "otpauth://totp/CompetenceHub:synthetic.enrollment@example.invalid"
            "?secret=JBSWY3DPEHPK3PXP&issuer=CompetenceHub"
        )

    async def confirm_totp_enrollment(self, **values):
        if (
            values["code"] != TOTP_CODE
            or self._identity(values["login_token"], values["csrf_token"])
            != ENROLLMENT_EMAIL
        ):
            return MfaRejected()
        outcome = self._session(ENROLLMENT_EMAIL)
        return replace(
            outcome,
            recovery_codes=RECOVERY_CODES,
        )

    async def verify_totp(self, **values):
        identity = self._identity(values["login_token"], values["csrf_token"])
        if values["code"] != TOTP_CODE or identity is None:
            return MfaRejected()
        return self._session(identity)

    async def verify_recovery_code(self, **values):
        identity = self._identity(values["login_token"], values["csrf_token"])
        if values["code"] != RECOVERY_CODE or identity is None:
            return MfaRejected()
        return self._session(identity)


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


class InMemoryCalendarRepository:
    TOPIC = CalendarTopic(
        UUID("00000000-0000-4000-8000-000000000920"),
        "Führung und Zusammenarbeit",
    )
    COACHES = {
        SYNTHETIC_IDENTITIES[COACH_EMAIL][0]: UUID(
            "00000000-0000-4000-8000-000000000921"
        ),
        SYNTHETIC_IDENTITIES[EMPTY_COACH_EMAIL][0]: UUID(
            "00000000-0000-4000-8000-000000000922"
        ),
    }

    def __init__(self) -> None:
        self._offers: dict[UUID, CalendarOfferDetail] = {}
        self._request_ids: dict[tuple[UUID, UUID], UUID] = {}
        self._decisions: dict[UUID, CalendarReviewDecision] = {}
        self._seed()

    def _seed(self) -> None:
        now = utc_now()
        states = ("draft", "in_review", "published", "changes_requested")
        for index, status in enumerate(states, start=1):
            offer_id = UUID(f"00000000-0000-4000-8000-{930 + index:012d}")
            revision_id = UUID(f"00000000-0000-4000-8000-{940 + index:012d}")
            starts_at = now + timedelta(days=7 + index * 4)
            draft = CalendarDraft(
                topic_id=self.TOPIC.id,
                title=f"Synthetisches Angebot {index}",
                summary="Ausschließlich für die lokale Browserabnahme.",
                starts_at=starts_at,
                ends_at=starts_at + timedelta(hours=2),
                time_zone="Europe/Berlin",
                format_code="online" if index % 2 else "praesenz",
                public_location=None if index % 2 else "Würzburg",
                capacity=12,
                review_threshold=6,
                decision_deadline=starts_at - timedelta(days=3),
                price_display_text="Preis nach Abstimmung",
            )
            revision = CalendarRevisionRecord(
                id=revision_id,
                offer_id=offer_id,
                revision_number=1,
                workflow_status=status,
                draft=draft,
                created_by_user_id=SYNTHETIC_IDENTITIES[COACH_EMAIL][0],
                submitted_at=now if status != "draft" else None,
                published_at=now if status == "published" else None,
                created_at=now,
                updated_at=now,
                topic_name=self.TOPIC.name,
            )
            self._offers[offer_id] = CalendarOfferDetail(
                offer=CalendarOfferRecord(
                    id=offer_id,
                    coach_id=self.COACHES[SYNTHETIC_IDENTITIES[COACH_EMAIL][0]],
                    created_by_user_id=SYNTHETIC_IDENTITIES[COACH_EMAIL][0],
                    client_request_id=UUID(
                        f"00000000-0000-4000-8000-{950 + index:012d}"
                    ),
                    lifecycle_status="active",
                    lock_version=1,
                    withdrawn_at=None,
                    created_at=now,
                    updated_at=now,
                    coach_display_name="Coach A",
                ),
                current_revision=revision,
                published_revision=revision if status == "published" else None,
            )
            if status == "changes_requested":
                self._decisions[offer_id] = CalendarReviewDecision(
                    "changes_requested",
                    "Bitte den öffentlichen Ort genauer beschreiben.",
                    now,
                )

    async def list_topics(
        self, *, actor_user_id: UUID, allow_any_coach: bool
    ) -> tuple[CalendarTopic, ...]:
        if allow_any_coach or actor_user_id in self.COACHES:
            return (self.TOPIC,)
        return ()

    def _visible(
        self, actor_user_id: UUID, allow_any_coach: bool, offer_id: UUID
    ) -> CalendarOfferDetail | None:
        detail = self._offers.get(offer_id)
        if detail is None:
            return None
        own_coach = self.COACHES.get(actor_user_id)
        if allow_any_coach or detail.offer.coach_id == own_coach:
            return detail
        return None

    async def create_offer(self, **values) -> CalendarOfferDetail:
        actor_user_id = values["actor_user_id"]
        request_id = values["client_request_id"]
        prior = self._request_ids.get((actor_user_id, request_id))
        if prior is not None:
            return self._offers[prior]
        coach_id = values["requested_coach_id"] or self.COACHES.get(actor_user_id)
        if coach_id is None:
            raise CalendarOfferNotFoundError("coach is unavailable")
        now = values["now"]
        offer_id = uuid4()
        revision = CalendarRevisionRecord(
            id=uuid4(),
            offer_id=offer_id,
            revision_number=1,
            workflow_status="draft",
            draft=values["draft"],
            created_by_user_id=actor_user_id,
            submitted_at=None,
            published_at=None,
            created_at=now,
            updated_at=now,
            topic_name=self.TOPIC.name,
        )
        detail = CalendarOfferDetail(
            offer=CalendarOfferRecord(
                id=offer_id,
                coach_id=coach_id,
                created_by_user_id=actor_user_id,
                client_request_id=request_id,
                lifecycle_status="active",
                lock_version=1,
                withdrawn_at=None,
                created_at=now,
                updated_at=now,
                coach_display_name="Coach A",
            ),
            current_revision=revision,
            published_revision=None,
        )
        self._offers[offer_id] = detail
        self._request_ids[(actor_user_id, request_id)] = offer_id
        return detail

    async def get_offer(self, **values) -> CalendarOfferDetail | None:
        return self._visible(
            values["actor_user_id"], values["allow_any_coach"], values["offer_id"]
        )

    async def list_offers(self, **values) -> tuple[CalendarOfferDetail, ...]:
        actor_user_id = values["actor_user_id"]
        allow_any = values["allow_any_coach"]
        requested = values["requested_coach_id"]
        visible = [
            detail
            for detail in self._offers.values()
            if self._visible(actor_user_id, allow_any, detail.offer.id) is not None
            and (requested is None or detail.offer.coach_id == requested)
        ]
        return tuple(
            sorted(visible, key=lambda item: item.offer.updated_at, reverse=True)[
                : values["limit"]
            ]
        )

    async def list_review_queue(self, **values) -> tuple[CalendarOfferDetail, ...]:
        return tuple(
            detail
            for detail in self._offers.values()
            if detail.offer.lifecycle_status == "active"
            and detail.current_revision.workflow_status == "in_review"
        )[: values["limit"]]

    async def get_review_decision(self, **values) -> CalendarReviewDecision | None:
        visible = self._visible(
            values["actor_user_id"], values["allow_any_coach"], values["offer_id"]
        )
        return self._decisions.get(values["offer_id"]) if visible else None

    async def list_public_offers(self, **values) -> tuple[PublicCalendarOffer, ...]:
        items = [
            self._public(detail)
            for detail in self._offers.values()
            if detail.offer.lifecycle_status == "active"
            and detail.current_revision.workflow_status == "published"
            and values["from_at"] <= detail.current_revision.draft.starts_at < values["to_at"]
        ]
        return tuple(item for item in items if item is not None)[: values["limit"]]

    async def get_public_offer(self, **values) -> PublicCalendarOffer | None:
        detail = self._offers.get(values["offer_id"])
        if (
            detail is None
            or detail.offer.lifecycle_status != "active"
            or detail.current_revision.workflow_status != "published"
        ):
            return None
        return self._public(detail)

    def _require_version(self, detail: CalendarOfferDetail, expected: int) -> None:
        if detail.offer.lock_version != expected:
            raise CalendarVersionConflictError("stale calendar offer version")

    def _store(
        self,
        detail: CalendarOfferDetail,
        revision: CalendarRevisionRecord,
        now: datetime,
        *,
        lifecycle_status: str | None = None,
    ) -> CalendarOfferDetail:
        offer = replace(
            detail.offer,
            lifecycle_status=lifecycle_status or detail.offer.lifecycle_status,
            lock_version=detail.offer.lock_version + 1,
            withdrawn_at=now if lifecycle_status == "withdrawn" else detail.offer.withdrawn_at,
            updated_at=now,
        )
        stored = CalendarOfferDetail(
            offer=offer,
            current_revision=revision,
            published_revision=(
                revision
                if revision.workflow_status == "published"
                else detail.published_revision
            ),
        )
        self._offers[offer.id] = stored
        return stored

    async def update_draft(self, **values) -> CalendarOfferDetail:
        detail = self._visible(
            values["actor_user_id"], values["allow_any_coach"], values["offer_id"]
        )
        if detail is None:
            raise CalendarOfferNotFoundError("calendar offer was not found")
        self._require_version(detail, values["expected_version"])
        current = detail.current_revision
        if current.workflow_status not in {"draft", "changes_requested", "published"}:
            raise CalendarTransitionConflictError("offer cannot be edited")
        new_revision = current.revision_number + (current.workflow_status != "draft")
        revision = replace(
            current,
            id=current.id if current.workflow_status == "draft" else uuid4(),
            revision_number=new_revision,
            workflow_status="draft",
            draft=values["draft"],
            submitted_at=None,
            published_at=None,
            updated_at=values["now"],
            topic_name=self.TOPIC.name,
        )
        return self._store(detail, revision, values["now"])

    async def submit_offer(self, **values) -> CalendarOfferDetail:
        detail = self._visible(
            values["actor_user_id"], values["allow_any_coach"], values["offer_id"]
        )
        if detail is None:
            raise CalendarOfferNotFoundError("calendar offer was not found")
        self._require_version(detail, values["expected_version"])
        if detail.current_revision.workflow_status != "draft":
            raise CalendarTransitionConflictError("only a draft may be submitted")
        revision = replace(
            detail.current_revision,
            workflow_status="in_review",
            submitted_at=values["now"],
            updated_at=values["now"],
        )
        return self._store(detail, revision, values["now"])

    async def review_offer(self, **values) -> CalendarOfferDetail:
        detail = self._offers.get(values["offer_id"])
        if detail is None:
            raise CalendarOfferNotFoundError("calendar offer was not found")
        self._require_version(detail, values["expected_version"])
        if detail.current_revision.workflow_status != "in_review":
            raise CalendarTransitionConflictError("offer is not in review")
        revision = replace(
            detail.current_revision,
            workflow_status=values["outcome"],
            published_at=values["now"] if values["outcome"] == "published" else None,
            updated_at=values["now"],
        )
        self._decisions[detail.offer.id] = CalendarReviewDecision(
            values["outcome"], values["note"], values["now"]
        )
        return self._store(detail, revision, values["now"])

    async def withdraw_offer(self, **values) -> CalendarOfferDetail:
        detail = self._visible(
            values["actor_user_id"], values["allow_any_coach"], values["offer_id"]
        )
        if detail is None:
            raise CalendarOfferNotFoundError("calendar offer was not found")
        self._require_version(detail, values["expected_version"])
        return self._store(
            detail,
            detail.current_revision,
            values["now"],
            lifecycle_status="withdrawn",
        )

    def _public(self, detail: CalendarOfferDetail) -> PublicCalendarOffer:
        draft = detail.current_revision.draft
        return PublicCalendarOffer(
            id=detail.offer.id,
            coach_display_name=detail.offer.coach_display_name or "Coach A",
            coach_profile_path=None,
            topic_id=draft.topic_id,
            topic_name=self.TOPIC.name,
            title=draft.title,
            summary=draft.summary,
            starts_at=draft.starts_at,
            ends_at=draft.ends_at,
            time_zone=draft.time_zone,
            format_code=draft.format_code,
            public_location=draft.public_location,
            capacity=draft.capacity,
            decision_deadline=draft.decision_deadline,
            price_display_text=draft.price_display_text,
            updated_at=detail.offer.updated_at,
        )


def create_acceptance_app(port: int = DEFAULT_PORT):
    sessions = SyntheticSessionRepository()
    login_service = SyntheticLoginService()
    return create_app(
        readiness_probe=_ready,
        session_repository=sessions,
        calendar_session_repository=sessions,
        login_service=login_service,
        mfa_service=SyntheticMfaService(sessions, login_service),
        company_service=CompanyService(InMemoryCompanyRepository()),
        calendar_service=CalendarService(InMemoryCalendarRepository()),
        calendar_cursor_hmac_key=b"synthetic-browser-calendar-cursor-key",
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
