from uuid import UUID

from pydantic import BaseModel


class CampaignRequestDto(BaseModel):
    template_id: UUID
    contact_ids: list[UUID]

