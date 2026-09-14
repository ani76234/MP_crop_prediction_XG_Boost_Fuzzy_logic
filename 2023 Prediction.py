import joblib
import pandas as pd
from pathlib import Path

# =====================================================
# Paths
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    "D:\KPMG project\DATA SET FOR XG BOOST/xgboost_wheat_yield_outputs_trial_2/wheat_yield_xgboost_trial_2.joblib"
)

INPUT_PATH = BASE_DIR / "MP_2023_ML_Model_Input.csv"

OUTPUT_PATH = BASE_DIR / "Predicted_Yield_2023.csv"

# =====================================================
# Load model
# =====================================================

bundle = joblib.load(MODEL_PATH)

model = bundle["model"]
feature_columns = bundle["feature_columns"]
district_categories = bundle["district_categories"]

# =====================================================
# Load input
# =====================================================

future = pd.read_csv(INPUT_PATH)

# Convert district exactly like training
future["District"] = (
    future["District"]
    .astype("string")
    .astype(pd.CategoricalDtype(categories=district_categories))
)

future["Year"] = future["Year"].astype(int)

# =====================================================
# Verify columns
# =====================================================

missing = set(feature_columns) - set(future.columns)

if missing:
    raise ValueError(f"Missing columns: {missing}")

# =====================================================
# Predict
# =====================================================

future["Predicted_Yield"] = model.predict(
    future[feature_columns]
)

future.to_csv(OUTPUT_PATH, index=False)

print("\nPrediction completed!\n")

print(future[["District","Predicted_Yield"]])