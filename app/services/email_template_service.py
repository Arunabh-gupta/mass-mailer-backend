from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.models.email_template import EmailTemplate
from app.dto.request.email_template_request_dto import EmailTemplateRequestDto

class EmailTemplateService:

    @staticmethod
    def list_email_templates(db: Session)->list[EmailTemplate]: 
        return db.query(EmailTemplate).all()
    
    @staticmethod
    def create_email_template(payload: EmailTemplateRequestDto, db: Session)->EmailTemplate:
        existing = (
            db.query(EmailTemplate)
            .filter(EmailTemplate.subject == payload.subject and EmailTemplate.body == payload.body)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Template with this subject and body already exists"
            )
        
        email_template = EmailTemplate(
            name=payload.name,
            subject=payload.subject,
            body=payload.body
        )

        db.add(email_template)
        db.commit()
        db.refresh(email_template)

        return email_template