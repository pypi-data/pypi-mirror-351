"""
Configuration module for the Edge MLOps Monitor.

This module handles loading, validating, and accessing configuration settings.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict, cast

import yaml

logger = logging.getLogger(__name__)


class SystemConfig(TypedDict):
    """System monitoring configuration."""

    sampling_interval_seconds: float
    max_memory_buffer_mb: int


class ModelLoggingConfig(TypedDict):
    """Model input/output logging configuration."""

    buffer_size: int
    log_level: str


class DriftDetectionConfig(TypedDict):
    """Drift detection configuration."""

    algorithm: str
    threshold: float
    reference_data_path: str
    check_frequency: int


class TelemetryConfig(TypedDict):
    """Telemetry upload configuration."""

    upload_interval_seconds: float
    max_batch_size: int
    retry_base_delay_seconds: float
    retry_max_delay_seconds: int
    retry_max_attempts: int


class StorageConfig(TypedDict):
    """Storage configuration."""

    type: str
    bucket: str
    prefix: str
    sqlite_path: str
    max_sqlite_size_mb: int


class MonitorConfig(TypedDict):
    """Complete monitor configuration."""

    system: SystemConfig
    model_logging: ModelLoggingConfig
    drift_detection: DriftDetectionConfig
    telemetry: TelemetryConfig
    storage: StorageConfig


# Default configuration values
DEFAULT_CONFIG: MonitorConfig = {
    "system": {"sampling_interval_seconds": 10, "max_memory_buffer_mb": 50},
    "model_logging": {"buffer_size": 1000, "log_level": "INFO"},
    "drift_detection": {
        "algorithm": "ks_test",
        "threshold": 0.05,
        "reference_data_path": "",
        "check_frequency": 100,
    },
    "telemetry": {
        "upload_interval_seconds": 300,
        "max_batch_size": 100,
        "retry_base_delay_seconds": 1,
        "retry_max_delay_seconds": 60,
        "retry_max_attempts": 5,
    },
    "storage": {
        "type": "s3",
        "bucket": "",
        "prefix": "",
        "sqlite_path": "edge_mlops_monitor.db",
        "max_sqlite_size_mb": 100,
    },
}


def load_config(config_path: Optional[str] = None) -> MonitorConfig:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file. If None, uses default config.

    Returns:
        Validated configuration dictionary.

    Raises:
        ValueError: If the configuration is invalid.
        FileNotFoundError: If the configuration file does not exist.
    """
    config = DEFAULT_CONFIG.copy()

    if config_path:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_file, "r") as f:
                user_config = yaml.safe_load(f)

            # Merge user config with default config
            if user_config:
                for section in config:
                    if section in user_config:
                        config[section].update(user_config[section])
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")

    # Validate configuration
    validate_config(cast(Dict[str, Any], config))

    return config


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the configuration.

    Args:
        config: Configuration dictionary to validate.

    Raises:
        ValueError: If the configuration is invalid.
    """
    # Validate system config
    if config["system"]["sampling_interval_seconds"] < 1:
        raise ValueError("System sampling interval must be at least 1 second")

    if config["system"]["max_memory_buffer_mb"] < 1:
        raise ValueError("System max memory buffer must be at least 1 MB")

    # Validate model logging config
    if config["model_logging"]["buffer_size"] < 1:
        raise ValueError("Model logging buffer size must be at least 1")

    # Validate drift detection config
    if config["drift_detection"]["algorithm"] not in ["ks_test"]:
        raise ValueError(
            f"Unsupported drift detection algorithm: {config['drift_detection']['algorithm']}"
        )

    if not (0 < config["drift_detection"]["threshold"] < 1):
        raise ValueError("Drift detection threshold must be between 0 and 1")

    if config["drift_detection"]["check_frequency"] < 1:
        raise ValueError("Drift detection check frequency must be at least 1")

    # Validate telemetry config
    if config["telemetry"]["upload_interval_seconds"] < 1:
        raise ValueError("Telemetry upload interval must be at least 1 second")

    if config["telemetry"]["max_batch_size"] < 1:
        raise ValueError("Telemetry max batch size must be at least 1")

    # Validate storage config
    if config["storage"]["type"] not in ["s3", "sqlite"]:
        raise ValueError(f"Unsupported storage type: {config['storage']['type']}")

    if config["storage"]["type"] == "s3" and not config["storage"]["bucket"]:
        raise ValueError("S3 bucket name is required for S3 storage")

    if config["storage"]["max_sqlite_size_mb"] < 1:
        raise ValueError("SQLite max size must be at least 1 MB")


def save_default_config(output_path: str) -> None:
    """
    Save the default configuration to a YAML file.

    Args:
        output_path: Path to save the default configuration.
    """
    with open(output_path, "w") as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
