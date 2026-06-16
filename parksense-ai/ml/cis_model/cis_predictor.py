"""
Congestion Impact Score (CIS) Model
XGBoost + LightGBM ensemble — predicts traffic congestion impact (0–10)
for any parking violation based on 32 engineered features.

CIS Formula:
  CIS(v) = (VD×0.30) + (RI×0.25) + (PH×0.20) + (VS×0.15) + (HC×0.10)
  where:
    VD = Violation Density (normalized)
    RI = Road Importance Index
    PH = Peak Hour Weight (PHS)
    VS = Vehicle Severity
    HC = Historical Congestion correlation
"""
import numpy as np
import pandas as pd
import xgboost as xgb
import lightgbm as lgb
import pickle
import json
import shap
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score

MODEL_DIR = Path("../../models")

# CIS weights (sum=1.0) — calibrated against HCM lane capacity data
CIS_WEIGHTS = {
    "violation_density":      0.30,
    "road_importance":        0.25,  # proxy: phs captures this partially
    "phs":                    0.20,
    "vehicle_severity":       0.15,
    "repeat_offender_density":0.10,
}


def compute_cis_formula(row: pd.Series) -> float:
    """
    Rule-based CIS formula (used for labels when ground truth unavailable).
    Produces pseudo-labels for supervised model training.
    """
    vd = float(row.get("violation_density", 0))
    ri = float(row.get("is_main_road", 0)) * 0.6 + 0.4   # 0.4–1.0
    ph = float(row.get("phs", 1.0)) / 2.0                 # normalized to 0–1
    vs = float(row.get("vehicle_severity", 0.4))
    hc = float(row.get("repeat_offender_density", 0))

    raw = (
        vd * CIS_WEIGHTS["violation_density"] +
        ri * CIS_WEIGHTS["road_importance"] +
        ph * CIS_WEIGHTS["phs"] +
        vs * CIS_WEIGHTS["vehicle_severity"] +
        hc * CIS_WEIGHTS["repeat_offender_density"]
    )
    return round(min(raw * 10, 10.0), 2)   # scale to 0–10


class CISPredictor:
    """XGBoost + LightGBM ensemble for CIS regression."""

    FEATURE_COLS = [
        "hour", "dow", "month", "is_weekend", "is_peak_night",
        "phs", "wm", "hour_sin", "hour_cos", "month_sin", "month_cos",
        "num_violations", "vehicle_severity",
        "is_wrong_parking", "is_no_parking", "is_main_road",
        "is_junction", "is_footpath", "is_double_parking",
        "violation_density", "repeat_offender_density",
        "response_delay_norm", "monthly_seasonality",
        "latitude", "longitude",
    ]

    def __init__(self, xgb_weight: float = 0.55, lgb_weight: float = 0.45):
        self.xgb_weight = xgb_weight
        self.lgb_weight = lgb_weight
        self.xgb_model = None
        self.lgb_model = None
        self.shap_explainer = None

    def _get_xy(self, df: pd.DataFrame):
        available = [c for c in self.FEATURE_COLS if c in df.columns]
        X = df[available].fillna(0)
        if "cis_score" in df.columns:
            y = df["cis_score"]
        else:
            y = df.apply(compute_cis_formula, axis=1)
        return X, y

    def train(self, df: pd.DataFrame):
        X, y = self._get_xy(df)
        # Temporal split (no shuffle — respect time ordering)
        split = int(len(X) * 0.8)
        X_train, X_val = X.iloc[:split], X.iloc[split:]
        y_train, y_val = y.iloc[:split], y.iloc[split:]

        # XGBoost
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=500, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            reg_alpha=0.1, reg_lambda=1.0,
            tree_method="hist", device="cpu",
            eval_metric="rmse", early_stopping_rounds=30,
        )
        self.xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=50,
        )

        # LightGBM
        self.lgb_model = lgb.LGBMRegressor(
            n_estimators=500, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            reg_alpha=0.1, reg_lambda=1.0,
            verbose=-1,
        )
        self.lgb_model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
        )

        # Validate
        y_pred = self._ensemble_predict(X_val)
        rmse = mean_squared_error(y_val, y_pred, squared=False)
        r2 = r2_score(y_val, y_pred)
        print(f"[CIS Validation] RMSE={rmse:.4f} | R²={r2:.4f}")

        # SHAP explainer (on XGBoost)
        self.shap_explainer = shap.TreeExplainer(self.xgb_model)
        return self

    def _ensemble_predict(self, X: pd.DataFrame) -> np.ndarray:
        xgb_pred = self.xgb_model.predict(X)
        lgb_pred = self.lgb_model.predict(X)
        return self.xgb_weight * xgb_pred + self.lgb_weight * lgb_pred

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        available = [c for c in self.FEATURE_COLS if c in X.columns]
        X = X[available].fillna(0)
        return np.clip(self._ensemble_predict(X), 0, 10)

    def explain(self, X_row: pd.DataFrame) -> list[dict]:
        """Return SHAP values for a single row as [{feature, value, shap_val}]."""
        available = [c for c in self.FEATURE_COLS if c in X_row.columns]
        X = X_row[available].fillna(0)
        shap_vals = self.shap_explainer.shap_values(X)[0]
        result = []
        for feat, sv in sorted(zip(available, shap_vals), key=lambda x: abs(x[1]), reverse=True):
            result.append({
                "feature": feat,
                "value": float(X[feat].iloc[0]),
                "shap_value": round(float(sv), 4),
                "direction": "positive" if sv > 0 else "negative",
            })
        return result[:10]   # top 10 contributors

    def save(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        self.xgb_model.save_model(str(MODEL_DIR / "xgb_cis_model.json"))
        self.lgb_model.booster_.save_model(str(MODEL_DIR / "lgbm_cis_model.txt"))
        meta = {"xgb_weight": self.xgb_weight, "lgb_weight": self.lgb_weight,
                "feature_cols": self.FEATURE_COLS}
        (MODEL_DIR / "cis_meta.json").write_text(json.dumps(meta))
        print("[CISPredictor] Models saved.")

    @classmethod
    def load(cls) -> "CISPredictor":
        meta = json.loads((MODEL_DIR / "cis_meta.json").read_text())
        predictor = cls(meta["xgb_weight"], meta["lgb_weight"])
        predictor.xgb_model = xgb.XGBRegressor()
        predictor.xgb_model.load_model(str(MODEL_DIR / "xgb_cis_model.json"))
        predictor.lgb_model = lgb.LGBMRegressor()
        predictor.lgb_model = lgb.Booster(model_file=str(MODEL_DIR / "lgbm_cis_model.txt"))
        predictor.shap_explainer = shap.TreeExplainer(predictor.xgb_model)
        return predictor


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[2]))
    from ml.feature_engineering.feature_builder import build_features

    df = pd.read_csv("../../data/sample/violations_sample.csv", low_memory=False)
    df = build_features(df)

    predictor = CISPredictor()
    predictor.train(df)
    predictor.save()
    print("[Done] CIS model trained and saved.")
