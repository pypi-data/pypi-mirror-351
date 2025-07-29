"""
Flask routes for AI Voice Generator.
"""

import io
import json
import logging
import os
import platform
import subprocess
from pathlib import Path

from flask import Response, jsonify, request, send_file

from .config import CACHE_KEYS_ORDER, MAX_CACHE_SIZE, TTS_CACHE, config
from .database import get_db_connection
from .providers import get_providers_config

logger = logging.getLogger(__name__)


def register_routes(app):
    """Register all routes with the Flask app."""

    @app.route("/")
    def index():
        """Serve the main frontend page."""
        return app.send_static_file("index.html")

    @app.route("/outputs/<filename>")
    def serve_audio_file(filename):
        """Serve audio files from the outputs directory."""
        try:
            outputs_dir = config.get_output_dir()
            if not outputs_dir.exists():
                return jsonify({"error": "Outputs directory not found"}), 404

            file_path = outputs_dir / filename
            if not file_path.exists():
                return jsonify({"error": "Audio file not found"}), 404

            # Security check - ensure file is in outputs directory
            if not str(file_path.resolve()).startswith(str(outputs_dir.resolve())):
                return jsonify({"error": "Invalid file path"}), 403

            return send_file(file_path, mimetype="audio/mp3", as_attachment=False)
        except Exception as e:
            logger.error(f"Error serving audio file {filename}: {str(e)}")
            return jsonify({"error": "Failed to serve audio file"}), 500

    @app.route("/services", methods=["GET"])
    def get_services():
        """Get list of available TTS services."""
        providers_config = get_providers_config()
        services_response = {}

        for provider_name, config in providers_config.items():
            is_configured = config["instance"] is not None
            services_response[provider_name] = {
                "label": config["label"],
                "configured": is_configured,
                "voices_endpoint": f"/voices/{provider_name}",
                "voice_type": config.get("voice_type", "dynamic"),
                "unavailable_reason": (
                    config["unavailable_reason"] if not is_configured else None
                ),
            }
        return jsonify(services_response)

    @app.route("/voices/<service_name>", methods=["GET"])
    def get_voices_by_service(service_name):
        """Get voices for a specific service."""
        service_name_lower = service_name.lower()
        providers_config = get_providers_config()
        provider_config = providers_config.get(service_name_lower)

        if not provider_config:
            logger.warning(
                f"/voices endpoint called with unknown service: {service_name}"
            )
            return jsonify({"error": f"Service '{service_name}' not found."}), 404

        if not provider_config["instance"]:
            logger.warning(
                f"/voices endpoint called for unavailable service: {service_name}"
            )
            return (
                jsonify(
                    {
                        "error": f"Service '{service_name}' is not configured or unavailable."
                    }
                ),
                503,
            )

        try:
            voices = provider_config["instance"].list_voices()
            return jsonify(voices)
        except RuntimeError as e:
            logger.error(f"Error listing voices for {service_name}: {e}")
            return (
                jsonify(
                    {"error": f"Failed to list voices for {service_name}: {str(e)}"}
                ),
                500,
            )
        except Exception as e:
            logger.error(f"Unexpected error listing voices for {service_name}: {e}")
            return (
                jsonify(
                    {
                        "error": f"An unexpected error occurred while listing voices for {service_name}."
                    }
                ),
                500,
            )

    @app.route("/generate", methods=["POST"])
    def generate_speech_route():
        """Generate speech from text."""
        try:
            data = request.json
            if not data:
                return jsonify({"error": "No JSON data received"}), 400

            service_name = data.get("service")
            title = data.get("title")
            text = data.get("text")
            voice_model_options = data.get("voice_model_options", {})

            if not all([service_name, title, text]):
                missing = [
                    field
                    for field in ["service", "title", "text"]
                    if not data.get(field)
                ]
                return (
                    jsonify(
                        {"error": f"Missing required fields: {', '.join(missing)}"}
                    ),
                    400,
                )

            service_name_lower = service_name.lower()
            providers_config = get_providers_config()

            if service_name_lower not in providers_config:
                return jsonify({"error": f"Unsupported service: {service_name}"}), 400

            provider_config = providers_config[service_name_lower]

            if not provider_config["instance"]:
                return (
                    jsonify(
                        {
                            "error": f"{provider_config['label']} provider is not available"
                        }
                    ),
                    503,
                )

            provider_instance = provider_config["instance"]

            # Create cache key
            stable_voice_options = tuple(
                sorted(voice_model_options.get("api_params", {}).items())
            )
            cache_key_parts = (service_name_lower, text, stable_voice_options)
            cache_key = hash(cache_key_parts)

            # Check cache
            if cache_key in TTS_CACHE:
                logger.info(f"Cache hit for key: {cache_key}")
                cached_audio_content, cached_output_file_name = TTS_CACHE[cache_key]

                # Move key to end for LRU
                if cache_key in CACHE_KEYS_ORDER:
                    CACHE_KEYS_ORDER.remove(cache_key)
                CACHE_KEYS_ORDER.append(cache_key)

                return send_file(
                    io.BytesIO(cached_audio_content),
                    mimetype="audio/mp3",
                    as_attachment=True,
                    download_name=cached_output_file_name,
                )

            logger.info(f"Cache miss for key: {cache_key}")

            try:
                audio_content, output_file_name = provider_instance.generate_speech(
                    text, title, voice_model_options
                )
            except ConnectionError as e:
                logger.error(
                    f"Connection error with {service_name_lower} provider: {e}"
                )
                return (
                    jsonify(
                        {
                            "error": f"Connection error with {service_name_lower} provider: {str(e)}"
                        }
                    ),
                    503,
                )
            except RuntimeError as e:
                logger.error(f"Runtime error with {service_name_lower} provider: {e}")
                return (
                    jsonify(
                        {"error": f"Error with {service_name_lower} provider: {str(e)}"}
                    ),
                    500,
                )
            except ValueError as ve:
                logger.error(
                    f"Input validation error for {service_name_lower} provider: {ve}"
                )
                return jsonify({"error": str(ve)}), 400
            except Exception as e:
                logger.error(
                    f"Unexpected error with {service_name_lower} provider: {e}"
                )
                return (
                    jsonify(
                        {
                            "error": f"Unexpected error with {service_name_lower} provider: {str(e)}"
                        }
                    ),
                    500,
                )

            if audio_content and output_file_name:
                # Save file to outputs directory
                outputs_dir = config.get_output_dir()
                file_path = outputs_dir / output_file_name

                with open(file_path, "wb") as f:
                    f.write(audio_content)
                logger.info(f"Audio file saved to: {file_path}")

                # Store in database
                try:
                    with get_db_connection() as conn:
                        conn.execute(
                            """INSERT INTO generation_history 
                               (title, service, voice, text_snippet, filename, file_path)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (
                                title,
                                service_name_lower,
                                str(
                                    voice_model_options.get("api_params", {}).get(
                                        "voice", "default"
                                    )
                                ),
                                text[:100] + "..." if len(text) > 100 else text,
                                output_file_name,
                                str(file_path.absolute()),
                            ),
                        )
                        conn.commit()
                    logger.info(f"Generation history saved to database")
                except Exception as e:
                    logger.error(f"Failed to save to database: {e}")

                # Store in cache
                if len(TTS_CACHE) >= MAX_CACHE_SIZE:
                    oldest_key = CACHE_KEYS_ORDER.pop(0)
                    del TTS_CACHE[oldest_key]
                    logger.info(f"Cache full. Removed oldest key: {oldest_key}")

                TTS_CACHE[cache_key] = (audio_content, output_file_name)
                CACHE_KEYS_ORDER.append(cache_key)
                logger.info(
                    f"Stored in cache. Key: {cache_key}. Cache size: {len(TTS_CACHE)}"
                )

                return send_file(
                    io.BytesIO(audio_content),
                    mimetype="audio/mp3",
                    as_attachment=True,
                    download_name=output_file_name,
                )
            else:
                logger.error("Audio generation failed for unknown reasons.")
                return (
                    jsonify({"error": "Audio generation failed for unknown reasons."}),
                    500,
                )

        except ValueError as ve:
            logger.error(f"General validation error: {str(ve)}")
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            logger.error(f"Unexpected critical error: {str(e)}")
            return (
                jsonify(
                    {"error": "An unexpected critical error occurred on the server."}
                ),
                500,
            )

    @app.route("/history", methods=["GET"])
    def get_history():
        """Get generation history from database."""
        try:
            with get_db_connection() as conn:
                cursor = conn.execute(
                    """SELECT id, title, service, voice, text_snippet, filename, 
                              timestamp, file_path 
                       FROM generation_history 
                       ORDER BY timestamp DESC"""
                )
                history = []
                for row in cursor.fetchall():
                    history.append(
                        {
                            "id": row["id"],
                            "title": row["title"],
                            "service": row["service"],
                            "voice": row["voice"],
                            "text_snippet": row["text_snippet"],
                            "filename": row["filename"],
                            "timestamp": row["timestamp"],
                            "file_path": row["file_path"],
                        }
                    )
            return jsonify(history), 200
        except Exception as e:
            logger.error(f"Error retrieving history: {str(e)}")
            return jsonify({"error": f"Failed to retrieve history: {str(e)}"}), 500

    @app.route("/history", methods=["DELETE"])
    def clear_history():
        """Clear all generation history."""
        try:
            with get_db_connection() as conn:
                conn.execute("DELETE FROM generation_history")
                conn.commit()
            logger.info("Generation history cleared")
            return jsonify({"message": "History cleared successfully"}), 200
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            return jsonify({"error": f"Failed to clear history: {str(e)}"}), 500

    @app.route("/optimize", methods=["POST"])
    def optimize_text():
        """Optimize text using AI providers."""
        try:
            data = request.json
            if not data:
                return jsonify({"error": "No JSON data received"}), 400

            text = data.get("text")
            service = data.get("service", "openai")
            mode = data.get("mode", "default")

            if not text:
                return jsonify({"error": "Text is required"}), 400

            # Try to use actual AI optimization
            try:
                from .config import config
                openai_key = config.get("OPENAI_API_KEY")
                
                if openai_key:
                    import openai
                    client = openai.OpenAI(api_key=openai_key)
                    
                    # Create optimization prompt based on mode
                    if mode == "shorter":
                        prompt = f"Make this text shorter and more concise while keeping the main message for text-to-speech: {text}"
                    elif mode == "longer":
                        prompt = f"Expand this text with more detail and context for text-to-speech narration: {text}"
                    elif mode == "retry":
                        prompt = f"Rewrite this text in a different way but with the same meaning for text-to-speech: {text}"
                    else:  # default
                        prompt = f"Optimize this text for text-to-speech by improving clarity, flow, and pronunciation: {text}"
                    
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=500,
                        temperature=0.7
                    )
                    
                    optimized_text = response.choices[0].message.content.strip()
                    
                else:
                    # Fallback to basic optimization if no API key
                    optimized_text = text.replace(" & ", " and ").replace("$", " dollars").replace("%", " percent")
                    
            except Exception as ai_error:
                logger.warning(f"AI optimization failed, using fallback: {str(ai_error)}")
                # Basic text improvements for TTS
                optimized_text = text.replace(" & ", " and ").replace("$", " dollars").replace("%", " percent")
            
            return jsonify({"optimized_text": optimized_text}), 200
        except Exception as e:
            logger.error(f"Error in text optimization: {str(e)}")
            return jsonify({"error": f"Text optimization failed: {str(e)}"}), 500

    @app.route("/analyze-emotion", methods=["POST"])
    def analyze_emotion():
        """Analyze emotion in text and suggest voice parameters."""
        try:
            data = request.json
            if not data:
                return jsonify({"error": "No JSON data received"}), 400

            text = data.get("text")
            service = data.get("service", "openai")
            voice_model_options = data.get("voice_model_options", {})

            if not text:
                return jsonify({"error": "Text is required"}), 400

            # Simple emotion analysis - in a full implementation this would
            # use AI to detect emotions and adjust voice parameters
            emotion_response = {
                "emotion": "neutral",
                "confidence": 0.8,
                "original_params": voice_model_options,
                "suggested_params": voice_model_options,
                "emotion_description": "Neutral tone detected"
            }
            
            return jsonify(emotion_response), 200
        except Exception as e:
            logger.error(f"Error in emotion analysis: {str(e)}")
            return jsonify({"error": f"Emotion analysis failed: {str(e)}"}), 500

    @app.route("/api-config", methods=["GET"])
    def get_api_config():
        """Get API configuration status."""
        try:
            from .config import config
            
            # Structure that matches frontend expectations
            config_status = {
                "openai": {
                    "configured": bool(config.get("OPENAI_API_KEY"))
                },
                "elevenlabs": {
                    "configured": bool(config.get("ELEVENLABS_API_KEY"))
                },
                "gemini": {
                    "configured": bool(config.get("GEMINI_API_KEY"))
                },
                "google": {
                    "configured": bool(config.get("GOOGLE_APPLICATION_CREDENTIALS"))
                },
                "config_file": str(config.config_file),
                "output_dir": str(config.get_output_dir())
            }
            
            return jsonify(config_status), 200
        except Exception as e:
            logger.error(f"Error getting API config: {str(e)}")
            return jsonify({"error": f"Failed to fetch API config status: {str(e)}"}), 500

    @app.route("/api-config", methods=["POST"])
    def update_api_config():
        """Update API configuration."""
        try:
            # Debug the request
            logger.info(f"API config update request - Content-Type: {request.headers.get('Content-Type')}")
            logger.info(f"Raw data: {request.get_data()}")
            
            data = request.json
            logger.info(f"Parsed JSON data: {data}")
            
            if data is None:
                logger.error("request.json returned None")
                return jsonify({"error": "No JSON data received - check Content-Type header"}), 400
            
            # Allow empty data (user might be clearing keys)
            from .config import config
            
            if len(data) == 0:
                logger.info("Empty data received - no keys to update")
                return jsonify({"message": "No configuration changes to save"}), 200
            
            updated_keys = []
            for key, value in data.items():
                if key.endswith("_API_KEY") or key == "GOOGLE_APPLICATION_CREDENTIALS":
                    if value and value.strip():  # Only set non-empty values
                        config.set(key, value.strip())
                        updated_keys.append(key)
                        logger.info(f"Updated {key}")
            
            message = f"Configuration updated successfully. Keys updated: {', '.join(updated_keys)}" if updated_keys else "No valid keys provided to update"
            return jsonify({"message": message}), 200
            
        except Exception as e:
            logger.error(f"Error updating API config: {str(e)}")
            return jsonify({"error": f"Failed to update API config: {str(e)}"}), 500

    @app.route("/open-downloads", methods=["GET"])
    def open_downloads_folder():
        """Open the downloads folder in the file manager."""
        try:
            # Get the downloads directory (same logic as in generate route)
            home_dir = Path.home()
            downloads_dir = home_dir / "Downloads" / "aivoicegen"
            
            # Create the directory if it doesn't exist
            downloads_dir.mkdir(parents=True, exist_ok=True)
            
            # Open the folder based on the operating system
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", str(downloads_dir)], check=True)
            elif system == "Windows":
                subprocess.run(["explorer", str(downloads_dir)], check=True)
            elif system == "Linux":
                subprocess.run(["xdg-open", str(downloads_dir)], check=True)
            else:
                return jsonify({"error": f"Unsupported operating system: {system}"}), 400
            
            return jsonify({"message": f"Downloads folder opened: {downloads_dir}"}), 200
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to open downloads folder: {str(e)}")
            return jsonify({"error": "Failed to open downloads folder"}), 500
        except Exception as e:
            logger.error(f"Error opening downloads folder: {str(e)}")
            return jsonify({"error": f"Error opening downloads folder: {str(e)}"}), 500
