
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Patient Follow-Up Manager"

    DB_HOST: str = "localhost"

    DB_PORT: int = 3306

    DB_USER: str

    DB_PASSWORD: str

    DB_NAME: str

    APP_ENV: str = "development"

    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Gmail SMTP configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_APP_PASSWORD: str
    SMTP_FROM_EMAIL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
