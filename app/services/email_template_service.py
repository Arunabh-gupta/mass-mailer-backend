from uuid import UUID

import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.campaign import Campaign
from app.db.models.email_template import EmailTemplate
from app.dto.request.email_template_request_dto import EmailTemplateRequestDto

logger = logging.getLogger(__name__)


class EmailTemplateService:
    @staticmethod
    def get_email_template(db: Session, template_id: UUID) -> EmailTemplate:
        email_template = (
            db.query(EmailTemplate)
            .filter(EmailTemplate.id == template_id)
            .first()
        )

        if not email_template:
            logger.warning("Email template not found for id=%s", template_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email template not found",
            )

        return email_template

    @staticmethod
    def list_email_templates(db: Session) -> list[EmailTemplate]:
        templates = db.query(EmailTemplate).all()
        logger.info("Fetched %s email templates", len(templates))
        return templates

    @staticmethod
    def create_email_template(payload: EmailTemplateRequestDto, db: Session) -> EmailTemplate:
        existing = (
            db.query(EmailTemplate)
            .filter(
                EmailTemplate.subject == payload.subject,
                EmailTemplate.body == payload.body,
            )
            .first()
        )

        if existing:
            logger.warning(
                "Duplicate email template create attempt for subject '%s'",
                payload.subject,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Template with this subject and body already exists",
            )

        email_template = EmailTemplate(
            name=payload.name,
            subject=payload.subject,
            body=payload.body,
        )

        db.add(email_template)
        db.commit()
        db.refresh(email_template)
        logger.info("Created email template with id=%s", email_template.id)

        return email_template

    @staticmethod
    def update_email_template(
        db: Session,
        template_id: UUID,
        payload: EmailTemplateRequestDto,
    ) -> EmailTemplate:
        email_template = EmailTemplateService.get_email_template(db, template_id)

        existing = (
            db.query(EmailTemplate)
            .filter(
                EmailTemplate.subject == payload.subject,
                EmailTemplate.body == payload.body,
                EmailTemplate.id != template_id,
            )
            .first()
        )

        if existing:
            logger.warning(
                "Duplicate email template update attempt for subject '%s'",
                payload.subject,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Template with this subject and body already exists",
            )

        email_template.name = payload.name
        email_template.subject = payload.subject
        email_template.body = payload.body

        db.commit()
        db.refresh(email_template)
        logger.info("Updated email template with id=%s", email_template.id)

        return email_template

    @staticmethod
    def delete_email_template(
        db: Session,
        template_id: UUID,
    ) -> None:
        email_template = EmailTemplateService.get_email_template(db, template_id)

        linked_campaign = (
            db.query(Campaign)
            .filter(Campaign.template_id == template_id)
            .first()
        )
        if linked_campaign:
            logger.warning(
                "Blocked delete for email template id=%s because it is used by campaign id=%s",
                template_id,
                linked_campaign.id,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email template is used by an existing campaign and cannot be deleted",
            )

        db.delete(email_template)
        db.commit()
        logger.info("Deleted email template with id=%s", template_id)
