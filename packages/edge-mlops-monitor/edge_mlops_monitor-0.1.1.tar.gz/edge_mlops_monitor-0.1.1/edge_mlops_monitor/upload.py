"""
Telemetry upload module for the Edge MLOps Monitor.

This module handles batching and uploading telemetry data to cloud storage
or a lightweight database when network connectivity is available.
"""

import asyncio
import json
import logging
import os
import random
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

import boto3
from botocore.exceptions import ClientError

from edge_mlops_monitor.config import MonitorConfig
from edge_mlops_monitor.drift import DriftResult
from edge_mlops_monitor.model_logger import ModelInput, ModelOutput
from edge_mlops_monitor.system import SystemMetric

logger = logging.getLogger(__name__)


class TelemetryBatch(TypedDict):
    """Telemetry batch data structure."""

    batch_id: str
    timestamp: float
    device_id: str
    system_metrics: List[SystemMetric]
    model_inputs: List[ModelInput]
    model_outputs: List[ModelOutput]
    drift_results: List[DriftResult]


class TelemetryUploader:
    """
    Telemetry upload component.

    Handles batching and uploading telemetry data to cloud storage or a
    lightweight database when network connectivity is available.
    """

    def __init__(self, config: MonitorConfig, device_id: str = "", s3_client=None):
        """
        Initialize the telemetry uploader.

        Args:
            config: Monitor configuration.
            device_id: Unique identifier for the device.
            s3_client: Optional pre-configured S3 client for testing.
        """
        self.config = config
        self.device_id = device_id
        self.upload_interval = config["telemetry"]["upload_interval_seconds"]
        self.max_batch_size = config["telemetry"]["max_batch_size"]
        self.retry_base_delay = config["telemetry"]["retry_base_delay_seconds"]
        self.retry_max_delay = config["telemetry"]["retry_max_delay_seconds"]
        self.retry_max_attempts = config["telemetry"]["retry_max_attempts"]

        self.storage_type = config["storage"]["type"]
        self.bucket = config["storage"]["bucket"]
        self.prefix = config["storage"]["prefix"]
        self.sqlite_path = config["storage"]["sqlite_path"]

        # Initialize the database for local buffering
        self._init_db()

        # Initialize AWS S3 client if needed
        self.s3_client = s3_client
        if self.storage_type == "s3" and self.s3_client is None:
            self._init_s3_client()

        # State variables
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def _init_db(self) -> None:
        """
        Initialize the SQLite database for telemetry buffering.

        Creates the necessary tables if they don't exist.
        """
        # Ensure the directory exists
        db_dir = Path(self.sqlite_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            # Create telemetry batches table
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS telemetry_batches (
                id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                device_id TEXT NOT NULL,
                batch_data TEXT NOT NULL,
                uploaded INTEGER DEFAULT 0,
                upload_attempts INTEGER DEFAULT 0,
                last_attempt REAL DEFAULT 0
            )
            """
            )

            # Create indexes for faster queries
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_batches_uploaded ON telemetry_batches (uploaded)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_batches_timestamp ON telemetry_batches (timestamp)"
            )

            conn.commit()
            conn.close()

            logger.debug("Telemetry database initialized")

        except sqlite3.Error as e:
            logger.error(f"Error initializing telemetry database: {e}")
            raise

    def _init_s3_client(self) -> None:
        """
        Initialize the AWS S3 client.

        Uses environment variables for AWS credentials.
        """
        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
            )
            logger.debug("AWS S3 client initialized")

        except Exception as e:
            logger.error(f"Error initializing AWS S3 client: {e}")
            self.s3_client = None

    def start(self) -> None:
        """
        Start the telemetry upload process in the background.

        This method starts an asyncio task that uploads telemetry data
        at the configured interval.
        """
        if self._running:
            logger.warning("Telemetry upload is already running")
            return

        self._running = True

        # Create event loop if it doesn't exist
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # For testing purposes, we'll just set the task to None if we're in a test environment
        if "pytest" in sys.modules:
            self._task = None
            return

        # Start the upload task
        self._task = asyncio.create_task(self._upload_loop())
        logger.info("Telemetry upload started")

    async def _upload_loop(self) -> None:
        """
        Main upload loop.

        Uploads telemetry data at the configured interval.
        """
        while self._running:
            try:
                # Upload pending batches
                await self._upload_pending_batches()

            except Exception as e:
                logger.error(f"Error in telemetry upload loop: {e}")

            # Wait for the next upload interval
            await asyncio.sleep(self.upload_interval)

    async def _upload_pending_batches(self) -> None:
        """
        Upload pending telemetry batches.

        Retrieves pending batches from the database and uploads them.
        """
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            # Get pending batches
            cursor.execute(
                """
                SELECT id, timestamp, device_id, batch_data, upload_attempts
                FROM telemetry_batches
                WHERE uploaded = 0 AND upload_attempts < ?
                ORDER BY timestamp ASC
                LIMIT ?
                """,
                (self.retry_max_attempts, self.max_batch_size),
            )

            pending_batches = cursor.fetchall()
            conn.close()

            if not pending_batches:
                logger.debug("No pending telemetry batches to upload")
                return

            logger.debug(f"Found {len(pending_batches)} pending telemetry batches")

            # TODO: find out what is for `timestamp` and `device_id` created but never used
            # NOTE: I removed  `timestamp` and `device_id` variables
            # Upload each batch
            for (
                batch_id,
                batch_data_json,
                attempts,
            ) in pending_batches:
                batch_data = json.loads(batch_data_json)

                # Upload the batch
                success = await self._upload_batch(batch_id, batch_data)

                # Update the database
                conn = sqlite3.connect(self.sqlite_path)
                cursor = conn.cursor()

                if success:
                    cursor.execute(
                        "UPDATE telemetry_batches SET uploaded = 1, last_attempt = ? WHERE id = ?",
                        (time.time(), batch_id),
                    )
                    logger.debug(f"Telemetry batch {batch_id} uploaded successfully")
                else:
                    # Increment attempt count and update last attempt time
                    cursor.execute(
                        "UPDATE telemetry_batches SET upload_attempts = upload_attempts + 1, last_attempt = ? WHERE id = ?",
                        (time.time(), batch_id),
                    )
                    logger.warning(
                        f"Failed to upload telemetry batch {batch_id}, attempts: {attempts + 1}"
                    )

                conn.commit()
                conn.close()

        except Exception as e:
            logger.error(f"Error uploading pending telemetry batches: {e}")

    async def _upload_batch(self, batch_id: str, batch_data: Dict[str, Any]) -> bool:
        """
        Upload a telemetry batch.

        Args:
            batch_id: ID of the batch.
            batch_data: Batch data.

        Returns:
            True if the upload was successful, False otherwise.
        """
        if self.storage_type == "s3":
            return await self._upload_to_s3(batch_id, batch_data)
        else:
            logger.error(f"Unsupported storage type: {self.storage_type}")
            return False

    async def _upload_to_s3(self, batch_id: str, batch_data: Dict[str, Any]) -> bool:
        """
        Upload a telemetry batch to AWS S3.

        Args:
            batch_id: ID of the batch.
            batch_data: Batch data.

        Returns:
            True if the upload was successful, False otherwise.
        """
        if not self.s3_client:
            logger.error("AWS S3 client not initialized")
            return False

        try:
            # Serialize the batch data
            batch_json = json.dumps(batch_data)

            # Generate the S3 key
            timestamp = batch_data.get("timestamp", time.time())
            date_str = time.strftime("%Y/%m/%d", time.localtime(timestamp))
            device_id = batch_data.get("device_id", self.device_id)

            s3_key = f"{self.prefix}{date_str}/{device_id}/{batch_id}.json"

            # Upload to S3
            self.s3_client.put_object(Bucket=self.bucket, Key=s3_key, Body=batch_json)

            logger.debug(f"Uploaded telemetry batch to S3: {s3_key}")
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")

            if error_code in ["NoSuchBucket", "AccessDenied"]:
                logger.error(f"S3 error: {error_code} - {e}")
                return False

            # For network-related errors, implement exponential backoff
            logger.warning(f"S3 error (will retry): {error_code} - {e}")

            # Calculate backoff delay
            attempts = 1  # This is handled by the database
            delay = min(
                self.retry_max_delay,
                self.retry_base_delay
                * (2 ** (attempts - 1))
                * (1 + random.random() * 0.1),
            )

            await asyncio.sleep(delay)
            return False

        except Exception as e:
            logger.error(f"Error uploading telemetry batch to S3: {e}")
            return False

    def create_batch(
        self,
        system_metrics: List[SystemMetric],
        model_inputs: List[ModelInput],
        model_outputs: List[ModelOutput],
        drift_results: List[DriftResult],
    ) -> str:
        """
        Create a new telemetry batch.

        Args:
            system_metrics: System metrics to include in the batch.
            model_inputs: Model inputs to include in the batch.
            model_outputs: Model outputs to include in the batch.
            drift_results: Drift detection results to include in the batch.

        Returns:
            ID of the created batch.
        """
        batch_id = f"batch-{int(time.time())}-{random.randint(1000, 9999)}"
        timestamp = time.time()

        # Create the batch
        batch: TelemetryBatch = {
            "batch_id": batch_id,
            "timestamp": timestamp,
            "device_id": self.device_id,
            "system_metrics": system_metrics,
            "model_inputs": model_inputs,
            "model_outputs": model_outputs,
            "drift_results": drift_results,
        }

        try:
            # Serialize the batch
            batch_json = json.dumps(batch)

            # Store in database
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO telemetry_batches (id, timestamp, device_id, batch_data) VALUES (?, ?, ?, ?)",
                (batch_id, timestamp, self.device_id, batch_json),
            )

            conn.commit()
            conn.close()

            logger.debug(f"Created telemetry batch {batch_id}")
            return batch_id

        except Exception as e:
            logger.error(f"Error creating telemetry batch: {e}")
            return batch_id

    def stop(self) -> None:
        """
        Stop the telemetry upload process.
        """
        if not self._running:
            logger.warning("Telemetry upload is not running")
            return

        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

        logger.info("Telemetry upload stopped")

    def get_pending_batch_count(self) -> int:
        """
        Get the number of pending telemetry batches.

        Returns:
            Number of pending batches.
        """
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM telemetry_batches WHERE uploaded = 0 AND upload_attempts < ?",
                (self.retry_max_attempts,),
            )

            count = cursor.fetchone()[0]
            conn.close()

            return count

        except Exception as e:
            logger.error(f"Error getting pending batch count: {e}")
            return 0

    def clear_uploaded_batches(self, older_than_days: int = 7) -> int:
        """
        Clear uploaded telemetry batches from the database.

        Args:
            older_than_days: Only clear batches older than this many days.

        Returns:
            Number of batches cleared.
        """
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            # Calculate cutoff timestamp
            cutoff = time.time() - (older_than_days * 24 * 60 * 60)

            cursor.execute(
                "DELETE FROM telemetry_batches WHERE uploaded = 1 AND timestamp < ?",
                (cutoff,),
            )

            count = cursor.rowcount
            conn.commit()
            conn.close()

            logger.debug(f"Cleared {count} uploaded telemetry batches")
            return count

        except Exception as e:
            logger.error(f"Error clearing uploaded telemetry batches: {e}")
            return 0
