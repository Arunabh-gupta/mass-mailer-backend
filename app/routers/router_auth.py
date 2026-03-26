from fastapi import APIRouter, Depends, status

from app.auth.dependencies import AuthenticatedUser, get_current_user
from app.controllers.auth_controller import AuthController
from app.dto.response.auth_me_response_dto import AuthMeResponseDto

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.get(
    "/me",
    response_model=AuthMeResponseDto,
    status_code=status.HTTP_200_OK,
)
def get_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return AuthController.get_me(current_user)
