# Viva Preparation

## A one-minute project explanation

We developed the Delhi Groundwater Monitoring and Forecasting System as a local Streamlit dashboard for the supplied Delhi telemetry CSV. It keeps all 96 stations available for monitoring and data-quality review, shows station histories and coverage, and evaluates a seven-calendar-day target using persistence, Linear Regression and Random Forest. The test split follows time order and purges seven days at the boundary so training labels are already known before the test period. Among 29 stations with enough dated examples, persistence had the lowest MAE for 26 and Linear Regression for 3. The system is an educational prototype because the meanings of zero and 999 and the source measurement context are not confirmed.

## Likely questions and answers

### Project and data

**1. What problem does the project address?**  
It makes a large station telemetry file easier to inspect by combining station coverage, data quality, time-series exploration and measured forecast comparisons in one dashboard.

**2. What does the dataset contain?**  
The inspected file has 173,132 rows and 21 columns. It covers 96 stations in 8 districts from 1 January 2021 to 14 October 2025. The app loads seven fields needed for station-level analysis.

**3. Why do your counts differ from the synopsis?**  
The current CSV was inspected directly and contains 173,132 rows and 96 stations. The synopsis estimates of about 257,361 rows and 91 stations do not match this file, so we report the measured file values.

**4. Why include all stations if some cannot be forecast?**  
Monitoring coverage and model eligibility answer different questions. Every station remains available in the map/coverage, station selector and quality views. Forecasts need enough usable variation and dated examples.

**5. What do the zero readings mean?**  
We do not know from the supplied materials. There are 112,496 zero readings and 65 all-zero station series. We preserve zeros and identify their concentration rather than claiming they are missing or valid water-level measurements.

**6. What does 999 mean?**  
The source convention is unconfirmed. We label 1,319 values as a candidate code, keep them visible in raw and quality views, and omit them from daily analytical aggregation.

**7. Did you delete the extreme negative reading?**  
No. The source CSV is read-only and the value remains visible in the station history and quality indicators. One reading at −847.345 m is flagged and omitted from the analytical daily series pending source context.

**8. How do you handle missing dates?**  
We leave them missing. We do not interpolate or invent observations. The series is put on a daily calendar for feature creation, but blank days stay blank.

### Processing and model design

**9. Why use a daily median?**  
It produces a robust daily summary from the available six-hourly observations and reduces the influence of a single reading within that date. It does not correct missing data or settle measurement conventions.

**10. What is the forecast target?**  
The station’s daily median seven calendar days after the feature date. It is seven calendar days, not seven future rows.

**11. Which features do you use?**  
Daily lags at 1, 7, 14 and 28 days; trailing means over 7 and 28 days using prior observations; and annual sine and cosine terms for calendar seasonality.

**12. What is persistence?**  
It predicts the latest available daily level for the target seven days later. It is a simple baseline that more complex models should beat to justify added complexity.

**13. Why compare Linear Regression and Random Forest?**  
They provide a linear and a nonlinear regression candidate using the same lag, rolling and calendar features. The project keeps the model set small and explainable.

**14. Why not use a random train/test split?**  
Random splits mix earlier and later examples. A chronological split better represents forecasting because training uses earlier dates and testing uses later dates.

**15. What is the seven-day purge for?**  
Each training row has a label seven days after its feature date. Near the test boundary, that label may not have been known at the first test forecast origin. We remove those boundary rows from training.

**16. What are MAE and RMSE?**  
MAE is the average absolute prediction error. RMSE is the square root of the average squared error and penalizes large misses more. Both are in meters, and lower is better.

**17. What did your network evaluation find?**  
Thirty stations met the candidate threshold, and 29 produced enough dated examples. Persistence had the lowest MAE at 26; Linear Regression at 3; Random Forest at 0. Median station MAE values are 0.0644 m, 0.2341 m and 0.2223 m respectively.

**18. Does that prove persistence is best for every future prediction?**  
No. It summarizes these chronological holdout periods in this dataset. Performance can change across stations and future periods.

### Implementation and limitations

**19. What does Streamlit do?**  
It serves the interactive Python dashboard locally in a browser. The app has Overview, Station Explorer, Forecast Lab, Model Evaluation, Data Quality and Insights tabs.

**20. What does Plotly do?**  
It creates interactive station maps, time-series charts, coverage plots and comparisons inside the dashboard.

**21. What does Pandas do?**  
It reads selected CSV columns, parses timestamps, groups records by station, computes coverage summaries and resamples readings into daily medians.

**22. What does Scikit-learn do?**  
It fits Linear Regression and Random Forest models and calculates MAE and RMSE. The persistence prediction is implemented directly as the baseline.

**23. Does the app forecast all 96 stations?**  
All 96 can be selected and reviewed. Only stations meeting the screening and training requirements produce numerical model forecasts. One station in the network evaluation had too few dated examples after lag construction.

**24. What are the main limitations?**  
Source conventions, measurement datum and context are unavailable. Many readings are zero, and the models do not use rainfall, pumping, geology or aquifer properties. Forecast scores are station- and period-specific.

**25. Can the dashboard claim groundwater depletion or recharge?**  
No. This dataset and prototype do not establish depletion, recharge, safe pumping, groundwater volume or operational warning thresholds.

**26. What is the Thapar-area bonus scope?**  
It is a planned extension. We will inspect the separate Thapar-area CSV first and add it only after checking schema, coverage, locations and measurement comparability.

**27. Is the dashboard publicly deployed?**  
No. It currently runs locally on localhost. Public deployment would need a hosting choice, resource checks, data access review and configuration.

## Code map for the viva

- `app.py` defines the six tabs, chart rendering, station controls, styling and cached calls.
- `groundwater/data.py` defines source-field names, safe CSV loading, station summaries, data-quality counts and daily aggregation.
- `groundwater/forecasting.py` defines model features, chronological evaluation, the seven-day purge and forecast generation.
- `work/evaluate_network.py` runs the same station-level evaluation across candidate stations and writes the results CSV plus source-file metadata.

## Demonstration sequence

1. Overview: show network counts, station map and monthly records.
2. Station Explorer: select Mungeshpur and distinguish raw readings from daily medians.
3. Data Quality: explain zero, 999, the extreme reading and coordinate screening.
4. Forecast Lab: choose an eligible station and identify the forecast date and candidate models.
5. Model Evaluation: show the chronological holdout and compare MAE and RMSE with persistence.
6. Insights: explain the network results and state that they describe data coverage and forecast errors, not aquifer conditions.
