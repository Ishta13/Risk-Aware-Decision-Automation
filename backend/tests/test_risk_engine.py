"""
Unit tests for risk_engine module
Tests core decision logic, confidence aggregation, and explanation generation
"""
import pytest
from backend.logic.risk_engine import (
    calculate_missing_ratio,
    risk_penalties,
    aggregate_confidence,
    decision_gate,
    generate_explanation,
    evaluate_decision,
    Decision
)


class TestCalculateMissingRatio:
    """Tests for missing_ratio calculation"""
    
    def test_no_missing_fields(self):
        """Test with all valid fields"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        result = calculate_missing_ratio(payload)
        assert result == 0.0
    
    def test_single_missing_field(self):
        """Test with one missing field"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": None,
            "property_value": 7500000,
            "property_age": 10
        }
        result = calculate_missing_ratio(payload)
        assert result == 0.2  # 1 out of 5
    
    def test_all_missing_fields(self):
        """Test with all fields missing"""
        payload = {
            "income": None,
            "age": None,
            "credit_score": None,
            "property_value": None,
            "property_age": None
        }
        result = calculate_missing_ratio(payload)
        assert result == 1.0
    
    def test_zero_as_missing(self):
        """Test that zero is treated as missing"""
        payload = {
            "income": 0,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        result = calculate_missing_ratio(payload)
        assert result == 0.2
    
    def test_empty_string_as_missing(self):
        """Test that empty string is treated as missing"""
        payload = {
            "income": "",
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        result = calculate_missing_ratio(payload)
        assert result == 0.2


class TestRiskPenalties:
    """Tests for risk_penalties calculation"""
    
    def test_no_penalties(self):
        """Test with all good metrics"""
        payload = {
            "income": 1000000,
            "age": 35,
            "credit_score": 750,
            "property_age": 10
        }
        penalty = risk_penalties(payload, affordability_ratio=3.0)
        assert penalty == 0.0
    
    def test_low_credit_score_penalty(self):
        """Test credit score < 500 penalty"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 450,
            "property_age": 10
        }
        penalty = risk_penalties(payload, affordability_ratio=5.0)
        assert penalty >= 0.25
    
    def test_moderate_credit_score_penalty(self):
        """Test credit score 500-600 penalty"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 550,
            "property_age": 10
        }
        penalty = risk_penalties(payload, affordability_ratio=5.0)
        assert penalty >= 0.15
    
    def test_very_high_affordability_penalty(self):
        """Test affordability ratio > 12 penalty"""
        payload = {
            "income": 100000,
            "age": 30,
            "credit_score": 700,
            "property_age": 10
        }
        penalty = risk_penalties(payload, affordability_ratio=15.0)
        assert penalty >= 0.40
    
    def test_moderate_affordability_penalty(self):
        """Test affordability ratio 6-12 penalty"""
        payload = {
            "income": 100000,
            "age": 30,
            "credit_score": 700,
            "property_age": 10
        }
        penalty = risk_penalties(payload, affordability_ratio=8.0)
        assert penalty >= 0.20
    
    def test_zero_income_penalty(self):
        """Test zero income penalty"""
        payload = {
            "income": 0,
            "age": 30,
            "credit_score": 700,
            "property_age": 10
        }
        penalty = risk_penalties(payload, affordability_ratio=10.0)
        assert penalty >= 0.30
    
    def test_very_old_property_penalty(self):
        """Test property age > 40 penalty"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 700,
            "property_age": 50
        }
        penalty = risk_penalties(payload, affordability_ratio=5.0)
        assert penalty >= 0.10
    
    def test_penalty_cap(self):
        """Test that penalty is capped at 0.6"""
        payload = {
            "income": 0,
            "age": 30,
            "credit_score": 350,
            "property_age": 50
        }
        penalty = risk_penalties(payload, affordability_ratio=15.0)
        assert penalty <= 0.6


class TestAggregateConfidence:
    """Tests for confidence aggregation"""
    
    def test_perfect_scores(self):
        """Test with perfect model and data quality"""
        confidence = aggregate_confidence(
            model_confidence=1.0,
            data_quality_score=1.0,
            penalty=0.0
        )
        assert confidence == 1.0
    
    def test_default_weights(self):
        """Test default weight distribution"""
        confidence = aggregate_confidence(
            model_confidence=0.8,
            data_quality_score=0.6,
            penalty=0.0
        )
        # Should be 0.7 * 0.8 + 0.3 * 0.6 = 0.56 + 0.18 = 0.74
        assert abs(confidence - 0.74) < 0.01
    
    def test_custom_weights(self):
        """Test custom weight specification"""
        confidence = aggregate_confidence(
            model_confidence=0.8,
            data_quality_score=0.6,
            penalty=0.0,
            weights={"model": 0.5, "quality": 0.5}
        )
        # Should be 0.5 * 0.8 + 0.5 * 0.6 = 0.4 + 0.3 = 0.7
        assert abs(confidence - 0.7) < 0.01
    
    def test_penalty_reduction(self):
        """Test that penalty reduces confidence"""
        conf_no_penalty = aggregate_confidence(
            model_confidence=0.8,
            data_quality_score=0.8,
            penalty=0.0
        )
        conf_with_penalty = aggregate_confidence(
            model_confidence=0.8,
            data_quality_score=0.8,
            penalty=0.2
        )
        assert conf_no_penalty > conf_with_penalty
    
    def test_confidence_bounds(self):
        """Test that confidence is bounded [0, 1]"""
        confidence = aggregate_confidence(
            model_confidence=0.2,
            data_quality_score=0.2,
            penalty=0.5
        )
        assert 0.0 <= confidence <= 1.0


class TestDecisionGate:
    """Tests for decision gate logic"""
    
    def test_auto_approve_high_confidence(self):
        """Test auto-approve with high confidence and no missing data"""
        decision = decision_gate(
            confidence=0.85,
            missing_ratio=0.0,
            quality_score=0.8,
            affordability_ratio=5.0,
            payload={
                "income": 1000000,
                "age": 35,
                "credit_score": 750,
                "property_age": 10,
                "property_value": 5000000
            }
        )
        assert decision == Decision.AUTO_APPROVE
    
    def test_human_review_medium_confidence(self):
        """Test human review with medium confidence"""
        decision = decision_gate(
            confidence=0.70,
            missing_ratio=0.0,
            quality_score=0.7,
            affordability_ratio=6.5,
            payload={
                "income": 600000,
                "age": 30,
                "credit_score": 680,
                "property_age": 10,
                "property_value": 4000000
            }
        )
        assert decision == Decision.HUMAN_REVIEW
    
    def test_reject_low_quality(self):
        """Test reject with low data quality"""
        decision = decision_gate(
            confidence=0.9,
            missing_ratio=0.5,
            quality_score=0.3,
            affordability_ratio=5.0,
            payload={
                "income": 1000000,
                "age": 35,
                "credit_score": 750,
                "property_age": 10,
                "property_value": 5000000
            }
        )
        assert decision == Decision.REJECT_LOW_TRUST
    
    def test_reject_very_low_credit(self):
        """Test reject with credit score < 400"""
        decision = decision_gate(
            confidence=0.5,
            missing_ratio=0.0,
            quality_score=0.8,
            affordability_ratio=5.0,
            payload={
                "income": 600000,
                "age": 30,
                "credit_score": 350,
                "property_age": 10,
                "property_value": 3000000
            }
        )
        assert decision == Decision.REJECT
    
    def test_reject_very_high_affordability(self):
        """Test reject with affordability > 12"""
        decision = decision_gate(
            confidence=0.7,
            missing_ratio=0.0,
            quality_score=0.8,
            affordability_ratio=15.0,
            payload={
                "income": 100000,
                "age": 30,
                "credit_score": 700,
                "property_age": 10,
                "property_value": 2000000
            }
        )
        assert decision == Decision.REJECT
    
    def test_human_review_zero_income(self):
        """Test human review with zero income"""
        decision = decision_gate(
            confidence=0.6,
            missing_ratio=0.0,
            quality_score=0.7,
            affordability_ratio=0.0,
            payload={
                "income": 0,
                "age": 30,
                "credit_score": 700,
                "property_age": 10,
                "property_value": 5000000
            }
        )
        assert decision == Decision.HUMAN_REVIEW


class TestGenerateExplanation:
    """Tests for explanation generation"""
    
    def test_low_confidence_reason(self):
        """Test that low confidence is mentioned"""
        explanation = generate_explanation(
            confidence=0.5,
            missing_fields=[],
            quality_issues=[],
            payload={"credit_score": 700, "property_age": 10},
            affordability_ratio=5.0
        )
        assert any("confidence" in signal.lower() for signal in explanation["signals"])
    
    def test_missing_fields_reason(self):
        """Test that missing fields are mentioned"""
        explanation = generate_explanation(
            confidence=0.7,
            missing_fields=["credit_score", "income"],
            quality_issues=[],
            payload={"credit_score": 700},
            affordability_ratio=5.0
        )
        assert any("missing" in signal.lower() for signal in explanation["signals"])
    
    def test_quality_issues_reason(self):
        """Test that quality issues are mentioned"""
        explanation = generate_explanation(
            confidence=0.7,
            missing_fields=[],
            quality_issues=["Income unrealistically low"],
            payload={"income": 5000, "credit_score": 700},
            affordability_ratio=5.0
        )
        assert "Income unrealistically low" in explanation["signals"]
    
    def test_credit_score_low_reason(self):
        """Test credit score analysis"""
        explanation = generate_explanation(
            confidence=0.7,
            missing_fields=[],
            quality_issues=[],
            payload={"income": 600000, "credit_score": 450, "property_age": 10},
            affordability_ratio=5.0
        )
        assert any("credit" in signal.lower() for signal in explanation["signals"])
    
    def test_affordability_reason(self):
        """Test affordability analysis"""
        explanation = generate_explanation(
            confidence=0.5,
            missing_fields=[],
            quality_issues=[],
            payload={"income": 100000, "credit_score": 700, "property_age": 10},
            affordability_ratio=15.0
        )
        assert any("affordability" in signal.lower() or "afford" in signal.lower() 
                   for signal in explanation["signals"])
    
    def test_all_checks_passed(self):
        """Test when all checks pass"""
        explanation = generate_explanation(
            confidence=0.85,
            missing_fields=[],
            quality_issues=[],
            payload={"income": 2000000, "credit_score": 800, "property_age": 5},
            affordability_ratio=2.0
        )
        assert "passed" in explanation["summary"].lower()


class TestEvaluateDecision:
    """Tests for complete decision evaluation"""
    
    def test_evaluate_decision_structure(self, valid_payload):
        """Test that evaluation returns correct structure"""
        result = evaluate_decision(
            payload={**valid_payload, "affordability_ratio": 5.0},
            model_confidence=0.75
        )
        
        assert "decision" in result
        assert "confidence" in result
        assert "data_quality_score" in result
        assert "missing_ratio" in result
        assert "explanation" in result
        assert "trace" in result
    
    def test_evaluate_decision_with_high_income(self, low_risk_payload):
        """Test evaluation with high income applicant"""
        result = evaluate_decision(
            payload={**low_risk_payload, "affordability_ratio": 2.0},
            model_confidence=0.85
        )
        
        assert result["confidence"] > 0.7
        assert result["decision"] in [d.value for d in Decision]
    
    def test_evaluate_decision_with_low_income(self, high_risk_payload):
        """Test evaluation with low income applicant"""
        result = evaluate_decision(
            payload={**high_risk_payload, "affordability_ratio": 10.0},
            model_confidence=0.60
        )
        
        # Should have lower confidence due to affordability
        assert result["confidence"] <= 0.75
    
    def test_evaluate_decision_zero_income(self, zero_income_payload):
        """Test evaluation with zero income"""
        result = evaluate_decision(
            payload={**zero_income_payload, "affordability_ratio": 999.0},
            model_confidence=0.5
        )
        
        # Should trigger human review or reject
        assert result["decision"] in ["Human Review", "Reject"]
    
    def test_evaluate_decision_returns_signals(self, valid_payload):
        """Test that explanation signals are returned"""
        result = evaluate_decision(
            payload={**valid_payload, "affordability_ratio": 5.0},
            model_confidence=0.75
        )
        
        assert "signals" in result["explanation"]
        assert isinstance(result["explanation"]["signals"], list)
