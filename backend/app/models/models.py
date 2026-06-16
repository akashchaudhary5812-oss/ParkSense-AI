from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from geoalchemy2 import Geometry
from app.core.database import Base

class Violation(Base):
    __tablename__ = "violations"

    id              = Column(String, primary_key=True, index=True)
    latitude        = Column(Float, nullable=False)
    longitude       = Column(Float, nullable=False)
    geom            = Column(Geometry("POINT", srid=4326))   # PostGIS point
    h3_index        = Column(String, index=True)             # H3 resolution-7 cell
    location        = Column(Text)
    vehicle_number  = Column(String, index=True)
    vehicle_type    = Column(String)
    violation_types = Column(ARRAY(String))                  # Parsed JSON array
    offence_codes   = Column(ARRAY(Integer))
    created_at      = Column(DateTime(timezone=True), index=True)
    modified_at     = Column(DateTime(timezone=True))
    police_station  = Column(String, index=True)
    center_code     = Column(Integer)
    junction_name   = Column(String, index=True)
    data_sent_to_scita       = Column(Boolean, default=False)
    scita_timestamp          = Column(DateTime(timezone=True))
    validation_status        = Column(String, default="unvalidated")
    validation_timestamp     = Column(DateTime(timezone=True))
    updated_vehicle_type     = Column(String)

    # Computed fields (set during ingestion)
    num_violations  = Column(Integer, default=1)
    cis_score       = Column(Float)                          # Congestion Impact Score
    eps_score       = Column(Float)                          # Enforcement Priority Score
    hour            = Column(Integer)
    day_of_week     = Column(Integer)
    month           = Column(Integer)
    is_peak_night   = Column(Boolean, default=False)         # 10PM–6AM
    is_weekend      = Column(Boolean, default=False)

class HotspotCluster(Base):
    __tablename__ = "hotspot_clusters"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id      = Column(Integer, index=True)
    centroid_lat    = Column(Float)
    centroid_lon    = Column(Float)
    geom            = Column(Geometry("POLYGON", srid=4326)) # Convex hull
    violation_count = Column(Integer)
    cis_score       = Column(Float)
    eps_score       = Column(Float)
    h3_cells        = Column(ARRAY(String))
    police_station  = Column(String)
    label           = Column(String)
    created_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    h3_index        = Column(String, index=True)
    forecast_hour   = Column(DateTime(timezone=True), index=True)
    p10             = Column(Float)
    p50             = Column(Float)
    p90             = Column(Float)
    model_version   = Column(String)
    created_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class PatrolRoute(Base):
    __tablename__ = "patrol_routes"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    police_station  = Column(String)
    shift_start     = Column(DateTime(timezone=True))
    shift_end       = Column(DateTime(timezone=True))
    route_geojson   = Column(JSON)                           # GeoJSON LineString
    waypoints       = Column(JSON)                           # List of {lat, lon, h3, eps}
    expected_interceptions = Column(Integer)
    created_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
