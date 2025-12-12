from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CLOUDRU_API_KEY: str
    CLOUDRU_BASE_URL: str
    CLOUDRU_MODEL: str

    class Config:
        env_file = ".env"

settings = Settings()
