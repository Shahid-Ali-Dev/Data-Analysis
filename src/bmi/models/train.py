from __future__ import annotations
import mlflow
import optuna
import duckdb
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.model_selection import TimeSeriesSplit
from lightgbm import LGBMRegressor
from bmi.utils.config import SETTINGS

FEATURES = ["doy","dow","month","lag1","lag7","lag14","r7","r14","arrivals_tonnes","delta"]

def load_data():
    con = duckdb.connect(str(SETTINGS.duckdb_path))
    df = con.execute("SELECT * FROM features ORDER BY date").df()
    df = df.dropna(subset=["lag1","lag7","lag14","r7","r14"]).copy()
    return df

def objective(trial, X, y):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 200, 1200),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_samples": trial.suggest_int("min_child_samples", 10, 100),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.0, 5.0),
        "random_state": 42,
    }
    model = LGBMRegressor(**params)
    tscv = TimeSeriesSplit(n_splits=5)
    mape_scores = []
    for tr_idx, va_idx in tscv.split(X):
        model.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        pred = model.predict(X.iloc[va_idx])
        mape_scores.append(mean_absolute_percentage_error(y.iloc[va_idx], pred))
    return np.mean(mape_scores)

def train_for_h(horizon: int = 7):
    df = load_data()
    y = df[f"target_h{horizon}"]
    X = df[FEATURES]
    mask = ~y.isna()
    X, y = X[mask], y[mask]

    mlflow.set_tracking_uri(SETTINGS.mlflow_uri)
    mlflow.set_experiment(f"BMI-PriceForecast-H{horizon}")
    with mlflow.start_run():
        study = optuna.create_study(direction="minimize")
        study.optimize(lambda tr: objective(tr, X, y), n_trials=int(SETTINGS.config["training"]["optuna_trials"]))
        best_params = study.best_params

        model = LGBMRegressor(**best_params, random_state=42)
        model.fit(X, y)
        pred = model.predict(X)
        mape = mean_absolute_percentage_error(y, pred)

        mlflow.log_params(best_params)
        mlflow.log_metric("mape_in_sample", float(mape))
        mlflow.sklearn.log_model(model, artifact_path="model")

        print(f"H{horizon} trained. In-sample MAPE: {mape:.3f}")
    return True

if __name__ == "__main__":
    for h in SETTINGS.config["defaults"]["horizons"]:
        train_for_h(horizon=h)
