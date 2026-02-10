from sqlalchemy.orm import Session
from app.db.models.email_template import EmailTemplate
from app.dto.request.email_template_request_dto import EmailTemplateRequestDto
from app.services.email_template_service import EmailTemplateService

class EmailTemplateController: 
    @staticmethod
    def create_email_template(
        db: Session,
        payload: EmailTemplateRequestDto
    ) -> EmailTemplate :
        return EmailTemplateService.create_email_template(payload, db)
    
    @staticmethod
    def list_email_templates(
        db: Session
    ) -> list[EmailTemplate]:
        return EmailTemplateService.list_email_templates(db)