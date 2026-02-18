from typing import Dict, List
from enum import Enum

from backend.logic.data_quality import data_quality
from backend.logic.decision_trace import build_decision_trace

# =================================================
# Decision Enum
# =================================================
class Decision(str, Enum):
    AUTO_APPROVE = "Auto-Approve"
    HUMAN_REVIEW = "Human Review"
    REJECT_LOW_TRUST = "Reject – Low Data Trust"
    REJECT = "Reject"

# =================================================
# Missing Ratio
# =================================================
def calculate_missing_ratio(payload: Dict[str, object]) -> float:
    missing_count = sum(
        1 for value in payload.values() if value in (None, "", 0)
    )
    total_fields = max(len(payload), 1)
    return round(missing_count / total_fields, 2)

# =================================================
# Risk Penalties (NEW – SAFE)
# =================================================
def risk_penalties(payload: Dict[str, object], affordability_ratio: float) -> float:
    penalty = 0.0

    income = payload.get("income", 0)
    credit_score = payload.get("credit_score", 0)
    property_age = payload.get("property_age", 0)

    # Credit risk
    if credit_score < 500:
        penalty += 0.25
    elif credit_score < 600:
        penalty += 0.15

    # Affordability stress
    if affordability_ratio > 12:
        penalty += 0.40
    elif affordability_ratio > 6:
        penalty += 0.20

    # Zero income (high uncertainty)
    if income == 0:
        penalty += 0.30

    # Very old property
    if property_age > 40:
        penalty += 0.10

    return min(penalty, 0.6)

# =================================================
# Confidence Aggregation (Improved)
# =================================================
def aggregate_confidence(
    model_confidence: float,
    data_quality_score: float,
    penalty: float,
    weights: Dict[str, float] | None = None
) -> float:
    if weights is None:
        weights = {"model": 0.7, "quality": 0.3}

    base_confidence = (
        weights["model"] * model_confidence +
        weights["quality"] * data_quality_score
    )

    adjusted_confidence = base_confidence - penalty
    return round(min(max(adjusted_confidence, 0.0), 1.0), 2)

# =================================================
# Decision Gate (CRITICAL FIX)
# =================================================
def decision_gate(
    confidence: float,
    missing_ratio: float,
    quality_score: float,
    affordability_ratio: float,
    payload: Dict[str, object]
) -> Decision:

    credit_score = payload.get("credit_score", 0)
    income = payload.get("income", 0)

    # 🚨 HARD STOPS (Non-negotiable)
    if quality_score < 0.5:
        return Decision.REJECT_LOW_TRUST

    if credit_score < 400:
        return Decision.REJECT

    if affordability_ratio > 12:
        return Decision.REJECT

    if income == 0:
        return Decision.HUMAN_REVIEW

    if affordability_ratio > 6:
        return Decision.HUMAN_REVIEW

    # 🔁 Soft decisions
    if confidence >= 0.80 and missing_ratio == 0:
        return Decision.AUTO_APPROVE

    if confidence >= 0.60:
        return Decision.HUMAN_REVIEW

    return Decision.REJECT

# =================================================
# Explanation Engine
# =================================================
def generate_explanation(
    confidence: float,
    missing_fields: List[str],
    quality_issues: List[str],
    payload: Dict[str, object] = None,
    affordability_ratio: float = 0
) -> Dict[str, List[str] | str]:

    signals: List[str] = []

    if confidence < 0.6:
        signals.append("Overall confidence below safe approval threshold")

    if missing_fields:
        signals.append(f"Missing or zero fields: {', '.join(missing_fields)}")

    if quality_issues:
        signals.extend(quality_issues)

    # Add specific risk factors if payload is provided
    if payload:
        credit_score = payload.get("credit_score", 0)
        income = payload.get("income", 0)
        property_age = payload.get("property_age", 0)
        
        if credit_score < 500:
            signals.append(f"Credit score ({credit_score}) is below 500 - indicates higher credit risk")
        elif credit_score < 600:
            signals.append(f"Credit score ({credit_score}) is fair - moderate credit risk present")
        
        if affordability_ratio > 12:
            signals.append(f"Affordability ratio ({affordability_ratio:.2f}) exceeds 12 - property is financially unaffordable")
        elif affordability_ratio > 6:
            signals.append(f"Affordability ratio ({affordability_ratio:.2f}) is high - significant financial stress detected")
        
        if income == 0:
            signals.append("Zero income - unable to assess financial capability")
        
        if property_age > 40:
            signals.append(f"Property age ({property_age} years) is very old - higher maintenance and depreciation risk")

    return {
        "summary": " | ".join(signals) if signals else "All risk, trust, and confidence checks passed",
        "signals": signals
    }

# =================================================
# Orchestrator (MAIN ENTRY)
# =================================================
def evaluate_decision(payload: Dict[str, object], model_confidence: float) -> Dict[str, object]:
    # 1️⃣ Data quality
    quality_score, quality_issues = data_quality(payload)

    # 2️⃣ Missing ratio
    missing_ratio = calculate_missing_ratio(payload)

    # 3️⃣ Affordability (passed from main.py)
    affordability_ratio = payload.get("affordability_ratio", 0)

    # 4️⃣ Risk penalties
    penalty = risk_penalties(payload, affordability_ratio)

    # 5️⃣ Aggregate confidence
    final_confidence = aggregate_confidence(
        model_confidence=model_confidence,
        data_quality_score=quality_score,
        penalty=penalty
    )

    # 6️⃣ Decision gate
    decision = decision_gate(
        confidence=final_confidence,
        missing_ratio=missing_ratio,
        quality_score=quality_score,
        affordability_ratio=affordability_ratio,
        payload=payload
    )

    # 7️⃣ Missing fields
    missing_fields = [k for k, v in payload.items() if v in (None, "", 0)]

    # 8️⃣ Explanation
    explanation = generate_explanation(
        confidence=final_confidence,
        missing_fields=missing_fields,
        quality_issues=quality_issues,
        payload=payload,
        affordability_ratio=affordability_ratio
    )

    # 9️⃣ Decision trace (audit-safe)
    decision_trace = build_decision_trace(
        payload=payload,
        model_confidence=model_confidence,
        final_confidence=final_confidence,
        data_quality_score=quality_score,
        missing_ratio=missing_ratio,
        decision=decision.value,
        reasons=explanation["signals"]
    )

    # 🔟 Final response (frontend-safe)
    return {
        "decision": decision.value,
        "confidence": final_confidence,
        "data_quality_score": quality_score,
        "missing_ratio": missing_ratio,
        "explanation": explanation,
        "trace": decision_trace
    }
