import os
from typing import Dict, List

import pandas as pd
from scipy import interpolate  # type: ignore[import-untyped]
from scipy.interpolate import RectBivariateSpline  # type: ignore[import-untyped]

# Column name mappings for different metrics
COLUMN_MAPPINGS = {
    # Engine metrics
    "engine": {
        "rpm": "HUB_RPM",  # Used in engine_working_hours and engine_starts
        "timestamp": "time",  # Used in engine_working_hours
    },
    # Hub metrics
    "hub": {
        "voltage": "voltage",
        "current": "engine_load",
        "throttle": "spark_dwell_time",
        "rpm": "rpm",  # Different from engine RPM column
    },
    # Temperature metrics
    "temperature": {
        "cht1": "intake_manifold_temperature",
        "cht2": "exhaust_gas_temperature",
        "air": "batt_curr",  # Air temperature is stored in battery current column
    },
    # Battery metrics
    "battery": {
        "current": "fuel_consumed",  # Battery current is stored in fuel consumed column
    },
}


def throttle_function(da120_data_path: str = "DA120/") -> RectBivariateSpline:
    """
    Create an interpolated throttle function from DA120 data files.

    Args:
        da120_data_path: Path to the DA120 data folder

    Returns:
        RectBivariateSpline: Interpolated throttle function
    """
    files: List[str] = [f for f in os.listdir(da120_data_path) if f.endswith(".csv")]
    df_dict: Dict[str, pd.DataFrame] = {}
    df_list: List[pd.DataFrame] = []
    throttles: List[float] = []
    # sorting files to increasing throttle value
    files.sort()

    for file in files:
        df_throttle = pd.DataFrame()
        throttle = file.split("_")[2]
        throttles.append(float(throttle))

        df = pd.read_csv(os.path.join(da120_data_path, file))
        df["RPM"] = 7.5 / 9 * df["RPM"] + 1500
        df_dict[throttle] = df

        # Function
        f = interpolate.interp1d(
            df["RPM"],
            df["power"],
            bounds_error=False,
            fill_value=(df["power"].iloc[0], df["power"].iloc[-1]),
        )
        max_rpm = float(max(df["RPM"]))
        rpms = [rpm for rpm in range(3000, int(max_rpm) + 100, 100)]
        power = f(rpms)
        df_throttle.index = pd.Index(rpms)
        df_throttle["power"] = power
        df_list += [df_throttle]

    df = pd.concat(df_list, axis=1).fillna(0)
    df.columns = pd.Index(throttles)

    throttle_function = interpolate.RectBivariateSpline(
        df.index.to_numpy(), df.columns.to_numpy(), df.values, kx=2, ky=2
    )

    return throttle_function
