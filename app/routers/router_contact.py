from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers.contact_controller import ContactController
from app.db.dependencies import get_db
from app.dto.request.contact_request_dto import ContactRequestDto
from app.dto.response.contact_response_dto import ContactResponseDto

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
)

@router.post(
    "",
    response_model=ContactResponseDto,
    status_code=status.HTTP_200_OK,
)
def create_contact(
    payload: ContactRequestDto,
    db: Session = Depends(get_db),
):
    return ContactController.create_contact(db, payload)


@router.get(
    "",
    response_model=list[ContactResponseDto],
    status_code=status.HTTP_200_OK,
)
def list_contacts(
    db: Session = Depends(get_db),
):
    return ContactController.list_contacts(db)


@router.get(
    "/{contact_id}",
    response_model=ContactResponseDto,
    status_code=status.HTTP_200_OK,
)
def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
):
    return ContactController.get_contact(db, contact_id)


@router.put(
    "/{contact_id}",
    response_model=ContactResponseDto,
    status_code=status.HTTP_200_OK,
)
def update_contact(
    contact_id: UUID,
    payload: ContactRequestDto,
    db: Session = Depends(get_db),
):
    return ContactController.update_contact(db, contact_id, payload)


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
):
    ContactController.delete_contact(db, contact_id)
