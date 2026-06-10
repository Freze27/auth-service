from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_TTL_MINUTES: int
    REFRESH_TOKEN_TTL_DAYS: int
    LOG_LEVEL: str = "INFO"


settings = Settings()
