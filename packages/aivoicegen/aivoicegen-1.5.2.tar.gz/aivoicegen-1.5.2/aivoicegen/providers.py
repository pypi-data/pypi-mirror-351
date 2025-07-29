"""
TTS Provider implementations for AI Voice Generator.
"""

import base64
import io
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import google.auth
import google.generativeai as genai
import requests
from elevenlabs import Voice, VoiceSettings
from elevenlabs.client import ElevenLabs
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import texttospeech_v1 as texttospeech
from google.oauth2 import service_account
from openai import OpenAI
from pydub import AudioSegment

from .config import API_CONFIG

logger = logging.getLogger(__name__)

# Global provider instances
openai_provider_instance = None
google_cloud_provider_instance = None
gemini_provider_instance = None
elevenlabs_provider_instance = None


class OpenAITTSProvider:
    """OpenAI Text-to-Speech provider."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.OpenAITTSProvider")
        api_key = API_CONFIG.get("openai_api_key")
        if not api_key:
            self.logger.error("OpenAI API key not found in API_CONFIG.")
            self.client = None
            raise ConnectionError("OpenAI API key not configured on server.")
        else:
            self.client = OpenAI(api_key=api_key)
            self.logger.info("OpenAITTSProvider initialized successfully.")

    def list_voices(self):
        """List available OpenAI voices."""
        self.logger.debug("Listing OpenAI voices (static list).")
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        models = ["tts-1", "tts-1-hd"]
        options = []
        for voice_name_val in voices:
            for model_name_val in models:
                options.append(
                    {
                        "voice_id": f"{voice_name_val}_{model_name_val}",
                        "name": f"{voice_name_val.capitalize()} ({model_name_val})",
                        "api_params": {
                            "voice": voice_name_val,
                            "model": model_name_val,
                        },
                    }
                )
        return options

    def _chunk_text(self, text, max_length=3000):
        """Split text into chunks while preserving sentence boundaries."""
        sentences = text.replace("\n", " ").split(". ")
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            if sentence != sentences[-1] or (
                sentence == sentences[-1] and not text.endswith(".")
            ):
                sentence += "."

            sentence_length = len(sentence) + (1 if current_chunk else 0)

            if current_length + sentence_length > max_length:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence.strip()]
                current_length = len(sentence.strip())
            else:
                current_chunk.append(sentence.strip())
                current_length += sentence_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return [chunk for chunk in chunks if chunk]

    def _concatenate_audio_files(self, audio_files):
        """Concatenate multiple audio files into a single AudioSegment."""
        combined = AudioSegment.empty()
        for audio_file_path in audio_files:
            try:
                segment = AudioSegment.from_mp3(audio_file_path)
                combined += segment
            except Exception as e:
                self.logger.error(
                    f"Error loading audio file {audio_file_path}: {str(e)}"
                )
                raise Exception(
                    f"Audio processing error with {os.path.basename(audio_file_path)}: {str(e)}"
                )
        return combined

    def generate_speech(self, text, title, voice_model_options=None):
        """Generate speech using OpenAI TTS."""
        if self.client is None:
            self.logger.error("OpenAI client not initialized. Cannot generate speech.")
            raise ConnectionError(
                "OpenAI provider is not configured (API key missing)."
            )

        if not text or not text.strip():
            self.logger.error("Input text is empty or whitespace only.")
            raise ValueError("Input text cannot be empty.")

        if voice_model_options is None:
            voice_model_options = {}

        api_params = voice_model_options.get("api_params", {})
        model = api_params.get("model", "tts-1")
        voice = api_params.get("voice", "alloy")
        speed = api_params.get("speed", 1.0)

        self.logger.debug(
            f"Generating speech with OpenAI. Model: {model}, Voice: {voice}, Speed: {speed}"
        )

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                text_chunks = self._chunk_text(text)

                if not text_chunks:
                    raise ValueError("No processable text chunks found for OpenAI.")

                audio_files = []
                for i, chunk_text_val in enumerate(text_chunks):
                    if not chunk_text_val.strip():
                        continue

                    response = self.client.audio.speech.create(
                        model=model, voice=voice, input=chunk_text_val, speed=speed
                    )
                    chunk_file = os.path.join(temp_dir, f"openai_chunk_{i}.mp3")
                    with open(chunk_file, "wb") as f:
                        f.write(response.content)

                    audio_files.append(chunk_file)

                if not audio_files:
                    raise Exception("No audio files were generated.")

                combined_audio = self._concatenate_audio_files(audio_files)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                output_file_name = f"{title.replace(' ', '_')}_openai_{timestamp}.mp3"
                output_file_path = os.path.join(temp_dir, output_file_name)

                combined_audio.export(output_file_path, format="mp3")

                with open(output_file_path, "rb") as f:
                    final_audio_content = f.read()

                return final_audio_content, output_file_name

        except ValueError as ve:
            self.logger.error(f"ValueError in generate_speech: {str(ve)}")
            raise
        except Exception as e:
            self.logger.error(f"OpenAI speech generation failed: {str(e)}")
            raise Exception(f"OpenAI speech generation failed: {str(e)}")


class GoogleCloudTTSProvider:
    """Google Cloud Text-to-Speech provider."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.GoogleCloudTTSProvider")
        self.credentials_path = API_CONFIG.get("google_application_credentials")
        self.client = None

        try:
            if self.credentials_path:
                if not os.path.exists(self.credentials_path):
                    self.logger.error(
                        f"Google credentials path does not exist: {self.credentials_path}"
                    )
                else:
                    self.client = (
                        texttospeech.TextToSpeechClient.from_service_account_file(
                            self.credentials_path
                        )
                    )
                    self.logger.info(
                        f"GoogleCloudTTSProvider initialized with service account: {self.credentials_path}"
                    )
            else:
                self.client = texttospeech.TextToSpeechClient()
                self.logger.info(
                    "GoogleCloudTTSProvider attempting to initialize using default application credentials."
                )
        except DefaultCredentialsError as e:
            self.logger.error(f"Google Cloud Default Credentials not found: {e}")
            self.client = None
        except Exception as e:
            self.logger.error(f"Failed to initialize GoogleCloudTTSProvider: {e}")
            self.client = None

    def list_voices(self):
        """List available Google Cloud voices."""
        self.logger.debug("Listing Google Cloud Text-to-Speech voices.")
        if not self.client:
            self.logger.error("GoogleCloudTTSProvider client not initialized.")
            return []

        try:
            response = self.client.list_voices()

            voices_list = []
            for voice in response.voices:
                if any("en-US" in lang_code for lang_code in voice.language_codes):
                    voices_list.append(
                        {
                            "voice_id": voice.name,
                            "name": voice.name,
                            "gender": texttospeech.SsmlVoiceGender(
                                voice.ssml_gender
                            ).name,
                            "language": list(voice.language_codes),
                            "api_params": {
                                "name": voice.name,
                                "language_code": voice.language_codes[0],
                            },
                        }
                    )
            return voices_list
        except Exception as e:
            self.logger.error(f"Error listing Google Cloud voices: {e}")
            raise RuntimeError(f"Failed to list Google Cloud voices: {e}")

    def generate_speech(self, text, title, voice_model_options=None):
        """Generate speech using Google Cloud TTS."""
        if not self.client:
            raise ConnectionError("GoogleCloudTTSProvider is not configured.")

        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")

        if voice_model_options is None:
            voice_model_options = {}

        api_params = voice_model_options.get("api_params", {})
        language_code = api_params.get("language_code", "en-US")
        voice_name = api_params.get("name", "en-US-Standard-C")

        try:
            input_text = texttospeech.SynthesisInput(text=text)
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language_code, name=voice_name
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = self.client.synthesize_speech(
                request={
                    "input": input_text,
                    "voice": voice_params,
                    "audio_config": audio_config,
                }
            )
            output_filename = f"{title.replace(' ', '_')}_googlecloud_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            return response.audio_content, output_filename
        except Exception as e:
            self.logger.error(f"Error generating speech with Google Cloud TTS: {e}")
            raise RuntimeError(f"Google Cloud TTS API error: {e}")


