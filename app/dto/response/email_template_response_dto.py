from datetime import datetime
from pydantic import BaseModel

class EmailTemplateResponseDto(BaseModel):
    name: str
    subject: str
    body: str
    created_at: datetime
    updated_at: datetime

    class Config: 
        from_attributes: True