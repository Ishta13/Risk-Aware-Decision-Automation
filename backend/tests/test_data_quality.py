"""
Unit tests for data_quality module
Tests data validation and quality scoring
"""
import pytest
from backend.logic.data_quality import data_quality


class TestDataQualityBasicValidation:
    """Tests for basic data quality checks"""
    
    def test_valid_payload(self):
        """Test with completely valid payload"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert score >= 0.8
        assert len(issues) == 0
    
    def test_missing_income(self):
        """Test detection of missing income"""
        payload = {
            "income": None,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert score < 1.0
        assert any("income" in issue.lower() for issue in issues)
    
    def test_missing_credit_score(self):
        """Test detection of missing credit score"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": None,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert score < 1.0
        assert any("credit" in issue.lower() for issue in issues)
    
    def test_empty_string_values(self):
        """Test detection of empty string as missing"""
        payload = {
            "income": "",
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert score < 1.0


class TestDataQualityIncomeValidation:
    """Tests for income validation"""
    
    def test_unrealistic_low_income(self):
        """Test detection of unrealistically low income"""
        payload = {
            "income": 5000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert score < 1.0
        assert any("income" in issue.lower() for issue in issues)
    
    def test_zero_income(self):
        """Test detection of zero income"""
        payload = {
            "income": 0,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert score < 1.0
    
    def test_minimum_valid_income(self):
        """Test income at minimum valid threshold"""
        payload = {
            "income": 10000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        # Should be valid at exactly 10000
        assert not any("income" in issue.lower() for issue in issues)
    
    def test_very_high_income(self):
        """Test with very high income (should be valid)"""
        payload = {
            "income": 50000000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert score > 0.7


class TestDataQualityCreditScoreValidation:
    """Tests for credit score validation"""
    
    def test_valid_credit_score(self):
        """Test valid credit score"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert not any("credit" in issue.lower() for issue in issues)
    
    def test_credit_score_too_low(self):
        """Test credit score below valid range"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 250,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert any("credit" in issue.lower() for issue in issues)
    
    def test_credit_score_too_high(self):
        """Test credit score above valid range"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 950,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert any("credit" in issue.lower() for issue in issues)
    
    def test_credit_score_minimum_boundary(self):
        """Test credit score at minimum valid boundary (300)"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 300,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert not any("credit" in issue.lower() for issue in issues)
    
    def test_credit_score_maximum_boundary(self):
        """Test credit score at maximum valid boundary (850)"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 850,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert not any("credit" in issue.lower() for issue in issues)


class TestDataQualityAgeValidation:
    """Tests for age validation"""
    
    def test_valid_age(self):
        """Test valid age"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert not any("age" in issue.lower() for issue in issues)
    
    def test_age_too_young(self):
        """Test age below valid range"""
        payload = {
            "income": 600000,
            "age": 10,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert any("age" in issue.lower() for issue in issues)
    
    def test_age_too_old(self):
        """Test age above valid range"""
        payload = {
            "income": 600000,
            "age": 150,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert any("age" in issue.lower() for issue in issues)
    
    def test_age_minimum_boundary(self):
        """Test age at minimum valid boundary (18)"""
        payload = {
            "income": 600000,
            "age": 18,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert not any("age" in issue.lower() for issue in issues)
    
    def test_age_maximum_boundary(self):
        """Test age at maximum valid boundary (100)"""
        payload = {
            "income": 600000,
            "age": 100,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 10
        }
        score, issues = data_quality(payload)
        
        assert not any("age" in issue.lower() for issue in issues)


class TestDataQualityPropertyAgeValidation:
    """Tests for property age validation"""
    
    def test_new_property(self):
        """Test with new property"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 1
        }
        score, issues = data_quality(payload)
        
        assert not any("property" in issue.lower() for issue in issues)
    
    def test_old_property(self):
        """Test detection of very old property"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 90
        }
        score, issues = data_quality(payload)
        
        assert any("property" in issue.lower() or "old" in issue.lower() for issue in issues)
    
    def test_property_age_boundary(self):
        """Test property age at boundary (80 years)"""
        payload = {
            "income": 600000,
            "age": 30,
            "credit_score": 720,
            "property_value": 7500000,
            "property_age": 80
        }
        score, issues = data_quality(payload)
        
        assert any("property" in issue.lower() or "old" in issue.lower() for issue in issues)


class TestDataQualityScoring:
    """Tests for overall quality score"""
    
    def test_score_is_bounded(self):
        """Test that quality score is between 0 and 1"""
        payload = {
            "income": 0,
            "age": 10,
            "credit_score": 250,
            "property_value": 7500000,
            "property_age": 90
        }
        score, issues = data_quality(payload)
        
        assert 0.0 <= score <= 1.0
    
    def test_multiple_issues_reduce_score(self):
        """Test that multiple issues reduce score more"""
        payload_one_issue = {
            "income": 600000,
            "age": 30,
            "credit_score": 250,
            "property_value": 7500000,
            "property_age": 10
        }
        score_one, _ = data_quality(payload_one_issue)
        
        payload_multiple_issues = {
            "income": 0,
            "age": 10,
            "credit_score": 250,
            "property_value": 7500000,
            "property_age": 90
        }
        score_multiple, _ = data_quality(payload_multiple_issues)
        
        assert score_multiple < score_one
