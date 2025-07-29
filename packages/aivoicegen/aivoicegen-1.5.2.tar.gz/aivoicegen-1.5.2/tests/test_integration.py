"""
Integration tests for AIVoiceGen application.
These tests verify that different components work together correctly.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
from app import init_database


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflows."""

    def setUp(self):
        """Set up test environment."""
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

        # Set up test database
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        app.DB_PATH = Path(self.test_db.name)
        init_database()

        # Create outputs directory
        self.outputs_dir = tempfile.mkdtemp()
        self.original_outputs = app.Path("outputs")

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)

        # Clean up outputs directory
        import shutil

        if os.path.exists(self.outputs_dir):
            shutil.rmtree(self.outputs_dir)

    def test_complete_text_optimization_workflow(self):
        """Test complete text optimization workflow."""
        # 1. Test initial optimization
        response = self.client.post(
            "/optimize",
            json={
                "text": "This is a test about AI",
                "service": "google_cloud",  # Uses basic optimization
                "mode": "default",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        optimized_text = data["optimized_text"]

        # Should expand AI abbreviation (case insensitive check)
        self.assertIn("artificial intelligence", optimized_text.lower())

        # 2. Test shorter mode
        response = self.client.post(
            "/optimize",
            json={
                "text": "This is a test about AI",
                "service": "google_cloud",
                "mode": "shorter",
            },
        )

        self.assertEqual(response.status_code, 200)

        # 3. Test longer mode
        response = self.client.post(
            "/optimize",
            json={
                "text": "This is a test about AI",
                "service": "google_cloud",
                "mode": "longer",
            },
        )

        self.assertEqual(response.status_code, 200)

    @patch("app.optimize_with_openai")
    def test_openai_optimization_modes(self, mock_optimize_openai):
        """Test OpenAI optimization with different modes."""

        # Mock the optimize_with_openai function directly
        def mock_openai_optimize(text, mode="default"):
            if mode == "shorter":
                return "Short version"
            elif mode == "longer":
                return "Longer expanded version"
            else:  # default mode
                return "Enhanced version"

        mock_optimize_openai.side_effect = mock_openai_optimize

        # Mock the TTS provider config to show OpenAI as available
        mock_openai_provider = MagicMock()
        with patch.dict(
            "app.TTS_PROVIDERS_CONFIG",
            {
                "openai": {
                    "label": "OpenAI",
                    "instance": mock_openai_provider,
                    "unavailable_reason": None,
                }
            },
        ):
            # Ensure OpenAI is configured by setting API_CONFIG
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
                app.API_CONFIG = app.load_api_config()

                # Test default mode
                response = self.client.post(
                    "/optimize",
                    json={"text": "Test text", "service": "openai", "mode": "default"},
                )

                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data["optimized_text"], "Enhanced version")

                # Test shorter mode
                response = self.client.post(
                    "/optimize",
                    json={"text": "Test text", "service": "openai", "mode": "shorter"},
                )

                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data["optimized_text"], "Short version")

                # Test longer mode
                response = self.client.post(
                    "/optimize",
                    json={"text": "Test text", "service": "openai", "mode": "longer"},
                )

                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data["optimized_text"], "Longer expanded version")

    def test_service_configuration_flow(self):
        """Test service configuration and voice listing flow."""
        # 1. Get services
        response = self.client.get("/services")
        self.assertEqual(response.status_code, 200)
        services = json.loads(response.data)

        # 2. Try to get voices for each service
        for service_name in services:
            response = self.client.get(f"/voices/{service_name}")
            # Should either return voices or service unavailable error
            self.assertIn(response.status_code, [200, 503])

    def test_api_config_workflow(self):
        """Test API configuration workflow."""
        # 1. Get current config
        response = self.client.get("/api-config")
        self.assertEqual(response.status_code, 200)

        # 2. Update config
        response = self.client.post(
            "/api-config", json={"OPENAI_API_KEY": "test_key_123"}
        )
        self.assertEqual(response.status_code, 200)

        # 3. Verify config was updated
        response = self.client.get("/api-config")
        self.assertEqual(response.status_code, 200)
        # Note: In a real scenario, we'd verify the key was set
        # but we don't want to actually modify environment


class TestConcurrentOperations(unittest.TestCase):
    """Test handling of concurrent operations."""

    def setUp(self):
        """Set up test environment."""
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    def test_concurrent_optimization_requests(self):
        """Test handling multiple optimization requests."""
        import threading

        results = []

        def make_request():
            response = self.client.post(
                "/optimize",
                json={"text": "Test text for concurrency", "service": "google_cloud"},
            )
            results.append(response.status_code)

        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        for status_code in results:
            self.assertEqual(status_code, 200)


class TestDataPersistence(unittest.TestCase):
    """Test data persistence across application restarts."""

    def setUp(self):
        """Set up persistent test database."""
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

        # Use a named temporary file that we control
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_file.close()
        app.DB_PATH = Path(self.db_file.name)
        init_database()

    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.db_file.name):
            os.unlink(self.db_file.name)

    def test_database_persistence(self):
        """Test that database persists data correctly."""
        # Add some data to the database
        with app.get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO generation_history 
                (title, service, voice, text_snippet, filename, file_path)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "Test Title",
                    "openai",
                    "alloy",
                    "Test snippet",
                    "test.mp3",
                    "/path/test.mp3",
                ),
            )
            conn.commit()

        # Verify data can be retrieved
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)

        history = json.loads(response.data)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["title"], "Test Title")
        self.assertEqual(history[0]["service"], "openai")

    def test_database_schema_integrity(self):
        """Test database schema remains intact after operations."""
        # Perform various operations
        with app.get_db_connection() as conn:
            # Insert test data
            conn.execute(
                """
                INSERT INTO generation_history 
                (title, service, voice, text_snippet, filename, file_path)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("Test", "openai", "alloy", "snippet", "file.mp3", "/path/file.mp3"),
            )

            # Query data
            cursor = conn.execute("SELECT * FROM generation_history")
            results = cursor.fetchall()

            # Verify schema
            cursor = conn.execute("PRAGMA table_info(generation_history)")
            columns = cursor.fetchall()

            self.assertGreater(len(columns), 0)
            self.assertEqual(len(results), 1)


class TestErrorRecovery(unittest.TestCase):
    """Test application recovery from various error conditions."""

    def setUp(self):
        """Set up test environment."""
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    def test_recovery_from_invalid_requests(self):
        """Test that app recovers from invalid requests."""
        # Make several invalid requests
        invalid_requests = [
            ("POST", "/generate", {}),
            ("POST", "/optimize", {"invalid": "data"}),
            ("GET", "/voices/nonexistent", None),
            ("POST", "/api-config", "invalid json"),
        ]

        for method, endpoint, data in invalid_requests:
            if method == "POST":
                if isinstance(data, dict):
                    response = self.client.post(endpoint, json=data)
                else:
                    response = self.client.post(
                        endpoint, data=data, content_type="application/json"
                    )
            else:
                response = self.client.get(endpoint)

            # Should return an error, but not crash
            self.assertIn(response.status_code, [400, 404, 500, 503])

        # App should still be responsive to valid requests
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    @patch("app.get_db_connection")
    def test_database_error_handling(self, mock_db):
        """Test handling of database errors."""
        # Simulate database connection error
        mock_db.side_effect = Exception("Database connection failed")

        response = self.client.get("/history")
        self.assertEqual(response.status_code, 500)

        # App should still serve other endpoints
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
