import logging
from uuid import UUID

logger = logging.getLogger(__name__)


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
    ) -> None:
        logger.info(
            (
                "Mock send email | campaign_id=%s contact_id=%s to=%s "
                "template_name=%s subject=%s contact_name=%s body=%s"
            ),
            campaign_id,
            contact_id,
            to_email,
            template_name,
            subject,
            contact_name,
            body,
        )
