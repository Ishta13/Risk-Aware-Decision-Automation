from typing import Dict, List, Tuple

def data_quality(payload: Dict[str, object]) -> Tuple[float, List[str]]:
    issues = []
    score = 1.0

    for k, v in payload.items():
        if v in (None, ""):
            issues.append(f"{k} missing")
            score -= 0.1

    if payload["income"] < 10000:
        issues.append("Income unrealistically low")
        score -= 0.2

    if not 300 <= payload["credit_score"] <= 850:
        issues.append("Invalid credit score")
        score -= 0.2

    if not 18 <= payload["age"] <= 100:
        issues.append("Invalid applicant age")
        score -= 0.2

    if payload["property_age"] > 80:
        issues.append("Very old property")
        score -= 0.1

    return round(max(score, 0.0), 2), issues
