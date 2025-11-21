from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    SECRET_KEY: str = "your-secret-key-change-in-production"  #
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI JWT Auth"

    # Email settings for fastapi-mail
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_FROM_NAME: str = PROJECT_NAME

    # Frontend URL for constructing links in emails
    CLIENT_BASE_URL: str = "http://localhost:5173"

    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
