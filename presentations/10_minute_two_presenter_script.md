# 10-minute presentation script

**Presenter 1:** Slides 1–5, about 5 minutes  
**Presenter 2:** Slides 6–10, about 5 minutes

## Presenter 1

### Slide 1 — Delhi Groundwater Monitoring and Forecasting System · 0:25

Good morning. We are presenting our Delhi Groundwater Monitoring and Forecasting System, developed as an MCA Data Science Foundation project. It turns six-hourly station telemetry into a dashboard for network coverage, station history, data quality, and cautious seven-day forecasts. We will show what the data supports, how the models were evaluated, and where interpretation needs care.

### Slide 2 — Project problem and objective · 0:55

Telemetry files are large, and stations can have very different coverage. Looking at one well alone would miss the network context. The dashboard keeps all 96 supplied Delhi stations in monitoring and quality views, then makes forecasts only for series with enough usable data. The aim is not to issue an operational warning. It is to make the observations, screening decisions, and model comparisons easier to inspect.

### Slide 3 — Delhi telemetry at a glance · 1:05

The current Delhi CSV contains 173,132 records across 96 stations and eight districts. Its timestamps begin on 1 January 2021 and end on 14 October 2025. The source describes six-hourly telemetry, while station-level checks identify irregular intervals in the supplied records. We use the actual file dimensions here, rather than the earlier approximate figures in the synopsis. All stations remain available in the monitoring views, including stations that are not eligible for forecasting.

### Slide 4 — Data quality decisions · 1:10

The file has a high share of exact-zero readings: 112,496, or 64.98 percent. We retain them in monitoring and flag all-zero stations so they do not become misleading forecast candidates. The repeated value 999 is treated as a candidate placeholder for daily analysis, and one value below minus 100 metres is screened from the analytical series. The original records remain available. We found no duplicate station and timestamp keys. These are transparent screening rules, not a claim that the provider confirmed the physical meaning of zero or 999.

### Slide 5 — Analysis pipeline · 1:25

This is the path from source file to dashboard. The loader reads only the fields needed for station analysis and caches the parsed file by its identity. We profile data quality before aggregation. For each station, available readings are summarized to a daily median; missing calendar days are not interpolated. The forecasting module builds a seven-day target, trains candidate models, and evaluates them using later dates. Streamlit presents those outputs in interactive views. The source data stays unchanged, and screening applies to analytical series only.

**Handoff:** “I’ll hand over to Presenter 2 to explain the forecast design and what the evaluation found.”

## Presenter 2

### Slide 6 — Forecast design and evaluation · 1:10

The target is the station's daily median level seven calendar days after a feature date. The features use observations available at that date: lags at 1, 7, 14, and 28 days, trailing means, and annual calendar terms. We compare Persistence, Linear Regression, and Random Forest. Evaluation is chronological. Earlier examples are used for training and later examples for testing. A seven-day purge removes training cases whose targets would not yet have been observed at the first test feature date. We report MAE and RMSE. Missing calendar days are not filled, and the dashboard does not display made-up confidence intervals.

### Slide 7 — Evaluation favors the persistence baseline · 1:30

Across 29 evaluated Delhi stations, Persistence had the lowest MAE at 26. Linear Regression was best at three. Random Forest was not best at any of the 29 stations. One of the 30 forecast candidates did not have enough dated examples for holdout evaluation. The honest result is that the simple baseline performed best most often. We do not claim machine learning improved the forecasts. For New Delhi Mungeshpur Mungeshpur, the holdout contains 173 test targets. Its MAE was 0.073 metres for Persistence, 0.093 for Linear Regression, and 0.168 for Random Forest. These figures describe this station and test period only.

### Slide 8 — Dashboard components · 1:05

The dashboard brings the analysis into seven areas. Overview summarizes the network and map. Station Explorer shows supplied observations and the station's daily history. Forecast Lab presents seven-day candidates. Model Evaluation compares actual and predicted test values with MAE and RMSE. Data Quality exposes coverage and flagged records. Insights summarizes network patterns. The Thapar Area tab adds a bounded regional bonus study. All Delhi stations remain visible in monitoring and quality pages. A station that is not forecast-ready is still part of the network; the interface explains why its forecast is unavailable.

### Slide 9 — Thapar-area bonus study · 0:55

For a regional bonus, we filtered the supplied statewide Punjab CSV to stations within a 25-kilometre straight-line radius of Thapar's published Patiala campus point. The app-ready subset contains 37 stations and 172,752 records, from 1 January 2021 to 22 September 2025. The closest supplied stations are two Krishi Vigyan Kendra sensors at about 3.85 and 4.02 kilometres. The source file has no station named Thapar and no measurement identified as an on-campus well. These stations are regional context, not a substitute for campus groundwater monitoring.

### Slide 10 — Interpretation and next steps · 0:20

To conclude, this prototype makes the supplied station data easier to monitor and compare. Its forecasts are educational and station-specific. Before making stronger hydrogeological interpretations, we need source confirmation for measurement conventions and direct campus measurements if they become available. Thank you.

## Source notes

- Delhi telemetry resource record: https://nwdp.nwic.gov.in/dataset/ground-water-level-telemetry-hourly-delhi-surface-water-and-ground-water-departments/resource/14c48913-600c-4e2c-9c77-8ef2e92e59e6
- Thapar campus location: https://www.thapar.edu/upload/files/Thapar%20SM%2030.09.2024.pdf
- Project calculations: `groundwater/data.py`, `groundwater/forecasting.py`, and `outputs/model_evaluation_by_station.csv`.
