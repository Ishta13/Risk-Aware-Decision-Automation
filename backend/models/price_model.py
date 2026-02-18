import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

# ----------------- Load Training Data -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "training_data.csv")

df = pd.read_csv(DATA_PATH)

# Features & target
X = df[["income", "age", "credit_score", "property_age"]]
y = df["property_value"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ----------------- Train Model -----------------
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ----------------- Save Model -----------------
SAVE_PATH = os.path.join(BASE_DIR, "..", "data", "price_model.pkl")

# Wrap in a bundle for future flexibility
model_bundle = {"model": model}

joblib.dump(model_bundle, SAVE_PATH)
print(f"[INFO] Model trained and saved at {SAVE_PATH}")
