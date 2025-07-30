"""
Lightweight Edge MLOps Monitor

A minimal Python library and agent designed specifically for monitoring machine learning models
deployed on resource-constrained edge devices.
"""

from edge_mlops_monitor.monitor import EdgeMonitor
from edge_mlops_monitor.config import load_config

__version__ = "0.1.0"
__all__ = ["EdgeMonitor", "load_config"]
