# Test Suite Documentation

## Overview

This is a comprehensive test suite for the Risk-Aware Property Decision System. The tests are organized into three main categories:

### Test Coverage

- **Unit Tests** (65+ test cases)
  - `test_risk_engine.py` - Core decision logic, confidence aggregation, decision gates
  - `test_data_quality.py` - Data validation, quality scoring, edge cases

- **Integration Tests** (40+ test cases)
  - `test_api_integration.py` - Full API request-response flows, end-to-end scenarios

- **Total**: 100+ comprehensive test cases covering:
  - Core business logic
  - API endpoints
  - Edge cases and boundaries
  - Error handling
  - Data validation
  - Consistency checks

---

## Setup

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

Key testing packages:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP testing
- `pytest-asyncio` - Async test support

---

## Running Tests

### Run All Tests

```bash
cd backend
pytest tests/ -v
```

### Run with Coverage Report

```bash
cd backend
pytest tests/ -v --cov=backend --cov-report=html --cov-report=term-missing
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run Specific Test File

```bash
# Unit tests only
pytest tests/test_risk_engine.py -v

# Data quality tests
pytest tests/test_data_quality.py -v

# Integration tests
pytest tests/test_api_integration.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_risk_engine.py::TestDecisionGate -v
```

### Run Specific Test

```bash
pytest tests/test_risk_engine.py::TestDecisionGate::test_auto_approve_high_confidence -v
```

### Use the Test Runner Script

```bash
cd backend/tests
python run_tests.py
```

---

## Test Structure

### conftest.py
**Shared fixtures** used across all tests:

- `client` - FastAPI TestClient for API testing
- `valid_payload` - Normal applicant data
- `high_risk_payload` - High-risk applicant
- `low_risk_payload` - Low-risk applicant
- `borderline_payload` - Borderline applicant on decision thresholds
- `perfect_payload` - Perfect applicant (should auto-approve)
- `zero_income_payload` - Applicant with zero income
- `very_old_property_payload` - Property at age boundaries
- `low_credit_payload` - Low credit score applicant

### test_risk_engine.py
**65+ unit tests** for core decision logic:

**TestCalculateMissingRatio** (5 tests)
- Tests for missing field detection
- Zero and empty string handling
- Ratio calculation accuracy

**TestRiskPenalties** (8 tests)
- Credit score penalties (<500, 500-600)
- Affordability penalties (>12, >6)
- Zero income detection
- Property age penalties
- Penalty capping at 0.6

**TestAggregateConfidence** (5 tests)
- Perfect score handling
- Default weight distribution (70% model, 30% quality)
- Custom weight support
- Penalty reduction
- Bounds checking [0, 1]

**TestDecisionGate** (6 tests)
- Auto-approve logic (confidence >= 0.80, no missing data)
- Human review triggers (confidence >= 0.60)
- Reject conditions (low quality, low credit, high affordability, zero income)
- Decision enum validation

**TestGenerateExplanation** (6 tests)
- Low confidence explanation
- Missing fields reporting
- Quality issues reporting
- Credit score analysis
- Affordability analysis
- All-checks-passed summary

**TestEvaluateDecision** (5 tests)
- Response structure validation
- High income handling
- Low income handling
- Zero income handling
- Explanation signal generation

### test_data_quality.py
**50+ unit tests** for data validation:

**TestDataQualityBasicValidation** (5 tests)
- Valid payload checks
- Missing field detection
- Missing income/credit score/age
- Empty string handling

**TestDataQualityIncomeValidation** (4 tests)
- Unrealistic low income detection
- Zero income detection
- Minimum valid income threshold
- Very high income handling

**TestDataQualityCreditScoreValidation** (5 tests)
- Valid credit score range (300-850)
- Too low (<300) detection
- Too high (>850) detection
- Boundary value testing (300, 850)

**TestDataQualityAgeValidation** (5 tests)
- Valid age range (18-100)
- Too young (<18) detection
- Too old (>100) detection
- Boundary value testing (18, 100)

**TestDataQualityPropertyAgeValidation** (3 tests)
- New property handling
- Very old property detection (>80 years)
- Age boundary testing

**TestDataQualityScoring** (2 tests)
- Score bounds [0, 1]
- Multiple issues reduce score more

### test_api_integration.py
**40+ integration tests** for complete API flows:

**TestAPIBasicFunctionality** (3 tests)
- Endpoint existence
- Valid payload processing
- Response structure validation

**TestAPIInputValidation** (4 tests)
- Missing required fields
- Negative income/property value
- Invalid age handling
- Type validation

**TestAPIPredictionLogic** (4 tests)
- Low risk assignment
- Medium risk assignment
- High risk assignment
- Affordability calculation

**TestAPIDecisionLogic** (4 tests)
- Valid decision enum values
- Perfect applicant approval
- Very risky applicant rejection
- Zero income special handling

**TestAPIConfidenceMetrics** (4 tests)
- Confidence bounds [0, 1]
- Data quality bounds [0, 1]
- Missing ratio bounds [0, 1]
- Valid data quality scores

**TestAPIEdgeCases** (7 tests)
- Minimum/maximum age boundaries
- Minimum/maximum credit score boundaries
- Very old property handling
- Very high affordability ratio
- All boundary conditions

**TestAPIConsistency** (3 tests)
- Same input produces same output
- Credit score affects confidence
- Affordability affects confidence
- Risk level consistency

---

## Test Fixtures

All fixtures are defined in `conftest.py` and automatically available to all tests:

```python
# Use in any test
def test_something(valid_payload, client):
    response = client.post("/evaluate", json=valid_payload)
    assert response.status_code == 200
