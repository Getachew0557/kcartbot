"""Configuration settings for KcartBot application."""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    gemini_api_key: str
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Configuration
    database_url: str
    vector_db_path: str = "./chroma_db"
    
    # Language Configuration
    default_language: str = "en"
    supported_languages: str = "en,am,am-latn"
    
    # Application Settings
    app_name: str = "KcartBot"
    app_version: str = "1.0.0"
    
    @property
    def supported_languages_list(self) -> List[str]:
        """Convert comma-separated string to list."""
        return [lang.strip() for lang in self.supported_languages.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

