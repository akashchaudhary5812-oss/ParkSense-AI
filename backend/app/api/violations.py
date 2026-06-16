from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.core.database import get_db
from app.models.models import Violation
from app.schemas.schemas import ViolationResponse, CISRequest, CISResponse
from app.services.cis_service import compute_cis
from typing import Optional

router = APIRouter()

@router.get("/", response_model=list[ViolationResponse])
async def list_violations(
    station: Optional[str] = None,
    hour: Optional[int] = None,
    vehicle_type: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    q = select(Violation)
    if station:
        q = q.where(Violation.police_station == station)
    if hour is not None:
        q = q.where(Violation.hour == hour)
    if vehicle_type:
        q = q.where(Violation.vehicle_type == vehicle_type)
    q = q.limit(limit).offset(offset).order_by(Violation.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()

@router.get("/stats/hourly")
async def hourly_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Violation.hour, func.count(Violation.id).label("count"))
        .group_by(Violation.hour)
        .order_by(Violation.hour)
    )
    return [{"hour": r.hour, "count": r.count} for r in result.all()]

@router.get("/stats/by-station")
async def station_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            Violation.police_station,
            func.count(Violation.id).label("total"),
            func.count(func.distinct(Violation.vehicle_number)).label("unique_vehicles"),
            func.avg(Violation.cis_score).label("avg_cis"),
        )
        .group_by(Violation.police_station)
        .order_by(func.count(Violation.id).desc())
        .limit(20)
    )
    return [
        {"station": r.police_station, "total": r.total,
         "unique_vehicles": r.unique_vehicles, "avg_cis": round(r.avg_cis or 0, 2)}
        for r in result.all()
    ]

@router.get("/stats/repeat-offenders")
async def repeat_offenders(threshold: int = 2, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Violation.vehicle_number, func.count(Violation.id).label("violations"))
        .group_by(Violation.vehicle_number)
        .having(func.count(Violation.id) >= threshold)
        .order_by(func.count(Violation.id).desc())
        .limit(50)
    )
    return [{"vehicle": r.vehicle_number, "violations": r.violations} for r in result.all()]

@router.post("/{violation_id}/cis", response_model=CISResponse)
async def get_cis_score(violation_id: str, db: AsyncSession = Depends(get_db)):
    v = await db.get(Violation, violation_id)
    if not v:
        raise HTTPException(status_code=404, detail="Violation not found")
    score, shap_vals = compute_cis(v)
    return {"violation_id": violation_id, "cis_score": score, "category": _cis_category(score), "shap_values": shap_vals}

def _cis_category(score: float) -> str:
    if score >= 8.0: return "CRITICAL"
    if score >= 6.0: return "HIGH"
    if score >= 4.0: return "MEDIUM"
    if score >= 2.0: return "LOW"
    return "NEGLIGIBLE"
