from sqlalchemy.orm import Session
from app.dto.request.recruiter_request_dto import RecruiterRequestDto
from app.db.models.recruiter import Recruiter
from fastapi import HTTPException, status
class RecruiterService:

    @staticmethod
    def create_recruiter( db: Session, payload: RecruiterRequestDto) -> Recruiter : 
        existing = (
            db.query(Recruiter)
            .filter(Recruiter.email == payload.email)
            .first()
        )

        if existing : 
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Recruiter with this email already exists"
            )
        
        recruiter = Recruiter(
            name=payload.name, 
            email=payload.email,
            company=payload.company,
            role=payload.role,
        )

        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)

        return recruiter

    @staticmethod
    def list_recruiters( db: Session) -> list[Recruiter]:
        return db.query(Recruiter).all()
