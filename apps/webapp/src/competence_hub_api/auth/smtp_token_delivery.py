import asyncio
from datetime import UTC, datetime
from email.message import EmailMessage
import smtplib
import ssl
from typing import Literal
from urllib.parse import quote
from uuid import UUID

from competence_hub_api.auth.token_delivery import TokenDeliveryError
from competence_hub_api.security.email_addresses import is_single_email_address


class SmtpTokenMessageAdapter:
    def __init__(
        self,
        *,
        host: str,
        port: int,
        tls_mode: Literal["starttls", "implicit"],
        username: str,
        password: str,
        sender: str,
        reply_to: str,
        account_action_base_url: str,
        timeout_seconds: float = 15.0,
    ) -> None:
        self._host = host
        self._port = port
        self._tls_mode = tls_mode
        self._username = username
        self._password = password
        self._sender = sender
        self._reply_to = reply_to
        self._account_action_base_url = account_action_base_url
        self._timeout_seconds = timeout_seconds

    async def deliver(
        self,
        *,
        delivery_id: UUID,
        purpose: Literal["invitation", "password_reset"],
        recipient_email: str,
        token: str,
        expires_at: datetime,
    ) -> None:
        del delivery_id
        try:
            if not is_single_email_address(recipient_email):
                raise ValueError("invalid delivery recipient")
            message = self._message(
                purpose=purpose,
                recipient_email=recipient_email,
                token=token,
                expires_at=expires_at,
            )
            await asyncio.to_thread(self._send, message)
        except (OSError, ValueError, smtplib.SMTPException, TimeoutError) as error:
            raise TokenDeliveryError("SMTP delivery failed") from error

    def _message(
        self,
        *,
        purpose: Literal["invitation", "password_reset"],
        recipient_email: str,
        token: str,
        expires_at: datetime,
    ) -> EmailMessage:
        action = "einladung" if purpose == "invitation" else "passwort-zuruecksetzen"
        link = (
            f"{self._account_action_base_url}#/{action}?token="
            f"{quote(token, safe='')}"
        )
        invitation = purpose == "invitation"
        subject = (
            "Ihre Einladung zum Competence Hub"
            if invitation
            else "Competence Hub: Passwort zurücksetzen"
        )
        instruction = (
            "Richten Sie über diesen Link Ihren persönlichen Zugang ein:"
            if invitation
            else "Legen Sie über diesen Link ein neues Passwort fest:"
        )
        expiry = expires_at.astimezone(UTC).strftime("%d.%m.%Y um %H:%M UTC")
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self._sender
        message["To"] = recipient_email
        message["Reply-To"] = self._reply_to
        message.set_content(
            "Hallo,\n\n"
            f"{instruction}\n\n{link}\n\n"
            f"Der Link ist bis {expiry} gültig und kann nur einmal verwendet werden.\n"
            "Falls Sie diese Nachricht nicht erwartet haben, ignorieren Sie sie bitte.\n\n"
            "Competence Hub"
        )
        return message

    def _send(self, message: EmailMessage) -> None:
        context = ssl.create_default_context()
        if self._tls_mode == "implicit":
            with smtplib.SMTP_SSL(
                self._host,
                self._port,
                timeout=self._timeout_seconds,
                context=context,
            ) as client:
                client.login(self._username, self._password)
                client.send_message(message)
            return
        with smtplib.SMTP(
            self._host,
            self._port,
            timeout=self._timeout_seconds,
        ) as client:
            client.ehlo()
            client.starttls(context=context)
            client.ehlo()
            client.login(self._username, self._password)
            client.send_message(message)