class ElevenLabsTTSProvider:
    """ElevenLabs Text-to-Speech provider."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ElevenLabsTTSProvider")
        self.api_key = API_CONFIG.get("elevenlabs_api_key")
        if not self.api_key:
            self.logger.error("ElevenLabs API key not found in API_CONFIG.")
            self.client = None
            raise ConnectionError("ElevenLabs API key not configured on server.")
        else:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
                self.client.voices.get_all()
                self.logger.info("ElevenLabsTTSProvider initialized successfully.")
            except Exception as e:
                self.logger.error(f"ElevenLabs error: {str(e)}")
                self.client = None
                raise ConnectionError(f"ElevenLabs initialization failed: {str(e)}")

    def list_voices(self):
        """List available ElevenLabs voices."""
        if self.client is None:
            return []

        try:
            api_voices = self.client.voices.get_all()
            formatted_voices = []
            for voice_obj in api_voices.voices:
                formatted_voices.append(
                    {
                        "voice_id": voice_obj.voice_id,
                        "name": voice_obj.name,
                        "category": voice_obj.category,
                        "labels": voice_obj.labels,
                        "api_params": {"voice_id": voice_obj.voice_id},
                    }
                )
            return formatted_voices
        except Exception as e:
            self.logger.error(f"ElevenLabs error listing voices: {str(e)}")
            raise RuntimeError(f"Failed to list ElevenLabs voices: {str(e)}")

    def generate_speech(self, text, title, voice_model_options=None):
        """Generate speech using ElevenLabs TTS."""
        if self.client is None:
            raise ConnectionError("ElevenLabs provider is not configured.")

        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")

        if voice_model_options is None:
            voice_model_options = {}

        api_params = voice_model_options.get("api_params", {})
        voice_id_param = api_params.get("voice_id")

        if not voice_id_param:
            all_voices = self.client.voices.get_all().voices
            if not all_voices:
                raise ValueError("No voices available in ElevenLabs account.")
            voice_id_param = all_voices[0].voice_id

        model_id = voice_model_options.get("model_id", "eleven_multilingual_v2")
        stability = voice_model_options.get("stability", 0.5)
        similarity_boost = voice_model_options.get("similarity_boost", 0.75)
        style = voice_model_options.get("style", 0.0)
        use_speaker_boost = voice_model_options.get("use_speaker_boost", True)

        try:
            audio_bytes = self.client.text_to_speech.convert(
                text=text,
                voice_id=str(voice_id_param),
                model_id=model_id,
                voice_settings=VoiceSettings(
                    stability=stability,
                    similarity_boost=similarity_boost,
                    style=style,
                    use_speaker_boost=use_speaker_boost,
                ),
            )

            if not isinstance(audio_bytes, bytes):
                try:
                    audio_bytes = b"".join(audio_bytes)
                except TypeError:
                    raise RuntimeError(
                        "ElevenLabs audio generation returned unexpected type."
                    )

            output_filename = f"{title.replace(' ', '_')}_elevenlabs_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            return audio_bytes, output_filename
        except Exception as e:
            self.logger.error(f"ElevenLabs error: {str(e)}")
            raise RuntimeError(f"ElevenLabs API operation failed: {str(e)}")


class GeminiTTSProvider:
    """Gemini Text-to-Speech provider."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.GeminiTTSProvider")

        self.api_key = None
        for key_name in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"]:
            if os.getenv(key_name):
                self.api_key = os.getenv(key_name)
                break

        if not self.api_key:
            raise ConnectionError("Gemini TTS API key not configured.")

        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def list_voices(self):
        """List available Gemini TTS voices."""
        voices = [
            {
                "voice_id": "Kore",
                "name": "Kore",
                "description": "Default voice",
                "api_params": {"voice_id": "Kore"},
            },
            {
                "voice_id": "Puck",
                "name": "Puck",
                "description": "Alternative voice",
                "api_params": {"voice_id": "Puck"},
            },
            {
                "voice_id": "Charon",
                "name": "Charon",
                "description": "Alternative voice",
                "api_params": {"voice_id": "Charon"},
            },
            {
                "voice_id": "Fenrir",
                "name": "Fenrir",
                "description": "Alternative voice",
                "api_params": {"voice_id": "Fenrir"},
            },
            {
                "voice_id": "Aoede",
                "name": "Aoede",
                "description": "Alternative voice",
                "api_params": {"voice_id": "Aoede"},
            },
        ]
        return voices

    def generate_speech(self, text, title, voice_model_options=None):
        """Generate speech using Gemini TTS."""
        if voice_model_options is None:
            voice_model_options = {}

        api_params = voice_model_options.get("api_params", {})
        voice = api_params.get("voice_id", "Kore")

        try:
            url = f"{self.base_url}/models/gemini-2.5-flash-preview-tts:generateContent?key={self.api_key}"

            data = {
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {
                    "response_modalities": ["AUDIO"],
                    "temperature": 1.0,
                },
            }

            headers = {"Content-Type": "application/json"}
            response = requests.post(url, headers=headers, json=data)

            if response.status_code != 200:
                error_msg = (
                    f"Gemini API error: {response.status_code} - {response.text}"
                )
                raise Exception(error_msg)

            result = response.json()

            if (
                "candidates" in result
                and result["candidates"]
                and "content" in result["candidates"][0]
                and "parts" in result["candidates"][0]["content"]
                and result["candidates"][0]["content"]["parts"]
                and "inlineData" in result["candidates"][0]["content"]["parts"][0]
            ):

                inline_data = result["candidates"][0]["content"]["parts"][0][
                    "inlineData"
                ]
                audio_data_bytes = base64.b64decode(inline_data["data"])

                # Convert PCM to MP3
                audio_segment = AudioSegment(
                    data=audio_data_bytes, sample_width=2, frame_rate=24000, channels=1
                )

                mp3_buffer = io.BytesIO()
                audio_segment.export(mp3_buffer, format="mp3")
                mp3_buffer.seek(0)

                filename = f"{title.replace(' ', '_')}_gemini_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                return mp3_buffer.getvalue(), filename
            else:
                raise Exception("No audio data in response")

        except Exception as e:
            self.logger.error(f"Gemini TTS generation failed: {str(e)}")
            raise Exception(f"Gemini TTS generation failed: {str(e)}")


