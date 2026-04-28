from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.constants import CampaignContactStatus


class CampaignContactResponseDto(BaseModel):
    id: UUID
    campaign_id: UUID
    contact_id: UUID
    contact_name: str
    contact_email: str
    contact_company: str
    contact_job_title: str | None
    status: CampaignContactStatus
    processed_at: datetime | None
    sent_at: datetime | None
    provider_message_id: str | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
