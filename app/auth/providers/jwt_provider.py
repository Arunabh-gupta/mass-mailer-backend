import logging

import jwt
from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError

from app.auth.types import AuthIdentity
from app.core.config import settings
logger = logging.getLogger(__name__)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_token(token: str) -> AuthIdentity:
    if not settings.auth_jwt_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backend auth is not configured",
        )

    decode_kwargs = {
        "algorithms": [settings.auth_jwt_algorithm],
        "options": {"verify_aud": False},
    }
    if settings.auth_jwt_issuer:
        decode_kwargs["issuer"] = settings.auth_jwt_issuer

    try:
        settings.auth_jwt_key = settings.auth_jwt_key.replace("\\n", "\n")   
        claims = jwt.decode(token, settings.auth_jwt_key, **decode_kwargs)
    except ExpiredSignatureError as exc:
        raise _unauthorized("Authentication token has expired") from exc
    except InvalidTokenError as exc:
        raise _unauthorized("Invalid authentication token") from exc

    if settings.auth_authorized_parties:
        authorized_party = claims.get("azp")
        if authorized_party and authorized_party not in settings.auth_authorized_parties:
            raise _unauthorized("Authentication token is not valid for this application")

    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject:
        raise _unauthorized("Authentication token is missing a subject")

    email = claims.get("email")
    normalized_email = email if isinstance(email, str) and email else None

    return AuthIdentity(
        provider=settings.auth_provider_name,
        subject=subject,
        email=normalized_email,
        claims=claims,
    )
