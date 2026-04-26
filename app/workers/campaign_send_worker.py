import json
import logging
import time
from datetime import datetime
from uuid import UUID

import app.db.models  # noqa: F401
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import CampaignContactStatus, CampaignStatus
from app.db.models.campaign import Campaign
from app.db.models.campaign_contact import CampaignContact
from app.db.models.contact import Contact
from app.db.models.email_template import EmailTemplate
from app.db.session import SessionLocal
from app.services.email_sender_service import MockEmailSenderService
from app.services.sqs_service import SqsService

logger = logging.getLogger(__name__)


def _compute_campaign_status(db: Session, campaign_id: UUID) -> str:
    statuses = [
        status
        for (status,) in (
            db.query(CampaignContact.status)
            .filter(CampaignContact.campaign_id == campaign_id)
            .all()
        )
    ]
    if not statuses or any(status == CampaignContactStatus.PENDING.value for status in statuses):
        return CampaignStatus.SENDING.value
    if any(status == CampaignContactStatus.FAILED.value for status in statuses):
        return CampaignStatus.FAILED.value
    return CampaignStatus.COMPLETED.value


def _process_campaign_contact_send(db: Session, payload: dict[str, str]) -> None:
    campaign_contact_id = UUID(payload["campaign_contact_id"])
    campaign_id = UUID(payload["campaign_id"])
    user_id = UUID(payload["user_id"])

    campaign_contact = (
        db.query(CampaignContact)
        .filter(CampaignContact.id == campaign_contact_id)
        .first()
    )
    if not campaign_contact:
        logger.warning("Campaign contact not found for queued job | payload=%s", payload)
        return

    if campaign_contact.status != CampaignContactStatus.PENDING.value:
        logger.info(
            "Skipping already processed campaign contact | campaign_contact_id=%s status=%s",
            campaign_contact.id,
            campaign_contact.status,
        )
        return

    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
        )
        .first()
    )
    if not campaign:
        logger.warning("Campaign not found for queued job | payload=%s", payload)
        return

    contact = (
        db.query(Contact)
        .filter(
            Contact.id == campaign_contact.contact_id,
            Contact.user_id == user_id,
        )
        .first()
    )
    template = (
        db.query(EmailTemplate)
        .filter(
            EmailTemplate.id == campaign.template_id,
            EmailTemplate.user_id == user_id,
        )
        .first()
    )

    if not contact or not template:
        campaign_contact.status = CampaignContactStatus.FAILED.value
        campaign_contact.error_message = "Contact or template not found"
        campaign.status = _compute_campaign_status(db, campaign_id)
        db.commit()
        return

    try:
        MockEmailSenderService.send_email(
            campaign_id=campaign.id,
            contact_id=contact.id,
            to_email=contact.email,
            subject=template.subject,
            body=template.body,
            template_name=template.name,
            contact_name=contact.name,
        )
        campaign_contact.status = CampaignContactStatus.SENT.value
        campaign_contact.sent_at = datetime.now()
        campaign_contact.error_message = None
    except Exception as exc:
        campaign_contact.status = CampaignContactStatus.FAILED.value
        campaign_contact.error_message = str(exc)

    campaign.status = _compute_campaign_status(db, campaign_id)
    db.commit()


def run_worker() -> None:
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    if not settings.aws_sqs_campaign_send_queue_url:
        raise RuntimeError("AWS_SQS_CAMPAIGN_SEND_QUEUE_URL is not configured")

    sqs_service = SqsService()
    queue_url = settings.aws_sqs_campaign_send_queue_url
    logger.info("Starting campaign send worker")

    while True:
        messages = sqs_service.receive_messages(
            queue_url=queue_url,
            max_number=5,
            wait_time_seconds=10,
            visibility_timeout=30,
        )
        if not messages:
            time.sleep(1)
            continue

        for message in messages:
            receipt_handle = message["ReceiptHandle"]
            payload = json.loads(message["Body"])

            try:
                if payload.get("job_type") != "campaign_contact_send":
                    logger.warning("Skipping unsupported SQS job | payload=%s", payload)
                else:
                    db = SessionLocal()
                    try:
                        _process_campaign_contact_send(db, payload)
                    finally:
                        db.close()

                sqs_service.delete_message(
                    queue_url=queue_url,
                    receipt_handle=receipt_handle,
                )
            except Exception:
                logger.exception("Failed processing SQS message | payload=%s", payload)


if __name__ == "__main__":
    run_worker()
