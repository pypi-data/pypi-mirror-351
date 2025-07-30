"""
Drift detection module for the Edge MLOps Monitor.

This module implements statistical drift detection algorithms to detect
changes in model output distributions.
"""

import json
import logging
import os
import time
import copy
from typing import Dict, List, Optional, TypedDict

from scipy import stats

from edge_mlops_monitor.config import MonitorConfig
from edge_mlops_monitor.model_logger import ModelLogger

logger = logging.getLogger(__name__)


class DriftResult(TypedDict):
    """Drift detection result data structure."""

    timestamp: float
    algorithm: str
    feature_name: str
    statistic: float
    p_value: float
    threshold: float
    is_drift: bool
    sample_size: int
    device_id: str


class DriftDetector:
    """
    Drift detection component.

    Implements statistical drift detection algorithms to detect changes in
    model output distributions.
    """

    def __init__(
        self, config: MonitorConfig, model_logger: ModelLogger, device_id: str = ""
    ):
        """
        Initialize the drift detector.

        Args:
            config: Monitor configuration.
            model_logger: Model logger instance.
            device_id: Unique identifier for the device.
        """
        self.config = config
        self.model_logger = model_logger
        self.device_id = device_id
        self.algorithm = config["drift_detection"]["algorithm"]
        self.threshold = config["drift_detection"]["threshold"]
        self.check_frequency = config["drift_detection"]["check_frequency"]
        self.reference_data_path = config["drift_detection"]["reference_data_path"]

        # Load reference data if available
        self.reference_data: Dict[str, List[float]] = {}
        if self.reference_data_path and os.path.exists(self.reference_data_path):
            self._load_reference_data()

        # Initialize drift results storage
        self.drift_results: List[DriftResult] = []

    def _load_reference_data(self) -> None:
        """
        Load reference data from file.

        The reference data file should be a JSON file with the following structure:
        {
            "feature_name1": [value1, value2, ...],
            "feature_name2": [value1, value2, ...],
            ...
        }
        """
        try:
            with open(self.reference_data_path, "r") as f:
                data = json.load(f)

            # Validate reference data
            if not isinstance(data, dict):
                raise ValueError("Reference data must be a dictionary")

            for feature_name, values in data.items():
                if not isinstance(values, list):
                    raise ValueError(
                        f"Reference data for feature '{feature_name}' must be a list"
                    )

                # Convert values to float if possible
                try:
                    self.reference_data[feature_name] = [float(v) for v in values]
                except (ValueError, TypeError):
                    logger.warning(
                        f"Could not convert reference data for feature '{feature_name}' to float"
                    )

            logger.info(
                f"Loaded reference data for {len(self.reference_data)} features"
            )

        except Exception as e:
            logger.error(f"Error loading reference data: {e}")

    def save_reference_data(self, output_path: Optional[str] = None) -> None:
        """
        Save current reference data to file.

        Args:
            output_path: Path to save the reference data. If None, uses the path from config.
        """
        path = output_path or self.reference_data_path
        if not path:
            logger.error("No output path specified for reference data")
            return

        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w") as f:
                json.dump(self.reference_data, f)

            logger.info(f"Saved reference data to {path}")

        except Exception as e:
            logger.error(f"Error saving reference data: {e}")

    def set_reference_data(self, feature_name: str, values: List[float]) -> None:
        """
        Set reference data for a feature.

        Args:
            feature_name: Name of the feature.
            values: Reference values for the feature.
        """
        self.reference_data[feature_name] = values
        logger.debug(
            f"Set reference data for feature '{feature_name}' with {len(values)} values"
        )

    def detect_drift(
        self, feature_name: str, current_values: List[float]
    ) -> DriftResult:
        """
        Detect drift for a specific feature.

        Args:
            feature_name: Name of the feature.
            current_values: Current values for the feature.

        Returns:
            Drift detection result.
        """
        timestamp = time.time()

        # Check if reference data exists for this feature
        if feature_name not in self.reference_data:
            logger.warning(f"No reference data for feature '{feature_name}'")
            return {
                "timestamp": timestamp,
                "algorithm": self.algorithm,
                "feature_name": feature_name,
                "statistic": 0.0,
                "p_value": 1.0,
                "threshold": self.threshold,
                "is_drift": False,
                "sample_size": len(current_values),
                "device_id": self.device_id,
            }

        reference_values = self.reference_data[feature_name]

        # Ensure we have enough data
        if len(reference_values) < 2 or len(current_values) < 2:
            logger.warning(
                f"Not enough data for drift detection for feature '{feature_name}'"
            )
            return {
                "timestamp": timestamp,
                "algorithm": self.algorithm,
                "feature_name": feature_name,
                "statistic": 0.0,
                "p_value": 1.0,
                "threshold": self.threshold,
                "is_drift": False,
                "sample_size": len(current_values),
                "device_id": self.device_id,
            }

        try:
            # Perform drift detection based on the configured algorithm
            if self.algorithm == "ks_test":
                # Kolmogorov-Smirnov test
                statistic, p_value = stats.ks_2samp(reference_values, current_values)
                # Ensure statistic and p_value are floats (handle tuple return in some scipy versions)
                if isinstance(statistic, tuple):
                    statistic = statistic[0]
                if isinstance(p_value, tuple):
                    p_value = p_value[0]
                if isinstance(statistic, (float, int)):
                    statistic_float = float(statistic)
                elif isinstance(statistic, str):
                    try:
                        statistic_float = float(statistic)
                    except (TypeError, ValueError):
                        logger.error(
                            f"Invalid statistic string: {statistic} for feature '{feature_name}'"
                        )
                        statistic_float = 0.0
                else:
                    logger.error(
                        f"Invalid statistic type: {type(statistic)} for feature '{feature_name}'"
                    )
                    statistic_float = 0.0

                if isinstance(p_value, (float, int)):
                    p_value_float = float(p_value)
                elif isinstance(p_value, str):
                    try:
                        p_value_float = float(p_value)
                    except (TypeError, ValueError):
                        logger.error(
                            f"Invalid p_value string: {p_value} for feature '{feature_name}'"
                        )
                        p_value_float = 1.0
                else:
                    logger.error(
                        f"Invalid p_value type: {type(p_value)} for feature '{feature_name}'"
                    )
                    p_value_float = 1.0
                is_drift = p_value_float < self.threshold

                result: DriftResult = {
                    "timestamp": timestamp,
                    "algorithm": self.algorithm,
                    "feature_name": feature_name,
                    "statistic": statistic_float,
                    "p_value": p_value_float,
                    "threshold": self.threshold,
                    "is_drift": is_drift,
                    "sample_size": len(current_values),
                    "device_id": self.device_id,
                }

                # Store the result
                self.drift_results.append(result)

                if is_drift:
                    logger.warning(
                        f"Drift detected for feature '{feature_name}': p-value={p_value:.4f}, threshold={self.threshold}"
                    )
                else:
                    logger.debug(
                        f"No drift detected for feature '{feature_name}': p-value={p_value:.4f}, threshold={self.threshold}"
                    )

                return result

            else:
                logger.error(f"Unsupported drift detection algorithm: {self.algorithm}")
                return {
                    "timestamp": timestamp,
                    "algorithm": self.algorithm,
                    "feature_name": feature_name,
                    "statistic": 0.0,
                    "p_value": 1.0,
                    "threshold": self.threshold,
                    "is_drift": False,
                    "sample_size": len(current_values),
                    "device_id": self.device_id,
                }

        except Exception as e:
            logger.error(f"Error detecting drift for feature '{feature_name}': {e}")
            return {
                "timestamp": timestamp,
                "algorithm": self.algorithm,
                "feature_name": feature_name,
                "statistic": 0.0,
                "p_value": 1.0,
                "threshold": self.threshold,
                "is_drift": False,
                "sample_size": len(current_values),
                "device_id": self.device_id,
            }

    def check_drift_from_recent_outputs(
        self, feature_names: List[str], sample_size: int = 100
    ) -> Dict[str, DriftResult]:
        """
        Check drift using recent model outputs.

        Args:
            feature_names: Names of the features to check.
            sample_size: Number of recent outputs to use.

        Returns:
            Dictionary mapping feature names to drift detection results.
        """
        # Get recent outputs
        outputs = self.model_logger.get_outputs(limit=sample_size)

        if not outputs:
            logger.warning("No recent outputs available for drift detection")
            return {}

        # Extract feature values
        feature_values: Dict[str, List[float]] = {name: [] for name in feature_names}

        for output in outputs:
            output_data = output["output_data"]

            for feature_name in feature_names:
                if feature_name in output_data:
                    try:
                        value = float(output_data[feature_name])
                        feature_values[feature_name].append(value)
                    except (ValueError, TypeError):
                        logger.warning(
                            f"Could not convert output value for feature '{feature_name}' to float"
                        )

        # Detect drift for each feature
        results: Dict[str, DriftResult] = {}

        for feature_name, values in feature_values.items():
            if values:  # Only check if we have values
                result = self.detect_drift(feature_name, values)
                results[feature_name] = result

        return results

    def get_drift_results(self) -> List[DriftResult]:
        """
        Get all drift detection results.

        Returns:
            List of drift detection results (deep copy).
        """
        return copy.deepcopy(self.drift_results)

    def clear_drift_results(self) -> None:
        """
        Clear all drift detection results.
        """
        self.drift_results.clear()
        logger.debug("Drift detection results cleared")
