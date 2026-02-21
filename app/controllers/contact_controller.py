from sqlalchemy.orm import Session

from app.db.models.contact import Contact
from app.dto.request.contact_request_dto import ContactRequestDto
from app.services.contact_service import ContactService


class ContactController:
    @staticmethod
    def create_contact(
        db: Session,
        payload: ContactRequestDto,
    ) -> Contact:
        return ContactService.create_contact(db, payload)

    @staticmethod
    def list_contacts(db: Session) -> list[Contact]:
        return ContactService.list_contacts(db)
