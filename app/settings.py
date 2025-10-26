from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #DATABASE
    DATABASE_URL: str
    DATABASE_URL_LOCAL: str

    # AUTH
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    #EMAIL
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    #APP CONFIG
    DEBUG: bool = True
    ENV: str = "development"

    #OTHER
    PROJECT_NAME: str = "IdeaBridge"

    #Config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
