from fastapi import FastAPI
from pydantic import BaseModel, Field
import pandas as pd
import joblib
import os

from backend.logic.risk_engine import evaluate_decision
from backend.database.db import init_db

# =================================================
# App Initialization
# =================================================
app = FastAPI(
    title="Risk-Aware Property Decision API",
    description="AI-powered property decision intelligence",
    version="1.1.0"
)

# =================================================
# Startup
# =================================================
@app.on_event("startup")
def on_startup():
    init_db()

# =================================================
# Input Schema
# =================================================
class PropertyData(BaseModel):
    income: float = Field(..., example=600000)
    age: int = Field(..., example=30)
    credit_score: int = Field(..., example=720)
    property_value: float = Field(..., example=7500000)
    property_age: int = Field(..., example=10)

# =================================================
# Load ML Model
# =================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "data", "price_model.pkl")

model_bundle = joblib.load(MODEL_PATH)
price_model = model_bundle["model"]
feature_cols = model_bundle.get("features")

# =================================================
# Risk Label (Based on Affordability)
# =================================================
def get_risk_label(affordability_ratio: float) -> str:
    if affordability_ratio > 10:
        return "High"
    if affordability_ratio > 5:
        return "Medium"
    return "Low"

# =================================================
# API Endpoint
# =================================================
@app.post("/evaluate")
def evaluate_property(data: PropertyData):
    payload = data.dict()

    # -----------------
    # ML Input Frame
    # -----------------
    df = pd.DataFrame([payload])
    if feature_cols:
        df = df[feature_cols]

    df = df.fillna(df.median(numeric_only=True))

    # -----------------
    # ML Adjustment Factor
    # -----------------
    raw_pred = float(price_model.predict(df)[0])

    # Normalize output safely
    adjustment_factor = max(min(raw_pred, 1.05), 0.6)

    # -----------------
    # Final Predicted Price (CORRECTED)
    # -----------------
    base_price = payload["property_value"]
    predicted_price = round(base_price * adjustment_factor, 2)

    # -----------------
    # Affordability
    # -----------------
    affordability_ratio = predicted_price / max(payload["income"], 1)

    # -----------------
    # Risk Label
    # -----------------
    risk_label = get_risk_label(affordability_ratio)

    # -----------------
    # Model confidence (updated formula)
    # -----------------
    # Normalize affordability (lower is better)
    affordability_penalty = min(0.4, affordability_ratio / 5)

    # Credit impact
    credit_factor = (payload["credit_score"] - 300) / 600  # 0 → 1

    model_confidence = round(
        0.6 * credit_factor + 0.4 * (1 - affordability_penalty),
        2
    )

    # -----------------
    # Decision Engine
    # -----------------
    decision_payload = payload | {
        "affordability_ratio": affordability_ratio
    }

    decision_output = evaluate_decision(
        decision_payload,
        model_confidence
    )

    # -----------------
    # Final Response
    # -----------------
    return {
        "prediction": {
            "predicted_price": predicted_price,
            "risk_level": risk_label,
            "affordability_ratio": round(affordability_ratio, 2),
        },
        "decision": decision_output
    }
