"""
Configuration management for AI Voice Generator.
"""

import json
import logging
import os
import platform
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Handles configuration management for AIVoiceGen."""
    
    def __init__(self):
        self.config_dir = Path.home() / '.aivoicegen'
        self.config_file = self.config_dir / 'config.json'
        self._config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def _save_config(self):
        """Save configuration to file."""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value, fallback to environment variable."""
        # First check config file
        if key in self._config:
            return self._config[key]
        
        # Fallback to environment variable
        env_value = os.getenv(key)
        if env_value:
            return env_value
            
        return default
    
    def set(self, key: str, value: str):
        """Set configuration value."""
        self._config[key] = value
        self._save_config()
    
    def get_downloads_dir(self) -> Path:
        """Get platform-specific downloads directory."""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return Path.home() / "Downloads"
        elif system == "Windows":
            return Path.home() / "Downloads"
        else:  # Linux
            # Try XDG user dirs first
            try:
                import subprocess
                result = subprocess.run(
                    ['xdg-user-dir', 'DOWNLOAD'], 
                    capture_output=True, text=True, check=True
                )
                return Path(result.stdout.strip())
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to common locations
                downloads_dir = Path.home() / "Downloads"
                if downloads_dir.exists():
                    return downloads_dir
                return Path.home() / "downloads"
    
    def get_output_dir(self) -> Path:
        """Get output directory for generated audio files."""
        custom_dir = self.get('OUTPUT_DIR')
        if custom_dir:
            return Path(custom_dir)
        
        # Default to Downloads/AIVoiceGen
        output_dir = self.get_downloads_dir() / "AIVoiceGen"
        output_dir.mkdir(exist_ok=True)
        return output_dir


# Global config instance
config = Config()


def load_api_config():
    """Load API keys and credentials from config file or environment variables."""
    api_config = {
        "openai_api_key": config.get("OPENAI_API_KEY"),
        "elevenlabs_api_key": (
            config.get("ELEVENLABS_API_KEY")
            or config.get("ELEVEN_API_KEY")
            or config.get("XI_API_KEY")
        ),
        "google_application_credentials": config.get("GOOGLE_APPLICATION_CREDENTIALS"),
        "gemini_api_key": (config.get("GEMINI_API_KEY") or config.get("GOOGLE_API_KEY")),
    }

    logger.info("API configuration loaded from config file and environment variables.")

    # Log which keys are found (without exposing the actual keys)
    for key, value in api_config.items():
        if value:
            logger.debug(f"{key} is set.")
        else:
            logger.debug(f"{key} is not set.")

    return api_config


# Load configuration
API_CONFIG = load_api_config()

# Database and cache configuration
DB_PATH = Path("history.db")
MAX_CACHE_SIZE = 100
ENV_FILE_PATH = Path(".env")

# Simple in-memory cache for TTS results
TTS_CACHE = {}
CACHE_KEYS_ORDER = []  # For LRU-like policy
