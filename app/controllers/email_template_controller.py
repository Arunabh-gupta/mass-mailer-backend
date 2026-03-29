from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.email_template import EmailTemplate
from app.dto.request.email_template_request_dto import EmailTemplateRequestDto
from app.services.email_template_service import EmailTemplateService


class EmailTemplateController:
    @staticmethod
    def get_email_template(
        db: Session,
        user_id: UUID,
        template_id: UUID,
    ) -> EmailTemplate:
        return EmailTemplateService.get_email_template(db, user_id, template_id)

    @staticmethod
    def create_email_template(
        db: Session,
        user_id: UUID,
        payload: EmailTemplateRequestDto,
    ) -> EmailTemplate:
        return EmailTemplateService.create_email_template(payload, db, user_id)

    @staticmethod
    def list_email_templates(
        db: Session,
        user_id: UUID,
    ) -> list[EmailTemplate]:
        return EmailTemplateService.list_email_templates(db, user_id)

    @staticmethod
    def update_email_template(
        db: Session,
        user_id: UUID,
        template_id: UUID,
        payload: EmailTemplateRequestDto,
    ) -> EmailTemplate:
        return EmailTemplateService.update_email_template(db, user_id, template_id, payload)

    @staticmethod
    def delete_email_template(
        db: Session,
        user_id: UUID,
        template_id: UUID,
    ) -> None:
        EmailTemplateService.delete_email_template(db, user_id, template_id)
