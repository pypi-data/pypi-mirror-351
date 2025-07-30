"""
Test configuration for the Edge MLOps Monitor.

This module provides fixtures and configuration for unit tests.
"""

import pytest
import copy

# Test configuration with valid values for all tests
TEST_CONFIG = {
    "system": {"sampling_interval_seconds": 1, "max_memory_buffer_mb": 10},
    "model_logging": {"buffer_size": 100, "log_level": "DEBUG"},
    "drift_detection": {
        "algorithm": "ks_test",  # Ensure valid algorithm
        "threshold": 0.05,
        "reference_data_path": "",
        "check_frequency": 10,
    },
    "telemetry": {
        "upload_interval_seconds": 10,
        "max_batch_size": 10,
        "retry_base_delay_seconds": 1,
        "retry_max_delay_seconds": 10,
        "retry_max_attempts": 3,
    },
    "storage": {
        "type": "sqlite",  # Use SQLite instead of S3 for tests
        "bucket": "test-bucket",  # Dummy value, not used with SQLite
        "prefix": "test-prefix/",
        "sqlite_path": ":memory:",  # Use in-memory SQLite for faster tests
        "max_sqlite_size_mb": 10,
    },
}


@pytest.fixture
def test_config():
    """
    Provide a fresh copy of the test configuration for each test.

    Returns:
        A deep copy of the test configuration to ensure isolation.
    """
    return copy.deepcopy(TEST_CONFIG)


# Override default configuration for tests
@pytest.fixture(autouse=True)
def mock_config(monkeypatch, test_config):
    """
    Override the default configuration for tests.

    This fixture ensures each test gets a fresh configuration with valid values.
    """

    # Override the default configuration
    monkeypatch.setattr("edge_mlops_monitor.config.DEFAULT_CONFIG", test_config)

    # Mock load_config to return a fresh copy of test_config
    def mock_load_config(config_path=None):
        from edge_mlops_monitor.config import validate_config

        config = copy.deepcopy(test_config)
        validate_config(config)
        return config

    monkeypatch.setattr("edge_mlops_monitor.config.load_config", mock_load_config)

    return test_config
