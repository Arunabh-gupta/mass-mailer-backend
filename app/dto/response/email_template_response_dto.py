from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class EmailTemplateResponseDto(BaseModel):
    id: UUID
    name: str
    subject: str
    body: str
    created_at: datetime
    updated_at: datetime

    class Config: 
        from_attributes: True