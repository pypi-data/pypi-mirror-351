"""
Unit tests for the configuration module.
"""

import os
import tempfile
import unittest
from typing import Any, Dict, cast

import yaml

from edge_mlops_monitor.config import load_config, save_default_config, validate_config


class TestConfig(unittest.TestCase):
    """Test cases for the configuration module."""

    def test_load_default_config(self):
        """Test loading the default configuration."""
        config = load_config()
        self.assertIsNotNone(config)
        self.assertIn("system", config)
        self.assertIn("model_logging", config)
        self.assertIn("drift_detection", config)
        self.assertIn("telemetry", config)
        self.assertIn("storage", config)

    def test_load_custom_config(self):
        """Test loading a custom configuration."""
        with tempfile.NamedTemporaryFile(
            suffix=".yaml", mode="w", delete=False
        ) as temp_file:
            temp_path = temp_file.name
            custom_config = {
                "system": {"sampling_interval_seconds": 20, "max_memory_buffer_mb": 100}
            }
            yaml.dump(custom_config, temp_file)

        try:
            config = load_config(temp_path)
            self.assertEqual(config["system"]["sampling_interval_seconds"], 20)
            self.assertEqual(config["system"]["max_memory_buffer_mb"], 100)
            # Other sections should use default values
            self.assertIn("model_logging", config)
            self.assertIn("drift_detection", config)
        finally:
            os.unlink(temp_path)

    def test_save_default_config(self):
        """Test saving the default configuration."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            save_default_config(temp_path)
            self.assertTrue(os.path.exists(temp_path))

            # Load the saved config and verify
            with open(temp_path, "r") as f:
                saved_config = yaml.safe_load(f)

            self.assertIn("system", saved_config)
            self.assertIn("model_logging", saved_config)
            self.assertIn("drift_detection", saved_config)
            self.assertIn("telemetry", saved_config)
            self.assertIn("storage", saved_config)
        finally:
            os.unlink(temp_path)

    def test_validate_config_valid(self):
        """Test validating a valid configuration."""
        config = load_config()
        try:
            validate_config(cast(Dict[str, Any], config))
        except ValueError:
            self.fail("validate_config() raised ValueError unexpectedly!")

    def test_validate_config_invalid_system(self):
        """Test validating an invalid system configuration."""
        config = load_config()
        config["system"]["sampling_interval_seconds"] = 0

        with self.assertRaises(ValueError):
            validate_config(cast(Dict[str, Any], config))

    def test_validate_config_invalid_model_logging(self):
        """Test validating an invalid model logging configuration."""
        config = load_config()
        config["model_logging"]["buffer_size"] = 0

        with self.assertRaises(ValueError):
            validate_config(cast(Dict[str, Any], config))

    def test_validate_config_invalid_drift_detection(self):
        """Test validating an invalid drift detection configuration."""
        config = load_config()
        config["drift_detection"]["algorithm"] = "invalid_algorithm"

        with self.assertRaises(ValueError):
            validate_config(cast(Dict[str, Any], config))

    def test_validate_config_invalid_telemetry(self):
        """Test validating an invalid telemetry configuration."""
        config = load_config()
        config["telemetry"]["upload_interval_seconds"] = 0

        with self.assertRaises(ValueError):
            validate_config(cast(Dict[str, Any], config))

    def test_validate_config_invalid_storage(self):
        """Test validating an invalid storage configuration."""
        config = load_config()
        config["storage"]["type"] = "invalid_type"

        with self.assertRaises(ValueError):
            validate_config(cast(Dict[str, Any], config))

    def test_file_not_found(self):
        """Test handling of non-existent configuration file."""
        with self.assertRaises(FileNotFoundError):
            load_config("/path/to/nonexistent/config.yaml")


if __name__ == "__main__":
    unittest.main()
