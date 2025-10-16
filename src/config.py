"""Configuration settings for KcartBot application."""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    gemini_api_key: str = "AIzaSyDayv0ihMD5eyVHZWs3LqRw8BWshFAOM98"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Configuration
    database_url: str = "sqlite:///./kcartbot.db"
    vector_db_path: str = "./chroma_db"
    
    # Language Configuration
    default_language: str = "en"
    supported_languages: List[str] = ["en", "am", "am-latn"]
    
    # Application Settings
    app_name: str = "KcartBot"
    app_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

