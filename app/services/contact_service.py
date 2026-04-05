import csv
from io import StringIO
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.db.models.campaign_contact import CampaignContact
from app.db.models.contact import Contact
from app.dto.request.contact_request_dto import ContactRequestDto
from app.dto.response.contact_import_response_dto import ContactImportErrorDto, ContactImportResponseDto

email_adapter = TypeAdapter(EmailStr)


class ContactService:
    @staticmethod
    def get_contact(db: Session, user_id: UUID, contact_id: UUID) -> Contact:
        contact = (
            db.query(Contact)
            .filter(
                Contact.id == contact_id,
                Contact.user_id == user_id,
            )
            .first()
        )
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return contact

    @staticmethod
    def create_contact(db: Session, user_id: UUID, payload: ContactRequestDto) -> Contact:
        existing = (
            db.query(Contact)
            .filter(
                Contact.user_id == user_id,
                Contact.email == payload.email,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A contact with this email already exists",
            )
        contact = Contact(
            user_id=user_id,
            name=payload.name,
            email=payload.email,
            company=payload.company,
            job_title=payload.job_title,
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    @staticmethod
    def import_contacts(db: Session, user_id: UUID, file: UploadFile) -> ContactImportResponseDto:
        filename = file.filename or ""
        if not filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Only CSV files are supported',
            )

        raw_bytes = file.file.read()
        if not raw_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='CSV file is empty',
            )

        try:
            decoded_csv = raw_bytes.decode('utf-8-sig')
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='CSV file must be UTF-8 encoded',
            ) from exc

        reader = csv.DictReader(StringIO(decoded_csv))
        if not reader.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='CSV file must contain a header row',
            )

        normalized_headers = [header.strip() for header in reader.fieldnames]
        required_headers = {'name', 'email', 'job_title', 'company'}
        if set(normalized_headers) != required_headers or len(normalized_headers) != len(required_headers):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='CSV headers must contain exactly these columns: name, email, job_title, company',
            )

        errors: list[ContactImportErrorDto] = []
        valid_rows: list[dict[str, str | int | None]] = []
        seen_emails: set[str] = set()
        total_rows = 0

        for row_number, row in enumerate(reader, start=2):
            values = [value.strip() for value in row.values() if isinstance(value, str)]
            if not any(values):
                continue

            total_rows += 1
            name = (row.get('name') or '').strip()
            email = (row.get('email') or '').strip()
            company = (row.get('company') or '').strip()
            job_title = (row.get('job_title') or '').strip()

            if not name:
                errors.append(ContactImportErrorDto(row=row_number, message='Missing name'))
                continue
            if not email:
                errors.append(ContactImportErrorDto(row=row_number, message='Missing email'))
                continue
            if not company:
                errors.append(ContactImportErrorDto(row=row_number, message='Missing company', email=email))
                continue

            try:
                normalized_email = str(email_adapter.validate_python(email))
            except ValidationError:
                errors.append(ContactImportErrorDto(row=row_number, message='Invalid email', email=email))
                continue

            if normalized_email in seen_emails:
                errors.append(ContactImportErrorDto(row=row_number, message='Duplicate email in CSV', email=normalized_email))
                continue

            seen_emails.add(normalized_email)
            valid_rows.append(
                {
                    'row': row_number,
                    'name': name,
                    'email': normalized_email,
                    'company': company,
                    'job_title': job_title or None,
                }
            )

        existing_emails = {
            email
            for (email,) in (
                db.query(Contact.email)
                .filter(
                    Contact.user_id == user_id,
                    Contact.email.in_([row['email'] for row in valid_rows]),
                )
                .all()
            )
        }

        contacts_to_create: list[Contact] = []
        for row in valid_rows:
            email = row['email']
            if email in existing_emails:
                errors.append(
                    ContactImportErrorDto(
                        row=int(row['row']),
                        message='A contact with this email already exists',
                        email=email,
                    )
                )
                continue

            contacts_to_create.append(
                Contact(
                    user_id=user_id,
                    name=str(row['name']),
                    email=str(email),
                    company=str(row['company']),
                    job_title=row['job_title'],
                )
            )

        if contacts_to_create:
            db.add_all(contacts_to_create)
            db.commit()

        return ContactImportResponseDto(
            total_rows=total_rows,
            imported_count=len(contacts_to_create),
            skipped_count=len(errors),
            errors=sorted(errors, key=lambda item: item.row),
        )

    @staticmethod
    def list_contacts(db: Session, user_id: UUID) -> list[Contact]:
        return (
            db.query(Contact)
            .filter(Contact.user_id == user_id)
            .all()
        )

    @staticmethod
    def update_contact(
        db: Session,
        user_id: UUID,
        contact_id: UUID,
        payload: ContactRequestDto,
    ) -> Contact:
        contact = ContactService.get_contact(db, user_id, contact_id)

        existing = (
            db.query(Contact)
            .filter(
                Contact.user_id == user_id,
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
        contact.job_title = payload.job_title

        db.commit()
        db.refresh(contact)
        return contact

    @staticmethod
    def delete_contact(
        db: Session,
        user_id: UUID,
        contact_id: UUID,
    ) -> None:
        contact = ContactService.get_contact(db, user_id, contact_id)

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
