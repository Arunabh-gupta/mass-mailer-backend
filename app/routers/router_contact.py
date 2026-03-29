from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_current_user_id
from app.controllers.contact_controller import ContactController
from app.db.dependencies import get_db
from app.dto.request.contact_request_dto import ContactRequestDto
from app.dto.response.contact_response_dto import ContactResponseDto

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
    dependencies=[Depends(get_current_user)],
)

@router.post(
    "",
    response_model=ContactResponseDto,
    status_code=status.HTTP_200_OK,
)
def create_contact(
    payload: ContactRequestDto,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return ContactController.create_contact(db, user_id, payload)


@router.get(
    "",
    response_model=list[ContactResponseDto],
    status_code=status.HTTP_200_OK,
)
def list_contacts(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return ContactController.list_contacts(db, user_id)


@router.get(
    "/{contact_id}",
    response_model=ContactResponseDto,
    status_code=status.HTTP_200_OK,
)
def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return ContactController.get_contact(db, user_id, contact_id)


@router.put(
    "/{contact_id}",
    response_model=ContactResponseDto,
    status_code=status.HTTP_200_OK,
)
def update_contact(
    contact_id: UUID,
    payload: ContactRequestDto,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return ContactController.update_contact(db, user_id, contact_id, payload)


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    ContactController.delete_contact(db, user_id, contact_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
