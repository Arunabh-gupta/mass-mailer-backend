from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str
    app_name: str
    debug: bool = False
    database_url: str
    cors_allowed_origins: list[str] = ["http://localhost:3000"]
    auth_provider_name: str = "clerk"
    auth_jwt_key: str | None = None
    auth_jwt_algorithm: str = "RS256"
    auth_jwt_issuer: str | None = None
    auth_authorized_parties: list[str] = []

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_allowed_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("auth_authorized_parties", mode="before")
    @classmethod
    def parse_auth_authorized_parties(cls, value):
        if isinstance(value, str):
            return [party.strip() for party in value.split(",") if party.strip()]
        return value

    class Config:
        env_file = ".env"


settings = Settings()
