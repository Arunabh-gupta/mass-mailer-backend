from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models.contact import Contact
from app.dto.request.contact_request_dto import ContactRequestDto


class ContactService:
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
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    @staticmethod
    def list_contacts(db: Session) -> list[Contact]:
        return db.query(Contact).all()
