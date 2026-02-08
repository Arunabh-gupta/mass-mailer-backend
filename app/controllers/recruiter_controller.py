from sqlalchemy.orm import Session

from app.services.recruiter_service import RecruiterService
from app.dto.request.recruiter_request_dto import RecruiterRequestDto
from app.db.models.recruiter import Recruiter

class RecruiterController:
    @staticmethod
    def create(
        db: Session,
        payload: RecruiterRequestDto,
    ) -> Recruiter:
        return RecruiterService.create_recruiter(db, payload)

    @staticmethod
    def list(db: Session) -> list[Recruiter]:
        return RecruiterService.list_recruiters(db)
