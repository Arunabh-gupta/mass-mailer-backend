from enum import Enum


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"


class CampaignContactStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

