# High-Resolution Wheat Yield Prediction System

### XGBoost + Google Earth Engine | Madhya Pradesh | 500 m Resolution

A two-stage machine learning and remote-sensing workflow for predicting wheat yield at the district level and spatially allocating those predictions to approximately 1.6 million 500 × 500 m grid cells across Madhya Pradesh.

#Note: All files were unable to be uploaded as the project is over 2 GB. Pl refer to final output and Portfolio to understand working. All code files uploaded.

## 1. Project Overview

Conventional agricultural yield statistics are generally available at the district level. District averages can hide substantial spatial variation in crop productivity.

This project addresses that limitation through a two-stage framework:

1. **District-level prediction:** An XGBoost regression model predicts wheat yield using historical yield information and seasonal environmental variables.
2. **Spatial disaggregation:** A Relative Productivity Index (RPI), calculated from local satellite-derived environmental conditions, distributes the district prediction across 500 × 500 m grid cells.

The final output is a high-resolution wheat yield map while maintaining consistency with the district-level model prediction.

## 2. Objectives

- Predict district-level wheat yield for Madhya Pradesh.
- Incorporate historical yield and environmental time-series information into a machine learning model.
- Generate a 500 × 500 m spatial grid across Madhya Pradesh.
- Estimate local environmental productivity for each grid cell.
- Calculate a Relative Productivity Index for spatial allocation.
- Produce a high-resolution wheat yield map.
- Preserve the district-level prediction when aggregating grid-level estimates.

## 3. Data Sources

### GADM
GADM administrative boundaries were used to obtain district-level boundaries for India. Madhya Pradesh districts were filtered from the national boundary dataset.

### Google Earth Engine
Google Earth Engine was used to extract seasonal environmental variables for **2015–2023**. Because wheat is a Rabi crop, the analysis considers the **November–May** growing season.

Variables:
- Mean NDVI
- Peak NDVI
- Mean EVI
- Peak EVI
- Mean Rainfall
- Mean Soil Moisture

### DESAGRI
Historical district-wise wheat agricultural statistics were obtained from the DESAGRI portal, including area, production and yield. Yield is the target variable for supervised learning.

## 4. Data Construction Pipeline

```text
GADM District Boundaries
          |
          v
Filter Madhya Pradesh
          |
          v
Google Earth Engine
2015–2023, November–May
          |
          v
Seasonal Environmental Features
NDVI | EVI | Rainfall | Soil Moisture
          |
          +----------------------+
          |                      |
          v                      v
Satellite Dataset        DESAGRI Yield Dataset
          |                      |
          +----------+-----------+
                     |
                     v
             Merge by District
                + Year
                     |
                     v
             Data Validation
                     |
                     v
          Time-Series Feature
              Engineering
                     |
                     v
          Machine Learning Dataset
                     |
                     v
               XGBoost Model
```

## 5. Feature Engineering

XGBoost is a tabular tree-based model and does not inherently understand temporal sequences. Historical features were therefore explicitly constructed.

### Historical Yield Features
- **Previous Year Yield:** Yield from the immediately preceding year.
- **Yield Lag-2:** Yield from two years earlier.
- **Yield Lag-3:** Yield from three years earlier.
- **Yield Rolling Mean 2:** Mean yield over the previous two years.
- **Yield Rolling Mean 3:** Mean yield over the previous three years.
- **Yield Rolling Std 3:** Three-year variability in yield.
- **Previous Yield Change:** Year-to-year change in yield.

### Environmental Time-Series Features
For rainfall, NDVI, peak NDVI, EVI, peak EVI and soil moisture:
- Lag-1
- Lag-2
- Rolling Mean-2
- Anomaly relative to the previous mean
- Change from the previous year

These features provide information about persistence, historical baselines, abnormal seasons and year-to-year environmental changes.

## 6. District-Level XGBoost Model

An **XGBoost Regressor** is trained using the engineered district-year dataset. The target variable is wheat yield.

XGBoost was selected because it captures nonlinear relationships and interactions, performs well on structured data, can incorporate categorical district information, provides feature-importance information, and is computationally practical for the available dataset.

## 7. Model Validation

A **walk-forward validation** strategy is used instead of randomly splitting observations.

```text
Past years  ---> Train
Future year ---> Test
```

The model is never allowed to use future observations when predicting an earlier period. This better represents real-world forecasting.

### Evaluation Metrics

- **R²:** Proportion of yield variability explained by the model.
- **RMSE:** Penalizes larger prediction errors more strongly.
- **MAE:** Average absolute prediction error.
- **MAPE:** Prediction error expressed as a percentage.

### Trial 2 Overall Walk-Forward Results

