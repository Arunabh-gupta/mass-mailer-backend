


from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.dto.request.email_template_request_dto import EmailTemplateRequestDto
from app.dto.response.email_template_response_dto import EmailTemplateResponseDto
from app.controllers.email_template_controller import EmailTemplateController

router = APIRouter(
    prefix="/email_template",
    tags=["Email_Templates"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=EmailTemplateResponseDto,
    status_code=status.HTTP_200_OK,
)
def create_email_template(
    payload: EmailTemplateRequestDto,
    db: Session = Depends(get_db),
): 
    return EmailTemplateController.create_email_template(db, payload)

@router.get(
    "",
    response_model=list[EmailTemplateResponseDto],
    status_code=status.HTTP_200_OK,
)
def list_email_templates(
    db: Session = Depends(get_db),
): 
    return EmailTemplateController.list_email_templates(db)