"""
Data Ingestion Script
Loads the raw BTP CSV into PostgreSQL + PostGIS.
Handles cleaning, deduplication, feature building, and CIS scoring.
"""
import asyncio
import ast
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.models.models import Base, Violation
from ml.feature_engineering.feature_builder import build_features

BBOX = settings.BENGALURU_BBOX
BATCH = 5000


def parse_violations(v):
    if pd.isna(v): return []
    try:
        result = ast.literal_eval(v)
        return list(result) if isinstance(result, list) else [str(result)]
    except Exception:
        return [str(v)]

def parse_codes(v):
    if pd.isna(v): return []
    try:
        result = ast.literal_eval(v)
        return [int(x) for x in result] if isinstance(result, list) else []
    except Exception:
        return []


async def ingest(csv_path: str):
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    Session = async_sessionmaker(engine, expire_on_commit=False)
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"[Ingestion] Loaded {len(df):,} rows from {csv_path}")

    # ── Clean ─────────────────────────────────────────────────────────────────
    df = df.drop_duplicates(subset=["id"])
    df = df[
        df["latitude"].between(BBOX["lat_min"], BBOX["lat_max"]) &
        df["longitude"].between(BBOX["lon_min"], BBOX["lon_max"])
    ]
    df = df.dropna(subset=["latitude", "longitude"])
    df = df.drop_duplicates(subset=["latitude", "longitude", "vehicle_number", "created_datetime"])
    print(f"[Ingestion] After cleaning: {len(df):,} rows")

    # ── Parse arrays ──────────────────────────────────────────────────────────
    df["violation_types_list"] = df["violation_type"].apply(parse_violations)
    df["offence_codes_list"]   = df["offence_code"].apply(parse_codes)

    # ── Feature engineering ───────────────────────────────────────────────────
    df = build_features(df)

    # ── Batch insert ──────────────────────────────────────────────────────────
    total = 0
    async with Session() as session:
        for start in range(0, len(df), BATCH):
            batch = df.iloc[start: start + BATCH]
            objects = []
            for _, row in batch.iterrows():
                v = Violation(
                    id                  = str(row["id"]),
                    latitude            = float(row["latitude"]),
                    longitude           = float(row["longitude"]),
                    geom                = f"SRID=4326;POINT({row['longitude']} {row['latitude']})",
                    h3_index            = row.get("h3_index"),
                    location            = str(row.get("location", "")) or None,
                    vehicle_number      = str(row["vehicle_number"]),
                    vehicle_type        = str(row["vehicle_type"]),
                    violation_types     = row["violation_types_list"],
                    offence_codes       = row["offence_codes_list"],
                    created_at          = pd.to_datetime(row["created_datetime"], utc=True, errors="coerce"),
                    police_station      = str(row.get("police_station", "")) or None,
                    junction_name       = str(row.get("junction_name", "")) or None,
                    data_sent_to_scita  = bool(row.get("data_sent_to_scita", False)),
                    validation_status   = str(row.get("validation_status", "unvalidated") or "unvalidated"),
                    updated_vehicle_type= str(row.get("updated_vehicle_type", "")) or None,
                    num_violations      = int(row.get("num_violations", 1)),
                    hour                = int(row.get("hour", 0)),
                    day_of_week         = int(row.get("dow", 0)),
                    month               = int(row.get("month", 1)),
                    is_peak_night       = bool(row.get("is_peak_night", False)),
                    is_weekend          = bool(row.get("is_weekend", False)),
                )
                objects.append(v)
            session.add_all(objects)
            await session.commit()
            total += len(batch)
            print(f"  ✓ Inserted {total:,} / {len(df):,} records")

    print(f"[Ingestion] Complete. {total:,} records loaded.")
    await engine.dispose()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to violations CSV")
    args = parser.parse_args()
    asyncio.run(ingest(args.file))
