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
