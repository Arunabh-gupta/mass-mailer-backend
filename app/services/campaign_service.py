from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import CampaignContactStatus, CampaignStatus
from app.db.models.campaign import Campaign
from app.db.models.campaign_contact import CampaignContact
from app.db.models.contact import Contact
from app.db.models.email_template import EmailTemplate
from app.dto.request.campaign_request_dto import CampaignRequestDto


class CampaignService:
    @staticmethod
    def get_campaign(db: Session, campaign_id: UUID) -> Campaign:
        campaign = (
            db.query(Campaign)
            .filter(Campaign.id == campaign_id)
            .first()
        )
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found",
            )
        return campaign

    @staticmethod
    def create_campaign(db: Session, payload: CampaignRequestDto) -> Campaign:
        template = (
            db.query(EmailTemplate)
            .filter(EmailTemplate.id == payload.template_id)
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

        # Guard against duplicates in request body.
        unique_contact_ids: list[UUID] = list(dict.fromkeys(payload.contact_ids))
        if len(unique_contact_ids) != len(payload.contact_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="contact_ids must not contain duplicates",
            )

        contacts = (
            db.query(Contact)
            .filter(Contact.id.in_(unique_contact_ids))
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
            template_id=payload.template_id,
            status=CampaignStatus.DRAFT.value,
            user_id=None,
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

        return campaign

    @staticmethod
    def list_campaigns(db: Session) -> list[Campaign]:
        return db.query(Campaign).all()

    @staticmethod
    def list_campaign_contacts(db: Session, campaign_id: UUID) -> list[CampaignContact]:
        # Ensure campaign exists for a clean 404 vs returning empty list.
        CampaignService.get_campaign(db, campaign_id)
        return (
            db.query(CampaignContact)
            .filter(CampaignContact.campaign_id == campaign_id)
            .all()
        )

    @staticmethod
    def update_campaign(
        db: Session,
        campaign_id: UUID,
        payload: CampaignRequestDto,
    ) -> Campaign:
        campaign = CampaignService.get_campaign(db, campaign_id)

        # Allow updates only before sending starts.
        if campaign.status != CampaignStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Campaign can only be updated while in draft status",
            )

        # Ensure nothing has been sent yet.
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
                .filter(EmailTemplate.id == payload.template_id)
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
                .filter(Contact.id.in_(unique_contact_ids))
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
        return campaign

