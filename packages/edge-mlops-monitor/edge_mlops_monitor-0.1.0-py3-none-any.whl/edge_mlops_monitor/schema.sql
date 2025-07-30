-- SQLite schema for the Edge MLOps Monitor

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    metric_type TEXT NOT NULL,
    value REAL NOT NULL,
    device_id TEXT NOT NULL
);

-- Create indexes for system metrics
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics (timestamp);
CREATE INDEX IF NOT EXISTS idx_system_metrics_type ON system_metrics (metric_type);
CREATE INDEX IF NOT EXISTS idx_system_metrics_device ON system_metrics (device_id);

-- Model inputs table
CREATE TABLE IF NOT EXISTS model_inputs (
    id TEXT PRIMARY KEY,
    timestamp REAL NOT NULL,
    input_data TEXT NOT NULL,
    device_id TEXT NOT NULL
);

-- Create indexes for model inputs
CREATE INDEX IF NOT EXISTS idx_inputs_timestamp ON model_inputs (timestamp);
CREATE INDEX IF NOT EXISTS idx_inputs_device ON model_inputs (device_id);

-- Model outputs table
CREATE TABLE IF NOT EXISTS model_outputs (
    id TEXT PRIMARY KEY,
    input_id TEXT NOT NULL,
    timestamp REAL NOT NULL,
    output_data TEXT NOT NULL,
    device_id TEXT NOT NULL,
    FOREIGN KEY (input_id) REFERENCES model_inputs (id)
);

-- Create indexes for model outputs
CREATE INDEX IF NOT EXISTS idx_outputs_timestamp ON model_outputs (timestamp);
CREATE INDEX IF NOT EXISTS idx_outputs_input_id ON model_outputs (input_id);
CREATE INDEX IF NOT EXISTS idx_outputs_device ON model_outputs (device_id);

-- Drift detection results table
CREATE TABLE IF NOT EXISTS drift_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    algorithm TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    statistic REAL NOT NULL,
    p_value REAL NOT NULL,
    threshold REAL NOT NULL,
    is_drift INTEGER NOT NULL,
    sample_size INTEGER NOT NULL,
    device_id TEXT NOT NULL
);

-- Create indexes for drift results
CREATE INDEX IF NOT EXISTS idx_drift_timestamp ON drift_results (timestamp);
CREATE INDEX IF NOT EXISTS idx_drift_feature ON drift_results (feature_name);
CREATE INDEX IF NOT EXISTS idx_drift_is_drift ON drift_results (is_drift);
CREATE INDEX IF NOT EXISTS idx_drift_device ON drift_results (device_id);

-- Telemetry batches table
CREATE TABLE IF NOT EXISTS telemetry_batches (
    id TEXT PRIMARY KEY,
    timestamp REAL NOT NULL,
    device_id TEXT NOT NULL,
    batch_data TEXT NOT NULL,
    uploaded INTEGER DEFAULT 0,
    upload_attempts INTEGER DEFAULT 0,
    last_attempt REAL DEFAULT 0
);

-- Create indexes for telemetry batches
CREATE INDEX IF NOT EXISTS idx_batches_uploaded ON telemetry_batches (uploaded);
CREATE INDEX IF NOT EXISTS idx_batches_timestamp ON telemetry_batches (timestamp);
CREATE INDEX IF NOT EXISTS idx_batches_device ON telemetry_batches (device_id);
