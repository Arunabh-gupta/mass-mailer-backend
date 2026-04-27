from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.constants import CampaignStatus
from app.dto.response.campaign_status_summary import CampaignStatusSummary


class CampaignResponseDto(BaseModel):
    id: UUID
    template_id: UUID
    status: CampaignStatus
    created_at: datetime
    status_summary: CampaignStatusSummary

    model_config = {"from_attributes": True}
