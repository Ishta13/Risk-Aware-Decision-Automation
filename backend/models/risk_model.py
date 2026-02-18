import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
from pathlib import Path

# Get project root safely
BASE_DIR = Path(__file__).resolve().parents[2]

# Build path to data file
DATA_PATH = BASE_DIR / "data" / "training_data.csv"

print("Loading data from:", DATA_PATH)

df = pd.read_csv(DATA_PATH)

X = df[['income','age','credit_score','property_value','property_age']].fillna(0)
y = df['risk'].map({"Low": 0, "Medium": 1, "High": 2})

model = DecisionTreeClassifier(max_depth=4)
model.fit(X, y)

# Save model next to this file
MODEL_PATH = Path(__file__).parent / "risk_model.pkl"
joblib.dump(model, MODEL_PATH)

print("✅ Risk model trained and saved at:", MODEL_PATH)
