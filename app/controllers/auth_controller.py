from app.auth.dependencies import AuthenticatedUser
from app.db.models.user import User


class AuthController:
    @staticmethod
    def get_me(current_user: AuthenticatedUser) -> User:
        return current_user.user
