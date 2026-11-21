# Project Guide for the Team

This note is a plain-language companion to the dashboard. It explains what the app does and how to discuss its choices in a presentation or viva.

## What the system does

The system reads groundwater telemetry for Delhi and makes it possible to:

1. See all 96 supplied monitoring stations on a map or in the coverage table.
2. Explore six-hourly readings and daily medians at a selected station.
3. Review missing values, duplicate timestamps, zero-heavy series, possible placeholder values, coordinate problems, and irregular sampling.
4. Compare station-level seven-calendar-day forecasts with a simple baseline.

The dashboard runs locally with Streamlit. It is an educational prototype, not an operational warning system.

## What we learned from this file

- The file has 173,132 observation rows and 21 columns.
- It covers 1 January 2021 through 14 October 2025, with 96 station names across 8 districts.
- The model uses only a small set of fields: station, agency, district, coordinates, acquisition time, and groundwater level.
- There are no duplicate station/timestamp keys in the inspected file.
- 112,496 readings (64.98%) equal zero; 65 station series contain only zeros.
- 1,319 readings equal 999; 1,318 belong to Bakhtawarpur Village.
- One reading is −847.345 m and two stations have invalid longitude coordinates.
- The CSV name and date range in the project handoff differ from the actual file. Always present the verified file statistics above.

The meanings of zero and 999 have not been confirmed with the data provider. They are therefore described as suspicious patterns or candidate codes rather than asserted to be missing-value conventions. The raw values remain available in the monitoring and quality views.

## Why all stations remain in the project

Every supplied station is available in the overview, station selector, and quality table. Forecasting eligibility is a separate question: a constant series of zeros does not provide meaningful variation for a regression model. Such stations are still monitored and their limitations are shown. A station also needs enough usable observations, dated features, and training examples before a numerical forecast is shown.

This distinction lets the project cover the whole monitoring network without pretending that every series can support a forecast.

## Forecasting in plain language

The target is a station's daily median groundwater level seven calendar days after the date used to create the input features. The process:

1. Combines each day's available six-hourly values using the median.
2. Leaves dates with no measurements empty; it does not fill them with invented observations.
3. Builds past-value features: values one, seven, fourteen, and twenty-eight days earlier.
4. Adds trailing seven- and twenty-eight-day averages and seasonal calendar features.
5. Trains on earlier examples and evaluates against a later chronological holdout, purging training labels that would not yet be known at the first test forecast origin.
6. Compares persistence, Linear Regression, and Random Forest Regression.

The dashboard omits the repeated 999 candidate code and the single reading below −100 m from the analytical daily series, but still displays them in raw data views and quality indicators. It retains zero readings and does not automatically reject negative values in the normal range.

The forecast date is seven days after the selected station's latest usable reading. Because the supplied dataset ends in 2025, a displayed forecast date can also be in 2025; it is a retrospective forecast from the available data, not a forecast from today's date.

## Results from one actual station

For New Delhi Mungeshpur Mungeshpur:

- The file has 3,852 six-hourly readings for the station.
- The daily series has 1,026 nonmissing daily medians.
- The latest usable day is 1 October 2025, so the forecast target is 8 October 2025.
- The chronological holdout contains 173 seven-day targets.

| Model | MAE | RMSE |
|---|---:|---:|
| Persistence | 0.073 m | 0.122 m |
| Linear Regression | 0.093 m | 0.144 m |
| Random Forest | 0.168 m | 0.309 m |

Persistence was strongest in this test. The network evaluation covers 30 candidate stations; 29 have enough dated examples. Persistence has the lowest MAE at 26 stations, Linear Regression at 3, and Random Forest at none. Median station MAE/RMSE are 0.0644/0.0828 m for Persistence, 0.2341/0.2589 m for Linear Regression, and 0.2223/0.3094 m for Random Forest. These values describe the evaluated periods and do not guarantee future performance.

## Terms to explain

- **Daily median:** the middle value of a station's readings for one date. It reduces the effect of a single unusually high or low reading within that day.
- **Lag feature:** an earlier observation supplied to the model, such as the value from seven days before the forecast origin.
- **Persistence baseline:** a simple comparison method that predicts the latest available daily value. A machine-learning model should be compared with it to show whether added complexity helps.
- **Chronological holdout:** the test set comes later in time than the training set. This better resembles forecasting and avoids random mixing of past and future examples.
- **MAE:** mean absolute error. It is the average size of the prediction error, in meters. Lower is better.
- **RMSE:** root mean squared error. It is also in meters, but it penalizes large misses more heavily. Lower is better.
- **Data leakage:** accidentally using information from the future while training or creating features. The feature columns here use dates at or before the forecast origin, and the split keeps later targets in the test period.

## Suggested presentation explanation

> “Our dashboard includes all stations for monitoring and data-quality review. Forecasting is offered only where the time series contains enough usable variation. We evaluate forecasts chronologically against a persistence baseline. For the Mungeshpur example, persistence had lower error than both machine-learning models, so we report that result honestly and do not claim the models work equally well across every station.”
