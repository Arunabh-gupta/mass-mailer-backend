from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.constants import CampaignStatus


class CampaignResponseDto(BaseModel):
    id: UUID
    template_id: UUID
    status: CampaignStatus
    created_at: datetime

    model_config = {"from_attributes": True}

