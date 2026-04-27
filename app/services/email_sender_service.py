import logging
from typing import Any
from uuid import UUID

import boto3

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_aws_session() -> boto3.session.Session:
    session_kwargs: dict[str, Any] = {}
    if settings.aws_profile:
        session_kwargs["profile_name"] = settings.aws_profile
    return boto3.session.Session(**session_kwargs)


def _render_template_text(value: str, *, contact_name: str) -> str:
    # Keep V1 templating intentionally small and predictable.
    return value.replace("{{name}}", contact_name).replace("{{contact_name}}", contact_name)
class MockEmailSenderService:
    @staticmethod
    def send_email(
        *,
        campaign_id: UUID,
        contact_id: UUID,
        to_email: str,
        subject: str,
        body: str,
        template_name: str,
        contact_name: str,
    ) -> dict[str, str]:
        rendered_subject = _render_template_text(subject, contact_name=contact_name)
        rendered_body = _render_template_text(body, contact_name=contact_name)
        logger.info(
            (
                "Mock send email | campaign_id=%s contact_id=%s to=%s "
                "template_name=%s subject=%s contact_name=%s body=%s"
            ),
            campaign_id,
            contact_id,
            to_email,
            template_name,
            rendered_subject,
            contact_name,
            rendered_body,
        )
        return {
            "provider": "mock",
            "message_id": f"mock-{campaign_id}-{contact_id}",
        }


class SesEmailSenderService:
    def __init__(self) -> None:
        if not settings.aws_ses_from_email:
            raise RuntimeError("AWS_SES_FROM_EMAIL is not configured")

        session = _build_aws_session()
        client_kwargs: dict[str, Any] = {
            "region_name": settings.aws_region,
        }
        if settings.aws_ses_endpoint_url:
            client_kwargs["endpoint_url"] = settings.aws_ses_endpoint_url
        self._client = session.client("ses", **client_kwargs)

    def send_email(
        self,
        *,
        campaign_id: UUID,
        contact_id: UUID,
        to_email: str,
        subject: str,
        body: str,
        template_name: str,
        contact_name: str,
    ) -> dict[str, str]:
        rendered_subject = _render_template_text(subject, contact_name=contact_name)
        rendered_body = _render_template_text(body, contact_name=contact_name)
        response = self._client.send_email(
            Source=settings.aws_ses_from_email,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": rendered_subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": rendered_body, "Charset": "UTF-8"},
                },
            },
        )
        logger.info(
            "SES send completed | campaign_id=%s contact_id=%s to=%s template_name=%s message_id=%s",
            campaign_id,
            contact_id,
            to_email,
            template_name,
            response.get("MessageId"),
        )
        return {
            "provider": "ses",
            "message_id": str(response.get("MessageId", "")),
        }


class EmailSenderService:
    @staticmethod
    def send_email(
        *,
        campaign_id: UUID,
        contact_id: UUID,
        to_email: str,
        subject: str,
        body: str,
        template_name: str,
        contact_name: str,
    ) -> dict[str, str]:
        provider = settings.email_provider.lower()
        sender_kwargs = {
            "campaign_id": campaign_id,
            "contact_id": contact_id,
            "to_email": to_email,
            "subject": subject,
            "body": body,
            "template_name": template_name,
            "contact_name": contact_name,
        }

        if provider == "mock":
            return MockEmailSenderService.send_email(**sender_kwargs)

        if provider == "ses":
            return SesEmailSenderService().send_email(**sender_kwargs)

        raise RuntimeError(f"Unsupported email provider: {settings.email_provider}")
