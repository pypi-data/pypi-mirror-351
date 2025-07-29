"""
Main Flask application module for AI Voice Generator.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .database import init_database
from .providers import init_providers
from .routes import register_routes


def create_app(config=None):
    """
    Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary

    Returns:
        Flask: Configured Flask application instance
    """
    # Determine paths relative to package location
    package_dir = Path(__file__).parent
    static_folder = package_dir / "static"

    app = Flask(__name__, static_folder=str(static_folder))
    CORS(app)

    # Load environment variables
    env_file_path = Path(".env")
    if env_file_path.exists():
        load_dotenv(env_file_path)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Apply any custom configuration
    if config:
        app.config.update(config)

    # Initialize database
    init_database()

    # Initialize TTS providers
    init_providers()

    # Register routes
    register_routes(app)

    return app


def run_app():
    """Run the Flask application."""
    app = create_app()
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    run_app()
