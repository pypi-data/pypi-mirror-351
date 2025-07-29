import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
from app import (
    ElevenLabsTTSProvider,
    GeminiTTSProvider,
    GoogleCloudTTSProvider,
    OpenAITTSProvider,
    get_db_connection,
    init_database,
    optimize_with_basic_rules,
)


class TestBasicOptimization(unittest.TestCase):
    """Test basic text optimization functions."""

    def test_optimize_with_basic_rules_simple_text(self):
        """Test basic optimization with simple text."""
        text = "Hello world"
        result = optimize_with_basic_rules(text)
        self.assertIn("Hello world", result)
        self.assertTrue(result.endswith("."))

    def test_optimize_with_basic_rules_abbreviations(self):
        """Test abbreviation expansion."""
        text = "Dr. Smith met with Mr. Johnson about AI"
        result = optimize_with_basic_rules(text)
        self.assertIn("Doctor Smith", result)
        self.assertIn("Mister Johnson", result)
        self.assertIn("Artificial Intelligence", result)

    def test_optimize_with_basic_rules_short_text_enhancement(self):
        """Test that short texts get engaging introductions."""
        text = "The weather is nice"
        result = optimize_with_basic_rules(text)
        self.assertTrue(
            result.startswith("Here's something interesting:")
            or result.startswith("Let me tell you about")
        )

    def test_optimize_with_basic_rules_whitespace_normalization(self):
        """Test whitespace normalization."""
        text = "Hello    world   with   spaces"
        result = optimize_with_basic_rules(text)
        self.assertNotIn("  ", result)  # No double spaces


class TestDatabaseFunctions(unittest.TestCase):
    """Test SQLite database functionality."""

    def setUp(self):
        """Set up test database."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        app.DB_PATH = Path(self.test_db.name)
        init_database()

    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)

    def test_database_initialization(self):
        """Test that database initializes correctly."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='generation_history'"
            )
            table_exists = cursor.fetchone() is not None
            self.assertTrue(table_exists)

    def test_database_schema(self):
        """Test that database schema is correct."""
        with get_db_connection() as conn:
            cursor = conn.execute("PRAGMA table_info(generation_history)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            expected_columns = [
                "id",
                "title",
                "service",
                "voice",
                "text_snippet",
                "filename",
                "timestamp",
                "file_path",
            ]
            for col in expected_columns:
                self.assertIn(col, column_names)


class TestFlaskApp(unittest.TestCase):
    """Test Flask application endpoints."""

    def setUp(self):
        """Set up test client."""
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

        # Set up test database
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        app.DB_PATH = Path(self.test_db.name)
        init_database()

    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)

    def test_index_route(self):
        """Test that index route serves HTML."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<!DOCTYPE html>", response.data)

    def test_services_route(self):
        """Test services endpoint."""
        response = self.client.get("/services")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        # Check that known services are present
        expected_services = ["openai", "elevenlabs", "gemini"]
        for service in expected_services:
            self.assertIn(service, data)

    def test_history_route_empty(self):
        """Test history endpoint with empty database."""
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

    def test_optimize_route_missing_data(self):
        """Test optimize endpoint with missing data."""
        response = self.client.post("/optimize", json={})
        self.assertEqual(response.status_code, 400)

    def test_optimize_route_missing_text(self):
        """Test optimize endpoint with missing text."""
        response = self.client.post("/optimize", json={"service": "openai"})
        self.assertEqual(response.status_code, 400)

    def test_optimize_route_missing_service(self):
        """Test optimize endpoint with missing service."""
        response = self.client.post("/optimize", json={"text": "test text"})
        self.assertEqual(response.status_code, 400)

    def test_optimize_route_unsupported_service(self):
        """Test optimize endpoint with unsupported service."""
        response = self.client.post(
            "/optimize", json={"text": "test text", "service": "nonexistent"}
        )
        self.assertEqual(response.status_code, 400)

    @patch("app.optimize_with_basic_rules")
    def test_optimize_route_basic_optimization(self, mock_optimize):
        """Test optimize endpoint with basic optimization."""
        mock_optimize.return_value = "optimized text"

        response = self.client.post(
            "/optimize",
            json={
                "text": "test text",
                "service": "google_cloud",  # Service without AI optimization
            },
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["optimized_text"], "optimized text")

    def test_api_config_get(self):
        """Test API config GET endpoint."""
        response = self.client.get("/api-config")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("openai", data)
        self.assertIn("elevenlabs", data)
        self.assertIn("gemini", data)


class TestTTSProviders(unittest.TestCase):
    """Test TTS provider classes."""

    def test_openai_provider_list_voices(self):
        """Test OpenAI provider voice listing."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            app.API_CONFIG = app.load_api_config()  # Reload config with test key
            provider = OpenAITTSProvider()
            voices = provider.list_voices()

            self.assertIsInstance(voices, list)
            self.assertGreater(len(voices), 0)

            # Check voice structure
            voice = voices[0]
            self.assertIn("voice_id", voice)
            self.assertIn("name", voice)
            self.assertIn("api_params", voice)

    def test_gemini_provider_list_voices(self):
        """Test Gemini provider voice listing."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
            provider = GeminiTTSProvider()
            voices = provider.list_voices()

            self.assertIsInstance(voices, list)
            self.assertGreater(len(voices), 0)

            # Check that known voices are present
            voice_ids = [v["voice_id"] for v in voices]
            self.assertIn("Kore", voice_ids)

    def test_openai_provider_no_api_key(self):
        """Test OpenAI provider without API key."""
        with patch.dict(os.environ, {}, clear=True):
            app.API_CONFIG = app.load_api_config()  # Reload config
            with self.assertRaises(ConnectionError):
                OpenAITTSProvider()

    @patch("app.texttospeech.TextToSpeechClient")
    def test_google_cloud_provider_initialization(self, mock_client):
        """Test Google Cloud TTS provider initialization."""
        with patch.dict(
            os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds.json"}
        ):
            with patch("os.path.exists", return_value=True):
                app.API_CONFIG = app.load_api_config()
                provider = GoogleCloudTTSProvider()
                self.assertIsNotNone(provider.client)

    def test_elevenlabs_provider_no_api_key(self):
        """Test ElevenLabs provider without API key."""
        with patch.dict(os.environ, {}, clear=True):
            app.API_CONFIG = app.load_api_config()
            with self.assertRaises(ConnectionError):
                ElevenLabsTTSProvider()


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""

    def test_load_api_config(self):
        """Test API configuration loading."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test_openai_key",
                "ELEVENLABS_API_KEY": "test_eleven_key",
                "GEMINI_API_KEY": "test_gemini_key",
            },
        ):
            config = app.load_api_config()

            self.assertEqual(config["openai_api_key"], "test_openai_key")
            self.assertEqual(config["elevenlabs_api_key"], "test_eleven_key")
            self.assertEqual(config["gemini_api_key"], "test_gemini_key")

    def test_load_api_config_missing_keys(self):
        """Test API configuration with missing keys."""
        with patch.dict(os.environ, {}, clear=True):
            config = app.load_api_config()

            self.assertIsNone(config["openai_api_key"])
            self.assertIsNone(config["elevenlabs_api_key"])
            self.assertIsNone(config["gemini_api_key"])


