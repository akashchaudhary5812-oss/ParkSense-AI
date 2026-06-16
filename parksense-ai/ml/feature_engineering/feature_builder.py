"""
Feature Engineering Engine
Computes all 32 features needed for ML models.
"""
import numpy as np
import pandas as pd
import h3
import ast
from datetime import datetime

# Vehicle severity weights (based on lane-blockage impact)
VEHICLE_SEVERITY = {
    "BUS (BMTC/KSRTC)": 1.0,
    "PRIVATE BUS": 0.95,
    "HGV": 0.92,
    "LORRY/GOODS VEHICLE": 0.90,
    "TEMPO": 0.88,
    "TANKER": 0.85,
    "MAXI-CAB": 0.70,
    "LGV": 0.65,
    "VAN": 0.60,
    "JEEP": 0.55,
    "CAR": 0.50,
    "PASSENGER AUTO": 0.45,
    "GOODS AUTO": 0.40,
    "MOTOR CYCLE": 0.25,
    "SCOOTER": 0.20,
    "MOPED": 0.18,
}

# Road importance index (approximated from violation junction codes)
ROAD_IMPORTANCE = {
    "primary": 1.0, "secondary": 0.7, "tertiary": 0.5,
    "residential": 0.3, "unknown": 0.4,
}

def peak_hour_score(hour: int) -> float:
    """PHS: weight violations by time-of-day risk (dataset: peak at 5AM)."""
    if hour in {4, 5, 6}:     return 2.0  # Night peak
    if hour in {3, 22, 23}:   return 1.7
    if hour in {0, 1, 2}:     return 1.5
    if hour in {7, 8, 19, 20, 21}: return 0.9
    if hour in {17, 18}:      return 0.8
    return 0.3  # 9AM–4PM low risk period

def cyclic_encode(val: float, period: float):
    """Encode cyclical features (hour, month, dow) as sin/cos pair."""
    return np.sin(2 * np.pi * val / period), np.cos(2 * np.pi * val / period)

def count_violations(vtype):
    """Count violation types per record (some have multiple)."""
    if pd.isna(vtype): return 1
    try:
        return len(ast.literal_eval(vtype))
    except Exception:
        return 1

def get_vehicle_severity(vtype: str) -> float:
    return VEHICLE_SEVERITY.get(str(vtype).upper(), 0.40)

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main feature engineering pipeline.
    Input: raw violations DataFrame
    Output: feature matrix with 32 columns
    """
    df = df.copy()

    # --- Temporal features ---
    df["created_datetime"] = pd.to_datetime(df["created_datetime"], utc=True, errors="coerce")
    df["hour"]        = df["created_datetime"].dt.hour
    df["dow"]         = df["created_datetime"].dt.dayofweek     # 0=Mon, 6=Sun
    df["month"]       = df["created_datetime"].dt.month
    df["week_of_year"]= df["created_datetime"].dt.isocalendar().week.astype(int)

    df["is_weekend"]   = df["dow"].isin([5, 6]).astype(int)
    df["is_peak_night"]= ((df["hour"] >= 22) | (df["hour"] <= 6)).astype(int)

    df["phs"]          = df["hour"].apply(peak_hour_score)           # Peak hour score
    df["wm"]           = df["is_weekend"].apply(lambda x: 1.18 if x else 1.00)  # Weekend multiplier

    # Cyclic encoding (avoids 23→0 discontinuity)
    df["hour_sin"], df["hour_cos"]   = zip(*df["hour"].apply(lambda h: cyclic_encode(h, 24)))
    df["month_sin"], df["month_cos"] = zip(*df["month"].apply(lambda m: cyclic_encode(m, 12)))
    df["dow_sin"],  df["dow_cos"]    = zip(*df["dow"].apply(lambda d: cyclic_encode(d, 7)))

    # --- Violation features ---
    df["num_violations"] = df["violation_type"].apply(count_violations)
    df["vehicle_severity"] = df["vehicle_type"].apply(get_vehicle_severity)

    # --- Derived boolean violation type flags ---
    df["is_wrong_parking"]   = df["violation_type"].str.contains("WRONG PARKING",   na=False).astype(int)
    df["is_no_parking"]      = df["violation_type"].str.contains("NO PARKING",       na=False).astype(int)
    df["is_main_road"]       = df["violation_type"].str.contains("MAIN ROAD",        na=False).astype(int)
    df["is_junction"]        = (df["junction_name"] != "No Junction").astype(int)
    df["is_footpath"]        = df["violation_type"].str.contains("FOOTPATH",         na=False).astype(int)
    df["is_double_parking"]  = df["violation_type"].str.contains("DOUBLE PARKING",   na=False).astype(int)

    # --- Spatial features ---
    df["lat_r"] = df["latitude"].round(3)
    df["lon_r"] = df["longitude"].round(3)

    # H3 cell indexing at resolution 7 (~460m)
    df["h3_index"] = df.apply(
        lambda r: h3.latlng_to_cell(r["latitude"], r["longitude"], 7)
        if pd.notna(r["latitude"]) else None,
        axis=1,
    )

    # Violation Density per H3 cell (computed over full dataset)
    h3_counts = df.groupby("h3_index")["id"].transform("count")
    df["violation_density"] = h3_counts / h3_counts.max()  # Normalized 0–1

    # Repeat offender density per H3 cell
    repeat_flags = df.groupby("vehicle_number")["id"].transform("count") >= 2
    df["is_repeat_offender"] = repeat_flags.astype(int)
    h3_repeat = df.groupby("h3_index")["is_repeat_offender"].transform("mean")
    df["repeat_offender_density"] = h3_repeat  # Ratio of repeat offenders in cell

    # SCITA response delay
    df["scita_ts"] = pd.to_datetime(df["data_sent_to_scita_timestamp"], utc=True, errors="coerce")
    df["response_delay_hours"] = (df["scita_ts"] - df["created_datetime"]).dt.total_seconds() / 3600
    df["response_delay_norm"] = (df["response_delay_hours"].clip(0, 168) / 168).fillna(0.5)

    # --- Monthly seasonality score ---
    monthly_counts = df.groupby("month")["id"].transform("count")
    df["monthly_seasonality"] = monthly_counts / monthly_counts.max()

    return df

FEATURE_COLUMNS = [
    "hour", "dow", "month", "week_of_year",
    "is_weekend", "is_peak_night",
    "phs", "wm",
    "hour_sin", "hour_cos", "month_sin", "month_cos", "dow_sin", "dow_cos",
    "num_violations", "vehicle_severity",
    "is_wrong_parking", "is_no_parking", "is_main_road",
    "is_junction", "is_footpath", "is_double_parking",
    "violation_density", "is_repeat_offender",
    "repeat_offender_density", "response_delay_norm",
    "monthly_seasonality",
    "latitude", "longitude",
]
