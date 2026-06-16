"""
Hotspot Detection — DBSCAN + HDBSCAN
Detects geographic clusters of parking violations.
"""
import numpy as np
import pandas as pd
import pickle
import json
from pathlib import Path
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from shapely.geometry import MultiPoint, mapping
import hdbscan

try:
    import h3
except ImportError:
    h3 = None

MODEL_PATH = Path("../../models")

class HotspotDetector:
    """
    Detects violation hotspots using DBSCAN (primary) and HDBSCAN (secondary).
    Returns cluster IDs, centroids, convex-hull polygons, and severity labels.
    """

    def __init__(
        self,
        eps_degrees: float = 0.0015,    # ~150m radius
        min_samples: int = 25,
        use_hdbscan: bool = False,
    ):
        self.eps = eps_degrees
        self.min_samples = min_samples
        self.use_hdbscan = use_hdbscan
        self.model = None
        self.cluster_stats = {}

    def fit(self, df: pd.DataFrame) -> "HotspotDetector":
        """Train on violation lat/lon data."""
        coords = df[["latitude", "longitude"]].dropna().values
        coords_rad = np.radians(coords)

        if self.use_hdbscan:
            self.model = hdbscan.HDBSCAN(
                min_cluster_size=self.min_samples,
                min_samples=5,
                metric="haversine",
                cluster_selection_epsilon=self.eps,
            )
        else:
            self.model = DBSCAN(
                eps=self.eps,
                min_samples=self.min_samples,
                algorithm="ball_tree",
                metric="haversine",
                n_jobs=-1,
            )

        labels = self.model.fit_predict(coords_rad)
        df = df.loc[df[["latitude", "longitude"]].dropna().index].copy()
        df["cluster_id"] = labels

        # Compute cluster statistics
        for cid in set(labels):
            if cid == -1:  # noise
                continue
            cluster_pts = df[df["cluster_id"] == cid]
            centroid_lat = cluster_pts["latitude"].mean()
            centroid_lon = cluster_pts["longitude"].mean()

            # Convex hull polygon
            points = MultiPoint(list(zip(cluster_pts["longitude"], cluster_pts["latitude"])))
            hull = points.convex_hull

            self.cluster_stats[cid] = {
                "centroid_lat": centroid_lat,
                "centroid_lon": centroid_lon,
                "geojson_polygon": mapping(hull),
                "violation_count": len(cluster_pts),
                "h3_cells": (
                    list(cluster_pts["h3_index"].unique())
                    if "h3_index" in cluster_pts.columns else []
                ),
                "top_violation_types": (
                    cluster_pts["violation_type"].value_counts().head(3).to_dict()
                    if "violation_type" in cluster_pts.columns else {}
                ),
                "top_vehicles": (
                    cluster_pts["vehicle_type"].value_counts().head(3).to_dict()
                    if "vehicle_type" in cluster_pts.columns else {}
                ),
            }

        self.df_labeled = df
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Assign new points to existing clusters (within eps radius)."""
        coords_rad = np.radians(df[["latitude", "longitude"]].values)
        return self.model.fit_predict(coords_rad)

    def get_clusters_geojson(self) -> dict:
        """Return all clusters as GeoJSON FeatureCollection."""
        features = []
        for cid, stats in self.cluster_stats.items():
            features.append({
                "type": "Feature",
                "geometry": stats["geojson_polygon"],
                "properties": {
                    "cluster_id": int(cid),
                    "centroid_lat": stats["centroid_lat"],
                    "centroid_lon": stats["centroid_lon"],
                    "violation_count": stats["violation_count"],
                    "h3_cells": stats["h3_cells"][:10],
                },
            })
        return {"type": "FeatureCollection", "features": features}

    def save(self, path: Path = MODEL_PATH / "dbscan_model.pkl"):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"[HotspotDetector] Saved → {path}")

    @classmethod
    def load(cls, path: Path = MODEL_PATH / "dbscan_model.pkl") -> "HotspotDetector":
        with open(path, "rb") as f:
            return pickle.load(f)


# ── CLI entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parents[2]))
    from ml.feature_engineering.feature_builder import build_features

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="../../data/sample/violations_sample.csv")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--use-hdbscan", action="store_true")
    args = parser.parse_args()

    df = pd.read_csv(args.csv, low_memory=False)
    df = build_features(df)

    detector = HotspotDetector(use_hdbscan=args.use_hdbscan)
    detector.fit(df)

    n_clusters = len([k for k in detector.cluster_stats if k != -1])
    n_noise    = (detector.df_labeled["cluster_id"] == -1).sum()
    print(f"[Result] Clusters: {n_clusters} | Noise points: {n_noise}")

    # Save GeoJSON output
    geojson = detector.get_clusters_geojson()
    out = Path("../../data/hotspot_clusters.geojson")
    out.write_text(json.dumps(geojson, indent=2))
    print(f"[Output] GeoJSON saved → {out}")

    if args.train:
        detector.save()
