from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Base App"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql://localhost/base_app"
    AUTH_ENABLED: bool = False
    CURRENT_USER: str = "system"
    REDIS_URL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