| Metric | Value |
|---|---:|
| R² | 0.4313 |
| RMSE | 0.7280 |
| MAE | 0.4930 |
| MAPE | 18.22% |

The model provides useful but imperfect decision-support estimates and is not intended to replace field-measured yield.

## 8. 500 × 500 m Grid Generation

District-level predictions do not show spatial variation within a district. Madhya Pradesh was therefore divided into **500 × 500 m grid cells** using Google Earth Engine.

The centroid of each grid cell was stored as:
- Latitude
- Longitude
- Grid ID
- District

Approximately **1.6 million grid points** were generated.

## 9. Grid-Level Environmental Features

For every grid centroid, the following variables were extracted:

- Mean NDVI
- Peak NDVI
- Mean EVI
- Peak EVI
- Mean Rainfall
- Mean Soil Moisture

These local measurements provide the environmental information required to distinguish relatively higher- and lower-productivity areas within the same district.

## 10. Relative Productivity Index

The six grid-level environmental variables are normalized so they can be combined despite having different numerical ranges.

A weighted productivity score is calculated as:

P(i) = Σ w_j × z_j(i)

where P(i) is the productivity score, w_j is the weight of environmental variable j, and z_j(i) is its normalized value at grid cell i.

### Wheat-Specific Weights

| Feature | Weight |
|---|---:|
| Peak NDVI | 0.30 |
| Mean NDVI | 0.25 |
| Peak EVI | 0.15 |
| Mean EVI | 0.10 |
| Rainfall | 0.10 |
| Soil Moisture | 0.10 |

The Relative Productivity Index is:

RPI(i) = P(i) / Mean_district(P)

This makes the district-average RPI equal to 1.

## 11. Grid-Level Yield Estimation

The district-level XGBoost prediction is allocated to individual grid cells using:

Grid Yield(i) = District Prediction × RPI(i)

Because the district-average RPI is 1:

Mean(Grid Yield) = District Prediction

Thus, the spatial allocation introduces intra-district variation without changing the district forecast on average.

## 12. Final Output

The final dataset contains grid-level predictions and spatial/productivity information, including:

- District
- Grid ID
- Latitude
- Longitude
- Grid Yield
- Predicted Yield
- Relative Productivity
- Environmental variables

The results are visualized over Madhya Pradesh district boundaries to produce the final **500 m wheat yield map**.

## 13. Interpretation

Higher predicted values represent grid cells with relatively higher productivity according to the selected environmental variables. Lower values represent relatively lower productivity.

Variation within a district represents differences in local environmental conditions. The map should be interpreted as an environmentally informed spatial allocation of the district-level model prediction.

## 14. Limitations

The current framework does not explicitly include:
- Irrigation intensity
- Fertilizer application
- Seed variety
- Pest and disease incidence
- Farm management practices
- Short-duration weather shocks

The RPI stage is an allocation mechanism rather than an independently trained grid-level yield model. Therefore, grid-level results represent relative spatial differentiation of the district prediction.

## 15. Future Improvements

Potential extensions include:
- Higher-frequency weather observations
- Irrigation and fertilizer proxies
- More precise crop masks
- Longer historical training data
- LSTM, Temporal CNN or Transformer approaches
- Grid-level uncertainty estimates
- Interactive web dashboard
- Field-level validation

## 16. Technologies Used

- **Python** — Data processing, feature engineering, machine learning and visualization
- **XGBoost** — District-level regression
- **Google Earth Engine** — Satellite/environmental data extraction and grid generation
- **GADM** — Administrative boundaries
- **Pandas / NumPy** — Data manipulation
- **Matplotlib / GeoPandas** — Visualization

## 17. Core Design Principle

The project deliberately separates **prediction** from **spatial allocation**:

```text
Historical Yield + Satellite Data
              |
              v
          XGBoost
              |
              v
     District Yield Forecast
              |
              v
    Local Satellite Conditions
              |
              v
 Relative Productivity Index
              |
              v
       500 m Grid Yield
              |
              v
     High-Resolution Map
```

This allows the model to be trained at the spatial scale where reliable historical yield labels are available while producing a substantially more spatially detailed final product.

## 18. Project Summary

The project establishes a two-stage framework combining machine learning with remote sensing. Historical district-level yield and seasonal satellite-derived environmental variables are transformed into a time-aware dataset and used to train an XGBoost regression model. The resulting district-level forecasts are then spatially disaggregated using a Relative Productivity Index calculated from local environmental conditions.

The final system produces approximately **1.6 million 500 × 500 m grid-level estimates** across Madhya Pradesh while preserving the district-level prediction on average.

The resulting map provides a higher-resolution representation of wheat productivity and demonstrates how district-level agricultural statistics can be combined with remotely sensed environmental information to create a spatially detailed decision-support product.
