from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_current_user_id
from app.controllers.email_template_controller import EmailTemplateController
from app.db.dependencies import get_db
from app.dto.request.email_template_request_dto import EmailTemplateRequestDto
from app.dto.response.email_template_response_dto import EmailTemplateResponseDto

router = APIRouter(
    prefix="/email_template",
    tags=["Email_Templates"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "",
    response_model=EmailTemplateResponseDto,
    status_code=status.HTTP_200_OK,
)
def create_email_template(
    payload: EmailTemplateRequestDto,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return EmailTemplateController.create_email_template(db, user_id, payload)


@router.get(
    "",
    response_model=list[EmailTemplateResponseDto],
    status_code=status.HTTP_200_OK,
)
def list_email_templates(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return EmailTemplateController.list_email_templates(db, user_id)


@router.get(
    "/{template_id}",
    response_model=EmailTemplateResponseDto,
    status_code=status.HTTP_200_OK,
)
def get_email_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return EmailTemplateController.get_email_template(db, user_id, template_id)


@router.put(
    "/{template_id}",
    response_model=EmailTemplateResponseDto,
    status_code=status.HTTP_200_OK,
)
def update_email_template(
    template_id: UUID,
    payload: EmailTemplateRequestDto,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return EmailTemplateController.update_email_template(db, user_id, template_id, payload)


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_email_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    EmailTemplateController.delete_email_template(db, user_id, template_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
