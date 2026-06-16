"""
CIS Service
Bridge between the API and the ML models.
"""
import pandas as pd
from app.models.models import Violation
from ml.cis_model.cis_predictor import CISPredictor
from ml.feature_engineering.feature_builder import build_features
import numpy as np

# Singleton predictor instance
_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        try:
            _predictor = CISPredictor.load()
        except Exception:
            # Fallback to untrained instance if model files not found
            _predictor = CISPredictor()
    return _predictor

def compute_cis(violation: Violation) -> tuple[float, list[dict]]:
    """
    Compute CIS score and SHAP explanations for a violation object.
    Returns (score, shap_values).
    """
    predictor = get_predictor()
    
    # Convert ORM model to DataFrame for feature engineering
    data = {
        "id": [violation.id],
        "latitude": [violation.latitude],
        "longitude": [violation.longitude],
        "created_datetime": [violation.created_at],
        "vehicle_type": [violation.vehicle_type],
        "violation_type": [", ".join(violation.violation_types) if violation.violation_types else ""],
        "police_station": [violation.police_station],
        "junction_name": [violation.junction_name],
        "vehicle_number": [violation.vehicle_number],
    }
    df = pd.DataFrame(data)
    
    # Run feature engineering
    df_feat = build_features(df)
    
    # Predict
    try:
        score = float(predictor.predict(df_feat)[0])
        # If model is trained, get SHAP explanations
        if predictor.shap_explainer:
            shap_vals = predictor.explain(df_feat)
        else:
            shap_vals = []
    except Exception:
        # Fallback to rule-based formula if model fails
        from ml.cis_model.cis_predictor import compute_cis_formula
        score = compute_cis_formula(df_feat.iloc[0])
        shap_vals = []
        
    return round(score, 2), shap_vals
