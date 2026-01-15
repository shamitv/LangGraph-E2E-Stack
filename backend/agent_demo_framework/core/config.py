from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
import agent_demo_framework

# Explicitly load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    PROJECT_NAME: str = "LangGraph E2E Demo"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./langgraph_demo.db"
    
    # Data Directory (package-relative)
    DATA_DIR: str = os.path.join(
        os.path.dirname(os.path.abspath(agent_demo_framework.__file__)),
        "data",
    )
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_MODEL_NAME: str = "gpt-5-nano"

    # Healthcare Agent Configuration
    HEALTHCARE_RECURSION_LIMIT: int = 100
    HEALTHCARE_STREAM_NODES: Optional[List[str]] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
