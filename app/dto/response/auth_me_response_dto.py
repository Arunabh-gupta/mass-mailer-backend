from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class AuthMeResponseDto(BaseModel):
    id: UUID
    auth_provider: str
    provider_user_id: str
    email: EmailStr | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
