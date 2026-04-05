from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.db.models.contact import Contact
from app.dto.request.contact_request_dto import ContactRequestDto
from app.dto.response.contact_import_response_dto import ContactImportResponseDto
from app.dto.response.contact_list_response_dto import ContactListResponseDto
from app.services.contact_service import ContactService


class ContactController:
    @staticmethod
    def get_contact(
        db: Session,
        user_id: UUID,
        contact_id: UUID,
    ) -> Contact:
        return ContactService.get_contact(db, user_id, contact_id)

    @staticmethod
    def create_contact(
        db: Session,
        user_id: UUID,
        payload: ContactRequestDto,
    ) -> Contact:
        return ContactService.create_contact(db, user_id, payload)

    @staticmethod
    def import_contacts(
        db: Session,
        user_id: UUID,
        file: UploadFile,
    ) -> ContactImportResponseDto:
        return ContactService.import_contacts(db, user_id, file)

    @staticmethod
    def list_contacts(
        db: Session,
        user_id: UUID,
        page: int,
        page_size: int,
        query: str | None,
        include_totals: bool,
    ) -> ContactListResponseDto:
        return ContactService.list_contacts(
            db,
            user_id,
            page=page,
            page_size=page_size,
            query=query,
            include_totals=include_totals,
        )

    @staticmethod
    def update_contact(
        db: Session,
        user_id: UUID,
        contact_id: UUID,
        payload: ContactRequestDto,
    ) -> Contact:
        return ContactService.update_contact(db, user_id, contact_id, payload)

    @staticmethod
    def delete_contact(
        db: Session,
        user_id: UUID,
        contact_id: UUID,
    ) -> None:
        ContactService.delete_contact(db, user_id, contact_id)
