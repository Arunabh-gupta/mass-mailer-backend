from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers.campaign_controller import CampaignController
from app.db.dependencies import get_db
from app.dto.request.campaign_request_dto import CampaignRequestDto
from app.dto.response.campaign_contact_response_dto import CampaignContactResponseDto
from app.dto.response.campaign_response_dto import CampaignResponseDto
from app.dto.response.campaign_send_response_dto import CampaignSendResponseDto


router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"],
)

@router.post(
    "",
    response_model=CampaignResponseDto,
    status_code=status.HTTP_200_OK,
)
def create_campaign(
    payload: CampaignRequestDto,
    db: Session = Depends(get_db),
):
    return CampaignController.create_campaign(db, payload)


@router.get(
    "",
    response_model=list[CampaignResponseDto],
    status_code=status.HTTP_200_OK,
)
def list_campaigns(
    db: Session = Depends(get_db),
):
    return CampaignController.list_campaigns(db)


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponseDto,
    status_code=status.HTTP_200_OK,
)
def get_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
):
    return CampaignController.get_campaign(db, campaign_id)


@router.get(
    "/{campaign_id}/contacts",
    response_model=list[CampaignContactResponseDto],
    status_code=status.HTTP_200_OK,
)
def list_campaign_contacts(
    campaign_id: UUID,
    db: Session = Depends(get_db),
):
    return CampaignController.list_campaign_contacts(db, campaign_id)


@router.patch(
    "/{campaign_id}",
    response_model=CampaignResponseDto,
    status_code=status.HTTP_200_OK,
)
def update_campaign(
    campaign_id: UUID,
    payload: CampaignRequestDto,
    db: Session = Depends(get_db),
):
    return CampaignController.update_campaign(db, campaign_id, payload)


@router.post(
    "/{campaign_id}/send",
    response_model=CampaignSendResponseDto,
    status_code=status.HTTP_200_OK,
)
def send_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
):
    return CampaignController.send_campaign(db, campaign_id)
