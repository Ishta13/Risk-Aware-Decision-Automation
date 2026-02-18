import requests
import json
import os

API_URL = "http://127.0.0.1:8000/evaluate"

# Your test cases (as defined previously)
test_cases = [
    {
        "name": "Perfect data, high income",
        "input": {"income": 1000000, "age": 35, "credit_score": 750, "property_value": 2000000, "property_age": 5}
    },
    {
        "name": "Low income, high property value",
        "input": {"income": 20000, "age": 28, "credit_score": 700, "property_value": 150000, "property_age": 10}
    },
    # Add other cases...
]

results = []

for case in test_cases:
    try:
        response = requests.post(API_URL, json=case["input"], timeout=10)
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        result = {"error": str(e)}

    output = {
        "test_case": case["name"],
        "input": case["input"],
        "output": result
    }
    results.append(output)
    print(f"✅ {case['name']} tested.")

# Save results to file
os.makedirs("tests/results", exist_ok=True)
with open("tests/results/test_results.json", "w") as f:
    json.dump(results, f, indent=4)

print("All test results saved to tests/results/test_results.json")
