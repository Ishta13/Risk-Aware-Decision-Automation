# backend/logic/decision_trace.py
from datetime import datetime
from typing import Dict, List


def build_decision_trace(
    payload: Dict,
    model_confidence: float,
    final_confidence: float,
    data_quality_score: float,
    missing_ratio: float,
    decision: str,
    reasons: List[str]
) -> Dict:
    """
    Creates a complete, auditable decision trace
    suitable for storage, compliance, and debugging.
    """

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "engine_version": "1.0.0",
        "input_snapshot": payload,
        "signals": {
            "model_confidence": model_confidence,
            "final_confidence": final_confidence,
            "data_quality_score": data_quality_score,
            "missing_ratio": missing_ratio
        },
        "decision": decision,
        "explanation": reasons
    }
