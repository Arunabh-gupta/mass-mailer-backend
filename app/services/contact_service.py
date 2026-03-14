from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models.campaign_contact import CampaignContact
from app.db.models.contact import Contact
from app.dto.request.contact_request_dto import ContactRequestDto


class ContactService:
    @staticmethod
    def get_contact(db: Session, contact_id: UUID) -> Contact:
        contact = (
            db.query(Contact)
            .filter(Contact.id == contact_id)
            .first()
        )
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return contact

    @staticmethod
    def create_contact(db: Session, payload: ContactRequestDto) -> Contact:
        existing = (
            db.query(Contact)
            .filter(Contact.email == payload.email)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A contact with this email already exists",
            )
        contact = Contact(
            name=payload.name,
            email=payload.email,
            company=payload.company,
            role=payload.role,
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    @staticmethod
    def list_contacts(db: Session) -> list[Contact]:
        return db.query(Contact).all()

    @staticmethod
    def update_contact(
        db: Session,
        contact_id: UUID,
        payload: ContactRequestDto,
    ) -> Contact:
        contact = ContactService.get_contact(db, contact_id)

        existing = (
            db.query(Contact)
            .filter(
                Contact.email == payload.email,
                Contact.id != contact_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A contact with this email already exists",
            )

        contact.name = payload.name
        contact.email = payload.email
        contact.company = payload.company
        contact.role = payload.role

        db.commit()
        db.refresh(contact)
        return contact

    @staticmethod
    def delete_contact(
        db: Session,
        contact_id: UUID,
    ) -> None:
        contact = ContactService.get_contact(db, contact_id)

        linked_campaign_contact = (
            db.query(CampaignContact)
            .filter(CampaignContact.contact_id == contact_id)
            .first()
        )
        if linked_campaign_contact:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact is used by an existing campaign and cannot be deleted",
            )

        db.delete(contact)
        db.commit()
