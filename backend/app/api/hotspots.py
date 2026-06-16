from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.models import HotspotCluster

router = APIRouter()

@router.get("/")
async def list_hotspots(
    min_cis: float = Query(0.0),
    station: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    q = select(HotspotCluster).where(HotspotCluster.cis_score >= min_cis)
    if station:
        q = q.where(HotspotCluster.police_station == station)
    q = q.order_by(HotspotCluster.cis_score.desc()).limit(limit)
    result = await db.execute(q)
    clusters = result.scalars().all()
    return [
        {
            "id": c.id,
            "cluster_id": c.cluster_id,
            "centroid_lat": c.centroid_lat,
            "centroid_lon": c.centroid_lon,
            "cis_score": c.cis_score,
            "eps_score": c.eps_score,
            "violation_count": c.violation_count,
            "police_station": c.police_station,
            "label": c.label,
            "category": _cis_category(c.cis_score),
        }
        for c in clusters
    ]

@router.get("/geojson")
async def hotspots_geojson(db: AsyncSession = Depends(get_db)):
    """Return clusters as GeoJSON FeatureCollection for map layers."""
    q = select(HotspotCluster).order_by(HotspotCluster.cis_score.desc()).limit(100)
    result = await db.execute(q)
    clusters = result.scalars().all()
    features = []
    for c in clusters:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [c.centroid_lon, c.centroid_lat],
            },
            "properties": {
                "id": c.id,
                "cis_score": c.cis_score,
                "eps_score": c.eps_score,
                "violation_count": c.violation_count,
                "label": c.label,
                "category": _cis_category(c.cis_score),
            },
        })
    return {"type": "FeatureCollection", "features": features}

@router.get("/junctions")
async def junction_risk(db: AsyncSession = Depends(get_db)):
    """Top junctions ranked by total violations (sourced from violations table)."""
    from app.models.models import Violation
    result = await db.execute(
        select(
            Violation.junction_name,
            func.count(Violation.id).label("count"),
            func.avg(Violation.cis_score).label("avg_cis"),
        )
        .where(Violation.junction_name != "No Junction")
        .where(Violation.junction_name.is_not(None))
        .group_by(Violation.junction_name)
        .order_by(func.count(Violation.id).desc())
        .limit(20)
    )
    return [
        {"junction": r.junction_name, "violations": r.count,
         "avg_cis": round(r.avg_cis or 0, 2)}
        for r in result.all()
    ]

def _cis_category(score: float) -> str:
    if score is None: return "UNKNOWN"
    if score >= 8.0: return "CRITICAL"
    if score >= 6.0: return "HIGH"
    if score >= 4.0: return "MEDIUM"
    return "LOW"
