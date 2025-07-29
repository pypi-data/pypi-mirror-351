"""
AI Voice Generator - Multi-provider Text-to-Speech web application.

A production-ready web application that converts text to speech using multiple TTS providers
including OpenAI, ElevenLabs, Google Cloud, and Gemini. Features intelligent text optimization,
advanced voice controls, persistent history, and a sleek dark-themed interface.
"""

__version__ = "1.5.2"
__author__ = "AI Voice Generator Team"
__email__ = "support@aivoicegen.com"
__license__ = "MIT"

from .app import create_app, init_database

__all__ = ["create_app", "init_database", "__version__"]
