import logging
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import settings
from app.services.sqs_service import SqsService

logger = logging.getLogger(__name__)


class CampaignQueueService:
    @staticmethod
    def _queue_url() -> str:
        if not settings.aws_sqs_campaign_send_queue_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Campaign send queue is not configured",
            )
        return settings.aws_sqs_campaign_send_queue_url

    @staticmethod
    def enqueue_campaign_contact_send(
        *,
        campaign_id: UUID,
        campaign_contact_id: UUID,
        user_id: UUID,
    ) -> None:
        queue_url = CampaignQueueService._queue_url()
        payload = {
            "job_type": "campaign_contact_send",
            "campaign_id": str(campaign_id),
            "campaign_contact_id": str(campaign_contact_id),
            "user_id": str(user_id),
        }
        SqsService().send_json_message(queue_url=queue_url, payload=payload)
        logger.info(
            "Queued campaign contact send | campaign_id=%s campaign_contact_id=%s user_id=%s",
            campaign_id,
            campaign_contact_id,
            user_id,
        )
