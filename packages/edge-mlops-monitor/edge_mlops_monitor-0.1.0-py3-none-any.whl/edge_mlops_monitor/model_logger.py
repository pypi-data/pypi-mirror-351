"""
Model input/output logging module for the Edge MLOps Monitor.

This module provides functionality for logging model inputs and outputs
with minimal overhead.
"""

import json
import logging
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict

from edge_mlops_monitor.config import MonitorConfig

logger = logging.getLogger(__name__)


class ModelInput(TypedDict):
    """Model input data structure."""

    id: str
    timestamp: float
    input_data: Dict[str, Any]
    device_id: str


class ModelOutput(TypedDict):
    """Model output data structure."""

    id: str
    input_id: str
    timestamp: float
    output_data: Dict[str, Any]
    device_id: str


class ModelLogger:
    """
    Model input/output logging component.

    Logs model inputs and outputs for analysis and drift detection.
    """

    def __init__(
        self, config: MonitorConfig, device_id: str = "", db_path: Optional[str] = None
    ):
        """
        Initialize the model logger.

        Args:
            config: Monitor configuration.
            device_id: Unique identifier for the device.
            db_path: Path to the SQLite database. If None, uses the path from config.
        """
        self.config = config
        self.device_id = device_id
        self.buffer_size = config["model_logging"]["buffer_size"]
        self.db_path = db_path or config["storage"]["sqlite_path"]

        # Initialize the database
        self._init_db()

    def _init_db(self) -> None:
        """
        Initialize the SQLite database for model logging.

        Creates the necessary tables if they don't exist.
        """
        # Ensure the directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create model inputs table
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS model_inputs (
                id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                input_data TEXT NOT NULL,
                device_id TEXT NOT NULL
            )
            """
            )

            # Create model outputs table
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS model_outputs (
                id TEXT PRIMARY KEY,
                input_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                output_data TEXT NOT NULL,
                device_id TEXT NOT NULL,
                FOREIGN KEY (input_id) REFERENCES model_inputs (id)
            )
            """
            )

            # Create indexes for faster queries
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_inputs_timestamp ON model_inputs (timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_outputs_timestamp ON model_outputs (timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_outputs_input_id ON model_outputs (input_id)"
            )

            conn.commit()
            conn.close()

            logger.debug("Model logging database initialized")

        except sqlite3.Error as e:
            logger.error(f"Error initializing model logging database: {e}")
            raise

    def log_input(self, input_data: Dict[str, Any]) -> str:
        """
        Log a model input.

        Args:
            input_data: Model input data.

        Returns:
            ID of the logged input.
        """
        input_id = str(uuid.uuid4())
        timestamp = time.time()

        try:
            # Validate input data
            if not isinstance(input_data, dict):
                raise ValueError("Input data must be a dictionary")

            # Serialize input data
            input_json = json.dumps(input_data)

            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO model_inputs (id, timestamp, input_data, device_id) VALUES (?, ?, ?, ?)",
                (input_id, timestamp, input_json, self.device_id),
            )

            # Enforce buffer size limit (FIFO)
            cursor.execute("SELECT COUNT(*) FROM model_inputs")
            count = cursor.fetchone()[0]

            if count > self.buffer_size:
                # Delete oldest records
                excess = count - self.buffer_size
                cursor.execute(
                    "DELETE FROM model_inputs WHERE id IN (SELECT id FROM model_inputs ORDER BY timestamp ASC LIMIT ?)",
                    (excess,),
                )
                logger.debug(f"Trimmed model inputs buffer by {excess} records")

            conn.commit()
            conn.close()

            logger.debug(f"Logged model input with ID {input_id}")
            return input_id

        except Exception as e:
            logger.error(f"Error logging model input: {e}")
            return input_id  # Return the ID even if logging failed

    def log_output(self, input_id: str, output_data: Dict[str, Any]) -> str:
        """
        Log a model output.

        Args:
            input_id: ID of the corresponding input.
            output_data: Model output data.

        Returns:
            ID of the logged output.
        """
        output_id = str(uuid.uuid4())
        timestamp = time.time()

        try:
            # Validate output data
            if not isinstance(output_data, dict):
                raise ValueError("Output data must be a dictionary")

            # Serialize output data
            output_json = json.dumps(output_data)

            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO model_outputs (id, input_id, timestamp, output_data, device_id) VALUES (?, ?, ?, ?, ?)",
                (output_id, input_id, timestamp, output_json, self.device_id),
            )

            # Enforce buffer size limit (FIFO)
            cursor.execute("SELECT COUNT(*) FROM model_outputs")
            count = cursor.fetchone()[0]

            if count > self.buffer_size:
                # Delete oldest records
                excess = count - self.buffer_size
                cursor.execute(
                    "DELETE FROM model_outputs WHERE id IN (SELECT id FROM model_outputs ORDER BY timestamp ASC LIMIT ?)",
                    (excess,),
                )
                logger.debug(f"Trimmed model outputs buffer by {excess} records")

            conn.commit()
            conn.close()

            logger.debug(f"Logged model output with ID {output_id}")
            return output_id

        except Exception as e:
            logger.error(f"Error logging model output: {e}")
            return output_id  # Return the ID even if logging failed

    def get_inputs(self, limit: int = 100, offset: int = 0) -> List[ModelInput]:
        """
        Get logged model inputs.

        Args:
            limit: Maximum number of inputs to retrieve.
            offset: Offset for pagination.

        Returns:
            List of model inputs.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, timestamp, input_data, device_id FROM model_inputs ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )

            inputs: List[ModelInput] = []
            for row in cursor.fetchall():
                input_id, timestamp, input_data_json, device_id = row
                input_data = json.loads(input_data_json)

                inputs.append(
                    {
                        "id": input_id,
                        "timestamp": timestamp,
                        "input_data": input_data,
                        "device_id": device_id,
                    }
                )

            conn.close()
            return inputs

        except Exception as e:
            logger.error(f"Error retrieving model inputs: {e}")
            return []

    def get_outputs(self, limit: int = 100, offset: int = 0) -> List[ModelOutput]:
        """
        Get logged model outputs.

        Args:
            limit: Maximum number of outputs to retrieve.
            offset: Offset for pagination.

        Returns:
            List of model outputs.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, input_id, timestamp, output_data, device_id FROM model_outputs ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )

            outputs: List[ModelOutput] = []
            for row in cursor.fetchall():
                output_id, input_id, timestamp, output_data_json, device_id = row
                output_data = json.loads(output_data_json)

                outputs.append(
                    {
                        "id": output_id,
                        "input_id": input_id,
                        "timestamp": timestamp,
                        "output_data": output_data,
                        "device_id": device_id,
                    }
                )

            conn.close()
            return outputs

        except Exception as e:
            logger.error(f"Error retrieving model outputs: {e}")
            return []

    def get_input_output_pairs(
        self, limit: int = 100, offset: int = 0
    ) -> List[Tuple[ModelInput, ModelOutput]]:
        """
        Get paired model inputs and outputs.

        Args:
            limit: Maximum number of pairs to retrieve.
            offset: Offset for pagination.

        Returns:
            List of (input, output) tuples.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    i.id, i.timestamp, i.input_data, i.device_id,
                    o.id, o.timestamp, o.output_data, o.device_id
                FROM model_inputs i
                JOIN model_outputs o ON i.id = o.input_id
                ORDER BY o.timestamp DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )

            pairs: List[Tuple[ModelInput, ModelOutput]] = []
            for row in cursor.fetchall():
                (
                    input_id,
                    input_timestamp,
                    input_data_json,
                    input_device_id,
                    output_id,
                    output_timestamp,
                    output_data_json,
                    output_device_id,
                ) = row

                input_data = json.loads(input_data_json)
                output_data = json.loads(output_data_json)

                model_input: ModelInput = {
                    "id": input_id,
                    "timestamp": input_timestamp,
                    "input_data": input_data,
                    "device_id": input_device_id,
                }

                model_output: ModelOutput = {
                    "id": output_id,
                    "input_id": input_id,
                    "timestamp": output_timestamp,
                    "output_data": output_data,
                    "device_id": output_device_id,
                }

                pairs.append((model_input, model_output))

            conn.close()
            return pairs

        except Exception as e:
            logger.error(f"Error retrieving model input-output pairs: {e}")
            return []

    def clear_logs(self) -> None:
        """
        Clear all logs from the database.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM model_outputs")
            cursor.execute("DELETE FROM model_inputs")

            conn.commit()
            conn.close()

            logger.debug("Model logs cleared")

        except Exception as e:
            logger.error(f"Error clearing model logs: {e}")
