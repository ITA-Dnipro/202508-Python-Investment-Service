from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")
    SERVICE_HOST: str = Field(default="0.0.0.0")
    SERVICE_PORT: int = Field(default=8005)

    GATEWAY_BASE: str = Field(default="http://krakend:8080")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
