from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from competence_hub_api.auth.mfa_repository import (
    MfaChallenge,
    RecoveryCodeRecord,
    SessionRecord,
)
from competence_hub_api.auth.postgres_login_repository import (
    RATE_LIMIT_BASE_DELAY_SECONDS,
    RATE_LIMIT_MAX_DELAY_SECONDS,
    RATE_LIMIT_THRESHOLD,
    RATE_LIMIT_WINDOW,
)

_FIND_ACTIVE_CHALLENGE = text(
    """
    SELECT
        challenge.id AS challenge_id,
        challenge.portal_user_id AS user_id,
        challenge.state,
        challenge.csrf_token_hash,
        portal_user.email,
        totp.encrypted_secret,
        totp.key_version,
        totp.enabled_at,
        totp.last_accepted_time_step
    FROM competence_hub.auth_login_challenges AS challenge
    JOIN competence_hub.portal_users AS portal_user
      ON portal_user.id = challenge.portal_user_id
     AND portal_user.active
    LEFT JOIN competence_hub.auth_totp_credentials AS totp
      ON totp.portal_user_id = challenge.portal_user_id
    WHERE challenge.token_hash = :token_hash
      AND challenge.consumed_at IS NULL
      AND challenge.revoked_at IS NULL
      AND challenge.expires_at > :now
      AND EXISTS (
          SELECT 1
          FROM competence_hub.user_roles AS user_role
          JOIN competence_hub.roles AS role
            ON role.id = user_role.role_id
           AND role.active
           AND role.code IN ('admin', 'internal')
          WHERE user_role.user_id = portal_user.id
      )
    """
)

_SAVE_PENDING_TOTP = text(
    """
    INSERT INTO competence_hub.auth_totp_credentials (
        portal_user_id,
        encrypted_secret,
        key_version
    )
    SELECT
        :user_id,
        :encrypted_secret,
        :key_version
    FROM competence_hub.auth_login_challenges AS challenge
    WHERE challenge.id = :challenge_id
      AND challenge.portal_user_id = :user_id
      AND challenge.state = 'mfa_enrollment_required'
      AND challenge.consumed_at IS NULL
      AND challenge.revoked_at IS NULL
      AND challenge.expires_at > :now
      AND EXISTS (
          SELECT 1
          FROM competence_hub.portal_users AS portal_user
          JOIN competence_hub.user_roles AS user_role
            ON user_role.user_id = portal_user.id
          JOIN competence_hub.roles AS role
            ON role.id = user_role.role_id
           AND role.active
           AND role.code IN ('admin', 'internal')
          WHERE portal_user.id = :user_id
            AND portal_user.active
      )
    ON CONFLICT (portal_user_id) DO UPDATE
    SET
        encrypted_secret = EXCLUDED.encrypted_secret,
        key_version = EXCLUDED.key_version,
        last_accepted_time_step = NULL
    WHERE auth_totp_credentials.enabled_at IS NULL
    """
)

_FIND_MFA_RATE_LIMIT = text(
    """
    SELECT max(blocked_until) AS blocked_until
    FROM competence_hub.auth_rate_limit_buckets
    WHERE action = 'mfa_verify'
      AND bucket_key_hash IN (:user_bucket_hash, :ip_bucket_hash)
      AND blocked_until > :now
    """
)

_RECORD_MFA_FAILURE = text(
    """
    INSERT INTO competence_hub.auth_rate_limit_buckets (
        action,
        bucket_key_hash,
        window_started_at,
        failed_attempts,
        blocked_until
    ) VALUES (
        'mfa_verify',
        :bucket_key_hash,
        :now,
        1,
        NULL
    )
    ON CONFLICT (action, bucket_key_hash) DO UPDATE
    SET
        window_started_at = CASE
            WHEN auth_rate_limit_buckets.window_started_at <= :window_cutoff
                THEN :now
            ELSE auth_rate_limit_buckets.window_started_at
        END,
        failed_attempts = CASE
            WHEN auth_rate_limit_buckets.window_started_at <= :window_cutoff
                THEN 1
            ELSE auth_rate_limit_buckets.failed_attempts + 1
        END,
        blocked_until = CASE
            WHEN auth_rate_limit_buckets.window_started_at <= :window_cutoff
                THEN NULL
            WHEN auth_rate_limit_buckets.failed_attempts + 1 >= :threshold
                THEN :now + make_interval(
                    secs => LEAST(
                        :max_delay_seconds,
                        :base_delay_seconds * power(
                            2,
                            LEAST(
                                10,
                                auth_rate_limit_buckets.failed_attempts + 1
                                    - :threshold
                            )
                        )
                    )::double precision
                )
            ELSE NULL
        END
    RETURNING blocked_until
    """
)

