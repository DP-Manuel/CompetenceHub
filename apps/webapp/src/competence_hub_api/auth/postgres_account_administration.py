from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from competence_hub_api.auth.account_administration import (
    InitialAdminAlreadyExistsError,
    InitialAdminConfigurationError,
)

_LOCK_INITIAL_ADMIN = text(
    "SELECT pg_advisory_xact_lock(hashtext('competence_hub.initial_admin'))"
)

_LOCK_EMPTY_TARGET = text(
    "LOCK TABLE competence_hub.portal_users, competence_hub.user_roles, "
    "competence_hub.coaches IN SHARE ROW EXCLUSIVE MODE"
)

_TARGET_IS_EMPTY = text(
    "SELECT NOT EXISTS (SELECT 1 FROM competence_hub.portal_users) "
    "AND NOT EXISTS (SELECT 1 FROM competence_hub.coaches)"
)

_BOOTSTRAP_WITHIN_DEADLINE = text("SELECT clock_timestamp() <= :bootstrap_deadline")

_ACTIVE_ADMIN_EXISTS = text("""
    SELECT EXISTS (
        SELECT 1
        FROM competence_hub.portal_users AS portal_user
        JOIN competence_hub.user_roles AS user_role
          ON user_role.user_id = portal_user.id
        JOIN competence_hub.roles AS role
          ON role.id = user_role.role_id
        WHERE portal_user.active
          AND role.active
          AND role.code = 'admin'
    )
    """)

_FIND_ADMIN_ROLE = text("""
    SELECT id
    FROM competence_hub.roles
    WHERE code = 'admin'
      AND active
    """)

_CREATE_USER = text("""
    INSERT INTO competence_hub.portal_users (
        display_name,
        email,
        active,
        created_at,
        updated_at
    ) VALUES (
        :display_name,
        :normalized_email,
        true,
        :now,
        :now
    )
    RETURNING id
    """)

_ASSIGN_ADMIN_ROLE = text("""
    INSERT INTO competence_hub.user_roles (
        user_id,
        role_id,
        assigned_at,
        assigned_by_user_id
    ) VALUES (
        :user_id,
        :role_id,
        :now,
        NULL
    )
    """)

_CREATE_PASSWORD_CREDENTIAL = text("""
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
    """)

_AUDIT_INITIAL_ADMIN = text("""
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
        'auth.initial_admin.create',
        'portal_user',
        :user_id,
        'success'
    )
    """)


class PostgresInitialAdminRepository:
    def __init__(
        self,
        engine: AsyncEngine,
        *,
        require_empty_target: bool = False,
        bootstrap_deadline: datetime | None = None,
    ) -> None:
        if bootstrap_deadline is not None and (
            not isinstance(bootstrap_deadline, datetime)
            or bootstrap_deadline.tzinfo is None
            or bootstrap_deadline.utcoffset() is None
        ):
            raise InitialAdminConfigurationError(
                "bootstrap deadline must be timezone-aware"
            )
        self._engine = engine
        self._require_empty_target = require_empty_target
        self._bootstrap_deadline = bootstrap_deadline

    async def create_initial_admin(
        self,
        *,
        normalized_email: str,
        display_name: str,
        password_hash: str,
        now: datetime,
    ) -> UUID:
        async with self._engine.begin() as connection:
            await connection.execute(_LOCK_INITIAL_ADMIN)
            if self._require_empty_target:
                await connection.execute(_LOCK_EMPTY_TARGET)
                empty = await connection.execute(_TARGET_IS_EMPTY)
                if not empty.scalar_one():
                    raise InitialAdminConfigurationError(
                        "bootstrap requires an empty target"
                    )
            if self._bootstrap_deadline is not None:
                fresh = await connection.execute(
                    _BOOTSTRAP_WITHIN_DEADLINE,
                    {"bootstrap_deadline": self._bootstrap_deadline},
                )
                if not fresh.scalar_one():
                    raise InitialAdminConfigurationError(
                        "bootstrap deadline has expired"
                    )
            existing_admin = await connection.execute(_ACTIVE_ADMIN_EXISTS)
            if existing_admin.scalar_one():
                raise InitialAdminAlreadyExistsError(
                    "an active initial administrator already exists"
                )

            # roles is read-only for the app; the advisory lock serializes bootstrap.
            role_result = await connection.execute(_FIND_ADMIN_ROLE)
            role_id = role_result.scalar_one_or_none()
            if role_id is None:
                raise InitialAdminConfigurationError(
                    "the active admin role is unavailable"
                )

            user_result = await connection.execute(
                _CREATE_USER,
                {
                    "normalized_email": normalized_email,
                    "display_name": display_name,
                    "now": now,
                },
            )
            user_id = user_result.scalar_one()
            await connection.execute(
                _ASSIGN_ADMIN_ROLE,
                {"user_id": user_id, "role_id": role_id, "now": now},
            )
            await connection.execute(
                _CREATE_PASSWORD_CREDENTIAL,
                {"user_id": user_id, "password_hash": password_hash, "now": now},
            )
            await connection.execute(
                _AUDIT_INITIAL_ADMIN,
                {"user_id": user_id, "now": now},
            )
            return user_id
