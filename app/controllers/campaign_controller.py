from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.campaign import Campaign
from app.db.models.campaign_contact import CampaignContact
from app.dto.request.campaign_request_dto import CampaignRequestDto
from app.dto.response.campaign_send_response_dto import CampaignSendResponseDto
from app.services.campaign_service import CampaignService


class CampaignController:
    @staticmethod
    def get_campaign(db: Session, campaign_id: UUID) -> Campaign:
        return CampaignService.get_campaign(db, campaign_id)

    @staticmethod
    def create_campaign(db: Session, payload: CampaignRequestDto) -> Campaign:
        return CampaignService.create_campaign(db, payload)

    @staticmethod
    def list_campaigns(db: Session) -> list[Campaign]:
        return CampaignService.list_campaigns(db)

    @staticmethod
    def list_campaign_contacts(db: Session, campaign_id: UUID) -> list[CampaignContact]:
        return CampaignService.list_campaign_contacts(db, campaign_id)

    @staticmethod
    def update_campaign(
        db: Session,
        campaign_id: UUID,
        payload: CampaignRequestDto,
    ) -> Campaign:
        return CampaignService.update_campaign(db, campaign_id, payload)

    @staticmethod
    def delete_campaign(db: Session, campaign_id: UUID) -> None:
        CampaignService.delete_campaign(db, campaign_id)

    @staticmethod
    def send_campaign(db: Session, campaign_id: UUID) -> CampaignSendResponseDto:
        return CampaignService.send_campaign(db, campaign_id)
