from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers.email_template_controller import EmailTemplateController
from app.db.dependencies import get_db
from app.dto.request.email_template_request_dto import EmailTemplateRequestDto
from app.dto.response.email_template_response_dto import EmailTemplateResponseDto

router = APIRouter(
    prefix="/email_template",
    tags=["Email_Templates"],
)


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


@router.get(
    "/{template_id}",
    response_model=EmailTemplateResponseDto,
    status_code=status.HTTP_200_OK,
)
def get_email_template(
    template_id: UUID,
    db: Session = Depends(get_db),
):
    return EmailTemplateController.get_email_template(db, template_id)


@router.put(
    "/{template_id}",
    response_model=EmailTemplateResponseDto,
    status_code=status.HTTP_200_OK,
)
def update_email_template(
    template_id: UUID,
    payload: EmailTemplateRequestDto,
    db: Session = Depends(get_db),
):
    return EmailTemplateController.update_email_template(db, template_id, payload)


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_email_template(
    template_id: UUID,
    db: Session = Depends(get_db),
):
    EmailTemplateController.delete_email_template(db, template_id)