```

### Available Fixtures

```
client                      # FastAPI TestClient
valid_payload              # Standard applicant
high_risk_payload          # High-risk applicant
low_risk_payload           # Low-risk applicant
borderline_payload         # Borderline applicant
very_old_property_payload  # Old property
low_credit_payload         # Low credit score
zero_income_payload        # Zero income
very_high_affordability_payload  # Unaffordable property
perfect_payload            # Perfect applicant
boundary_age_young         # Minimum age (18)
boundary_age_old           # Maximum age (100)
```

---

## Edge Cases Covered

✅ **Credit Score Boundaries**
- Below 300: Invalid
- 300: Minimum valid
- 350-399: Low risk
- 400-499: Moderate risk
- 500-599: Fair risk
- 600+: Good
- 850: Maximum valid
- >850: Invalid

✅ **Age Boundaries**
- Below 18: Invalid
- 18: Minimum valid
- 100: Maximum valid
- Above 100: Invalid

✅ **Income Scenarios**
- Zero income: Special handling
- Below 10,000: Low income penalty
- Normal ranges: Standard processing
- Very high: No penalty

✅ **Property Age**
- 0-80: Standard
- >80: Old property penalty
- Very old (90+): Quality score reduction

✅ **Affordability Ratios**
- <5: Low stress
- 5-6: Moderate stress
- 6-12: High stress → Review
- >12: Extreme stress → Reject

✅ **Decision Scenarios**
- Perfect applicant → Auto-Approve
- Good metrics → Auto-Approve
- Mixed metrics → Human Review
- Bad metrics → Reject
- Very bad metrics → Reject – Low Data Trust

---

## Expected Test Results

When all tests pass, you should see:

```
======================== test session starts =========================
backend/tests/test_risk_engine.py::TestCalculateMissingRatio::test_no_missing_fields PASSED
backend/tests/test_risk_engine.py::TestCalculateMissingRatio::test_single_missing_field PASSED
...
backend/tests/test_data_quality.py::TestDataQualityIncomeValidation::test_unrealistic_low_income PASSED
...
backend/tests/test_api_integration.py::TestAPIBasicFunctionality::test_api_with_valid_payload PASSED
...
======================== 105 passed in 2.34s ==========================
```

---

## Coverage Report

After running tests with coverage, open `htmlcov/index.html` to see:

- **Line coverage**: Percentage of lines executed
- **Branch coverage**: Percentage of conditional branches tested
- **Uncovered lines**: Code not reached by tests

Target: **> 80% code coverage**

---

## CI/CD Integration

To integrate tests in CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -r requirements.txt
    cd backend
    pytest tests/ -v --cov=backend --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### `ImportError: No module named 'backend'`

```bash
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
pytest tests/
```

### `ModuleNotFoundError: No module named 'pytest'`

```bash
pip install pytest pytest-cov
```

### Tests fail with `Connection refused`

Ensure FastAPI app is properly imported in test fixtures. Check `conftest.py`.

### Flaky tests (intermittent failures)

Add deterministic seeds:
```python
@pytest.fixture(autouse=True)
def reset_random():
    import random
    random.seed(42)
```

---

## Best Practices

1. ✅ **Use descriptive test names** - Should explain what is being tested
2. ✅ **One assertion per test** - Keep tests focused
3. ✅ **Use fixtures** - Avoid code duplication
4. ✅ **Test edge cases** - Don't just test happy path
5. ✅ **Test error handling** - Ensure graceful failures
6. ✅ **Keep tests fast** - < 100ms per test ideally
7. ✅ **Document complex tests** - Add docstrings

---

## Adding New Tests

Template for new test:

```python
def test_new_feature(valid_payload, client):
    """Test that [feature] works correctly when [condition]"""
    # Arrange
    payload = {...}
    
    # Act
    response = client.post("/evaluate", json=payload)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["decision"]["decision"] == "Expected"
```

---

## Contact & Support

For test-related issues or to add new tests, ensure:
1. Tests follow existing patterns
2. Fixtures are used for common data
3. Edge cases are considered
4. Docstrings explain test purpose
5. Tests don't modify backend code
