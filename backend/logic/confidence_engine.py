import numpy as np
import pandas as pd

def estimate_confidence(model, df: pd.DataFrame, runs: int = 25) -> float:
    """
    RandomForest prediction stability confidence
    """
    preds = []

    for _ in range(runs):
        preds.append(model.predict(df)[0])

    mean = np.mean(preds)
    std = np.std(preds)

    if mean == 0:
        return 0.5

    confidence = 1 - (std / abs(mean))

    return round(min(max(confidence, 0.45), 0.95), 2)
