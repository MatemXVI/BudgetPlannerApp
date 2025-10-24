from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore',)
    app_name: str = 'Budget Planner API'
    env: str = 'development'
    database_url: str = 'sqlite:///./budget_planner.db'
    cors_origins: List[str] = ['http://localhost','http://localhost:5173','http://127.0.0.1:5173']

    google_client_id: Optional[str] = None     # GOOGLE_CLIENT_ID
    google_client_secret: Optional[str] = None # GOOGLE_CLIENT_SECRET
    server_base_url: str = 'http://localhost:8000'  # SERVER_BASE_URL

settings = Settings()