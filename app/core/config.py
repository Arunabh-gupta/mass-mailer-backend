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
    aws_region: str = "us-east-1"
    aws_profile: str | None = None
    aws_sqs_endpoint_url: str | None = None
    aws_sqs_campaign_send_queue_url: str | None = None

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

    @field_validator("aws_profile", "aws_sqs_endpoint_url", "aws_sqs_campaign_send_queue_url", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value

    class Config:
        env_file = ".env"


settings = Settings()
