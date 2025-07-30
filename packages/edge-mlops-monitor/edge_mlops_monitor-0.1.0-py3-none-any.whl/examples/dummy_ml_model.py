"""
Example script demonstrating integration with a dummy ML model.

This script shows how to use the Edge MLOps Monitor with a simple ML model.
"""

import argparse
import json
import logging
import os
import random
import time
from typing import Dict, List

from edge_mlops_monitor import EdgeMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DummyModel:
    """
    A dummy ML model for demonstration purposes.

    This model predicts housing prices based on simple features.
    """

    def __init__(self, drift_after: int = 0, drift_magnitude: float = 0.0):
        """
        Initialize the dummy model.

        Args:
            drift_after: Number of predictions after which to introduce drift.
                         If 0, no drift is introduced.
            drift_magnitude: Magnitude of the drift to introduce.
        """
        self.prediction_count = 0
        self.drift_after = drift_after
        self.drift_magnitude = drift_magnitude
        logger.info("Dummy model initialized")

    def predict(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Make a prediction based on input features.

        Args:
            features: Dictionary of input features.

        Returns:
            Dictionary with prediction results.
        """
        self.prediction_count += 1

        # Extract features with defaults
        bedrooms = features.get("bedrooms", 3)
        bathrooms = features.get("bathrooms", 2)
        sqft = features.get("sqft", 1500)
        age = features.get("age", 15)

        # Base price calculation
        base_price = (
            100000
            + (bedrooms * 20000)
            + (bathrooms * 15000)
            + (sqft * 100)
            - (age * 1000)
        )

        # Add some randomness
        noise = random.uniform(-10000, 10000)
        price = base_price + noise

        # Introduce drift if configured
        if self.drift_after > 0 and self.prediction_count > self.drift_after:
            # Apply drift to price
            drift_factor = (
                self.drift_magnitude * (self.prediction_count - self.drift_after) / 100
            )
            price = price * (1 + drift_factor)

            logger.debug(f"Applied drift factor: {1 + drift_factor}")

        # Calculate confidence score (just for demonstration)
        confidence = random.uniform(0.7, 0.99)

        return {"price": price, "confidence": confidence}


def generate_random_features() -> Dict[str, float]:
    """
    Generate random housing features.

    Returns:
        Dictionary of random features.
    """
    return {
        "bedrooms": random.randint(1, 5),
        "bathrooms": random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4]),
        "sqft": random.randint(800, 3000),
        "age": random.randint(0, 50),
    }


def create_reference_data(
    model: DummyModel, num_samples: int = 100
) -> Dict[str, List[float]]:
    """
    Create reference data for drift detection.

    Args:
        model: Model to use for predictions.
        num_samples: Number of samples to generate.

    Returns:
        Dictionary mapping feature names to lists of values.
    """
    reference_data: Dict[str, List[float]] = {"price": [], "confidence": []}

    for _ in range(num_samples):
        features = generate_random_features()
        prediction = model.predict(features)

        reference_data["price"].append(prediction["price"])
        reference_data["confidence"].append(prediction["confidence"])

    return reference_data


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Edge MLOps Monitor Demo")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument(
        "--predictions", type=int, default=1000, help="Number of predictions to make"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.1,
        help="Interval between predictions in seconds",
    )
    parser.add_argument(
        "--drift-after",
        type=int,
        default=500,
        help="Introduce drift after this many predictions",
    )
    parser.add_argument(
        "--drift-magnitude",
        type=float,
        default=0.2,
        help="Magnitude of drift to introduce",
    )
    parser.add_argument(
        "--reference-data", type=str, help="Path to save reference data"
    )
    args = parser.parse_args()

    # Initialize the model
    model = DummyModel(
        drift_after=args.drift_after, drift_magnitude=args.drift_magnitude
    )

    # Create reference data
    reference_data = create_reference_data(model)

    # Save reference data if path provided
    if args.reference_data:
        os.makedirs(
            os.path.dirname(os.path.abspath(args.reference_data)), exist_ok=True
        )
        with open(args.reference_data, "w") as f:
            json.dump(reference_data, f)
        logger.info(f"Saved reference data to {args.reference_data}")

    # Initialize the monitor
    monitor = EdgeMonitor(config_path=args.config)

    # Set reference data for drift detection
    for feature_name, values in reference_data.items():
        monitor.set_reference_data(feature_name, values)

    # Start monitoring
    monitor.start()

    try:
        # Make predictions
        for i in range(args.predictions):
            # Generate random features
            features = generate_random_features()

            # Log the input
            input_id = monitor.log_model_input(features)

            # Make prediction
            prediction = model.predict(features)

            # Log the output
            monitor.log_model_output(input_id, prediction)

            # Create telemetry batch every 100 predictions
            if i > 0 and i % 100 == 0:
                monitor.create_telemetry_batch()
                logger.info(f"Completed {i} predictions")

            # Sleep for the specified interval
            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")

    finally:
        # Stop monitoring
        monitor.stop()
        logger.info("Monitoring stopped")

        # Print final status
        status = monitor.get_status()
        logger.info(f"Final status: {status}")


if __name__ == "__main__":
    main()
