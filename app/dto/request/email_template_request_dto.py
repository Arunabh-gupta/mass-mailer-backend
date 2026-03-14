from pydantic import BaseModel
from uuid import UUID
from typing import Optional
class EmailTemplateRequestDto(BaseModel):
    name: str
    subject: str
    body: str