"""
Configuration module for the Practice Routines API.

This module centralizes all configuration settings and supports
environment-based configurations (development/production).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""

    # Environment
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # ChromaDB Configuration
    DB_PATH = os.getenv("CHROMA_DB_PATH", "../data/chroma_data")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "guitar_routines")

    # Flask Configuration
    FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5050"))

    # CORS Configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")  # In production, set to specific origins

    # Routines Data
    ROUTINES_FILE = os.getenv("ROUTINES_FILE", "routines/routines.json")

    @classmethod
    def validate(cls):
        """
        Validate required configuration settings.

        Raises:
            ValueError: If required settings are missing or invalid.
        """
        errors = []

        # Validate required settings
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required. Set it in your .env file.")

        if not cls.COLLECTION_NAME:
            errors.append("COLLECTION_NAME cannot be empty.")

        if not cls.DB_PATH:
            errors.append("CHROMA_DB_PATH cannot be empty.")

        # Check if routines file exists
        if not Path(cls.ROUTINES_FILE).exists():
            errors.append(f"Routines file not found: {cls.ROUTINES_FILE}")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {err}" for err in errors))

    @classmethod
    def get_summary(cls):
        """
        Get a summary of current configuration (for debugging).

        Returns:
            dict: Configuration summary with sensitive values masked.
        """
        return {
            "env": cls.ENV,
            "debug": cls.DEBUG,
            "openai_api_key": "***" + cls.OPENAI_API_KEY[-4:] if cls.OPENAI_API_KEY else "NOT SET",
            "embedding_model": cls.EMBEDDING_MODEL,
            "db_path": cls.DB_PATH,
            "collection_name": cls.COLLECTION_NAME,
            "flask_host": cls.FLASK_HOST,
            "flask_port": cls.FLASK_PORT,
            "cors_origins": cls.CORS_ORIGINS,
            "routines_file": cls.ROUTINES_FILE,
        }


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    FLASK_HOST = "127.0.0.1"


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False

    @classmethod
    def validate(cls):
        """Additional production validation."""
        super().validate()

        # In production, CORS should not be wide open
        if cls.CORS_ORIGINS == "*":
            print("WARNING: CORS is set to '*' in production. Consider restricting to specific origins.")


# Select configuration based on environment
def get_config():
    """
    Get the appropriate configuration class based on environment.

    Returns:
        Config: Configuration class instance.
    """
    env = os.getenv("FLASK_ENV", "development")

    if env == "production":
        return ProductionConfig
    else:
        return DevelopmentConfig


# Get active configuration
settings = get_config()

# Validate configuration on module import
settings.validate()