class TestTextOptimizationModes(unittest.TestCase):
    """Test different text optimization modes."""

    @patch("app.OpenAI")
    def test_openai_optimization_default_mode(self, mock_openai_class):
        """Test OpenAI optimization in default mode."""
        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Enhanced text"
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            app.API_CONFIG = app.load_api_config()
            result = app.optimize_with_openai("test text", "default")

            self.assertEqual(result, "Enhanced text")
            mock_client.chat.completions.create.assert_called_once()

    @patch("app.OpenAI")
    def test_openai_optimization_shorter_mode(self, mock_openai_class):
        """Test OpenAI optimization in shorter mode."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Short text"
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            app.API_CONFIG = app.load_api_config()
            result = app.optimize_with_openai("test text", "shorter")

            self.assertEqual(result, "Short text")
            # Check that max_tokens is set for shorter mode
            call_args = mock_client.chat.completions.create.call_args
            self.assertEqual(call_args[1]["max_tokens"], 400)


class TestErrorHandling(unittest.TestCase):
    """Test error handling throughout the application."""

    def setUp(self):
        """Set up test client."""
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    def test_generate_route_missing_data(self):
        """Test generate endpoint with missing data."""
        response = self.client.post("/generate", json={})
        self.assertEqual(response.status_code, 400)

    def test_generate_route_missing_fields(self):
        """Test generate endpoint with missing required fields."""
        response = self.client.post("/generate", json={"service": "openai"})
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn("Missing required fields", data["error"])

    def test_generate_route_unsupported_service(self):
        """Test generate endpoint with unsupported service."""
        response = self.client.post(
            "/generate",
            json={"service": "nonexistent", "title": "test", "text": "test text"},
        )
        self.assertEqual(response.status_code, 400)

    def test_voices_route_unknown_service(self):
        """Test voices endpoint with unknown service."""
        response = self.client.get("/voices/nonexistent")
        self.assertEqual(response.status_code, 404)

    def test_api_config_invalid_json(self):
        """Test API config endpoint with invalid JSON."""
        response = self.client.post(
            "/api-config", data="invalid json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    # Create test loader and suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestBasicOptimization,
        TestDatabaseFunctions,
        TestFlaskApp,
        TestTTSProviders,
        TestUtilityFunctions,
        TestTextOptimizationModes,
        TestErrorHandling,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with error code if tests failed
    exit(0 if result.wasSuccessful() else 1)
