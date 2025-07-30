"""
Unit tests for the model logging module.
"""

import json
import os
import sqlite3
import tempfile
import time
import unittest

from edge_mlops_monitor.config import load_config
from edge_mlops_monitor.model_logger import ModelLogger


class TestModelLogger(unittest.TestCase):
    """Test cases for the model logging module."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = load_config()
        # Create a temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.device_id = "test-device"
        self.model_logger = ModelLogger(self.config, device_id=self.device_id, db_path=self.db_path)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary database file
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_initialization(self):
        """Test initialization of the model logger."""
        self.assertEqual(self.model_logger.device_id, self.device_id)
        self.assertEqual(self.model_logger.db_path, self.db_path)
        self.assertEqual(self.model_logger.buffer_size, self.config["model_logging"]["buffer_size"])
        
        # Verify database tables were created
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check model_inputs table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_inputs'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check model_outputs table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_outputs'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_inputs_timestamp'")
        self.assertIsNotNone(cursor.fetchone())
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_outputs_timestamp'")
        self.assertIsNotNone(cursor.fetchone())
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_outputs_input_id'")
        self.assertIsNotNone(cursor.fetchone())
        
        conn.close()

    def test_log_input(self):
        """Test logging a model input."""
        input_data = {"feature1": 1.0, "feature2": 2.0}
        input_id = self.model_logger.log_input(input_data)
        
        # Verify input was logged
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, input_data, device_id FROM model_inputs WHERE id = ?", (input_id,))
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], input_id)
        self.assertEqual(json.loads(row[1]), input_data)
        self.assertEqual(row[2], self.device_id)

    def test_log_output(self):
        """Test logging a model output."""
        # First log an input
        input_data = {"feature1": 1.0, "feature2": 2.0}
        input_id = self.model_logger.log_input(input_data)
        
        # Then log an output
        output_data = {"prediction": 3.0, "confidence": 0.9}
        output_id = self.model_logger.log_output(input_id, output_data)
        
        # Verify output was logged
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, input_id, output_data, device_id FROM model_outputs WHERE id = ?", (output_id,))
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], output_id)
        self.assertEqual(row[1], input_id)
        self.assertEqual(json.loads(row[2]), output_data)
        self.assertEqual(row[3], self.device_id)

    def test_get_inputs(self):
        """Test getting logged model inputs."""
        # Log some inputs
        input_ids = []
        for i in range(5):
            input_data = {"feature1": float(i), "feature2": float(i * 2)}
            input_id = self.model_logger.log_input(input_data)
            input_ids.append(input_id)
            time.sleep(0.01)  # Ensure different timestamps
        
        # Get inputs
        inputs = self.model_logger.get_inputs(limit=3)
        
        # Verify inputs
        self.assertEqual(len(inputs), 3)
        self.assertEqual(inputs[0]["id"], input_ids[4])  # Most recent first
        self.assertEqual(inputs[1]["id"], input_ids[3])
        self.assertEqual(inputs[2]["id"], input_ids[2])
        
        # Check pagination
        inputs = self.model_logger.get_inputs(limit=2, offset=2)
        self.assertEqual(len(inputs), 2)
        self.assertEqual(inputs[0]["id"], input_ids[2])
        self.assertEqual(inputs[1]["id"], input_ids[1])

    def test_get_outputs(self):
        """Test getting logged model outputs."""
        # Log some inputs and outputs
        output_ids = []
        for i in range(5):
            input_data = {"feature1": float(i), "feature2": float(i * 2)}
            input_id = self.model_logger.log_input(input_data)
            
            output_data = {"prediction": float(i * 3), "confidence": 0.8 + float(i) / 10}
            output_id = self.model_logger.log_output(input_id, output_data)
            output_ids.append(output_id)
            time.sleep(0.01)  # Ensure different timestamps
        
        # Get outputs
        outputs = self.model_logger.get_outputs(limit=3)
        
        # Verify outputs
        self.assertEqual(len(outputs), 3)
        self.assertEqual(outputs[0]["id"], output_ids[4])  # Most recent first
        self.assertEqual(outputs[1]["id"], output_ids[3])
        self.assertEqual(outputs[2]["id"], output_ids[2])
        
        # Check pagination
        outputs = self.model_logger.get_outputs(limit=2, offset=2)
        self.assertEqual(len(outputs), 2)
        self.assertEqual(outputs[0]["id"], output_ids[2])
        self.assertEqual(outputs[1]["id"], output_ids[1])

    def test_get_input_output_pairs(self):
        """Test getting paired model inputs and outputs."""
        # Log some inputs and outputs
        pairs = []
        for i in range(5):
            input_data = {"feature1": float(i), "feature2": float(i * 2)}
            input_id = self.model_logger.log_input(input_data)
            
            output_data = {"prediction": float(i * 3), "confidence": 0.8 + float(i) / 10}
            output_id = self.model_logger.log_output(input_id, output_data)
            
            pairs.append((input_id, output_id))
            time.sleep(0.01)  # Ensure different timestamps
        
        # Get input-output pairs
        io_pairs = self.model_logger.get_input_output_pairs(limit=3)
        
        # Verify pairs
        self.assertEqual(len(io_pairs), 3)
        self.assertEqual(io_pairs[0][0]["id"], pairs[4][0])  # Most recent first
        self.assertEqual(io_pairs[0][1]["id"], pairs[4][1])
        self.assertEqual(io_pairs[1][0]["id"], pairs[3][0])
        self.assertEqual(io_pairs[1][1]["id"], pairs[3][1])
        self.assertEqual(io_pairs[2][0]["id"], pairs[2][0])
        self.assertEqual(io_pairs[2][1]["id"], pairs[2][1])

    def test_buffer_size_limit(self):
        """Test enforcing buffer size limit."""
        # Set a small buffer size
        self.model_logger.buffer_size = 3
        
        # Log more inputs than the buffer size
        input_ids = []
        for i in range(5):
            input_data = {"feature1": float(i), "feature2": float(i * 2)}
            input_id = self.model_logger.log_input(input_data)
            input_ids.append(input_id)
        
        # Verify only the most recent inputs are kept
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM model_inputs")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 3)
        
        # Get inputs and verify they are the most recent ones
        inputs = self.model_logger.get_inputs(limit=5)
        self.assertEqual(len(inputs), 3)
        self.assertEqual(inputs[0]["id"], input_ids[4])
        self.assertEqual(inputs[1]["id"], input_ids[3])
        self.assertEqual(inputs[2]["id"], input_ids[2])

    def test_clear_logs(self):
        """Test clearing all logs."""
        # Log some inputs and outputs
        for i in range(3):
            input_data = {"feature1": float(i), "feature2": float(i * 2)}
            input_id = self.model_logger.log_input(input_data)
            
            output_data = {"prediction": float(i * 3), "confidence": 0.8 + float(i) / 10}
            self.model_logger.log_output(input_id, output_data)
        
        # Clear logs
        self.model_logger.clear_logs()
        
        # Verify logs were cleared
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM model_inputs")
        input_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM model_outputs")
        output_count = cursor.fetchone()[0]
        
        conn.close()
        
        self.assertEqual(input_count, 0)
        self.assertEqual(output_count, 0)


if __name__ == "__main__":
    unittest.main()
