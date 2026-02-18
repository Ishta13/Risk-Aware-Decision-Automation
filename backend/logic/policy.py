"""
Policy configuration used for decision governance.
This file documents thresholds separately from model logic.
"""

DECISION_POLICY = {
    "version": "v1-default",

    "auto_approve": {
        "min_confidence": 0.85,
        "min_data_quality": 0.7,
        "missing_fields_allowed": 0
    },

    "human_review": {
        "min_confidence": 0.6
    },

    "reject": {
        "reason": "Low confidence or poor data quality"
    }
}
