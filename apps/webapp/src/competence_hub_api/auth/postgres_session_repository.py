from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from competence_hub_api.auth.session_repository import SessionPrincipal

_GET_ACTIVE_SESSION = text(
    """
    WITH refreshed_session AS (
        UPDATE competence_hub.auth_sessions AS session
        SET
            last_seen_at = :now,
            idle_expires_at = LEAST(
                session.absolute_expires_at,
                :now + make_interval(
                    secs => CAST(:idle_timeout_seconds AS double precision)
                )
            )
        FROM competence_hub.portal_users AS portal_user
        WHERE session.portal_user_id = portal_user.id
          AND session.token_hash = :token_hash
          AND session.authentication_level = 'mfa'
          AND session.revoked_at IS NULL
          AND session.idle_expires_at > :now
          AND session.absolute_expires_at > :now
          AND portal_user.active
          AND EXISTS (
              SELECT 1
              FROM competence_hub.user_roles AS user_role
              JOIN competence_hub.roles AS role
                ON role.id = user_role.role_id
              WHERE user_role.user_id = portal_user.id
                AND role.active
                AND role.code IN ('admin', 'internal')
          )
        RETURNING
            session.id,
            session.portal_user_id,
            session.authenticated_at,
            session.idle_expires_at,
            session.absolute_expires_at,
            session.csrf_token_hash
    )
    SELECT
        refreshed_session.id AS session_id,
        refreshed_session.portal_user_id AS user_id,
        portal_user.display_name,
        refreshed_session.authenticated_at,
        refreshed_session.idle_expires_at,
        refreshed_session.absolute_expires_at,
        refreshed_session.csrf_token_hash,
        array_agg(role.code ORDER BY role.code) AS roles
    FROM refreshed_session
    JOIN competence_hub.portal_users AS portal_user
      ON portal_user.id = refreshed_session.portal_user_id
    JOIN competence_hub.user_roles AS user_role
      ON user_role.user_id = refreshed_session.portal_user_id
    JOIN competence_hub.roles AS role
      ON role.id = user_role.role_id
     AND role.active
     AND role.code IN ('admin', 'internal')
    GROUP BY
        refreshed_session.id,
        refreshed_session.portal_user_id,
        portal_user.display_name,
        refreshed_session.authenticated_at,
        refreshed_session.idle_expires_at,
        refreshed_session.absolute_expires_at,
        refreshed_session.csrf_token_hash
    """
)

_FIND_ACTIVE_SESSION = text(
    """
    SELECT
        session.id AS session_id,
        session.portal_user_id AS user_id,
        portal_user.display_name,
        session.authenticated_at,
        session.idle_expires_at,
        session.absolute_expires_at,
        session.csrf_token_hash,
        array_agg(role.code ORDER BY role.code) AS roles
    FROM competence_hub.auth_sessions AS session
    JOIN competence_hub.portal_users AS portal_user
      ON portal_user.id = session.portal_user_id
     AND portal_user.active
    JOIN competence_hub.user_roles AS user_role
      ON user_role.user_id = portal_user.id
    JOIN competence_hub.roles AS role
      ON role.id = user_role.role_id
     AND role.active
     AND role.code IN ('admin', 'internal')
    WHERE session.token_hash = :token_hash
      AND session.authentication_level = 'mfa'
      AND session.revoked_at IS NULL
      AND session.idle_expires_at > :now
      AND session.absolute_expires_at > :now
    GROUP BY
        session.id,
        session.portal_user_id,
        portal_user.display_name,
        session.authenticated_at,
        session.idle_expires_at,
        session.absolute_expires_at,
        session.csrf_token_hash
    """
)

_REVOKE_SESSION = text(
    """
    WITH revoked_session AS (
        UPDATE competence_hub.auth_sessions
        SET revoked_at = :now, revoke_reason = :reason
        WHERE token_hash = :token_hash
          AND revoked_at IS NULL
        RETURNING id, portal_user_id
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
        portal_user_id,
        :now,
        'auth.session.logout',
        'auth_session',
        id,
        'success'
    FROM revoked_session
    """
)


class PostgresSessionRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def refresh_active_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
        idle_timeout: timedelta,
    ) -> SessionPrincipal | None:
        idle_timeout_seconds = int(idle_timeout.total_seconds())
        if idle_timeout_seconds <= 0:
            raise ValueError("idle timeout must be positive")

        async with self._engine.begin() as connection:
            result = await connection.execute(
                _GET_ACTIVE_SESSION,
                {
                    "token_hash": token_hash,
                    "now": now,
                    "idle_timeout_seconds": idle_timeout_seconds,
                },
            )
            row = result.mappings().one_or_none()

        if row is None:
            return None

        return SessionPrincipal(
            session_id=row["session_id"],
            user_id=row["user_id"],
            display_name=row["display_name"],
            roles=tuple(row["roles"]),
            authenticated_at=row["authenticated_at"],
            idle_expires_at=row["idle_expires_at"],
            absolute_expires_at=row["absolute_expires_at"],
            csrf_token_hash=bytes(row["csrf_token_hash"]),
        )

    async def find_active_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
    ) -> SessionPrincipal | None:
        async with self._engine.connect() as connection:
            result = await connection.execute(
                _FIND_ACTIVE_SESSION,
                {"token_hash": token_hash, "now": now},
            )
            row = result.mappings().one_or_none()

        if row is None:
            return None

        return SessionPrincipal(
            session_id=row["session_id"],
            user_id=row["user_id"],
            display_name=row["display_name"],
            roles=tuple(row["roles"]),
            authenticated_at=row["authenticated_at"],
            idle_expires_at=row["idle_expires_at"],
            absolute_expires_at=row["absolute_expires_at"],
            csrf_token_hash=bytes(row["csrf_token_hash"]),
        )

    async def revoke_session(
        self,
        token_hash: bytes,
        *,
        now: datetime,
        reason: str,
    ) -> None:
        if not reason.strip():
            raise ValueError("revocation reason must not be empty")

        async with self._engine.begin() as connection:
            await connection.execute(
                _REVOKE_SESSION,
                {"token_hash": token_hash, "now": now, "reason": reason},
            )
