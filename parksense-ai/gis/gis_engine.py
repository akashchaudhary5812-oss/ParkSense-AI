"""
GIS Intelligence Layer
- H3 hexagonal indexing
- Violation heatmap generation
- Hotspot polygon builder
- Patrol route mapper
"""
import geopandas as gpd
import pandas as pd
import numpy as np
import h3
from shapely.geometry import Point, Polygon, LineString, mapping
from shapely.ops import unary_union
import json
from pathlib import Path
from typing import Optional


# ── H3 Indexing ───────────────────────────────────────────────────────────────
def add_h3_index(df: pd.DataFrame, resolution: int = 7) -> pd.DataFrame:
    """Add H3 cell index to violation DataFrame."""
    df = df.copy()
    df["h3_index"] = df.apply(
        lambda r: h3.latlng_to_cell(r["latitude"], r["longitude"], resolution)
        if pd.notna(r["latitude"]) and pd.notna(r["longitude"]) else None,
        axis=1,
    )
    return df


def h3_to_geojson_polygon(h3_index: str) -> dict:
    """Convert H3 cell to GeoJSON polygon."""
    boundary = h3.cell_to_boundary(h3_index)
    coords = [[lon, lat] for lat, lon in boundary]
    coords.append(coords[0])  # close ring
    return {"type": "Polygon", "coordinates": [coords]}


# ── Heatmap Aggregation ───────────────────────────────────────────────────────
def build_h3_heatmap(df: pd.DataFrame, resolution: int = 7,
                     value_col: str = "count") -> dict:
    """
    Aggregate violations into H3 hexagonal grid.
    Returns GeoJSON FeatureCollection suitable for Kepler.gl / Mapbox.
    """
    if "h3_index" not in df.columns:
        df = add_h3_index(df, resolution)

    agg = df.groupby("h3_index").agg(
        count=("id", "count"),
        avg_cis=("cis_score", "mean"),
        avg_severity=("vehicle_severity", "mean"),
    ).reset_index()

    max_count = agg["count"].max()
    agg["density_norm"] = agg["count"] / max_count

    features = []
    for _, row in agg.iterrows():
        if row["h3_index"] is None:
            continue
        geom = h3_to_geojson_polygon(row["h3_index"])
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "h3_index": row["h3_index"],
                "count": int(row["count"]),
                "density_norm": round(row["density_norm"], 4),
                "avg_cis": round(row.get("avg_cis") or 0, 2),
            },
        })
    return {"type": "FeatureCollection", "features": features}


# ── Hotspot Polygon Builder ───────────────────────────────────────────────────
def build_cluster_polygons(df: pd.DataFrame, cluster_col: str = "cluster_id") -> dict:
    """
    Build convex hull polygons for DBSCAN clusters.
    Returns GeoJSON FeatureCollection.
    """
    features = []
    for cid in df[cluster_col].unique():
        if cid == -1:
            continue
        cluster = df[df[cluster_col] == cid]
        points = [Point(lon, lat) for lat, lon in
                  zip(cluster["latitude"], cluster["longitude"])]
        if len(points) < 3:
            continue
        hull = unary_union(points).convex_hull
        cis  = cluster["cis_score"].mean() if "cis_score" in cluster.columns else 0

        features.append({
            "type": "Feature",
            "geometry": mapping(hull),
            "properties": {
                "cluster_id": int(cid),
                "violation_count": len(cluster),
                "avg_cis": round(cis, 2),
                "category": _cis_cat(cis),
                "centroid_lat": cluster["latitude"].mean(),
                "centroid_lon": cluster["longitude"].mean(),
                "top_station": cluster["police_station"].mode()[0]
                    if "police_station" in cluster.columns else "",
            },
        })
    return {"type": "FeatureCollection", "features": features}


# ── Patrol Route GeoJSON ──────────────────────────────────────────────────────
def patrol_route_to_geojson(waypoints: list[dict]) -> dict:
    """
    Convert RL patrol optimizer waypoints to GeoJSON LineString.
    waypoints: [{lat, lon, h3_index, expected_violations, arrive_time}]
    """
    coords = [[w["lon"], w["lat"]] for w in waypoints]
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords},
                "properties": {
                    "total_waypoints": len(waypoints),
                    "expected_interceptions": sum(
                        w.get("expected_violations", 0) for w in waypoints
                    ),
                },
            },
            *[
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [w["lon"], w["lat"]]},
                    "properties": {
                        "sequence": i + 1,
                        "h3_index": w.get("h3_index"),
                        "expected_violations": w.get("expected_violations", 0),
                        "arrive_time": w.get("arrive_time", ""),
                    },
                }
                for i, w in enumerate(waypoints)
            ],
        ],
    }


def _cis_cat(score: float) -> str:
    if score >= 8.0: return "CRITICAL"
    if score >= 6.0: return "HIGH"
    if score >= 4.0: return "MEDIUM"
    return "LOW"
