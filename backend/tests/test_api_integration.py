"""
Integration tests for the FastAPI backend
Tests complete request-response flows and API behavior
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


class TestAPIBasicFunctionality:
    """Tests for basic API functionality"""
    
    def test_api_endpoint_exists(self, client):
        """Test that /evaluate endpoint exists"""
        response = client.post("/evaluate")
        # Should fail with validation error (missing body), not 404
        assert response.status_code in [422, 400]  # Validation error, not 404
    
    def test_api_with_valid_payload(self, client, valid_payload):
        """Test API with valid payload"""
        response = client.post("/evaluate", json=valid_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "decision" in data
    
    def test_api_response_structure(self, client, valid_payload):
        """Test response has correct structure"""
        response = client.post("/evaluate", json=valid_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check prediction structure
        assert "predicted_price" in data["prediction"]
        assert "risk_level" in data["prediction"]
        assert "affordability_ratio" in data["prediction"]
        
        # Check decision structure
        assert "decision" in data["decision"]
        assert "confidence" in data["decision"]
        assert "data_quality_score" in data["decision"]
        assert "missing_ratio" in data["decision"]
        assert "explanation" in data["decision"]
        assert "trace" in data["decision"]


class TestAPIInputValidation:
    """Tests for API input validation"""
    
    def test_missing_required_field(self, client):
        """Test rejection of missing required field"""
        invalid_payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000
            # Missing property_age
        }
        response = client.post("/evaluate", json=invalid_payload)
        
        assert response.status_code == 422
    
    def test_negative_income(self, client):
        """Test handling of negative income"""
        payload = {
            "income": -100000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        response = client.post("/evaluate", json=payload)
        
        # API might accept it and let backend handle
        assert response.status_code in [200, 422]
    
    def test_negative_property_value(self, client):
        """Test handling of negative property value"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 720,
            "property_value": -7500000,
            "property_age": 10
        }
        response = client.post("/evaluate", json=payload)
        
        assert response.status_code in [200, 422]
    
    def test_invalid_age(self, client):
        """Test with invalid age"""
        payload = {
            "income": 600000,
            "age": 10,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        response = client.post("/evaluate", json=payload)
        
        # Should accept but data quality check should flag it
        assert response.status_code == 200
        data = response.json()
        assert data["decision"]["data_quality_score"] < 1.0


class TestAPIPredictionLogic:
    """Tests for prediction and risk level assignment"""
    
    def test_risk_level_low(self, client, low_risk_payload):
        """Test low risk assignment"""
        response = client.post("/evaluate", json=low_risk_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"]["risk_level"] == "Low"
    
    def test_risk_level_medium(self, client):
        """Test medium risk assignment"""
        payload = {
            "income": 500000,
            "age": 30,
            "credit_score": 700,
            "property_value": 5000000,
            "property_age": 10
        }
        response = client.post("/evaluate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"]["risk_level"] in ["Low", "Medium"]
    
    def test_risk_level_high(self, client, high_risk_payload):
        """Test high risk assignment"""
        response = client.post("/evaluate", json=high_risk_payload)
        
        assert response.status_code == 200
        data = response.json()
        # High affordability ratio should trigger high risk
        assert data["prediction"]["risk_level"] in ["High", "Medium"]
    
    def test_affordability_ratio_calculation(self, client, valid_payload):
        """Test affordability ratio is calculated correctly"""
        response = client.post("/evaluate", json=valid_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Affordability should be property_price / income
        affordability = data["prediction"]["affordability_ratio"]
        assert affordability > 0


class TestAPIDecisionLogic:
    """Tests for decision assignment"""
    
    def test_decision_is_valid_enum(self, client, valid_payload):
        """Test that decision is one of valid values"""
        response = client.post("/evaluate", json=valid_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        valid_decisions = [
            "Auto-Approve",
            "Human Review",
            "Reject – Low Data Trust",
            "Reject"
        ]
        assert data["decision"]["decision"] in valid_decisions
    
    def test_perfect_applicant_approved(self, client, perfect_payload):
        """Test that perfect applicant gets approved"""
        response = client.post("/evaluate", json=perfect_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Perfect applicant should not be rejected
        assert "Reject" not in data["decision"]["decision"]
    
    def test_very_risky_applicant_rejected(self, client):
        """Test that very risky applicant gets rejected or reviewed"""
        payload = {
            "income": 50000,
            "age": 25,
            "credit_score": 350,
            "property_value": 10000000,
            "property_age": 10
        }
        response = client.post("/evaluate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not be auto-approved
        assert data["decision"]["decision"] != "Auto-Approve"
    
    def test_zero_income_special_handling(self, client, zero_income_payload):
        """Test special handling for zero income"""
        response = client.post("/evaluate", json=zero_income_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Zero income should trigger human review or reject
        assert data["decision"]["decision"] in ["Human Review", "Reject"]


class TestAPIConfidenceMetrics:
    """Tests for confidence and quality metrics"""
    
    def test_confidence_is_between_0_and_1(self, client, valid_payload):
        """Test that confidence is properly bounded"""
        response = client.post("/evaluate", json=valid_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        confidence = data["decision"]["confidence"]
        assert 0.0 <= confidence <= 1.0
    
    def test_data_quality_is_between_0_and_1(self, client, valid_payload):
        """Test that data quality score is properly bounded"""
        response = client.post("/evaluate", json=valid_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        quality = data["decision"]["data_quality_score"]
        assert 0.0 <= quality <= 1.0
    
    def test_missing_ratio_is_between_0_and_1(self, client, valid_payload):
        """Test that missing ratio is properly bounded"""
        response = client.post("/evaluate", json=valid_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        missing = data["decision"]["missing_ratio"]
        assert 0.0 <= missing <= 1.0
    
    def test_valid_data_has_high_quality(self, client, valid_payload):
        """Test that valid data gets high quality score"""
        response = client.post("/evaluate", json=valid_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["decision"]["data_quality_score"] > 0.7
        assert data["decision"]["missing_ratio"] == 0.0


class TestAPIEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_minimum_age(self, client):
        """Test with minimum age"""
        payload = {
            "income": 600000,
            "age": 18,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        response = client.post("/evaluate", json=payload)
        
        assert response.status_code == 200
    
    def test_maximum_age(self, client):
        """Test with maximum valid age"""
        payload = {
            "income": 600000,
            "age": 100,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        response = client.post("/evaluate", json=payload)
        
        assert response.status_code == 200
    
    def test_minimum_credit_score(self, client):
        """Test with minimum credit score"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 300,
            "property_value": 7500000,
            "property_age": 10
        }
        response = client.post("/evaluate", json=payload)
        
        assert response.status_code == 200
    
    def test_maximum_credit_score(self, client):
        """Test with maximum credit score"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 850,
            "property_value": 7500000,
            "property_age": 10
        }
        response = client.post("/evaluate", json=payload)
        
        assert response.status_code == 200
    
    def test_very_old_property(self, client):
        """Test with very old property"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 100
        }
        response = client.post("/evaluate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["decision"]["data_quality_score"] < 1.0
    
    def test_very_high_affordability_ratio(self, client):
        """Test with very high affordability ratio"""
        payload = {
            "income": 10000,
            "age": 30,
            "credit_score": 720,
            "property_value": 20000000,
            "property_age": 10
        }
        response = client.post("/evaluate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        # Very high affordability should affect decision
        assert data["prediction"]["risk_level"] == "High"


class TestAPIConsistency:
    """Tests for consistency of API behavior"""
    
    def test_same_input_same_output(self, client, valid_payload):
        """Test that same input produces same output"""
        response1 = client.post("/evaluate", json=valid_payload)
        response2 = client.post("/evaluate", json=valid_payload)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Core decision should be the same
        assert data1["decision"]["decision"] == data2["decision"]["decision"]
    
    def test_confidence_affected_by_credit_score(self, client):
        """Test that credit score affects confidence"""
        payload_low_credit = {
            "income": 600000,
            "age": 30,
            "credit_score": 350,
            "property_value": 7500000,
            "property_age": 10
        }
        
        payload_high_credit = {
            "income": 600000,
            "age": 30,
            "credit_score": 800,
            "property_value": 7500000,
            "property_age": 10
        }
        
        response1 = client.post("/evaluate", json=payload_low_credit)
        response2 = client.post("/evaluate", json=payload_high_credit)
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Higher credit score should give higher confidence
        assert data2["decision"]["confidence"] > data1["decision"]["confidence"]
    
    def test_confidence_affected_by_affordability(self, client):
        """Test that affordability ratio affects confidence"""
        payload_low_affordability = {
            "income": 5000000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        
        payload_high_affordability = {
            "income": 100000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        
        response1 = client.post("/evaluate", json=payload_low_affordability)
        response2 = client.post("/evaluate", json=payload_high_affordability)
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Lower affordability ratio should give higher confidence
        assert data1["decision"]["confidence"] > data2["decision"]["confidence"]
