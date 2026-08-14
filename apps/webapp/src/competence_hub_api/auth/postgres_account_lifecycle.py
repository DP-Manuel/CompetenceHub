from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from competence_hub_api.auth.account_lifecycle import (
    AccountLifecycleConfigurationError,
    IdempotencyConflictError,
    InvitationIssueResult,
    InvitationConflictError,
)

RATE_LIMIT_WINDOW = timedelta(minutes=15)
RATE_LIMIT_THRESHOLD = 5
RATE_LIMIT_BASE_DELAY_SECONDS = 30
RATE_LIMIT_MAX_DELAY_SECONDS = 15 * 60
_ALLOWED_ACTIONS = frozenset({"invitation", "password_reset"})

_FIND_RATE_LIMIT = text(
    """
    SELECT max(blocked_until) AS blocked_until
    FROM competence_hub.auth_rate_limit_buckets
    WHERE action = :action
      AND bucket_key_hash = ANY(:bucket_hashes)
      AND blocked_until > :now
    """
)

_RECORD_RATE_LIMIT_ATTEMPT = text(
    """
    INSERT INTO competence_hub.auth_rate_limit_buckets (
        action,
        bucket_key_hash,
        window_started_at,
        failed_attempts,
        blocked_until
    ) VALUES (
        :action,
        :bucket_hash,
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

_LOCK_EMAIL = text(
    "SELECT pg_advisory_xact_lock(hashtextextended(:normalized_email, 0))"
)

_LOCK_IDEMPOTENCY = text(
    "SELECT pg_advisory_xact_lock(hashtextextended(:lock_key, 0))"
)

_DELETE_EXPIRED_IDEMPOTENCY = text(
    """
    DELETE FROM competence_hub.auth_idempotency_records
    WHERE actor_user_id = :actor_user_id
      AND scope = 'auth.invitation.issue'
      AND key_hash = :key_hash
      AND expires_at <= :now
    """
)

_FIND_IDEMPOTENCY = text(
    """
    SELECT request_fingerprint, result_entity_id
    FROM competence_hub.auth_idempotency_records
    WHERE actor_user_id = :actor_user_id
      AND scope = 'auth.invitation.issue'
      AND key_hash = :key_hash
      AND expires_at > :now
    FOR UPDATE
    """
)

_LOOKUP_IDEMPOTENCY = text(
    """
    SELECT request_fingerprint, result_entity_id
    FROM competence_hub.auth_idempotency_records
    WHERE actor_user_id = :actor_user_id
      AND scope = 'auth.invitation.issue'
      AND key_hash = :key_hash
      AND expires_at > :now
    """
)

_CREATE_IDEMPOTENCY = text(
    """
    INSERT INTO competence_hub.auth_idempotency_records (
        actor_user_id,
        scope,
        key_hash,
        request_fingerprint,
        result_entity_type,
        result_entity_id,
        created_at,
        expires_at
    ) VALUES (
        :actor_user_id,
        'auth.invitation.issue',
        :key_hash,
        :request_fingerprint,
        'portal_user',
        :result_entity_id,
        :now,
        :expires_at
    )
    """
)

_FIND_INVITEE = text(
    """
    SELECT
        portal_user.id,
        portal_user.active,
        EXISTS (
            SELECT 1
            FROM competence_hub.auth_password_credentials AS credential
            WHERE credential.portal_user_id = portal_user.id
        ) AS has_credential
    FROM competence_hub.portal_users AS portal_user
    WHERE lower(portal_user.email) = :normalized_email
    FOR UPDATE OF portal_user
    """
)

_CREATE_INACTIVE_USER = text(
    """
    INSERT INTO competence_hub.portal_users (
        display_name,
        email,
        active,
        created_at,
        updated_at
    ) VALUES (
        :display_name,
        :normalized_email,
        false,
        :now,
        :now
    )
    RETURNING id
    """
)

_UPDATE_INACTIVE_USER = text(
    """
    UPDATE competence_hub.portal_users
    SET display_name = :display_name,
        updated_at = :now
    WHERE id = :user_id
      AND NOT active
    """
)

_FIND_ROLES = text(
    """
    SELECT id, code
    FROM competence_hub.roles
    WHERE code = ANY(:role_codes)
      AND active
    """
)

_ASSIGN_ROLE = text(
    """
    INSERT INTO competence_hub.user_roles (
        user_id,
        role_id,
        assigned_at,
        assigned_by_user_id
    ) VALUES (
        :user_id,
        :role_id,
        :now,
        :actor_user_id
    )
    ON CONFLICT (user_id, role_id) DO NOTHING
    """
)

_REVOKE_OPEN_TOKENS = text(
    """
    WITH revoked_tokens AS (
        UPDATE competence_hub.auth_one_time_tokens
        SET revoked_at = :now
        WHERE portal_user_id = :user_id
          AND purpose = :purpose
          AND consumed_at IS NULL
          AND revoked_at IS NULL
        RETURNING id
    )
    UPDATE competence_hub.auth_token_delivery_outbox
    SET status = 'canceled',
        recipient_email = NULL,
        encrypted_payload = NULL,
        key_version = NULL,
        claimed_at = NULL,
        claim_id = NULL,
        lease_expires_at = NULL,
        completed_at = :now,
        last_error_code = 'token_revoked'
    WHERE one_time_token_id IN (SELECT id FROM revoked_tokens)
      AND status IN ('pending', 'processing')
    """
)

_CREATE_ONE_TIME_TOKEN = text(
    """
    INSERT INTO competence_hub.auth_one_time_tokens (
        portal_user_id,
        purpose,
        token_hash,
        created_by_user_id,
        created_at,
        expires_at
    ) VALUES (
        :user_id,
        :purpose,
        :token_hash,
        :actor_user_id,
        :now,
        :expires_at
    )
    RETURNING id
    """
)

_CREATE_OUTBOX = text(
    """
    INSERT INTO competence_hub.auth_token_delivery_outbox (
        id,
        one_time_token_id,
        purpose,
        template_code,
        recipient_email,
        encrypted_payload,
        key_version,
        available_at,
        created_at,
        expires_at,
        updated_at
    ) VALUES (
        :outbox_id,
        :one_time_token_id,
        :purpose,
        :template_code,
        :recipient_email,
        :encrypted_payload,
        :key_version,
        :now,
        :now,
        :expires_at,
        :now
    )
    """
)

_FIND_RESET_USER = text(
    """
    SELECT portal_user.id
    FROM competence_hub.portal_users AS portal_user
    JOIN competence_hub.auth_password_credentials AS credential
      ON credential.portal_user_id = portal_user.id
    WHERE lower(portal_user.email) = :normalized_email
      AND portal_user.active
      AND EXISTS (
          SELECT 1
          FROM competence_hub.user_roles AS user_role
          JOIN competence_hub.roles AS role ON role.id = user_role.role_id
          WHERE user_role.user_id = portal_user.id
            AND role.active
            AND role.code IN ('admin', 'internal')
      )
    FOR UPDATE OF portal_user
    """
)

_FIND_VALID_TOKEN = text(
    """
    SELECT token.portal_user_id
    FROM competence_hub.auth_one_time_tokens AS token
    JOIN competence_hub.portal_users AS portal_user
      ON portal_user.id = token.portal_user_id
    WHERE token.token_hash = :token_hash
      AND token.purpose = :purpose
      AND token.consumed_at IS NULL
      AND token.revoked_at IS NULL
      AND token.expires_at > :now
      AND (
          :purpose = 'invitation'
          OR (
              portal_user.active
              AND EXISTS (
                  SELECT 1
                  FROM competence_hub.user_roles AS user_role
                  JOIN competence_hub.roles AS role
                    ON role.id = user_role.role_id
                  WHERE user_role.user_id = portal_user.id
                    AND role.active
                    AND role.code IN ('admin', 'internal')
              )
          )
      )
    FOR UPDATE OF token, portal_user
    """
)

_UPSERT_PASSWORD = text(
    """
    INSERT INTO competence_hub.auth_password_credentials (
        portal_user_id,
        password_hash,
        password_changed_at,
        created_at,
        updated_at
    ) VALUES (
        :user_id,
        :password_hash,
        :now,
        :now,
        :now
    )
    ON CONFLICT (portal_user_id) DO UPDATE
    SET password_hash = EXCLUDED.password_hash,
        password_changed_at = EXCLUDED.password_changed_at,
        updated_at = EXCLUDED.updated_at
    """
)

_ACTIVATE_USER = text(
    """
    UPDATE competence_hub.portal_users
    SET active = true,
        updated_at = :now
    WHERE id = :user_id
    """
)

_CONSUME_TOKEN = text(
    """
    UPDATE competence_hub.auth_one_time_tokens
    SET consumed_at = :now
    WHERE token_hash = :token_hash
      AND consumed_at IS NULL
      AND revoked_at IS NULL
    """
)

_REVOKE_CHALLENGES = text(
    """
    UPDATE competence_hub.auth_login_challenges
    SET revoked_at = :now
    WHERE portal_user_id = :user_id
      AND consumed_at IS NULL
      AND revoked_at IS NULL
    """
)

_CREATE_ENROLLMENT_CHALLENGE = text(
    """
    INSERT INTO competence_hub.auth_login_challenges (
        portal_user_id,
        token_hash,
        csrf_token_hash,
        state,
        created_at,
        expires_at
    ) VALUES (
        :user_id,
        :login_token_hash,
        :csrf_token_hash,
        'mfa_enrollment_required',
        :now,
        :expires_at
    )
    """
)

_REVOKE_SESSIONS = text(
    """
    UPDATE competence_hub.auth_sessions
    SET revoked_at = :now,
        revoke_reason = :reason
    WHERE portal_user_id = :user_id
      AND revoked_at IS NULL
    """
)

_AUDIT = text(
    """
    INSERT INTO competence_hub.audit_events (
        actor_user_id,
        occurred_at,
        action,
        entity_type,
        entity_id,
        outcome
    ) VALUES (
        :actor_user_id,
        :now,
        :action,
        'portal_user',
        :user_id,
        :outcome
    )
    """
)


class PostgresAccountLifecycleRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def find_invitation_idempotency(
        self,
        *,
        actor_user_id: UUID,
        idempotency_key_hash: bytes,
        request_fingerprint: bytes,
        now: datetime,
    ) -> InvitationIssueResult | None:
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _LOOKUP_IDEMPOTENCY,
                {
                    "actor_user_id": actor_user_id,
                    "key_hash": idempotency_key_hash,
                    "now": now,
                },
            )
            existing = result.mappings().one_or_none()
        if existing is None:
            return None
        if bytes(existing["request_fingerprint"]) != bytes(request_fingerprint):
            raise IdempotencyConflictError(
                "idempotency key was already used for another request"
            )
        return InvitationIssueResult(
            user_id=existing["result_entity_id"],
            replayed=True,
        )

    async def find_rate_limit(
        self,
        action: str,
        bucket_hashes: tuple[bytes, ...],
        *,
        now: datetime,
    ) -> datetime | None:
        _validate_action(action)
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _FIND_RATE_LIMIT,
                {"action": action, "bucket_hashes": list(bucket_hashes), "now": now},
            )
            return result.scalar_one_or_none()

    async def record_rate_limit_attempt(
        self,
        action: str,
        bucket_hashes: tuple[bytes, ...],
        *,
        now: datetime,
    ) -> datetime | None:
        _validate_action(action)
        blocked: list[datetime] = []
        parameters = {
            "action": action,
            "now": now,
            "window_cutoff": now - RATE_LIMIT_WINDOW,
            "threshold": RATE_LIMIT_THRESHOLD,
            "base_delay_seconds": RATE_LIMIT_BASE_DELAY_SECONDS,
            "max_delay_seconds": RATE_LIMIT_MAX_DELAY_SECONDS,
        }
        async with self._engine.begin() as connection:
            for bucket_hash in sorted(set(bucket_hashes)):
                result = await connection.execute(
                    _RECORD_RATE_LIMIT_ATTEMPT,
                    {**parameters, "bucket_hash": bucket_hash},
                )
                blocked_until = result.scalar_one_or_none()
                if blocked_until is not None:
                    blocked.append(blocked_until)
        return max(blocked, default=None)

    async def issue_invitation(
        self,
        *,
        actor_user_id: UUID,
        normalized_email: str,
        display_name: str,
        role_codes: tuple[str, ...],
        token_hash: bytes,
        outbox_id: UUID,
        encrypted_payload: bytes,
        payload_key_version: str,
        idempotency_key_hash: bytes,
        request_fingerprint: bytes,
        now: datetime,
        expires_at: datetime,
        idempotency_expires_at: datetime,
    ) -> InvitationIssueResult:
        async with self._engine.begin() as connection:
            idempotency_parameters = {
                "actor_user_id": actor_user_id,
                "key_hash": idempotency_key_hash,
                "now": now,
            }
            await connection.execute(
                _LOCK_IDEMPOTENCY,
                {
                    "lock_key": (
                        f"{actor_user_id}:auth.invitation.issue:"
                        f"{idempotency_key_hash.hex()}"
                    )
                },
            )
            await connection.execute(
                _DELETE_EXPIRED_IDEMPOTENCY,
                idempotency_parameters,
            )
            idempotency_result = await connection.execute(
                _FIND_IDEMPOTENCY,
                idempotency_parameters,
            )
            existing_idempotency = idempotency_result.mappings().one_or_none()
            if existing_idempotency is not None:
                if bytes(existing_idempotency["request_fingerprint"]) != bytes(
                    request_fingerprint
                ):
                    raise IdempotencyConflictError(
                        "idempotency key was already used for another request"
                    )
                return InvitationIssueResult(
                    user_id=existing_idempotency["result_entity_id"],
                    replayed=True,
                )

            await connection.execute(
                _LOCK_EMAIL,
                {"normalized_email": normalized_email},
            )
            existing_result = await connection.execute(
                _FIND_INVITEE,
                {"normalized_email": normalized_email},
            )
            existing = existing_result.mappings().one_or_none()
            if existing is not None and (
                existing["active"] or existing["has_credential"]
            ):
                raise InvitationConflictError("account already provisioned")
            if existing is None:
                created = await connection.execute(
                    _CREATE_INACTIVE_USER,
                    {
                        "normalized_email": normalized_email,
                        "display_name": display_name,
                        "now": now,
                    },
                )
                user_id = created.scalar_one()
            else:
                user_id = existing["id"]
                await connection.execute(
                    _UPDATE_INACTIVE_USER,
                    {"user_id": user_id, "display_name": display_name, "now": now},
                )

            roles_result = await connection.execute(
                _FIND_ROLES,
                {"role_codes": list(role_codes)},
            )
            roles = roles_result.mappings().all()
            if {row["code"] for row in roles} != set(role_codes):
                raise AccountLifecycleConfigurationError(
                    "requested invitation role is unavailable"
                )
            for role in roles:
                await connection.execute(
                    _ASSIGN_ROLE,
                    {
                        "user_id": user_id,
                        "role_id": role["id"],
                        "actor_user_id": actor_user_id,
                        "now": now,
                    },
                )
            await connection.execute(
                _REVOKE_OPEN_TOKENS,
                {"user_id": user_id, "purpose": "invitation", "now": now},
            )
            token_result = await connection.execute(
                _CREATE_ONE_TIME_TOKEN,
                {
                    "user_id": user_id,
                    "purpose": "invitation",
                    "token_hash": token_hash,
                    "actor_user_id": actor_user_id,
                    "now": now,
                    "expires_at": expires_at,
                },
            )
            one_time_token_id = token_result.scalar_one()
            await connection.execute(
                _CREATE_OUTBOX,
                {
                    "outbox_id": outbox_id,
                    "one_time_token_id": one_time_token_id,
                    "purpose": "invitation",
                    "template_code": "auth_invitation_v1",
                    "recipient_email": normalized_email,
                    "encrypted_payload": encrypted_payload,
                    "key_version": payload_key_version,
                    "now": now,
                    "expires_at": expires_at,
                },
            )
            await connection.execute(
                _AUDIT,
                {
                    "actor_user_id": actor_user_id,
                    "now": now,
                    "action": "auth.invitation.issue",
                    "user_id": user_id,
                    "outcome": "success",
                },
            )
            await connection.execute(
                _CREATE_IDEMPOTENCY,
                {
                    "actor_user_id": actor_user_id,
                    "key_hash": idempotency_key_hash,
                    "request_fingerprint": request_fingerprint,
                    "result_entity_id": user_id,
                    "now": now,
                    "expires_at": idempotency_expires_at,
                },
            )
            return InvitationIssueResult(user_id=user_id, replayed=False)

    async def request_password_reset(
        self,
        *,
        normalized_email: str,
        token_hash: bytes,
        outbox_id: UUID,
        encrypted_payload: bytes,
        payload_key_version: str,
        now: datetime,
        expires_at: datetime,
    ) -> UUID | None:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _FIND_RESET_USER,
                {"normalized_email": normalized_email},
            )
            user_id = result.scalar_one_or_none()
            if user_id is not None:
                await connection.execute(
                    _REVOKE_OPEN_TOKENS,
                    {"user_id": user_id, "purpose": "password_reset", "now": now},
                )
                token_result = await connection.execute(
                    _CREATE_ONE_TIME_TOKEN,
                    {
                        "user_id": user_id,
                        "purpose": "password_reset",
                        "token_hash": token_hash,
                        "actor_user_id": None,
                        "now": now,
                        "expires_at": expires_at,
                    },
                )
                one_time_token_id = token_result.scalar_one()
                await connection.execute(
                    _CREATE_OUTBOX,
                    {
                        "outbox_id": outbox_id,
                        "one_time_token_id": one_time_token_id,
                        "purpose": "password_reset",
                        "template_code": "auth_password_reset_v1",
                        "recipient_email": normalized_email,
                        "encrypted_payload": encrypted_payload,
                        "key_version": payload_key_version,
                        "now": now,
                        "expires_at": expires_at,
                    },
                )
            await connection.execute(
                _AUDIT,
                {
                    "actor_user_id": None,
                    "now": now,
                    "action": "auth.password_reset.request",
                    "user_id": user_id,
                    "outcome": "accepted",
                },
            )
            return user_id

    async def accept_invitation(
        self,
        *,
        token_hash: bytes,
        password_hash: str,
        login_token_hash: bytes,
        csrf_token_hash: bytes,
        now: datetime,
        challenge_expires_at: datetime,
    ) -> UUID | None:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _FIND_VALID_TOKEN,
                {"token_hash": token_hash, "purpose": "invitation", "now": now},
            )
            user_id = result.scalar_one_or_none()
            if user_id is None:
                return None
            await connection.execute(
                _UPSERT_PASSWORD,
                {"user_id": user_id, "password_hash": password_hash, "now": now},
            )
            await connection.execute(
                _ACTIVATE_USER,
                {"user_id": user_id, "now": now},
            )
            await connection.execute(
                _CONSUME_TOKEN,
                {"token_hash": token_hash, "now": now},
            )
            await connection.execute(
                _REVOKE_OPEN_TOKENS,
                {"user_id": user_id, "purpose": "invitation", "now": now},
            )
            await connection.execute(
                _REVOKE_CHALLENGES,
                {"user_id": user_id, "now": now},
            )
            await connection.execute(
                _CREATE_ENROLLMENT_CHALLENGE,
                {
                    "user_id": user_id,
                    "login_token_hash": login_token_hash,
                    "csrf_token_hash": csrf_token_hash,
                    "now": now,
                    "expires_at": challenge_expires_at,
                },
            )
            await connection.execute(
                _AUDIT,
                {
                    "actor_user_id": user_id,
                    "now": now,
                    "action": "auth.invitation.accept",
                    "user_id": user_id,
                    "outcome": "success",
                },
            )
            return user_id

    async def confirm_password_reset(
        self,
        *,
        token_hash: bytes,
        password_hash: str,
        now: datetime,
    ) -> UUID | None:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                _FIND_VALID_TOKEN,
                {"token_hash": token_hash, "purpose": "password_reset", "now": now},
            )
            user_id = result.scalar_one_or_none()
            if user_id is None:
                return None
            await connection.execute(
                _UPSERT_PASSWORD,
                {"user_id": user_id, "password_hash": password_hash, "now": now},
            )
            await connection.execute(
                _CONSUME_TOKEN,
                {"token_hash": token_hash, "now": now},
            )
            await connection.execute(
                _REVOKE_OPEN_TOKENS,
                {"user_id": user_id, "purpose": "password_reset", "now": now},
            )
            await connection.execute(
                _REVOKE_SESSIONS,
                {"user_id": user_id, "now": now, "reason": "password_reset"},
            )
            await connection.execute(
                _REVOKE_CHALLENGES,
                {"user_id": user_id, "now": now},
            )
            await connection.execute(
                _AUDIT,
                {
                    "actor_user_id": user_id,
                    "now": now,
                    "action": "auth.password_reset.confirm",
                    "user_id": user_id,
                    "outcome": "success",
                },
            )
            return user_id


def _validate_action(action: str) -> None:
    if action not in _ALLOWED_ACTIONS:
        raise ValueError("invalid account lifecycle rate-limit action")
