from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "Budget Planner API"
    env: str = os.getenv("ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./budget_planner.db")
    cors_origins: list[str] = [
        "http://localhost",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


settings = Settings()