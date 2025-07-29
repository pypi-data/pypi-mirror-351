"""
Configuration management for AI Voice Generator.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_api_config():
    """Load API keys and credentials from environment variables."""
    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "elevenlabs_api_key": (
            os.getenv("ELEVENLABS_API_KEY")
            or os.getenv("ELEVEN_API_KEY")
            or os.getenv("XI_API_KEY")
        ),
        "google_application_credentials": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        "gemini_api_key": (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
    }

    logger.info("API configuration loaded from environment variables.")

    # Log which keys are found (without exposing the actual keys)
    for key, value in config.items():
        if value:
            logger.debug(f"{key} is set.")
        else:
            logger.debug(f"{key} is not set.")

    return config


# Load configuration
API_CONFIG = load_api_config()

# Database and cache configuration
DB_PATH = Path("history.db")
MAX_CACHE_SIZE = 100
ENV_FILE_PATH = Path(".env")

# Simple in-memory cache for TTS results
TTS_CACHE = {}
CACHE_KEYS_ORDER = []  # For LRU-like policy
