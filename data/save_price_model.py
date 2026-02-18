# save_price_model.py
import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Step 1: Load your dataset
data_path = r"C:\Users\Ishta\OneDrive\Desktop\Risk-Aware Decision Automation\data\training_data.csv"
data = pd.read_csv(data_path)

# Step 2: Inspect columns to choose features and target
print("Columns in dataset:", data.columns)
print(data.head())

# Step 3: Define feature columns and target column
feature_columns = ["income", "age", "credit_score", "property_value", "property_age"]  # Use only existing columns
target_column = "price"

# Optional: check if all columns exist
for col in feature_columns + [target_column]:
    if col not in data.columns:
        raise ValueError(f"Column '{col}' not found in dataset!")

# Step 4: Prepare features and handle missing values
X = data[feature_columns].fillna(data[feature_columns].median())  # Fill missing values with median
y = data[target_column]

# Step 5: Train a simple Linear Regression model
model = LinearRegression()
model.fit(X, y)

# Step 6: Save the trained model
model_path = r"C:\Users\Ishta\OneDrive\Desktop\Risk-Aware Decision Automation\data\price_model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(model, f)

print(f"Model trained and saved to {model_path}")
