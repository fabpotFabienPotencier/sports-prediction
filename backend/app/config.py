from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    
    # App settings
    APP_NAME: str = "Sports Prediction Bot"
    DEBUG: bool = False
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 