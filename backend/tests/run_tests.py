"""
Comprehensive test runner and coverage report generator
Run this file to execute all tests and generate coverage reports
"""

import subprocess
import sys
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

def run_tests():
    """Execute all tests with coverage reporting"""
    
    print("=" * 70)
    print("RISK-AWARE DECISION SYSTEM - TEST SUITE RUNNER")
    print("=" * 70)
    print()
    
    # Change to backend directory
    os.chdir(PROJECT_ROOT / "backend")
    
    # Test 1: Run all tests with coverage
    print("📊 Running tests with coverage analysis...")
    print("-" * 70)
    
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=backend",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-x"
    ]
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print("\n❌ Tests failed!")
        return False
    
    print()
    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print()
    
    # Test 2: Run unit tests only
    print("🧪 Running unit tests only...")
    print("-" * 70)
    
    cmd_unit = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_risk_engine.py",
        "tests/test_data_quality.py",
        "-v",
        "--tb=short"
    ]
    
    subprocess.run(cmd_unit, capture_output=False)
    
    print()
    
    # Test 3: Run integration tests only
    print("🔗 Running integration tests...")
    print("-" * 70)
    
    cmd_integration = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_api_integration.py",
        "-v",
        "--tb=short"
    ]
    
    subprocess.run(cmd_integration, capture_output=False)
    
    print()
    print("=" * 70)
    print("📈 Coverage report generated in htmlcov/index.html")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
