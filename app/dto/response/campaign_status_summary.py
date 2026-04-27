from pydantic import BaseModel


class CampaignStatusSummary(BaseModel):
    total_recipients: int
    pending_recipients: int
    sent_recipients: int
    failed_recipients: int
