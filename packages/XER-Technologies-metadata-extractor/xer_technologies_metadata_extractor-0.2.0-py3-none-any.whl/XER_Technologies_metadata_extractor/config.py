"""
Configuration module for XER Technologies Metadata Extractor.

Contains column definitions, validation rules, and other configuration constants.
"""

from typing import Dict, List

# XFD Column definitions for different versions
XFD_COLUMNS: Dict[str, List[str]] = {
    "v2.9.1": [
        "time",
        "gen_status",
        "gen_speed",
        "batt_curr",
        "load_curr",
        "power",
        "voltage",
        "rectifier_tem",
        "current_setpoint",
        "gen_temp",
        "run_time",
        "maintenance",
        "ecu_health",
        "ecu_index",
        "rpm",
        "fuel_consumed",
        "fuel_flow",
        "engine_load",
        "throttle_position",
        "spark_dwell_time",
        "barometric_pressure",
        "intake_manifold_pressure",
        "intake_manifold_temperature",
        "cylinder_head_temperature",
        "ignition_timing",
        "injection_time",
        "exhaust_gas_temperature",
        "throttle_out",
        "Pt_compensation",
    ],
    "v3.1.1": [
        "time",
        "gen_status",
        "gen_speed",
        "batt_curr",
        "load_curr",
        "power",
        "voltage",
        "rectifier_tem",
        "current_setpoint",
        "gen_temp",
        "run_time",
        "maintenance",
        "ecu_health",
        "ecu_index",
        "rpm",
        "fuel_consumed",
        "fuel_flow",
        "engine_load",
        "throttle_position",
        "spark_dwell_time",
        "barometric_pressure",
        "intake_manifold_pressure",
        "intake_manifold_temperature",
        "cylinder_head_temperature",
        "ignition_timing",
        "injection_time",
        "exhaust_gas_temperature",
        "throttle_out",
        "Pt_compensation",
    ],
}

# File validation settings
SUPPORTED_FILE_EXTENSIONS = [".csv", ".bin"]
MIN_CSV_LINES = 10
MIN_BIN_FILE_SIZE = 1024  # 1KB minimum for Mission Planner files
CSV_ENCODING = "utf-8"

# Filename patterns
XFD_FILENAME_PREFIX = "XFD_"
BIN_FILENAME_PATTERN = r"\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}\.bin$"
