from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

FEATURES = ["lag_1", "lag_7", "lag_14", "lag_28", "mean_7", "mean_28", "day_of_year_sin", "day_of_year_cos"]
MIN_TRAIN_ROWS = 60
MIN_VALID_READINGS = 100
HORIZON_DAYS = 7


def _feature_frame(daily: pd.Series, horizon: int = HORIZON_DAYS) -> pd.DataFrame:
    calendar = daily.asfreq("D")
    frame = pd.DataFrame(index=calendar.index)
    for lag in (1, 7, 14, 28):
        frame[f"lag_{lag}"] = calendar.shift(lag)
    frame["mean_7"] = calendar.shift(1).rolling(7, min_periods=4).mean()
    frame["mean_28"] = calendar.shift(1).rolling(28, min_periods=14).mean()
    day = frame.index.dayofyear
    frame["day_of_year_sin"] = np.sin(2 * np.pi * day / 365.25)
    frame["day_of_year_cos"] = np.cos(2 * np.pi * day / 365.25)
    frame["target"] = calendar.shift(-horizon)
    frame["persistence"] = calendar
    return frame


def _models() -> dict[str, object]:
    return {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=160, min_samples_leaf=3, max_features=0.8,
            random_state=42, n_jobs=-1,
        ),
    }


def evaluate_station(daily: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    features = _feature_frame(daily)
    usable = features.dropna(subset=FEATURES + ["target", "persistence"]).copy()
    if len(usable) < MIN_TRAIN_ROWS + 20:
        return pd.DataFrame(), pd.DataFrame(), (
            f"Only {len(usable)} dated training examples remain after the seven-day target "
            f"and lag requirements; at least {MIN_TRAIN_ROWS + 20} are required."
        )
    split = max(MIN_TRAIN_ROWS, int(len(usable) * 0.8))
    if split >= len(usable):
        return pd.DataFrame(), pd.DataFrame(), "There is not enough history for a chronological holdout evaluation."
    test = usable.iloc[split:]
    first_test_origin = test.index.min()
    # At each test origin, training labels must already have been observed.
    # A seven-day target therefore purges training examples whose target date
    # falls after the first test feature date.
    train = usable.iloc[:split]
    train = train.loc[train.index + pd.Timedelta(days=HORIZON_DAYS) <= first_test_origin]
    if len(train) < MIN_TRAIN_ROWS:
        return pd.DataFrame(), pd.DataFrame(), (
            "The seven-day leakage gap leaves fewer than 60 training examples."
        )
    predictions_by_model = {"Persistence": test["persistence"].to_numpy()}
    for name, model in _models().items():
        model.fit(train[FEATURES], train["target"])
        predictions_by_model[name] = model.predict(test[FEATURES])
    results, predictions = [], []
    for name, values in predictions_by_model.items():
        results.append({
            "Model": name,
            "MAE (m)": mean_absolute_error(test["target"], values),
            "RMSE (m)": mean_squared_error(test["target"], values) ** 0.5,
            "Test observations": len(test),
        })
        predictions.extend(
            {"Date": date + pd.Timedelta(days=HORIZON_DAYS), "Actual": actual, "Predicted": pred, "Model": name}
            for date, actual, pred in zip(test.index, test["target"], values)
        )
    return pd.DataFrame(results).sort_values("MAE (m)"), pd.DataFrame(predictions), ""


def forecast_station(daily: pd.Series) -> tuple[pd.DataFrame, str]:
    """Fit all eligible history and predict seven days after the latest valid date."""
    if daily.dropna().nunique() < 2:
        return pd.DataFrame(), "This station has no variation in its reported values, so a meaningful forecast is unavailable."
    if daily.dropna().shape[0] < MIN_VALID_READINGS:
        return pd.DataFrame(), f"This station has fewer than {MIN_VALID_READINGS} usable readings."
    training = _feature_frame(daily).dropna(subset=FEATURES + ["target"])
    if len(training) < MIN_TRAIN_ROWS:
        return pd.DataFrame(), f"Only {len(training)} supervised examples remain; at least {MIN_TRAIN_ROWS} are required."
    last_date = daily.dropna().index.max()
    features = _feature_frame(daily, horizon=0)
    x = features.loc[[last_date], FEATURES]
    if x.isna().any(axis=None):
        return pd.DataFrame(), "Recent gaps leave too little history to calculate the forecast features."
    fitted = _models()
    for model in fitted.values():
        model.fit(training[FEATURES], training["target"])
    forecast_date = last_date + pd.Timedelta(days=HORIZON_DAYS)
    rows = [{
        "Model": "Persistence",
        "Forecast date": forecast_date,
        "Forecast (m)": float(daily.loc[last_date]),
    }]
    rows.extend([
        {"Model": name, "Forecast date": forecast_date, "Forecast (m)": float(model.predict(x)[0])}
        for name, model in fitted.items()
    ])
    return pd.DataFrame(rows), ""

