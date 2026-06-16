from fastapi import APIRouter, Query
from app.models.models import ForecastResult
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from datetime import datetime, timezone, timedelta

router = APIRouter()

@router.get("/zone/{h3_index}")
async def zone_forecast(
    h3_index: str,
    hours: int = Query(72, le=72, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """Return 72-hour violation forecast for a specific H3 cell."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(ForecastResult)
        .where(ForecastResult.h3_index == h3_index)
        .where(ForecastResult.forecast_hour >= now)
        .where(ForecastResult.forecast_hour <= now + timedelta(hours=hours))
        .order_by(ForecastResult.forecast_hour)
    )
    rows = result.scalars().all()
    return [
        {
            "hour": r.forecast_hour.isoformat(),
            "p10": r.p10,
            "p50": r.p50,
            "p90": r.p90,
        }
        for r in rows
    ]

@router.get("/top-risk-zones")
async def top_risk_zones(
    lookahead_hours: int = 24,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Top H3 cells predicted to have highest violations in the next N hours."""
    from sqlalchemy import func
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(
            ForecastResult.h3_index,
            func.sum(ForecastResult.p50).label("total_predicted"),
            func.max(ForecastResult.p90).label("peak_p90"),
        )
        .where(ForecastResult.forecast_hour >= now)
        .where(ForecastResult.forecast_hour <= now + timedelta(hours=lookahead_hours))
        .group_by(ForecastResult.h3_index)
        .order_by(func.sum(ForecastResult.p50).desc())
        .limit(limit)
    )
    return [
        {"h3_index": r.h3_index, "predicted_total": round(r.total_predicted, 1),
         "peak_p90": round(r.peak_p90, 1)}
        for r in result.all()
    ]
