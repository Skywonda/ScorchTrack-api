import os
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ScorchTrack API"
    
    DATABASE_URL: str
    
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    WHATSAPP_API_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_VERIFY_TOKEN: str
    WHATSAPP_GROUP_ID: str  
    BOT_USER_ID: str  
    
    GREEN_API_INSTANCE_ID: str
    GREEN_API_ACCESS_TOKEN: str
    GREEN_API_WEBHOOK_TOKEN: str
    
    GEMINI_API_KEY: str
    
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0") 
    
    CORS_ORIGINS: list[str] = ["*"]  
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'
    )

settings = Settings()