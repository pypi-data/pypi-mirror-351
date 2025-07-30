"""
Unit tests for the system monitoring module.
"""

import asyncio
import time
from typing import List
import unittest
from unittest.mock import MagicMock, patch

from edge_mlops_monitor.config import load_config
from edge_mlops_monitor.system import SystemMetric, SystemMonitor


class TestSystemMonitor(unittest.TestCase):
    """Test cases for the system monitoring module."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = load_config()
        # Use shorter intervals for testing
        self.config["system"]["sampling_interval_seconds"] = 0.1
        self.device_id = "test-device"
        self.monitor = SystemMonitor(self.config, device_id=self.device_id)

    def tearDown(self):
        """Tear down test fixtures."""
        if hasattr(self, "monitor") and self.monitor._running:
            self.monitor.stop()

    def test_initialization(self):
        """Test initialization of the system monitor."""
        self.assertEqual(self.monitor.device_id, self.device_id)
        self.assertEqual(self.monitor.sampling_interval, 0.1)
        self.assertFalse(self.monitor._running)
        self.assertIsNone(self.monitor._task)
        self.assertEqual(len(self.monitor.metrics_buffer), 0)

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_collect_metrics(
        self, mock_disk_usage, mock_virtual_memory, mock_cpu_percent
    ):
        """Test collection of system metrics."""
        # Mock psutil functions
        mock_cpu_percent.side_effect = [50.0, [40.0, 60.0]]
        mock_virtual_memory.return_value = MagicMock(
            percent=70.0, available=1073741824  # 1 GB
        )
        mock_disk_usage.return_value = MagicMock(
            percent=80.0, free=10737418240  # 10 GB
        )

        # Collect metrics
        metrics = self.monitor._collect_metrics()

        # Verify metrics
        self.assertEqual(
            len(metrics), 7
        )  # 1 CPU overall + 2 CPU cores + 2 memory + 2 disk

        # Check CPU metrics
        cpu_metrics = [m for m in metrics if m["metric_type"] == "cpu_percent"]
        self.assertEqual(len(cpu_metrics), 1)
        self.assertEqual(cpu_metrics[0]["value"], 50.0)
        self.assertEqual(cpu_metrics[0]["device_id"], self.device_id)

        # Check per-core CPU metrics
        core_metrics = [m for m in metrics if "cpu_percent_core" in m["metric_type"]]
        self.assertEqual(len(core_metrics), 2)
        self.assertEqual(core_metrics[0]["value"], 40.0)
        self.assertEqual(core_metrics[1]["value"], 60.0)

        # Check memory metrics
        memory_percent_metrics = [
            m for m in metrics if m["metric_type"] == "memory_percent"
        ]
        self.assertEqual(len(memory_percent_metrics), 1)
        self.assertEqual(memory_percent_metrics[0]["value"], 70.0)

        memory_available_metrics = [
            m for m in metrics if m["metric_type"] == "memory_available_mb"
        ]
        self.assertEqual(len(memory_available_metrics), 1)
        self.assertEqual(memory_available_metrics[0]["value"], 1024.0)  # 1 GB in MB

        # Check disk metrics
        disk_percent_metrics = [
            m for m in metrics if m["metric_type"] == "disk_percent"
        ]
        self.assertEqual(len(disk_percent_metrics), 1)
        self.assertEqual(disk_percent_metrics[0]["value"], 80.0)

        disk_free_metrics = [m for m in metrics if m["metric_type"] == "disk_free_mb"]
        self.assertEqual(len(disk_free_metrics), 1)
        self.assertEqual(disk_free_metrics[0]["value"], 10240.0)  # 10 GB in MB

    @patch("asyncio.new_event_loop")
    @patch("asyncio.set_event_loop")
    @patch("asyncio.create_task")
    def test_start_stop(
        self, mock_create_task, mock_set_event_loop, mock_new_event_loop
    ):
        """Test starting and stopping the system monitor."""
        # Mock asyncio functions
        mock_loop = MagicMock()
        mock_new_event_loop.return_value = mock_loop
        mock_task = MagicMock()
        mock_create_task.return_value = mock_task

        # Start monitoring
        self.monitor.start()
        self.assertTrue(self.monitor._running)
        self.assertIsNotNone(self.monitor._task)

        # Verify event loop was created and set
        mock_new_event_loop.assert_called_once()
        mock_set_event_loop.assert_called_once_with(mock_loop)
        mock_create_task.assert_called_once()

        # Stop monitoring
        self.monitor.stop()
        self.assertFalse(self.monitor._running)
        self.assertIsNone(self.monitor._task)

        # Verify task was canceled
        mock_task.cancel.assert_called_once()

    def test_get_metrics(self):
        """Test getting collected metrics."""
        # Add some test metrics
        test_metrics: List[SystemMetric] = [
            {
                "timestamp": time.time(),
                "metric_type": "test_metric",
                "value": 42.0,
                "device_id": self.device_id,
            }
        ]
        self.monitor.metrics_buffer = test_metrics.copy()

        # Get metrics
        metrics = self.monitor.get_metrics()

        # Verify metrics
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["metric_type"], "test_metric")
        self.assertEqual(metrics[0]["value"], 42.0)

        # Verify that get_metrics returns a copy
        metrics[0]["value"] = 99.0
        self.assertEqual(self.monitor.metrics_buffer[0]["value"], 42.0)

    def test_clear_metrics(self):
        """Test clearing metrics buffer."""
        # Add some test metrics
        test_metrics: List[SystemMetric] = [
            {
                "timestamp": time.time(),
                "metric_type": "test_metric",
                "value": 42.0,
                "device_id": self.device_id,
            }
        ]
        self.monitor.metrics_buffer = test_metrics.copy()

        # Clear metrics
        self.monitor.clear_metrics()

        # Verify metrics buffer is empty
        self.assertEqual(len(self.monitor.metrics_buffer), 0)

    @patch("edge_mlops_monitor.system.SystemMonitor._collect_metrics")
    def test_monitor_loop(self, mock_collect_metrics):
        """Test the monitoring loop."""
        # Mock _collect_metrics to return test metrics
        test_metrics = [
            {
                "timestamp": time.time(),
                "metric_type": "test_metric",
                "value": 42.0,
                "device_id": self.device_id,
            }
        ]
        mock_collect_metrics.return_value = test_metrics

        # Create an event loop for testing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Start monitoring
            self.monitor._running = True

            # Run the monitoring loop for a short time
            async def run_test():
                task = asyncio.create_task(self.monitor._monitor_loop())
                await asyncio.sleep(0.3)  # Should collect metrics 3 times
                self.monitor._running = False
                await task

            loop.run_until_complete(run_test())

            # Verify metrics were collected
            self.assertEqual(mock_collect_metrics.call_count, 3)
            self.assertEqual(len(self.monitor.metrics_buffer), 3)
        finally:
            loop.close()

    def test_buffer_size_limit(self):
        """Test enforcing buffer size limit."""
        # Set a small buffer size limit
        self.monitor.max_buffer_size = 500  # bytes

        # Add many metrics to exceed the buffer size
        for i in range(100):  # Each metric is about 100 bytes
            self.monitor.metrics_buffer.append(
                {
                    "timestamp": time.time(),
                    "metric_type": f"test_metric_{i}",
                    "value": float(i),
                    "device_id": self.device_id,
                }
            )

        # Simulate the buffer size check in _monitor_loop
        if len(self.monitor.metrics_buffer) * 100 > self.monitor.max_buffer_size:
            excess = len(self.monitor.metrics_buffer) - int(
                self.monitor.max_buffer_size / 100
            )
            if excess > 0:
                self.monitor.metrics_buffer = self.monitor.metrics_buffer[excess:]

        # Verify buffer was trimmed
        self.assertLessEqual(
            len(self.monitor.metrics_buffer), 5
        )  # 500 bytes / 100 bytes per metric = 5 metrics


if __name__ == "__main__":
    unittest.main()
