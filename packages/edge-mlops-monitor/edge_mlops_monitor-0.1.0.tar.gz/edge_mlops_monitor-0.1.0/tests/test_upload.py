"""
Unit tests for the telemetry upload module.
"""

import asyncio
import json
import os
import sqlite3
import tempfile
import time
from typing import List
import unittest
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from edge_mlops_monitor.config import load_config
from edge_mlops_monitor.drift import DriftResult
from edge_mlops_monitor.model_logger import ModelInput, ModelOutput
from edge_mlops_monitor.system import SystemMetric
from edge_mlops_monitor.upload import TelemetryUploader


class TestTelemetryUploader(unittest.TestCase):
    """Test cases for the telemetry upload module."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = load_config()
        # Create a temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Update config with test settings
        self.config["storage"]["sqlite_path"] = self.db_path
        self.config["storage"]["type"] = "s3"
        self.config["storage"]["bucket"] = "test-bucket"
        self.config["storage"]["prefix"] = "test-prefix/"
        self.config["telemetry"]["upload_interval_seconds"] = 0.1  # Fast for testing
        self.config["telemetry"]["retry_base_delay_seconds"] = 0.1  # Fast for testing

        self.device_id = "test-device"

        # Create a mock S3 client
        self.mock_s3 = MagicMock()

        # Initialize uploader with mock S3 client
        self.uploader = TelemetryUploader(
            self.config, device_id=self.device_id, s3_client=self.mock_s3
        )

    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the uploader if running
        if hasattr(self, "uploader") and self.uploader._running:
            self.uploader.stop()

        # Remove the temporary database file
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_initialization(self):
        """Test initialization of the telemetry uploader."""
        self.assertEqual(self.uploader.device_id, self.device_id)
        self.assertEqual(
            self.uploader.upload_interval,
            self.config["telemetry"]["upload_interval_seconds"],
        )
        self.assertEqual(
            self.uploader.max_batch_size, self.config["telemetry"]["max_batch_size"]
        )
        self.assertEqual(
            self.uploader.retry_base_delay,
            self.config["telemetry"]["retry_base_delay_seconds"],
        )
        self.assertEqual(
            self.uploader.retry_max_delay,
            self.config["telemetry"]["retry_max_delay_seconds"],
        )
        self.assertEqual(
            self.uploader.retry_max_attempts,
            self.config["telemetry"]["retry_max_attempts"],
        )
        self.assertEqual(self.uploader.storage_type, self.config["storage"]["type"])
        self.assertEqual(self.uploader.bucket, self.config["storage"]["bucket"])
        self.assertEqual(self.uploader.prefix, self.config["storage"]["prefix"])
        self.assertEqual(self.uploader.sqlite_path, self.db_path)
        self.assertFalse(self.uploader._running)
        self.assertIsNone(self.uploader._task)

        # Verify database tables were created
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check telemetry_batches table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='telemetry_batches'"
        )
        self.assertIsNotNone(cursor.fetchone())

        # Check indexes
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_batches_uploaded'"
        )
        self.assertIsNotNone(cursor.fetchone())

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_batches_timestamp'"
        )
        self.assertIsNotNone(cursor.fetchone())

        conn.close()

    def test_create_batch(self):
        """Test creating a telemetry batch."""
        # Create test data
        system_metrics: List[SystemMetric] = [
            {
                "timestamp": time.time(),
                "metric_type": "cpu_percent",
                "value": 50.0,
                "device_id": self.device_id,
            }
        ]

        model_inputs: List[ModelInput] = [
            {
                "id": "input-1",
                "timestamp": time.time(),
                "input_data": {"feature1": 1.0},
                "device_id": self.device_id,
            }
        ]

        model_outputs: List[ModelOutput] = [
            {
                "id": "output-1",
                "input_id": "input-1",
                "timestamp": time.time(),
                "output_data": {"prediction": 2.0},
                "device_id": self.device_id,
            }
        ]

        drift_results: List[DriftResult] = [
            {
                "timestamp": time.time(),
                "algorithm": "ks_test",
                "feature_name": "prediction",
                "statistic": 0.2,
                "p_value": 0.3,
                "threshold": 0.05,
                "is_drift": False,
                "sample_size": 5,
                "device_id": self.device_id,
            }
        ]

        # Create batch
        batch_id = self.uploader.create_batch(
            system_metrics=system_metrics,
            model_inputs=model_inputs,
            model_outputs=model_outputs,
            drift_results=drift_results,
        )

        # Verify batch was created
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, device_id, batch_data, uploaded FROM telemetry_batches WHERE id = ?",
            (batch_id,),
        )
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], batch_id)
        self.assertEqual(row[1], self.device_id)

        # Verify batch data
        batch_data = json.loads(row[2])
        self.assertEqual(batch_data["batch_id"], batch_id)
        self.assertEqual(batch_data["device_id"], self.device_id)
        self.assertEqual(len(batch_data["system_metrics"]), 1)
        self.assertEqual(len(batch_data["model_inputs"]), 1)
        self.assertEqual(len(batch_data["model_outputs"]), 1)
        self.assertEqual(len(batch_data["drift_results"]), 1)

        # Verify batch is not uploaded
        self.assertEqual(row[3], 0)

    def test_upload_batch_success(self):
        """Test uploading a batch successfully."""
        # Create a batch
        batch_id = self.uploader.create_batch(
            system_metrics=[], model_inputs=[], model_outputs=[], drift_results=[]
        )

        # Upload the batch
        with patch("asyncio.sleep", return_value=None):  # Skip sleep
            result = asyncio.run(
                self.uploader._upload_batch(batch_id, {"batch_id": batch_id})
            )

        # Verify upload was successful
        self.assertTrue(result)
        self.assertTrue(self.mock_s3.put_object.called)

    def test_upload_batch_failure(self):
        """Test handling upload failure."""
        # Configure mock S3 client to raise an error
        self.mock_s3.put_object.side_effect = ClientError(
            {"Error": {"Code": "NetworkError", "Message": "Network error"}}, "PutObject"
        )

        # Create a batch
        batch_id = self.uploader.create_batch(
            system_metrics=[], model_inputs=[], model_outputs=[], drift_results=[]
        )

        # Upload the batch
        with patch("asyncio.sleep", return_value=None):  # Skip sleep
            result = asyncio.run(
                self.uploader._upload_batch(batch_id, {"batch_id": batch_id})
            )

        # Verify upload failed
        self.assertFalse(result)

    async def async_test_upload_pending_batches(self):
        """Async helper for testing uploading pending batches."""
        # Create some batches
        for _ in range(3):
            self.uploader.create_batch(
                system_metrics=[], model_inputs=[], model_outputs=[], drift_results=[]
            )

        # Upload pending batches
        with patch("asyncio.sleep", return_value=None):  # Skip sleep
            await self.uploader._upload_pending_batches()

        # Verify batches were uploaded
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM telemetry_batches WHERE uploaded = 1")
        uploaded_count = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(uploaded_count, 3)
        self.assertEqual(self.mock_s3.put_object.call_count, 3)

    def test_upload_pending_batches(self):
        """Test uploading pending batches."""
        asyncio.run(self.async_test_upload_pending_batches())

    def test_get_pending_batch_count(self):
        """Test getting the number of pending batches."""
        # Create some batches
        for _ in range(3):
            self.uploader.create_batch(
                system_metrics=[], model_inputs=[], model_outputs=[], drift_results=[]
            )

        # Get pending batch count
        count = self.uploader.get_pending_batch_count()

        # Verify count
        self.assertEqual(count, 3)

    def test_clear_uploaded_batches(self):
        """Test clearing uploaded batches."""
        # Create some batches
        batch_ids = []
        for _ in range(3):
            batch_id = self.uploader.create_batch(
                system_metrics=[], model_inputs=[], model_outputs=[], drift_results=[]
            )
            batch_ids.append(batch_id)

        # Mark batches as uploaded
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE telemetry_batches SET uploaded = 1")
        conn.commit()
        conn.close()

        # Set timestamp to old value
        old_timestamp = time.time() - (8 * 24 * 60 * 60)  # 8 days ago
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE telemetry_batches SET timestamp = ?", (old_timestamp,))
        conn.commit()
        conn.close()

        # Clear uploaded batches older than 7 days
        cleared = self.uploader.clear_uploaded_batches(older_than_days=7)

        # Verify batches were cleared
        self.assertEqual(cleared, 3)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM telemetry_batches")
        count = cursor.fetchone()[0]
        conn.close()

        self.assertEqual(count, 0)

    @patch("asyncio.new_event_loop")
    @patch("asyncio.set_event_loop")
    def test_start_stop(self, mock_set_event_loop, mock_new_event_loop):
        """Test starting and stopping the telemetry uploader."""
        # Mock the event loop
        mock_loop = MagicMock()
        mock_new_event_loop.return_value = mock_loop

        # Start uploader
        with patch("asyncio.create_task", return_value=MagicMock()):
            self.uploader.start()
            self.assertTrue(self.uploader._running)

            # Stop uploader
            self.uploader.stop()
            self.assertFalse(self.uploader._running)


if __name__ == "__main__":
    unittest.main()
