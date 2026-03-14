from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str
    app_name: str
    debug: bool = False
    database_url: str
    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_allowed_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    class Config:
        env_file = ".env"

settings = Settings()