_INCREMENT_CHALLENGE_FAILURES = text(
    """
    UPDATE competence_hub.auth_login_challenges
    SET failed_attempts = failed_attempts + 1
    WHERE id = :challenge_id
      AND portal_user_id = :user_id
      AND consumed_at IS NULL
      AND revoked_at IS NULL
    """
)

_AUDIT_MFA_FAILURE = text(
    """
    INSERT INTO competence_hub.audit_events (
        actor_user_id,
        occurred_at,
        action,
        entity_type,
        entity_id,
        outcome
    ) VALUES (
        :user_id,
        :now,
        'auth.mfa.verify',
        'auth_login_challenge',
        :challenge_id,
        'failure'
    )
    """
)

_ENABLE_ENROLLED_TOTP = text(
    """
    UPDATE competence_hub.auth_totp_credentials
    SET
        enabled_at = :now,
        last_accepted_time_step = :accepted_time_step
    WHERE portal_user_id = :user_id
      AND enabled_at IS NULL
      AND (
          last_accepted_time_step IS NULL
          OR last_accepted_time_step < :accepted_time_step
      )
    """
)

_ACCEPT_TOTP_STEP = text(
    """
    UPDATE competence_hub.auth_totp_credentials
    SET last_accepted_time_step = :accepted_time_step
    WHERE portal_user_id = :user_id
      AND enabled_at IS NOT NULL
      AND (
          last_accepted_time_step IS NULL
          OR last_accepted_time_step < :accepted_time_step
      )
    """
)

_CONSUME_CHALLENGE = text(
    """
    UPDATE competence_hub.auth_login_challenges
    SET consumed_at = :now
    WHERE id = :challenge_id
      AND portal_user_id = :user_id
      AND state = :state
      AND consumed_at IS NULL
      AND revoked_at IS NULL
      AND expires_at > :now
      AND EXISTS (
          SELECT 1
          FROM competence_hub.portal_users AS portal_user
          JOIN competence_hub.user_roles AS user_role
            ON user_role.user_id = portal_user.id
          JOIN competence_hub.roles AS role
            ON role.id = user_role.role_id
           AND role.active
           AND role.code IN ('admin', 'internal')
          WHERE portal_user.id = :user_id
            AND portal_user.active
      )
    """
)

_DELETE_RECOVERY_CODES = text(
    """
    DELETE FROM competence_hub.auth_recovery_codes
    WHERE portal_user_id = :user_id
    """
)

_INSERT_RECOVERY_CODE = text(
    """
    INSERT INTO competence_hub.auth_recovery_codes (
        portal_user_id,
        code_hash,
        key_version
    ) VALUES (
        :user_id,
        :code_hash,
        :key_version
    )
    """
)

_CONSUME_RECOVERY_CODE = text(
    """
    UPDATE competence_hub.auth_recovery_codes
    SET used_at = :now
    WHERE portal_user_id = :user_id
      AND code_hash = :code_hash
      AND key_version = :key_version
      AND used_at IS NULL
    """
)

_INSERT_SESSION = text(
    """
    INSERT INTO competence_hub.auth_sessions (
        portal_user_id,
        token_hash,
        csrf_token_hash,
        authenticated_at,
        mfa_completed_at,
        last_seen_at,
        idle_expires_at,
        absolute_expires_at
    ) VALUES (
        :user_id,
        :token_hash,
        :csrf_token_hash,
        :now,
        :now,
        :now,
        :idle_expires_at,
        :absolute_expires_at
    )
    """
)

