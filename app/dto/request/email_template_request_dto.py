from pydantic import BaseModel

class EmailTemplateRequestDto(BaseModel):
    name: str
    subject: str
    body: str