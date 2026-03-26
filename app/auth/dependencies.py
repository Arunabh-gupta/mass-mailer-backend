from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.providers.jwt_provider import verify_token
from app.auth.types import AuthIdentity
from app.db.dependencies import get_db
from app.db.models.user import User
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    user: User
    identity: AuthIdentity


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Missing authentication token")

    identity = verify_token(credentials.credentials)
    user = AuthService.get_or_create_user_from_identity(db, identity)
    return AuthenticatedUser(user=user, identity=identity)
