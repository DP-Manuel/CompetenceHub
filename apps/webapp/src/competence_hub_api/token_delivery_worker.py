import asyncio
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import create_async_engine

from competence_hub_api.auth.postgres_token_delivery import (
    PostgresTokenDeliveryOutboxRepository,
)
from competence_hub_api.auth.smtp_token_delivery import SmtpTokenMessageAdapter
from competence_hub_api.auth.token_delivery import TokenDeliveryWorker
from competence_hub_api.config import TokenDeliverySettings
from competence_hub_api.security.secret_encryption import SecretCipher


async def run_once(settings: TokenDeliverySettings) -> bool:
    engine = create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
        hide_parameters=True,
    )
    try:
        cipher = SecretCipher(
            settings.outbox_encryption_keys,
            settings.outbox_active_key_version,
            context="auth-token-outbox",
        )
        adapter = SmtpTokenMessageAdapter(
            host=settings.smtp_host,
            port=settings.smtp_port,
            tls_mode=settings.smtp_tls_mode,  # type: ignore[arg-type]
            username=settings.smtp_username,
            password=settings.smtp_password,
            sender=settings.smtp_from,
            reply_to=settings.smtp_reply_to,
            account_action_base_url=settings.account_action_base_url,
        )
        worker = TokenDeliveryWorker(
            PostgresTokenDeliveryOutboxRepository(engine),
            adapter,
            cipher,
        )
        return await worker.run_once(now=datetime.now(UTC))
    finally:
        await engine.dispose()


def main() -> int:
    processed = asyncio.run(run_once(TokenDeliverySettings.from_environment()))
    return 0 if processed else 0


if __name__ == "__main__":
    raise SystemExit(main())
