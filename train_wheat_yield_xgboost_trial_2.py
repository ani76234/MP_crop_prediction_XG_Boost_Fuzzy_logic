"""Trial 2: walk-forward XGBoost using engineered temporal wheat-yield features.

Run after installing requirements_wheat_xgboost.txt:
    python train_wheat_yield_xgboost_trial_2.py
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor


matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "Trial_Data1_with_2015_history.csv"
OUTPUT_DIR = BASE_DIR / "xgboost_wheat_yield_outputs_trial_2"
RANDOM_STATE = 42
MIN_TRAINING_YEARS = 2
TARGET_COLUMN = "Yield"
STATUS_COLUMN = "Predictors_Available"

CURRENT_SEASON_FEATURES = [
    "Mean_Rainfall", "Mean_NDVI", "Peak_NDVI", "Mean_EVI", "Peak_EVI", "Mean_Soil_Moisture",
]
YIELD_HISTORY_FEATURES = [
    # Previous_Year_Yield is intentionally used instead of duplicate Yield_Lag_1.
    "Previous_Year_Yield", "Yield_Lag_2", "Yield_Lag_3", "Yield_Rolling_Mean_2",
    "Yield_Rolling_Mean_3", "Yield_Rolling_Std_3", "Previous_Yield_Change",
]
SEASONAL_TEMPORAL_FEATURES = [
    f"{feature}_{suffix}"
    for feature in CURRENT_SEASON_FEATURES
    for suffix in [
        "Lag_1", "Lag_2", "Rolling_Mean_2", "Anomaly_vs_Prior_Mean", "Change_From_Lag_1"
    ]
]

# Explicit list ensures source columns such as Area, Production, Season, State,
# District_Key, Predictors_Available, and any future extra fields are never
# passed to the model.
FEATURE_COLUMNS = [
    "District", "Year", *CURRENT_SEASON_FEATURES, *YIELD_HISTORY_FEATURES, *SEASONAL_TEMPORAL_FEATURES,
]
NUMERIC_FEATURES = [feature for feature in FEATURE_COLUMNS if feature != "District"]


def prepare_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load Trial Data 1 and prepare XGBoost-native categorical/numeric types."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Trial 2 dataset not found: {DATA_PATH}")
    data = pd.read_csv(DATA_PATH)
    missing_columns = sorted(set(FEATURE_COLUMNS + [TARGET_COLUMN]).difference(data.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    if STATUS_COLUMN in data.columns:
        data = data.loc[data[STATUS_COLUMN].fillna(False)].copy()

    features = data.loc[:, FEATURE_COLUMNS].copy()
    target = pd.to_numeric(data[TARGET_COLUMN], errors="coerce")
    if target.isna().any() or features["District"].isna().any():
        raise ValueError("Yield and District must not contain missing values.")

    # Native categorical support: do not label-encode or one-hot encode districts.
    features["District"] = features["District"].astype("string").astype("category")
    for feature in NUMERIC_FEATURES:
        features[feature] = pd.to_numeric(features[feature], errors="coerce")
    if features["Year"].isna().any():
        raise ValueError("Year must be numeric and non-missing.")
    features["Year"] = features["Year"].astype("int64")

    # Missing lag values mean that an older observation does not exist. Leave
    # them as NaN: XGBoost learns an appropriate missing-value tree branch.
    return features, target


def create_model() -> XGBRegressor:
    """Build a regularized gradient-boosted tree model for each time fold."""
    return XGBRegressor(
        objective="reg:squarederror",
        n_estimators=600,
        learning_rate=0.025,
        max_depth=3,
        min_child_weight=4,
        subsample=0.85,
        colsample_bytree=0.80,
        reg_alpha=0.10,
        reg_lambda=1.5,
        tree_method="hist",
        enable_categorical=True,
        importance_type="gain",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )


def calculate_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    """Calculate regression metrics for a single fold or all out-of-fold rows."""
    if np.any(actual == 0):
        raise ValueError("MAPE is undefined when actual Yield includes zero.")
    return {
        "R2": float(r2_score(actual, predicted)),
        "RMSE": float(np.sqrt(mean_squared_error(actual, predicted))),
        "MAE": float(mean_absolute_error(actual, predicted)),
        "MAPE_percent": float(np.mean(np.abs((actual - predicted) / actual)) * 100),
    }


def save_plots(predictions: pd.DataFrame, importance: pd.DataFrame) -> None:
    """Create diagnostics using predictions that were all made on future years."""
    ordered = importance.sort_values("Importance", ascending=True)
    plt.figure(figsize=(11, 10))
    plt.barh(ordered["Feature"], ordered["Importance"], color="#2b6cb0")
    plt.xlabel("Gain importance from final model")
    plt.title("Trial 2: Feature Importance")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "feature_importance.png", dpi=300)
    plt.close()

    actual = predictions["Actual_Yield"].to_numpy()
    predicted = predictions["Predicted_Yield"].to_numpy()
    lower, upper = min(actual.min(), predicted.min()), max(actual.max(), predicted.max())
    plt.figure(figsize=(7, 7))
    plt.scatter(actual, predicted, alpha=0.75, color="#2b6cb0", edgecolors="white")
    plt.plot([lower, upper], [lower, upper], "r--", label="Perfect prediction")
    plt.xlabel("Actual Yield")
    plt.ylabel("Predicted Yield")
    plt.title("Trial 2: Walk-Forward Predicted vs Actual")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "predicted_vs_actual.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 6))
    plt.scatter(predicted, actual - predicted, alpha=0.75, color="#2b6cb0", edgecolors="white")
    plt.axhline(0, color="red", linestyle="--")
    plt.xlabel("Predicted Yield")
    plt.ylabel("Residual (Actual - Predicted)")
    plt.title("Trial 2: Walk-Forward Residuals")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "residual_plot.png", dpi=300)
    plt.close()


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    features, target = prepare_data()
    years = sorted(features["Year"].unique())
    if len(years) <= MIN_TRAINING_YEARS:
        raise ValueError("Not enough years for walk-forward validation.")

    fold_metrics: list[dict[str, float | int]] = []
    predictions: list[pd.DataFrame] = []

    # Expanding walk-forward validation: every test year is unseen during fit.
    for test_year in years[MIN_TRAINING_YEARS:]:
        train_mask = features["Year"] < test_year
        test_mask = features["Year"] == test_year
        model = create_model()
        model.fit(features.loc[train_mask], target.loc[train_mask], verbose=False)
        predicted = model.predict(features.loc[test_mask])
        actual = target.loc[test_mask].to_numpy()
        metrics = calculate_metrics(actual, predicted)
        metrics.update({"Test_Year": int(test_year), "Training_Rows": int(train_mask.sum()), "Test_Rows": int(test_mask.sum())})
        fold_metrics.append(metrics)
        predictions.append(pd.DataFrame({
            "Year": features.loc[test_mask, "Year"].to_numpy(),
            "District": features.loc[test_mask, "District"].astype(str).to_numpy(),
            "Actual_Yield": actual,
            "Predicted_Yield": predicted,
            "Residual": actual - predicted,
        }))
        print(
            f"Test year {test_year} | R²: {metrics['R2']:.4f} | RMSE: {metrics['RMSE']:.4f} | "
            f"MAE: {metrics['MAE']:.4f} | MAPE: {metrics['MAPE_percent']:.2f}%"
        )

    walk_forward_predictions = pd.concat(predictions, ignore_index=True)
    overall_metrics = calculate_metrics(
        walk_forward_predictions["Actual_Yield"].to_numpy(), walk_forward_predictions["Predicted_Yield"].to_numpy()
    )
    pd.DataFrame(fold_metrics).to_csv(OUTPUT_DIR / "walk_forward_fold_metrics.csv", index=False)
    walk_forward_predictions.to_csv(OUTPUT_DIR / "walk_forward_predictions.csv", index=False)
    (OUTPUT_DIR / "overall_walk_forward_metrics.json").write_text(json.dumps(overall_metrics, indent=2), encoding="utf-8")

    print("\nOverall walk-forward evaluation")
    print("-" * 35)
    print(f"R²:   {overall_metrics['R2']:.4f}")
    print(f"RMSE: {overall_metrics['RMSE']:.4f}")
    print(f"MAE:  {overall_metrics['MAE']:.4f}")
    print(f"MAPE: {overall_metrics['MAPE_percent']:.2f}%")

    # Retrain only after validation, using all observed years for deployment.
    final_model = create_model()
    final_model.fit(features, target, verbose=False)
    importance = pd.DataFrame({"Feature": FEATURE_COLUMNS, "Importance": final_model.feature_importances_})
    importance.sort_values("Importance", ascending=False).to_csv(OUTPUT_DIR / "feature_importance.csv", index=False)
    save_plots(walk_forward_predictions, importance)

    model_bundle = {
        "model": final_model,
        "feature_columns": FEATURE_COLUMNS,
        "district_categories": features["District"].cat.categories.tolist(),
        "walk_forward_metrics": overall_metrics,
        "validation_method": "expanding walk-forward; 2016-2017 training then 2018-2022 tests",
    }
    joblib.dump(model_bundle, OUTPUT_DIR / "wheat_yield_xgboost_trial_2.joblib")
    final_model.save_model(OUTPUT_DIR / "wheat_yield_xgboost_trial_2.json")
    print(f"\nTrial 2 artifacts saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
