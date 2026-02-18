"""
Pytest configuration and shared fixtures for all tests
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Fixture for FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def valid_payload():
    """Base valid applicant data"""
    return {
        "income": 600000,
        "age": 30,
        "credit_score": 720,
        "property_value": 7500000,
        "property_age": 10
    }


@pytest.fixture
def high_risk_payload():
    """High-risk applicant (low income, high property value)"""
    return {
        "income": 200000,
        "age": 25,
        "credit_score": 550,
        "property_value": 5000000,
        "property_age": 15
    }


@pytest.fixture
def low_risk_payload():
    """Low-risk applicant (high income, low property value)"""
    return {
        "income": 2000000,
        "age": 40,
        "credit_score": 800,
        "property_value": 3000000,
        "property_age": 5
    }


@pytest.fixture
def borderline_payload():
    """Borderline applicant (on decision thresholds)"""
    return {
        "income": 500000,
        "age": 28,
        "credit_score": 600,
        "property_value": 6000000,
        "property_age": 20
    }


@pytest.fixture
def very_old_property_payload():
    """Property at age boundary (very old)"""
    return {
        "income": 800000,
        "age": 35,
        "credit_score": 700,
        "property_value": 4000000,
        "property_age": 50
    }


@pytest.fixture
def low_credit_payload():
    """Applicant with low credit score"""
    return {
        "income": 1000000,
        "age": 45,
        "credit_score": 350,
        "property_value": 8000000,
        "property_age": 8
    }


@pytest.fixture
def zero_income_payload():
    """Applicant with zero income"""
    return {
        "income": 0,
        "age": 30,
        "credit_score": 700,
        "property_value": 5000000,
        "property_age": 10
    }


@pytest.fixture
def very_high_affordability_payload():
    """Applicant with very high affordability ratio (unaffordable)"""
    return {
        "income": 100000,
        "age": 26,
        "credit_score": 650,
        "property_value": 10000000,
        "property_age": 5
    }


@pytest.fixture
def perfect_payload():
    """Perfect applicant (high income, good credit, low property value)"""
    return {
        "income": 5000000,
        "age": 40,
        "credit_score": 850,
        "property_value": 2000000,
        "property_age": 3
    }


@pytest.fixture
def boundary_age_young():
    """Applicant at young age boundary"""
    return {
        "income": 600000,
        "age": 18,
        "credit_score": 700,
        "property_value": 7500000,
        "property_age": 10
    }


@pytest.fixture
def boundary_age_old():
    """Applicant at old age boundary"""
    return {
        "income": 600000,
        "age": 100,
        "credit_score": 700,
        "property_value": 7500000,
        "property_age": 10
    }
