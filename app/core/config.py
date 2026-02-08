from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str
    app_name: str
    debug: bool = False
    database_url: str
    class Config:
        env_file = ".env"

settings = Settings()