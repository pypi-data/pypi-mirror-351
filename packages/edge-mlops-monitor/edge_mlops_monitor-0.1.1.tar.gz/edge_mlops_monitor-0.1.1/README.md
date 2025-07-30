# Lightweight Edge MLOps Monitor

A minimal Python library and agent designed specifically for monitoring machine learning models deployed on resource-constrained edge devices (e.g., IoT sensors, embedded systems running Linux).

## Overview

The Lightweight Edge MLOps Monitor provides essential monitoring capabilities for ML models running on edge devices with limited resources:

- **System Health Monitoring**: Track CPU and memory usage with minimal overhead
- **Model Input/Output Logging**: Log model inputs and outputs for analysis
- **Drift Detection**: Detect statistical drift in model outputs using the Kolmogorov-Smirnov test
- **Telemetry Upload**: Efficiently batch and upload telemetry data to cloud storage when network connectivity is available

## Key Features

- **Resource Efficient**: Optimized for devices with constrained CPU, memory, and power
- **Minimal Dependencies**: Uses only essential libraries (`psutil`, `scipy`, `boto3`, `PyYAML`)
- **Type Safe**: Fully typed with Python 3.10+ type hints and `mypy` compatibility
- **Robust Error Handling**: Graceful handling of network failures, disk full scenarios, and other edge cases
- **Configurable**: Easily adjust sampling rates, buffer sizes, and other parameters via YAML configuration

## Installation

```bash
pip install edge-mlops-monitor
```

Or install from source:

```bash
git clone https://github.com/Edmon02/edge-mlops-monitor.git
cd edge-mlops-monitor
pip install -e .
```

## Quick Start

1. Create a configuration file `config.yaml`:

```yaml
system:
  sampling_interval_seconds: 10
  max_memory_buffer_mb: 50

model_logging:
  buffer_size: 1000
  log_level: INFO

drift_detection:
  algorithm: ks_test
  threshold: 0.05
  reference_data_path: "/path/to/reference_data.json"
  check_frequency: 100  # Check after every 100 predictions

telemetry:
  upload_interval_seconds: 300
  max_batch_size: 100
  retry_base_delay_seconds: 1
  retry_max_delay_seconds: 60
  retry_max_attempts: 5

storage:
  type: "s3"
  bucket: "your-telemetry-bucket"
  prefix: "edge-device-1/"
  sqlite_path: "/path/to/local/buffer.db"
  max_sqlite_size_mb: 100
```

2. Use the monitor in your ML application:

```python
from edge_mlops_monitor import EdgeMonitor

# Initialize the monitor
monitor = EdgeMonitor(config_path="config.yaml")

# Start system monitoring in the background
monitor.start_system_monitoring()

# In your ML inference loop
def predict(input_data):
    # Log the input
    input_id = monitor.log_model_input(input_data)
    
    # Make prediction with your model
    prediction = my_model.predict(input_data)
    
    # Log the output
    monitor.log_model_output(input_id, prediction)
    
    return prediction

# When shutting down
monitor.stop()
```

## Documentation

For detailed documentation, please see:

- [Installation Guide](https://github.com/Edmon02/edge-mlops-monitor/blob/main/docs/installation.md)
- [Configuration Options](https://github.com/Edmon02/edge-mlops-monitor/blob/main/docs/configuration.md)
- [API Reference](https://github.com/Edmon02/edge-mlops-monitor/blob/main/docs/api.md)
- [Troubleshooting](https://github.com/Edmon02/edge-mlops-monitor/blob/main/docs/troubleshooting.md)
- [Publishing Guide](https://github.com/Edmon02/edge-mlops-monitor/blob/main/docs/publishing.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
