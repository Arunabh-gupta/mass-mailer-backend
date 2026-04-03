from pydantic import BaseModel, EmailStr


class ContactRequestDto(BaseModel):
    name: str
    email: EmailStr
    company: str
    job_title: str | None = None
