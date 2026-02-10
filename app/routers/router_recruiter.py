from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.controllers.recruiter_controller import RecruiterController
from app.dto.request.recruiter_request_dto import RecruiterRequestDto
from app.dto.response.recruiter_response_dto import RecruiterResponseDto

router = APIRouter(
    prefix="/recruiters",
    tags=["Recruiters"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=RecruiterResponseDto,
    status_code=status.HTTP_200_OK,
)
def create_recruiter(
    payload: RecruiterRequestDto,
    db: Session = Depends(get_db),
):
    return RecruiterController.create(db, payload)


@router.get(
    "",
    response_model=list[RecruiterResponseDto],
    status_code=status.HTTP_200_OK,
)
def list_recruiters(
    db: Session = Depends(get_db),
):
    return RecruiterController.list(db)
