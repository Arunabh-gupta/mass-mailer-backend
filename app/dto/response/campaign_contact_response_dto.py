from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.constants import CampaignContactStatus


class CampaignContactResponseDto(BaseModel):
    id: UUID
    campaign_id: UUID
    contact_id: UUID
    status: CampaignContactStatus
    sent_at: datetime | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

