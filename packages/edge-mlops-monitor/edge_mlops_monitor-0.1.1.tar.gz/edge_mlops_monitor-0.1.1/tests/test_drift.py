"""
Unit tests for the drift detection module.
"""

import os
import tempfile
import time
from typing import List
import unittest
from unittest.mock import patch

from edge_mlops_monitor.config import load_config
from edge_mlops_monitor.drift import DriftDetector, DriftResult
from edge_mlops_monitor.model_logger import ModelLogger


class TestDriftDetector(unittest.TestCase):
    """Test cases for the drift detection module."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = load_config()
        # Create a temporary database file for model logger
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Create a temporary reference data file
        self.temp_ref = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_ref.close()
        self.ref_path = self.temp_ref.name

        # Update config with test paths
        self.config["storage"]["sqlite_path"] = self.db_path
        self.config["drift_detection"]["reference_data_path"] = self.ref_path
        self.config["drift_detection"]["threshold"] = 0.05

        self.device_id = "test-device"
        self.model_logger = ModelLogger(
            self.config, device_id=self.device_id, db_path=self.db_path
        )
        self.drift_detector = DriftDetector(
            self.config, self.model_logger, device_id=self.device_id
        )

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary files
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
        if os.path.exists(self.ref_path):
            os.unlink(self.ref_path)

    def test_initialization(self):
        """Test initialization of the drift detector."""
        self.assertEqual(self.drift_detector.device_id, self.device_id)
        self.assertEqual(
            self.drift_detector.algorithm, self.config["drift_detection"]["algorithm"]
        )
        self.assertEqual(
            self.drift_detector.threshold, self.config["drift_detection"]["threshold"]
        )
        self.assertEqual(
            self.drift_detector.check_frequency,
            self.config["drift_detection"]["check_frequency"],
        )
        self.assertEqual(self.drift_detector.reference_data_path, self.ref_path)
        self.assertEqual(len(self.drift_detector.reference_data), 0)
        self.assertEqual(len(self.drift_detector.drift_results), 0)

    def test_set_reference_data(self):
        """Test setting reference data."""
        feature_name = "test_feature"
        values = [1.0, 2.0, 3.0, 4.0, 5.0]

        self.drift_detector.set_reference_data(feature_name, values)

        self.assertIn(feature_name, self.drift_detector.reference_data)
        self.assertEqual(self.drift_detector.reference_data[feature_name], values)

    def test_save_load_reference_data(self):
        """Test saving and loading reference data."""
        # Set reference data
        self.drift_detector.set_reference_data("feature1", [1.0, 2.0, 3.0])
        self.drift_detector.set_reference_data("feature2", [4.0, 5.0, 6.0])

        # Save reference data
        self.drift_detector.save_reference_data()

        # Create a new drift detector to load the saved data
        new_detector = DriftDetector(
            self.config, self.model_logger, device_id=self.device_id
        )

        # Verify reference data was loaded
        self.assertIn("feature1", new_detector.reference_data)
        self.assertIn("feature2", new_detector.reference_data)
        self.assertEqual(new_detector.reference_data["feature1"], [1.0, 2.0, 3.0])
        self.assertEqual(new_detector.reference_data["feature2"], [4.0, 5.0, 6.0])

    @patch("scipy.stats.ks_2samp")
    def test_detect_drift_no_drift(self, mock_ks_2samp):
        """Test drift detection with no drift."""
        # Mock KS test to return no drift
        mock_ks_2samp.return_value = (0.2, 0.3)  # statistic, p-value

        # Set reference data
        feature_name = "test_feature"
        reference_values = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.drift_detector.set_reference_data(feature_name, reference_values)

        # Test values similar to reference
        current_values = [1.1, 2.1, 3.1, 4.1, 5.1]

        # Detect drift
        result = self.drift_detector.detect_drift(feature_name, current_values)

        # Verify result
        self.assertEqual(result["algorithm"], "ks_test")
        self.assertEqual(result["feature_name"], feature_name)
        self.assertEqual(result["statistic"], 0.2)
        self.assertEqual(result["p_value"], 0.3)
        self.assertEqual(result["threshold"], 0.05)
        self.assertFalse(result["is_drift"])
        self.assertEqual(result["sample_size"], len(current_values))
        self.assertEqual(result["device_id"], self.device_id)

        # Verify drift results were stored
        self.assertEqual(len(self.drift_detector.drift_results), 1)
        self.assertEqual(self.drift_detector.drift_results[0], result)

    @patch("scipy.stats.ks_2samp")
    def test_detect_drift_with_drift(self, mock_ks_2samp):
        """Test drift detection with drift."""
        # Mock KS test to return drift
        mock_ks_2samp.return_value = (0.8, 0.01)  # statistic, p-value

        # Set reference data
        feature_name = "test_feature"
        reference_values = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.drift_detector.set_reference_data(feature_name, reference_values)

        # Test values very different from reference
        current_values = [10.0, 20.0, 30.0, 40.0, 50.0]

        # Detect drift
        result = self.drift_detector.detect_drift(feature_name, current_values)

        # Verify result
        self.assertEqual(result["algorithm"], "ks_test")
        self.assertEqual(result["feature_name"], feature_name)
        self.assertEqual(result["statistic"], 0.8)
        self.assertEqual(result["p_value"], 0.01)
        self.assertEqual(result["threshold"], 0.05)
        self.assertTrue(result["is_drift"])
        self.assertEqual(result["sample_size"], len(current_values))
        self.assertEqual(result["device_id"], self.device_id)

        # Verify drift results were stored
        self.assertEqual(len(self.drift_detector.drift_results), 1)
        self.assertEqual(self.drift_detector.drift_results[0], result)

    def test_detect_drift_no_reference_data(self):
        """Test drift detection with no reference data."""
        feature_name = "nonexistent_feature"
        current_values = [1.0, 2.0, 3.0]

        # Detect drift
        result = self.drift_detector.detect_drift(feature_name, current_values)

        # Verify result
        self.assertEqual(result["algorithm"], "ks_test")
        self.assertEqual(result["feature_name"], feature_name)
        self.assertEqual(result["statistic"], 0.0)
        self.assertEqual(result["p_value"], 1.0)
        self.assertEqual(result["threshold"], 0.05)
        self.assertFalse(result["is_drift"])
        self.assertEqual(result["sample_size"], len(current_values))
        self.assertEqual(result["device_id"], self.device_id)

    def test_detect_drift_insufficient_data(self):
        """Test drift detection with insufficient data."""
        feature_name = "test_feature"
        reference_values = [1.0]  # Only one value
        current_values = [2.0]  # Only one value

        self.drift_detector.set_reference_data(feature_name, reference_values)

        # Detect drift
        result = self.drift_detector.detect_drift(feature_name, current_values)

        # Verify result
        self.assertEqual(result["algorithm"], "ks_test")
        self.assertEqual(result["feature_name"], feature_name)
        self.assertEqual(result["statistic"], 0.0)
        self.assertEqual(result["p_value"], 1.0)
        self.assertEqual(result["threshold"], 0.05)
        self.assertFalse(result["is_drift"])
        self.assertEqual(result["sample_size"], len(current_values))
        self.assertEqual(result["device_id"], self.device_id)

    def test_check_drift_from_recent_outputs(self):
        """Test checking drift from recent model outputs."""
        # Set reference data
        self.drift_detector.set_reference_data(
            "price", [100.0, 110.0, 120.0, 130.0, 140.0]
        )
        self.drift_detector.set_reference_data(
            "confidence", [0.8, 0.85, 0.9, 0.95, 0.99]
        )

        # Log some model outputs
        for i in range(5):
            input_id = self.model_logger.log_input({"feature1": float(i)})
            self.model_logger.log_output(
                input_id,
                {"price": 100.0 + float(i) * 10.0, "confidence": 0.8 + float(i) * 0.05},
            )

        # Check drift
        with patch(
            "edge_mlops_monitor.drift.DriftDetector.detect_drift"
        ) as mock_detect_drift:
            # Mock detect_drift to return test results
            mock_detect_drift.side_effect = lambda feature_name, values: {
                "timestamp": time.time(),
                "algorithm": "ks_test",
                "feature_name": feature_name,
                "statistic": 0.2,
                "p_value": 0.3,
                "threshold": 0.05,
                "is_drift": False,
                "sample_size": len(values),
                "device_id": self.device_id,
            }

            results = self.drift_detector.check_drift_from_recent_outputs(
                ["price", "confidence"]
            )

            # Verify results
            self.assertEqual(len(results), 2)
            self.assertIn("price", results)
            self.assertIn("confidence", results)
            self.assertEqual(results["price"]["feature_name"], "price")
            self.assertEqual(results["confidence"]["feature_name"], "confidence")

            # Verify detect_drift was called for each feature
            self.assertEqual(mock_detect_drift.call_count, 2)

    def test_get_drift_results(self):
        """Test getting drift detection results."""
        # Add some test results
        test_results: List[DriftResult] = [
            {
                "timestamp": time.time(),
                "algorithm": "ks_test",
                "feature_name": "feature1",
                "statistic": 0.2,
                "p_value": 0.3,
                "threshold": 0.05,
                "is_drift": False,
                "sample_size": 5,
                "device_id": self.device_id,
            },
            {
                "timestamp": time.time(),
                "algorithm": "ks_test",
                "feature_name": "feature2",
                "statistic": 0.8,
                "p_value": 0.01,
                "threshold": 0.05,
                "is_drift": True,
                "sample_size": 5,
                "device_id": self.device_id,
            },
        ]
        self.drift_detector.drift_results = test_results.copy()

        # Get results
        results = self.drift_detector.get_drift_results()

        # Verify results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["feature_name"], "feature1")
        self.assertEqual(results[1]["feature_name"], "feature2")

        # Verify that get_drift_results returns a copy
        results[0]["feature_name"] = "modified"
        self.assertEqual(
            self.drift_detector.drift_results[0]["feature_name"], "feature1"
        )

    def test_clear_drift_results(self):
        """Test clearing drift detection results."""
        # Add some test results
        test_results: List[DriftResult] = [
            {
                "timestamp": time.time(),
                "algorithm": "ks_test",
                "feature_name": "feature1",
                "statistic": 0.2,
                "p_value": 0.3,
                "threshold": 0.05,
                "is_drift": False,
                "sample_size": 5,
                "device_id": self.device_id,
            }
        ]
        self.drift_detector.drift_results = test_results.copy()

        # Clear results
        self.drift_detector.clear_drift_results()

        # Verify results were cleared
        self.assertEqual(len(self.drift_detector.drift_results), 0)


if __name__ == "__main__":
    unittest.main()
