from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.contact import Contact
from app.dto.request.contact_request_dto import ContactRequestDto
from app.services.contact_service import ContactService


class ContactController:
    @staticmethod
    def get_contact(
        db: Session,
        contact_id: UUID,
    ) -> Contact:
        return ContactService.get_contact(db, contact_id)

    @staticmethod
    def create_contact(
        db: Session,
        payload: ContactRequestDto,
    ) -> Contact:
        return ContactService.create_contact(db, payload)

    @staticmethod
    def list_contacts(db: Session) -> list[Contact]:
        return ContactService.list_contacts(db)

    @staticmethod
    def update_contact(
        db: Session,
        contact_id: UUID,
        payload: ContactRequestDto,
    ) -> Contact:
        return ContactService.update_contact(db, contact_id, payload)

    @staticmethod
    def delete_contact(
        db: Session,
        contact_id: UUID,
    ) -> None:
        ContactService.delete_contact(db, contact_id)
