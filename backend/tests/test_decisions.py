import pytest
from backend.logic.risk_engine import evaluate_decision

# ----------------------------
# Helper payloads
# ----------------------------
def base_payload():
    return {
        "income": 1500000,
        "age": 35,
        "credit_score": 780,
        "property_value": 6000000,
        "property_age": 5
    }

def stressed_payload():
    return {
        "income": 1050000,     # -30%
        "age": 35,
        "credit_score": 680,   # -100
        "property_value": 7800000,  # +30%
        "property_age": 5
    }


# ----------------------------
# TEST CASES
# ----------------------------

def test_auto_approve_case():
    result = evaluate_decision(
        payload=base_payload(),
        model_confidence=0.87
    )
    assert result["decision"] == "Auto-Approve"
    assert result["confidence"] >= 0.85


def test_human_review_case():
    result = evaluate_decision(
        payload=stressed_payload(),
        model_confidence=0.60
    )
    assert result["decision"] in ["Human Review", "Reject"]
    assert result["confidence"] < 0.75


def test_reject_low_data_quality():
    bad_payload = base_payload()
    bad_payload["income"] = None

    result = evaluate_decision(
        payload=bad_payload,
        model_confidence=0.9
    )

    assert result["decision"] == "Reject – Low Data Trust"


def test_invalid_age_reject():
    bad_payload = base_payload()
    bad_payload["age"] = 150

    result = evaluate_decision(
        payload=bad_payload,
        model_confidence=0.9
    )

    assert result["decision"] == "Reject"
