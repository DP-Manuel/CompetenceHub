from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from competence_hub_api.auth.login_repository import LoginAccount

RATE_LIMIT_WINDOW = timedelta(minutes=15)
RATE_LIMIT_THRESHOLD = 5
RATE_LIMIT_BASE_DELAY_SECONDS = 30
RATE_LIMIT_MAX_DELAY_SECONDS = 15 * 60

_FIND_LOGIN_ACCOUNT = text(
    """
    SELECT
        portal_user.id AS user_id,
        portal_user.active,
        credential.password_hash,
        COALESCE(
            array_agg(DISTINCT role.code ORDER BY role.code)
                FILTER (WHERE role.active),
            ARRAY[]::text[]
        ) AS roles,
        EXISTS (
            SELECT 1
            FROM competence_hub.auth_totp_credentials AS totp
            WHERE totp.portal_user_id = portal_user.id
              AND totp.enabled_at IS NOT NULL
        ) AS mfa_enrolled
    FROM competence_hub.portal_users AS portal_user
    LEFT JOIN competence_hub.auth_password_credentials AS credential
      ON credential.portal_user_id = portal_user.id
    LEFT JOIN competence_hub.user_roles AS user_role
      ON user_role.user_id = portal_user.id
    LEFT JOIN competence_hub.roles AS role
      ON role.id = user_role.role_id
    WHERE lower(portal_user.email) = :normalized_email
    GROUP BY
        portal_user.id,
        portal_user.active,
        credential.password_hash
    """
)

_FIND_LOGIN_RATE_LIMIT = text(
    """
    SELECT max(blocked_until) AS blocked_until
    FROM competence_hub.auth_rate_limit_buckets
    WHERE action = 'login'
      AND bucket_key_hash IN (:account_bucket_hash, :ip_bucket_hash)
      AND blocked_until > :now
    """
)

_RECORD_LOGIN_FAILURE = text(
    """
    INSERT INTO competence_hub.auth_rate_limit_buckets (
        action,
        bucket_key_hash,
        window_started_at,
        failed_attempts,
        blocked_until
    ) VALUES (
        'login',
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

_AUDIT_LOGIN_FAILURE = text(
    """
    INSERT INTO competence_hub.audit_events (
        actor_user_id,
        occurred_at,
        action,
        entity_type,
        entity_id,
        outcome
    ) VALUES (
        NULL,
        :now,
        'auth.login.first_factor',
        'portal_user',
        :user_id,
        'failure'
    )
    """
)

_CREATE_LOGIN_CHALLENGE = text(
    """
    WITH revoked_challenges AS (
        UPDATE competence_hub.auth_login_challenges
        SET revoked_at = :now
        WHERE portal_user_id = :user_id
          AND consumed_at IS NULL
          AND revoked_at IS NULL
    ),
    created_challenge AS (
        INSERT INTO competence_hub.auth_login_challenges (
            portal_user_id,
            token_hash,
            csrf_token_hash,
            state,
            created_at,
            expires_at
        ) VALUES (
            :user_id,
            :token_hash,
            :csrf_token_hash,
            :state,
            :now,
            :expires_at
        )
        RETURNING id
    )
    INSERT INTO competence_hub.audit_events (
        actor_user_id,
        occurred_at,
        action,
        entity_type,
        entity_id,
        outcome
    )
    SELECT
        :user_id,
        :now,
        'auth.login.first_factor',
        'auth_login_challenge',
        id,
        'success'
    FROM created_challenge
    """
)

_CLEAR_ACCOUNT_RATE_LIMIT = text(
    """
    DELETE FROM competence_hub.auth_rate_limit_buckets
    WHERE action = 'login'
      AND bucket_key_hash = :account_bucket_hash
    """
)


class PostgresLoginRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def find_login_account(self, normalized_email: str) -> LoginAccount | None:
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _FIND_LOGIN_ACCOUNT,
                {"normalized_email": normalized_email},
            )
            row = result.mappings().one_or_none()

        if row is None:
            return None

        return LoginAccount(
            user_id=row["user_id"],
            password_hash=row["password_hash"],
            active=row["active"],
            roles=tuple(row["roles"]),
            mfa_enrolled=row["mfa_enrolled"],
        )

    async def find_login_rate_limit(
        self,
        account_bucket_hash: bytes,
        ip_bucket_hash: bytes,
        *,
        now: datetime,
    ) -> datetime | None:
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _FIND_LOGIN_RATE_LIMIT,
                {
                    "account_bucket_hash": account_bucket_hash,
                    "ip_bucket_hash": ip_bucket_hash,
                    "now": now,
                },
            )
            return result.scalar_one_or_none()

    async def record_failed_login(
        self,
        account_bucket_hash: bytes,
        ip_bucket_hash: bytes,
        *,
        user_id: UUID | None,
        now: datetime,
    ) -> datetime | None:
        blocked_until_values: list[datetime] = []
        parameters = {
            "now": now,
            "window_cutoff": now - RATE_LIMIT_WINDOW,
            "threshold": RATE_LIMIT_THRESHOLD,
            "base_delay_seconds": RATE_LIMIT_BASE_DELAY_SECONDS,
            "max_delay_seconds": RATE_LIMIT_MAX_DELAY_SECONDS,
        }
        bucket_hashes = sorted({account_bucket_hash, ip_bucket_hash})

        async with self._engine.begin() as connection:
            for bucket_hash in bucket_hashes:
                result = await connection.execute(
                    _RECORD_LOGIN_FAILURE,
                    {**parameters, "bucket_key_hash": bucket_hash},
                )
                blocked_until = result.scalar_one_or_none()
                if blocked_until is not None:
                    blocked_until_values.append(blocked_until)

            await connection.execute(
                _AUDIT_LOGIN_FAILURE,
                {"user_id": user_id, "now": now},
            )

        return max(blocked_until_values, default=None)

    async def create_login_challenge(
        self,
        *,
        user_id: UUID,
        token_hash: bytes,
        csrf_token_hash: bytes,
        state: str,
        account_bucket_hash: bytes,
        now: datetime,
        expires_at: datetime,
    ) -> None:
        if state not in {"mfa_required", "mfa_enrollment_required"}:
            raise ValueError("invalid login challenge state")
        if expires_at <= now:
            raise ValueError("login challenge expiry must be in the future")

        async with self._engine.begin() as connection:
            await connection.execute(
                _CREATE_LOGIN_CHALLENGE,
                {
                    "user_id": user_id,
                    "token_hash": token_hash,
                    "csrf_token_hash": csrf_token_hash,
                    "state": state,
                    "now": now,
                    "expires_at": expires_at,
                },
            )
            await connection.execute(
                _CLEAR_ACCOUNT_RATE_LIMIT,
                {"account_bucket_hash": account_bucket_hash},
            )
