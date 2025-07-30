"""
Main monitor module for the Edge MLOps Monitor.

This module provides the main EdgeMonitor class that integrates all components.
"""

import logging
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional

from edge_mlops_monitor.config import load_config
from edge_mlops_monitor.drift import DriftDetector, DriftResult
from edge_mlops_monitor.model_logger import ModelLogger, ModelInput, ModelOutput
from edge_mlops_monitor.system import SystemMonitor, SystemMetric
from edge_mlops_monitor.upload import TelemetryUploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            "edge_mlops_monitor.log", mode="a", maxBytes=10 * 1024 * 1024, backupCount=3
        ),
    ],
)

logger = logging.getLogger(__name__)


class EdgeMonitor:
    """
    Main Edge MLOps Monitor class.

    Integrates system monitoring, model logging, drift detection, and telemetry upload.
    """

    def __init__(self, config_path: Optional[str] = None, device_id: str = ""):
        """
        Initialize the Edge MLOps Monitor.

        Args:
            config_path: Path to the configuration file. If None, uses default config.
            device_id: Unique identifier for the device. If empty, auto-generated.
        """
        # Load configuration
        self.config = load_config(config_path)

        # Initialize components
        self.device_id = device_id
        self.system_monitor = SystemMonitor(self.config, device_id=self.device_id)
        self.model_logger = ModelLogger(self.config, device_id=self.device_id)
        self.drift_detector = DriftDetector(
            self.config, self.model_logger, device_id=self.device_id
        )
        self.telemetry_uploader = TelemetryUploader(
            self.config, device_id=self.device_id
        )

        # Prediction counter for drift detection
        self.prediction_count = 0
        self.drift_check_frequency = self.config["drift_detection"]["check_frequency"]

        logger.info("Edge MLOps Monitor initialized")

    def start_system_monitoring(self) -> None:
        """
        Start system monitoring in the background.
        """
        self.system_monitor.start()
        logger.info("System monitoring started")

    def stop_system_monitoring(self) -> None:
        """
        Stop system monitoring.
        """
        self.system_monitor.stop()
        logger.info("System monitoring stopped")

    def start_telemetry_upload(self) -> None:
        """
        Start telemetry upload in the background.
        """
        self.telemetry_uploader.start()
        logger.info("Telemetry upload started")

    def stop_telemetry_upload(self) -> None:
        """
        Stop telemetry upload.
        """
        self.telemetry_uploader.stop()
        logger.info("Telemetry upload stopped")

    def log_model_input(self, input_data: Dict[str, Any]) -> str:
        """
        Log a model input.

        Args:
            input_data: Model input data.

        Returns:
            ID of the logged input.
        """
        return self.model_logger.log_input(input_data)

    def log_model_output(self, input_id: str, output_data: Dict[str, Any]) -> str:
        """
        Log a model output and check for drift if needed.

        Args:
            input_id: ID of the corresponding input.
            output_data: Model output data.

        Returns:
            ID of the logged output.
        """
        output_id = self.model_logger.log_output(input_id, output_data)

        # Increment prediction counter
        self.prediction_count += 1

        # Check for drift if needed
        if self.prediction_count % self.drift_check_frequency == 0:
            # Get feature names from output data

            # NOTE: find out what this variable for
            # feature_names = list(output_data.keys())

            # Check drift for numerical features
            numerical_features = []
            for name, value in output_data.items():
                try:
                    float(value)  # Check if value can be converted to float
                    numerical_features.append(name)
                except (ValueError, TypeError):
                    pass

            if numerical_features:
                drift_results = self.drift_detector.check_drift_from_recent_outputs(
                    numerical_features, sample_size=self.drift_check_frequency
                )

                # Log drift results if any drift detected
                drift_detected = any(
                    result["is_drift"] for result in drift_results.values()
                )
                if drift_detected:
                    logger.warning("Drift detected in model outputs")

                    # Create a telemetry batch with drift results
                    self.create_telemetry_batch(include_drift=True)

        return output_id

    def create_telemetry_batch(
        self,
        include_system: bool = True,
        include_model: bool = True,
        include_drift: bool = True,
        max_records: int = 100,
    ) -> str:
        """
        Create a telemetry batch with current data.

        Args:
            include_system: Whether to include system metrics.
            include_model: Whether to include model inputs/outputs.
            include_drift: Whether to include drift results.
            max_records: Maximum number of records to include.

        Returns:
            ID of the created batch.
        """
        # Collect data
        system_metrics: List[SystemMetric] = []
        model_inputs: List[ModelInput] = []
        model_outputs: List[ModelOutput] = []
        drift_results: List[DriftResult] = []

        if include_system:
            system_metrics = self.system_monitor.get_metrics()
            # Limit to max_records
            if len(system_metrics) > max_records:
                system_metrics = system_metrics[-max_records:]

        if include_model:
            model_inputs = self.model_logger.get_inputs(limit=max_records)
            model_outputs = self.model_logger.get_outputs(limit=max_records)

        if include_drift:
            drift_results = self.drift_detector.get_drift_results()
            # Limit to max_records
            if len(drift_results) > max_records:
                drift_results = drift_results[-max_records:]

        # Create the batch
        batch_id = self.telemetry_uploader.create_batch(
            system_metrics=system_metrics,
            model_inputs=model_inputs,
            model_outputs=model_outputs,
            drift_results=drift_results,
        )

        logger.debug(f"Created telemetry batch {batch_id}")
        return batch_id

    def set_reference_data(self, feature_name: str, values: List[float]) -> None:
        """
        Set reference data for drift detection.

        Args:
            feature_name: Name of the feature.
            values: Reference values for the feature.
        """
        self.drift_detector.set_reference_data(feature_name, values)

    def save_reference_data(self, output_path: Optional[str] = None) -> None:
        """
        Save current reference data to file.

        Args:
            output_path: Path to save the reference data. If None, uses the path from config.
        """
        self.drift_detector.save_reference_data(output_path)

    def start(self) -> None:
        """
        Start all monitoring components.
        """
        self.start_system_monitoring()
        self.start_telemetry_upload()
        logger.info("Edge MLOps Monitor started")

    def stop(self) -> None:
        """
        Stop all monitoring components.
        """
        self.stop_system_monitoring()
        self.stop_telemetry_upload()
        logger.info("Edge MLOps Monitor stopped")

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the monitor.

        Returns:
            Dictionary with status information.
        """
        return {
            "system_metrics_count": len(self.system_monitor.get_metrics()),
            "pending_telemetry_batches": self.telemetry_uploader.get_pending_batch_count(),
            "prediction_count": self.prediction_count,
            "drift_results_count": len(self.drift_detector.get_drift_results()),
        }
