"""Configuration settings for the application."""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    GOOGLE_API_KEY: str = ""
    
    # Model Settings
    GEMINI_FLASH_MODEL: str = "gemini-3-flash-preview"
    GEMINI_IMAGE_MODEL: str = "gemini-3-pro-image-preview"
    
    # Thinking Level: minimal, low, medium, high
    THINKING_LEVEL: str = "medium"
    
    # File Storage
    UPLOAD_DIR: str = "data/uploads"
    VECTORDB_DIR: str = "data/vectordb"
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
