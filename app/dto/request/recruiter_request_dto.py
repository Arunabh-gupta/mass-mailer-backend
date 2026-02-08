from pydantic import BaseModel, EmailStr

class RecruiterRequestDto(BaseModel):
    name: str
    email: EmailStr
    company: str
    role: str | None = None