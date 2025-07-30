"""
System health monitoring module for the Edge MLOps Monitor.

This module collects CPU and memory usage metrics with minimal overhead.
"""

# FIXME: Need to optimize CPU metrics collection for better performance on low-power devices

import asyncio
import logging
import time
import copy
from typing import List, Optional, TypedDict

import psutil

from edge_mlops_monitor.config import MonitorConfig

logger = logging.getLogger(__name__)


class SystemMetric(TypedDict):
    """System metric data structure."""

    timestamp: float
    metric_type: str
    value: float
    device_id: str


class SystemMonitor:
    """
    System health monitoring component.

    Collects CPU and memory usage metrics at configurable intervals.
    """

    def __init__(self, config: MonitorConfig, device_id: str = ""):
        """
        Initialize the system monitor.

        Args:
            config: Monitor configuration.
            device_id: Unique identifier for the device.
        """
        self.config = config
        self.device_id = device_id or self._get_device_id()
        self.sampling_interval = config["system"]["sampling_interval_seconds"]
        self.max_buffer_size = (
            config["system"]["max_memory_buffer_mb"] * 1024 * 1024
        )  # Convert to bytes
        self.metrics_buffer: List[SystemMetric] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def _get_device_id(self) -> str:
        """
        Get a unique identifier for the device.

        Returns:
            Device identifier string.
        """
        try:
            # Try to use the hostname as the device ID
            return psutil.net_if_addrs()["eth0"][0].address.replace(":", "")
        except (KeyError, IndexError, AttributeError):
            try:
                # TODO: find out what is `interface` variable can do
                # Fall back to the MAC address of the first network interface
                for (
                    _,
                    addrs,
                ) in (
                    psutil.net_if_addrs().items()
                ):  # NOTE: I convert `interface` variable with `_` symbol
                    for addr in addrs:
                        if addr.family == psutil.AF_LINK:
                            return addr.address.replace(":", "")
            except (IndexError, AttributeError):
                pass

        # If all else fails, use a timestamp-based ID
        return f"device-{int(time.time())}"

    def start(self) -> None:
        """
        Start the system monitoring in the background.

        This method starts an asyncio task that collects system metrics
        at the configured interval.
        """
        if self._running:
            logger.warning("System monitoring is already running")
            return

        self._running = True

        # Create event loop if it doesn't exist
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Start the monitoring task
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("System monitoring started")

    async def _monitor_loop(self) -> None:
        """
        Main monitoring loop.

        Collects system metrics at the configured interval.
        """
        while self._running:
            try:
                # Collect CPU and memory metrics
                metrics = self._collect_metrics()

                # Add metrics to buffer
                self.metrics_buffer.extend(metrics)

                # Enforce buffer size limit (FIFO)
                if (
                    len(self.metrics_buffer) * 100 > self.max_buffer_size
                ):  # Approximate size check
                    excess = len(self.metrics_buffer) - int(self.max_buffer_size / 100)
                    if excess > 0:
                        self.metrics_buffer = self.metrics_buffer[excess:]
                        logger.debug(f"Trimmed metrics buffer by {excess} records")

            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")

            # Wait for the next collection interval
            await asyncio.sleep(self.sampling_interval)

    def _collect_metrics(self) -> List[SystemMetric]:
        """
        Collect system metrics.

        Returns:
            List of system metrics.
        """
        timestamp = time.time()
        metrics: List[SystemMetric] = []

        try:
            # CPU usage (per core and overall)
            cpu_percent = psutil.cpu_percent(interval=0.1)  # Quick sample
            metrics.append(
                {
                    "timestamp": timestamp,
                    "metric_type": "cpu_percent",
                    "value": cpu_percent,
                    "device_id": self.device_id,
                }
            )

            # Per-core CPU usage (optional, can be disabled for lower overhead)
            cpu_percent_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            for i, percent in enumerate(cpu_percent_per_core):
                metrics.append(
                    {
                        "timestamp": timestamp,
                        "metric_type": f"cpu_percent_core_{i}",
                        "value": percent,
                        "device_id": self.device_id,
                    }
                )

            # Memory usage
            memory = psutil.virtual_memory()
            metrics.append(
                {
                    "timestamp": timestamp,
                    "metric_type": "memory_percent",
                    "value": memory.percent,
                    "device_id": self.device_id,
                }
            )
            metrics.append(
                {
                    "timestamp": timestamp,
                    "metric_type": "memory_available_mb",
                    "value": memory.available / (1024 * 1024),  # Convert to MB
                    "device_id": self.device_id,
                }
            )

            # Disk usage
            disk = psutil.disk_usage("/")
            metrics.append(
                {
                    "timestamp": timestamp,
                    "metric_type": "disk_percent",
                    "value": disk.percent,
                    "device_id": self.device_id,
                }
            )
            metrics.append(
                {
                    "timestamp": timestamp,
                    "metric_type": "disk_free_mb",
                    "value": disk.free / (1024 * 1024),  # Convert to MB
                    "device_id": self.device_id,
                }
            )

        except Exception as e:
            logger.error(f"Error collecting specific metric: {e}")

        return metrics

    def stop(self) -> None:
        """
        Stop the system monitoring.
        """
        if not self._running:
            logger.warning("System monitoring is not running")
            return

        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

        logger.info("System monitoring stopped")

    def get_metrics(self) -> List[SystemMetric]:
        """
        Get the collected metrics.

        Returns:
            List of system metrics (deep copy).
        """
        return copy.deepcopy(self.metrics_buffer)

    def clear_metrics(self) -> None:
        """
        Clear the metrics buffer.
        """
        self.metrics_buffer.clear()
        logger.debug("Metrics buffer cleared")
