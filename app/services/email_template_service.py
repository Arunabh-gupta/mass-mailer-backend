import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.email_template import EmailTemplate
from app.dto.request.email_template_request_dto import EmailTemplateRequestDto

logger = logging.getLogger(__name__)


class EmailTemplateService:

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
