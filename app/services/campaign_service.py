import logging
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import CampaignContactStatus, CampaignStatus
from app.db.models.campaign import Campaign
from app.db.models.campaign_contact import CampaignContact
from app.db.models.contact import Contact
from app.db.models.email_template import EmailTemplate
from app.dto.request.campaign_request_dto import CampaignRequestDto
from app.dto.response.campaign_contact_response_dto import CampaignContactResponseDto
from app.dto.response.campaign_response_dto import CampaignResponseDto
from app.dto.response.campaign_send_response_dto import CampaignSendResponseDto
from app.dto.response.campaign_status_summary import CampaignStatusSummary
from app.services.campaign_queue_service import CampaignQueueService

logger = logging.getLogger(__name__)


class CampaignService:
    @staticmethod
    def get_campaign_model(db: Session, user_id: UUID, campaign_id: UUID) -> Campaign:
        campaign = (
            db.query(Campaign)
            .filter(
                Campaign.id == campaign_id,
                Campaign.user_id == user_id,
            )
            .first()
        )
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found",
            )
        return campaign

    @staticmethod
    def build_status_summary(
        db: Session,
        campaign_id: UUID,
    ) -> CampaignStatusSummary:
        campaign_contacts = (
            db.query(CampaignContact.status)
            .filter(CampaignContact.campaign_id == campaign_id)
            .all()
        )
        statuses = [status for (status,) in campaign_contacts]
        total_recipients = len(statuses)
        pending_recipients = sum(status == CampaignContactStatus.PENDING.value for status in statuses)
        sent_recipients = sum(status == CampaignContactStatus.SENT.value for status in statuses)
        failed_recipients = sum(status == CampaignContactStatus.FAILED.value for status in statuses)

        return CampaignStatusSummary(
            total_recipients=total_recipients,
            pending_recipients=pending_recipients,
            sent_recipients=sent_recipients,
            failed_recipients=failed_recipients,
        )

    @staticmethod
    def build_campaign_response(
        db: Session,
        campaign: Campaign,
    ) -> CampaignResponseDto:
        return CampaignResponseDto(
            id=campaign.id,
            template_id=campaign.template_id,
            status=CampaignStatus(campaign.status),
            created_at=campaign.created_at,
            status_summary=CampaignService.build_status_summary(db, campaign.id),
        )

    @staticmethod
    def get_campaign(db: Session, user_id: UUID, campaign_id: UUID) -> CampaignResponseDto:
        campaign = CampaignService.get_campaign_model(db, user_id, campaign_id)
        return CampaignService.build_campaign_response(db, campaign)

    @staticmethod
    def create_campaign(db: Session, user_id: UUID, payload: CampaignRequestDto) -> CampaignResponseDto:
        template = (
            db.query(EmailTemplate)
            .filter(
                EmailTemplate.id == payload.template_id,
                EmailTemplate.user_id == user_id,
            )
            .first()
        )
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email template not found",
            )

        if not payload.contact_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="contact_ids must contain at least one contact id",
            )

        unique_contact_ids: list[UUID] = list(dict.fromkeys(payload.contact_ids))
        if len(unique_contact_ids) != len(payload.contact_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="contact_ids must not contain duplicates",
            )

        contacts = (
            db.query(Contact)
            .filter(
                Contact.user_id == user_id,
                Contact.id.in_(unique_contact_ids),
            )
            .all()
        )

        if len(contacts) != len(unique_contact_ids):
            found = {c.id for c in contacts}
            missing = [str(cid) for cid in unique_contact_ids if cid not in found]
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Some contacts were not found", "missing_contact_ids": missing},
            )

        campaign = Campaign(
            user_id=user_id,
            template_id=payload.template_id,
            status=CampaignStatus.DRAFT.value,
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        campaign_contacts = [
            CampaignContact(
                campaign_id=campaign.id,
                contact_id=cid,
                status=CampaignContactStatus.PENDING.value,
            )
            for cid in unique_contact_ids
        ]
        db.add_all(campaign_contacts)
        db.commit()

        return CampaignService.build_campaign_response(db, campaign)

    @staticmethod
    def list_campaigns(db: Session, user_id: UUID) -> list[CampaignResponseDto]:
        campaigns = (
            db.query(Campaign)
            .filter(Campaign.user_id == user_id)
            .all()
        )
        return [CampaignService.build_campaign_response(db, campaign) for campaign in campaigns]

    @staticmethod
    def list_campaign_contacts(
        db: Session,
        user_id: UUID,
        campaign_id: UUID,
    ) -> list[CampaignContactResponseDto]:
        CampaignService.get_campaign(db, user_id, campaign_id)
        campaign_contacts = (
            db.query(CampaignContact, Contact)
            .join(Contact, Contact.id == CampaignContact.contact_id)
            .filter(CampaignContact.campaign_id == campaign_id)
            .filter(Contact.user_id == user_id)
            .all()
        )
        return [
            CampaignContactResponseDto(
                id=campaign_contact.id,
                campaign_id=campaign_contact.campaign_id,
                contact_id=campaign_contact.contact_id,
                contact_name=contact.name,
                contact_email=contact.email,
                contact_company=contact.company,
                contact_job_title=contact.job_title,
                status=CampaignContactStatus(campaign_contact.status),
                processed_at=campaign_contact.processed_at,
                sent_at=campaign_contact.sent_at,
                provider_message_id=campaign_contact.provider_message_id,
                error_message=campaign_contact.error_message,
                created_at=campaign_contact.created_at,
            )
            for campaign_contact, contact in campaign_contacts
        ]

    @staticmethod
    def update_campaign(
        db: Session,
        user_id: UUID,
        campaign_id: UUID,
        payload: CampaignRequestDto,
    ) -> CampaignResponseDto:
        campaign = CampaignService.get_campaign_model(db, user_id, campaign_id)

        if campaign.status != CampaignStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Campaign can only be updated while in draft status",
            )

        any_non_pending = (
            db.query(CampaignContact)
            .filter(
                CampaignContact.campaign_id == campaign_id,
                CampaignContact.status != CampaignContactStatus.PENDING.value,
            )
            .first()
        )
        if any_non_pending:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Campaign can only be updated while all recipients are pending",
            )

        if payload.template_id is not None:
            template = (
                db.query(EmailTemplate)
                .filter(
                    EmailTemplate.id == payload.template_id,
                    EmailTemplate.user_id == user_id,
                )
                .first()
            )
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Email template not found",
                )
            campaign.template_id = payload.template_id

        if payload.contact_ids is not None:
            if not payload.contact_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="contact_ids must contain at least one contact id",
                )

            unique_contact_ids: list[UUID] = list(dict.fromkeys(payload.contact_ids))
            if len(unique_contact_ids) != len(payload.contact_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="contact_ids must not contain duplicates",
                )

            contacts = (
                db.query(Contact)
                .filter(
                    Contact.user_id == user_id,
                    Contact.id.in_(unique_contact_ids),
                )
                .all()
            )

            if len(contacts) != len(unique_contact_ids):
                found = {c.id for c in contacts}
                missing = [str(cid) for cid in unique_contact_ids if cid not in found]
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"message": "Some contacts were not found", "missing_contact_ids": missing},
                )

            existing_rows = (
                db.query(CampaignContact)
                .filter(CampaignContact.campaign_id == campaign_id)
                .all()
            )
            existing_ids = {row.contact_id for row in existing_rows}
            desired_ids = set(unique_contact_ids)

            to_remove = existing_ids - desired_ids
            to_add = desired_ids - existing_ids

            if to_remove:
                (
                    db.query(CampaignContact)
                    .filter(
                        CampaignContact.campaign_id == campaign_id,
                        CampaignContact.contact_id.in_(list(to_remove)),
                    )
                    .delete(synchronize_session=False)
                )

            if to_add:
                db.add_all(
                    [
                        CampaignContact(
                            campaign_id=campaign_id,
                            contact_id=cid,
                            status=CampaignContactStatus.PENDING.value,
                        )
                        for cid in to_add
                    ]
                )

        db.commit()
        db.refresh(campaign)
        return CampaignService.build_campaign_response(db, campaign)

    @staticmethod
    def delete_campaign(db: Session, user_id: UUID, campaign_id: UUID) -> None:
        campaign = CampaignService.get_campaign_model(db, user_id, campaign_id)
        if campaign.status == CampaignStatus.SENDING.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Campaign cannot be deleted while it is sending",
            )

        (
            db.query(CampaignContact)
            .filter(CampaignContact.campaign_id == campaign_id)
            .delete(synchronize_session=False)
        )
        db.delete(campaign)
        db.commit()

    @staticmethod
    def send_campaign(
        db: Session,
        user_id: UUID,
        campaign_id: UUID,
    ) -> CampaignSendResponseDto:
        campaign = CampaignService.get_campaign_model(db, user_id, campaign_id)
        if campaign.status != CampaignStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Campaign can only be sent while in draft status",
            )

        template = (
            db.query(EmailTemplate)
            .filter(
                EmailTemplate.id == campaign.template_id,
                EmailTemplate.user_id == user_id,
            )
            .first()
        )
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email template not found",
            )

        campaign_contacts = (
            db.query(CampaignContact, Contact)
            .join(Contact, Contact.id == CampaignContact.contact_id)
            .filter(
                CampaignContact.campaign_id == campaign_id,
                Contact.user_id == user_id,
            )
            .all()
        )
        if not campaign_contacts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign has no recipients",
            )

        try:
            for campaign_contact, _contact in campaign_contacts:
                campaign_contact.processed_at = None
                campaign_contact.sent_at = None
                campaign_contact.provider_message_id = None
                campaign_contact.error_message = None
                campaign_contact.status = CampaignContactStatus.PENDING.value
                CampaignQueueService.enqueue_campaign_contact_send(
                    campaign_id=campaign.id,
                    campaign_contact_id=campaign_contact.id,
                    user_id=user_id,
                )
        except Exception:
            logger.exception(
                "Failed to enqueue campaign send jobs | campaign_id=%s user_id=%s",
                campaign_id,
                user_id,
            )
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to queue campaign send jobs",
            )

        campaign.status = CampaignStatus.COMPLETED.value
        db.commit()
        db.refresh(campaign)
        logger.info(
            "Queued campaign send | campaign_id=%s recipients=%s user_id=%s status=%s",
            campaign_id,
            len(campaign_contacts),
            user_id,
            campaign.status,
        )
        return CampaignSendResponseDto(
            campaign_id=campaign.id,
            status=CampaignStatus(campaign.status),
            total_recipients=len(campaign_contacts),
            sent_recipients=0,
            mode="sqs",
        )
