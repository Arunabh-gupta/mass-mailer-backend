from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class ContactResponseDto(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    company: str
    created_at: datetime

    model_config = {"from_attributes": True}
