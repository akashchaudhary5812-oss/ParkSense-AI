"""
Enforcement Priority Score (EPS) Engine
Real-time ranking of violation zones by enforcement urgency.

EPS Formula:
  EPS(zone, t) = VF×0.35 + CIS×0.30 + RR×0.20 + RD×0.15

  VF  = Violation Frequency (last 7 days, normalized)
  CIS = Avg Congestion Impact Score for zone
  RR  = Repeat Rate (fraction of repeat offenders)
  RD  = Response Delay penalty (0–1, higher = overdue patrol)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Optional


class EPSEngine:

    WEIGHTS = {"vf": 0.35, "cis": 0.30, "rr": 0.20, "rd": 0.15}

    def __init__(self, lookback_days: int = 7, patrol_overdue_hours: int = 24):
        self.lookback_days = lookback_days
        self.patrol_overdue_hours = patrol_overdue_hours

    def compute(
        self,
        df_violations: pd.DataFrame,
        last_patrol_times: Optional[dict] = None,  # {zone_id: datetime}
    ) -> pd.DataFrame:
        """
        Compute EPS for all active zones.
        df_violations: recent violations with h3_index, cis_score, vehicle_number columns.
        Returns DataFrame sorted by EPS descending.
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=self.lookback_days)
        df = df_violations[pd.to_datetime(df_violations["created_at"], utc=True) >= cutoff].copy()

        if df.empty:
            return pd.DataFrame()

        # ── Violation Frequency (VF) ───────────────────────────────────────────
        zone_counts = df.groupby("h3_index")["id"].count().rename("raw_count")
        vf = (zone_counts / zone_counts.max()).rename("vf")

        # ── Average CIS ────────────────────────────────────────────────────────
        avg_cis = df.groupby("h3_index")["cis_score"].mean().rename("avg_cis")
        cis_norm = (avg_cis / 10.0).rename("cis_norm")   # already 0–10 scale → /10

        # ── Repeat Rate (RR) ──────────────────────────────────────────────────
        df["is_repeat"] = (
            df.groupby("vehicle_number")["id"].transform("count") >= 2
        ).astype(int)
        rr = df.groupby("h3_index")["is_repeat"].mean().rename("rr")

        # ── Response Delay (RD) ───────────────────────────────────────────────
        if last_patrol_times:
            overdue_hours = {
                zone: (now - ts).total_seconds() / 3600
                for zone, ts in last_patrol_times.items()
            }
            rd_series = pd.Series(
                {
                    zone: min(h / self.patrol_overdue_hours, 1.0)
                    for zone, h in overdue_hours.items()
                }
            ).rename("rd")
        else:
            rd_series = pd.Series({idx: 0.5 for idx in zone_counts.index}, name="rd")

        # ── Assemble ──────────────────────────────────────────────────────────
        result = pd.concat([vf, cis_norm, rr, rd_series], axis=1).fillna(0)
        result["eps"] = (
            result["vf"]       * self.WEIGHTS["vf"] +
            result["cis_norm"] * self.WEIGHTS["cis"] +
            result["rr"]       * self.WEIGHTS["rr"] +
            result["rd"]       * self.WEIGHTS["rd"]
        ) * 10  # scale to 0–10

        result = result.reset_index().rename(columns={"index": "h3_index"})
        result["category"] = result["eps"].apply(self._category)
        result["raw_violations"] = zone_counts.reindex(result["h3_index"]).values
        result = result.sort_values("eps", ascending=False).reset_index(drop=True)
        result["priority_rank"] = result.index + 1
        return result

    @staticmethod
    def _category(eps: float) -> str:
        if eps >= 8.0: return "CRITICAL"
        if eps >= 6.0: return "HIGH"
        if eps >= 4.0: return "MEDIUM"
        return "LOW"

    @staticmethod
    def action_recommendation(row: dict) -> str:
        cat = row.get("category", "LOW")
        viol = row.get("raw_violations", 0)
        actions = {
            "CRITICAL": f"🚨 Deploy 2 patrol units + tow vehicle immediately. Est. {viol} interceptions.",
            "HIGH": f"🚔 Deploy 1 patrol unit within 30 minutes. Est. {viol//2} interceptions.",
            "MEDIUM": "👁 Monitor via CCTV. Deploy on next available rotation.",
            "LOW": "📋 Log only. Review in weekly pattern analysis.",
        }
        return actions.get(cat, "📋 Log only.")