_AUDIT_MFA_SUCCESS = text(
    """
    INSERT INTO competence_hub.audit_events (
        actor_user_id,
        occurred_at,
        action,
        entity_type,
        entity_id,
        outcome
    ) VALUES (
        :user_id,
        :now,
        :action,
        'auth_login_challenge',
        :challenge_id,
        'success'
    )
    """
)

_CLEAR_USER_MFA_RATE_LIMIT = text(
    """
    DELETE FROM competence_hub.auth_rate_limit_buckets
    WHERE action = 'mfa_verify'
      AND bucket_key_hash = :user_bucket_hash
    """
)


class _AtomicMfaRejected(Exception):
    pass


class PostgresMfaRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def find_active_challenge(
        self,
        token_hash: bytes,
        *,
        now: datetime,
    ) -> MfaChallenge | None:
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _FIND_ACTIVE_CHALLENGE,
                {"token_hash": token_hash, "now": now},
            )
            row = result.mappings().one_or_none()
        if row is None:
            return None
        encrypted_secret = row["encrypted_secret"]
        return MfaChallenge(
            challenge_id=row["challenge_id"],
            user_id=row["user_id"],
            email=row["email"],
            state=row["state"],
            csrf_token_hash=bytes(row["csrf_token_hash"]),
            encrypted_totp_secret=(
                bytes(encrypted_secret) if encrypted_secret is not None else None
            ),
            totp_key_version=row["key_version"],
            totp_enabled_at=row["enabled_at"],
            last_accepted_time_step=row["last_accepted_time_step"],
        )

    async def save_pending_totp(
        self,
        *,
        challenge_id: UUID,
        user_id: UUID,
        encrypted_secret: bytes,
        key_version: str,
        now: datetime,
    ) -> bool:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _SAVE_PENDING_TOTP,
                {
                    "challenge_id": challenge_id,
                    "user_id": user_id,
                    "encrypted_secret": encrypted_secret,
                    "key_version": key_version,
                    "now": now,
                },
            )
            return result.rowcount == 1

    async def find_mfa_rate_limit(
        self,
        user_bucket_hash: bytes,
        ip_bucket_hash: bytes,
        *,
        now: datetime,
    ) -> datetime | None:
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _FIND_MFA_RATE_LIMIT,
                {
                    "user_bucket_hash": user_bucket_hash,
                    "ip_bucket_hash": ip_bucket_hash,
                    "now": now,
                },
            )
            return result.scalar_one_or_none()

    async def record_failed_mfa(
        self,
        *,
        challenge_id: UUID,
        user_id: UUID,
        user_bucket_hash: bytes,
        ip_bucket_hash: bytes,
        now: datetime,
    ) -> datetime | None:
        blocked_values: list[datetime] = []
        parameters = {
            "now": now,
            "window_cutoff": now - RATE_LIMIT_WINDOW,
            "threshold": RATE_LIMIT_THRESHOLD,
            "base_delay_seconds": RATE_LIMIT_BASE_DELAY_SECONDS,
            "max_delay_seconds": RATE_LIMIT_MAX_DELAY_SECONDS,
        }
        async with self._engine.begin() as connection:
            for bucket_hash in sorted({user_bucket_hash, ip_bucket_hash}):
                result = await connection.execute(
                    _RECORD_MFA_FAILURE,
                    {**parameters, "bucket_key_hash": bucket_hash},
                )
                blocked_until = result.scalar_one_or_none()
                if blocked_until is not None:
                    blocked_values.append(blocked_until)
            await connection.execute(
                _INCREMENT_CHALLENGE_FAILURES,
                {"challenge_id": challenge_id, "user_id": user_id},
            )
            await connection.execute(
                _AUDIT_MFA_FAILURE,
                {
                    "challenge_id": challenge_id,
                    "user_id": user_id,
                    "now": now,
                },
            )
        return max(blocked_values, default=None)

    async def complete_totp(
        self,
        *,
        challenge_id: UUID,
        user_id: UUID,
        accepted_time_step: int,
        enrollment: bool,
        recovery_codes: tuple[RecoveryCodeRecord, ...],
        session: SessionRecord,
        user_bucket_hash: bytes,
        now: datetime,
    ) -> bool:
        try:
            async with self._engine.begin() as connection:
                credential_result = await connection.execute(
                    _ENABLE_ENROLLED_TOTP if enrollment else _ACCEPT_TOTP_STEP,
                    {
                        "user_id": user_id,
                        "accepted_time_step": accepted_time_step,
                        "now": now,
                    },
                )
                if credential_result.rowcount != 1:
                    raise _AtomicMfaRejected()
                await self._consume_challenge(
                    connection,
                    challenge_id=challenge_id,
                    user_id=user_id,
                    state=(
                        "mfa_enrollment_required" if enrollment else "mfa_required"
                    ),
                    now=now,
                )
                if enrollment:
                    await connection.execute(
                        _DELETE_RECOVERY_CODES,
                        {"user_id": user_id},
                    )
                    for recovery_code in recovery_codes:
                        await connection.execute(
                            _INSERT_RECOVERY_CODE,
                            {
                                "user_id": user_id,
                                "code_hash": recovery_code.digest,
                                "key_version": recovery_code.key_version,
                            },
                        )
                await self._finish_success(
                    connection,
                    challenge_id=challenge_id,
                    user_id=user_id,
                    action=("auth.mfa.enrollment" if enrollment else "auth.mfa.verify"),
                    session=session,
                    user_bucket_hash=user_bucket_hash,
                    now=now,
                )
        except _AtomicMfaRejected:
            return False
        return True

    async def complete_recovery(
        self,
        *,
        challenge_id: UUID,
        user_id: UUID,
        candidate_digests: tuple[RecoveryCodeRecord, ...],
        session: SessionRecord,
        user_bucket_hash: bytes,
        now: datetime,
    ) -> bool:
        try:
            async with self._engine.begin() as connection:
                consumed = False
                for candidate in candidate_digests:
                    result = await connection.execute(
                        _CONSUME_RECOVERY_CODE,
                        {
                            "user_id": user_id,
                            "code_hash": candidate.digest,
                            "key_version": candidate.key_version,
                            "now": now,
                        },
                    )
                    if result.rowcount == 1:
                        consumed = True
                        break
                if not consumed:
                    raise _AtomicMfaRejected()
                await self._consume_challenge(
                    connection,
                    challenge_id=challenge_id,
                    user_id=user_id,
                    state="mfa_required",
                    now=now,
                )
                await self._finish_success(
                    connection,
                    challenge_id=challenge_id,
                    user_id=user_id,
                    action="auth.mfa.recovery",
                    session=session,
                    user_bucket_hash=user_bucket_hash,
                    now=now,
                )
        except _AtomicMfaRejected:
            return False
        return True

    async def _consume_challenge(
        self,
        connection,
        *,
        challenge_id: UUID,
        user_id: UUID,
        state: str,
        now: datetime,
    ) -> None:
        result = await connection.execute(
            _CONSUME_CHALLENGE,
            {
                "challenge_id": challenge_id,
                "user_id": user_id,
                "state": state,
                "now": now,
            },
        )
        if result.rowcount != 1:
            raise _AtomicMfaRejected()

    async def _finish_success(
        self,
        connection,
        *,
        challenge_id: UUID,
        user_id: UUID,
        action: str,
        session: SessionRecord,
        user_bucket_hash: bytes,
        now: datetime,
    ) -> None:
        await connection.execute(
            _INSERT_SESSION,
            {
                "user_id": user_id,
                "token_hash": session.token_hash,
                "csrf_token_hash": session.csrf_token_hash,
                "idle_expires_at": session.idle_expires_at,
                "absolute_expires_at": session.absolute_expires_at,
                "now": now,
            },
        )
        await connection.execute(
            _AUDIT_MFA_SUCCESS,
            {
                "challenge_id": challenge_id,
                "user_id": user_id,
                "action": action,
                "now": now,
            },
        )
        await connection.execute(
            _CLEAR_USER_MFA_RATE_LIMIT,
            {"user_bucket_hash": user_bucket_hash},
        )