def init_providers():
    """Initialize all TTS provider instances."""
    global openai_provider_instance, google_cloud_provider_instance
    global gemini_provider_instance, elevenlabs_provider_instance

    try:
        openai_provider_instance = OpenAITTSProvider()
    except Exception as e:
        logger.warning(f"Failed to initialize OpenAI: {e}")
        openai_provider_instance = None

    try:
        google_cloud_provider_instance = GoogleCloudTTSProvider()
        if not google_cloud_provider_instance.client:
            google_cloud_provider_instance = None
    except Exception as e:
        logger.warning(f"Failed to initialize Google Cloud: {e}")
        google_cloud_provider_instance = None

    try:
        gemini_provider_instance = GeminiTTSProvider()
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini: {e}")
        gemini_provider_instance = None

    try:
        elevenlabs_provider_instance = ElevenLabsTTSProvider()
    except Exception as e:
        logger.warning(f"Failed to initialize ElevenLabs: {e}")
        elevenlabs_provider_instance = None


def get_providers_config():
    """Get the configuration for all TTS providers."""
    return {
        "openai": {
            "instance": openai_provider_instance,
            "label": "OpenAI",
            "requires_api_key_per_request": False,
            "voice_type": "static",
            "unavailable_reason": (
                None
                if openai_provider_instance
                else "Initialization failed (API key missing or invalid)."
            ),
        },
        "google_cloud": {
            "instance": google_cloud_provider_instance,
            "label": "Google Cloud Text-to-Speech",
            "requires_api_key_per_request": False,
            "voice_type": "dynamic",
            "unavailable_reason": (
                None
                if (
                    google_cloud_provider_instance
                    and google_cloud_provider_instance.client
                )
                else "Initialization failed (check credentials)."
            ),
        },
        "gemini": {
            "instance": gemini_provider_instance,
            "label": "Gemini",
            "requires_api_key_per_request": False,
            "voice_type": "static",
            "unavailable_reason": (
                None
                if gemini_provider_instance
                else "Initialization failed (API key missing or invalid)."
            ),
        },
        "elevenlabs": {
            "instance": elevenlabs_provider_instance,
            "label": "ElevenLabs",
            "requires_api_key_per_request": False,
            "voice_type": "dynamic",
            "unavailable_reason": (
                None
                if elevenlabs_provider_instance
                else "Initialization failed (API key missing or invalid)."
            ),
        },
    }
