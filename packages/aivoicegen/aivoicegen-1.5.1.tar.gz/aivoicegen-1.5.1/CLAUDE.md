# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python app.py
```
The application runs on `http://127.0.0.1:5000/`

### Alternative: Using the CLI
```bash
# Install and run via CLI
pip install -e .
aivoicegen

# Configuration management
aivoicegen config init
aivoicegen config list
aivoicegen config set --key OPENAI_API_KEY
```

### Running Tests
```bash
python -m unittest discover tests
```

### Virtual Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## Configuration

### New Configuration System (v1.1.0+)
The application now uses a centralized configuration system:

- **Config File**: `~/.aivoicegen/config.json`
- **Output Directory**: `~/Downloads/AIVoiceGen/` (platform-aware)
- **Interactive Setup**: `aivoicegen config init`

### Environment Variables (Fallback)
Required environment variables for TTS providers:
- `OPENAI_API_KEY`: For OpenAI TTS
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud service account JSON
- `ELEVENLABS_API_KEY`: For ElevenLabs TTS
- `GEMINI_API_KEY`: Optional fallback for voice listing

## Architecture Overview

AIVoiceGen is a Flask-based TTS web application using a **provider pattern** to support multiple Text-to-Speech services.

### Provider Pattern Implementation
Each TTS provider (OpenAI, Gemini/Google Cloud, ElevenLabs) is implemented as a class with:
- `__init__()`: Initializes API clients using configuration system
- `list_voices()`: Returns available voices with metadata
- `generate_speech()`: Converts text to audio bytes

Providers are instantiated globally at startup. Failed providers are set to `None` for graceful degradation.

### Key API Endpoints
- `GET /services`: Lists available TTS services
- `GET /voices/<service_name>`: Returns voices for a service
- `POST /generate`: Main TTS generation endpoint
- `GET /`: Serves the frontend

### Audio Processing
- **OpenAI**: Chunks text (3000 char limit) and concatenates audio segments
- **Other providers**: Direct synthesis without chunking
- All audio returned as MP3 via BytesIO (no temporary files)
- Files saved to user's Downloads directory automatically

### Frontend Architecture
Single-page application in `static/index.html` using:
- Vanilla JavaScript (no framework)
- Bulma CSS for styling
- Dynamic service/voice loading from backend APIs
- File upload and audio playback capabilities

### Configuration Management
The application uses a hybrid configuration approach:
- **Primary**: JSON config file at `~/.aivoicegen/config.json`
- **Fallback**: Environment variables for backward compatibility
- **CLI Management**: Interactive setup and management commands

### Error Handling Pattern
- Provider initialization failures are caught and logged
- Runtime errors return appropriate HTTP status codes (400, 500, 503)
- Frontend displays errors via toast notifications
- Each provider can fail independently without affecting others

### File Management
- **Smart Output Directory**: Platform-aware Downloads folder detection
- **Organized Storage**: Files saved to `Downloads/AIVoiceGen/`
- **Database Tracking**: SQLite database for generation history
- **Security**: Path validation for served files

## Development Notes

### Package Structure
```
aivoicegen/
├── __init__.py          # Package initialization
├── app.py               # Flask application factory
├── cli.py               # Command-line interface
├── config.py            # Configuration management
├── database.py          # Database operations
├── providers.py         # TTS provider implementations
├── routes.py            # Flask route handlers
└── static/
    └── index.html       # Frontend application
```

## Documentation Structure

The `/docs/` directory contains comprehensive project documentation:

| File | Purpose | When to Reference |
|------|---------|-------------------|
| **`secrets.md`** | API key setup guide | When user needs TTS provider configuration |
| **`PRD.md`** | Product Requirements Document | For understanding user stories and requirements |
| **`design.md`** | System architecture and design | For technical implementation questions |
| **`future_architecture.md`** | Planned enhancements | For roadmap and feature planning |
| **`todolist.md`** | Development tasks | For tracking project progress |

### Using Documentation for Development

**When helping users:**
1. **Configuration issues**: Reference `docs/secrets.md` for API setup
2. **Architecture questions**: Use `docs/design.md` for system understanding
3. **Feature requests**: Check `docs/PRD.md` for user stories and requirements
4. **Technical implementation**: Combine `docs/design.md` with code analysis

**Documentation Principles:**
- Keep docs synchronized with code changes
- Update relevant docs when modifying architecture
- Reference specific doc sections when providing guidance
- Use docs to understand user intent and system design

### Important Instructions
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.