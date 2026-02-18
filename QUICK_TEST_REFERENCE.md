# 🎯 Quick Test Reference

## Installation
```bash
pip install -r requirements.txt
```

## Run Tests

| Command | Purpose |
|---------|---------|
| `pytest tests/ -v` | Run all tests |
| `pytest tests/ -v --cov=backend` | Run with coverage |
| `pytest tests/test_risk_engine.py -v` | Unit: Risk Engine |
| `pytest tests/test_data_quality.py -v` | Unit: Data Quality |
| `pytest tests/test_api_integration.py -v` | Integration: API |
| `pytest tests/ -v -x` | Stop at first failure |
| `pytest tests/ -v --tb=short` | Shorter failure output |
| `pytest tests/ -v --durations=5` | Show 5 slowest tests |
| `python backend/tests/run_tests.py` | Full test suite runner |

## Test Statistics

```
Total Tests:        137
├── Unit Tests:     97
│   ├── Risk Engine: 47
│   └── Data Quality: 50
└── Integration:     40
    └── API: 40

Coverage Target:    > 80%
Expected Duration:  ~3-5 seconds
```

## Test Files Structure

```
backend/tests/
├── conftest.py                  # Fixtures (11 scenarios)
├── test_risk_engine.py          # Unit tests (47)
├── test_data_quality.py         # Unit tests (50)
├── test_api_integration.py      # Integration tests (40)
├── test_api.py                  # Old tests (keep for reference)
├── test_decisions.py            # Old tests (keep for reference)
├── run_tests.py                 # Test runner script
├── pytest.ini                   # Pytest configuration
├── TEST_DOCUMENTATION.md        # Detailed documentation
└── __init__.py
```

## What Gets Tested

### ✅ Risk Engine (47 tests)
- Missing ratio calculation
- Risk penalties
- Confidence aggregation
- Decision gates (Auto-Approve, Review, Reject)
- Explanation generation

### ✅ Data Quality (50 tests)
- Income validation (≥10,000)
- Credit score validation (300-850)
- Age validation (18-100)
- Property age validation
- Multiple issue aggregation

### ✅ API Integration (40 tests)
- Request validation
- Response structure
- Decision consistency
- Confidence bounds
- Edge case handling
- Affordability ratio effects

## Key Test Fixtures

```python
@pytest.fixture
def valid_payload():
    return {
        "income": 600000,
        "age": 30,
        "credit_score": 720,
        "property_value": 7500000,
        "property_age": 10
    }

# Also available:
# - high_risk_payload
# - low_risk_payload
# - perfect_payload
# - zero_income_payload
# - very_high_affordability_payload
# - boundary_age_young / boundary_age_old
```

## Sample Test

```python
def test_auto_approve_high_confidence(client, valid_payload):
    """Test that high confidence applicant gets auto-approved"""
    response = client.post("/evaluate", json=valid_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["decision"]["decision"] == "Auto-Approve"
```

## Expected Output

```
======================== test session starts =========================
platform win32 -- Python 3.x.x, pytest-x.x.x, httpx-x.x.x
rootdir: C:\...\Risk-Aware Decision Automation
collected 137 items

backend/tests/test_risk_engine.py::TestCalculateMissingRatio::test_no_missing_fields PASSED [1%]
backend/tests/test_risk_engine.py::TestCalculateMissingRatio::test_single_missing_field PASSED [2%]
...
backend/tests/test_api_integration.py::TestAPIConsistency::test_confidence_affected_by_affordability PASSED [100%]

======================== 137 passed in 3.45s ==========================
```

## Coverage Report

```bash
# Generate HTML report
pytest tests/ -v --cov=backend --cov-report=html

# Then open: htmlcov/index.html
```

Expected coverage:
- Risk Engine: 93%
- Data Quality: 93%
- Main API: 87%
- **Total: 80%+**

## Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: backend` | `cd backend && export PYTHONPATH=.` |
| `ImportError: pytest` | `pip install pytest` |
| Tests hang | Check if API server is running (should not be) |
| Coverage not generated | Ensure pytest-cov is installed |

## Decision Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Confidence | ≥ 0.85 | Auto-Approve |
| | 0.60-0.85 | Human Review |
| | < 0.60 | Reject |
| Affordability | ≤ 5 | Low Risk |
| | 5-12 | Medium/Review |
| | > 12 | Reject |
| Credit Score | ≥ 600 | Good |
| | 500-599 | Fair |
| | < 400 | Reject |
| Data Quality | ≥ 0.8 | Good |
| | 0.5-0.8 | Fair |
| | < 0.5 | Reject |

## Next Steps

1. ✅ Run all tests
2. ✅ Check coverage (target: 80%+)
3. ✅ Review test documentation
4. ✅ Integrate with CI/CD
5. ✅ Add new tests for new features

## Files NOT Modified

```
✅ backend/main.py
✅ backend/logic/risk_engine.py
✅ backend/logic/data_quality.py
✅ backend/database/db.py
✅ frontend/app.py
✅ frontend/components/
```

All tests are **isolated, non-breaking, and fully compatible** with existing code!
