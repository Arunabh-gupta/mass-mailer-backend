from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr

class RecruiterResponseDto(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    company: str
    role: str | None
    created_at: datetime
    update_at: datetime
    class Config: 
        # this tell pydantic that I'll be converting SQLAlchemy object into this DTO
        from_attributes: True