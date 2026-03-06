from uuid import UUID

from pydantic import BaseModel

from app.core.constants import CampaignStatus


class CampaignSendResponseDto(BaseModel):
    campaign_id: UUID
    status: CampaignStatus
    total_recipients: int
    sent_recipients: int
    mode: str
