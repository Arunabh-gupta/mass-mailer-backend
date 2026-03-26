from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.types import AuthIdentity
from app.db.models.user import User


class AuthService:
    @staticmethod
    def get_or_create_user_from_identity(db: Session, identity: AuthIdentity) -> User:
        if not identity.subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        user = (
            db.query(User)
            .filter(
                User.auth_provider == identity.provider,
                User.provider_user_id == identity.subject,
            )
            .first()
        )

        if not user:
            user = User(
                auth_provider=identity.provider,
                provider_user_id=identity.subject,
                email=identity.email,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

        if identity.email and user.email != identity.email:
            user.email = identity.email
            db.commit()
            db.refresh(user)

        return user
