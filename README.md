# Delhi Groundwater Monitoring and Forecasting System

A local Streamlit dashboard for monitoring Delhi groundwater telemetry, exploring all supplied stations, reviewing data quality, and comparing seven-calendar-day station-level forecasts.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create an isolated environment and install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Start the dashboard:

   ```powershell
   $env:STREAMLIT_CONFIG_DIR = (Join-Path (Get-Location) '.streamlit')
   .\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
   ```

5. The default CSV is `Used dataasets/gwl_tel_6_hourly_delhi_sw_gw_dl_2021_2025.csv` in this project folder. If it is elsewhere, enter its full path in the sidebar. You can also set `DELHI_GW_CSV` before launching.

The app runs locally and opens in a browser with seven tabs: Overview, Station Explorer, Forecast Lab, Model Evaluation, Data Quality, Insights, and Thapar Area (Bonus). The raw CSVs are read only. Streamlit caches parsed copies in memory while the app process is running; changing a file's size or modified time refreshes its cache. Bind to localhost for the local demo.

## Current supplied file

The inspected file contains 173,132 rows and 21 source columns. The dashboard reads seven fields needed for station-level analysis. Its timestamps span 1 January 2021 through 14 October 2025, and it contains 96 stations across 8 districts. These observed values take precedence over earlier estimates in the project handoff.

Initial data-quality scan:

- No duplicate station/timestamp keys were found.
- Per-station coverage includes observed days, calendar coverage, typical sampling interval, and positive intervals that differ from six hours.
- 112,496 readings (64.98%) are exactly zero; 65 station series contain only zeros.
- 1,319 readings equal 999, mostly at Bakhtawarpur Village. They are treated as a placeholder candidate for analytical aggregation, while remaining visible in raw views.
- One reading is below −100 m (−847.345 m). It is flagged and omitted from analytical aggregation; the supplied raw value remains visible.
- Two stations have out-of-range longitude values, so their locations are omitted from the map but the stations remain in the dashboard.

The zero and 999 readings may reflect source-system conventions. The dashboard shows them instead of silently overwriting the input and limits forecasting to stations with sufficient nonzero history. Confirming measurement and sentinel conventions with the source provider would improve the scientific interpretation.

## Forecast method

The target is the station's daily median level seven calendar days after a feature date. Candidate models are:

- Persistence baseline: latest daily value.
- Linear Regression.
- Random Forest Regression.

Features use observations available by the feature date: 1-, 7-, 14-, and 28-day lags; trailing 7- and 28-day means; and annual sine/cosine calendar terms. Missing days are not interpolated. Evaluation uses time-ordered training and holdout periods and purges training examples whose seven-day target would fall after the first test feature date. Metrics are MAE and RMSE in meters. No confidence intervals are generated.

The network evaluation includes 30 forecast candidates; 29 have enough dated examples for a holdout. Persistence has the lowest MAE for 26 stations, Linear Regression for 3, and Random Forest for none. Median station MAE/RMSE are 0.0644/0.0828 m for Persistence, 0.2341/0.2589 m for Linear Regression, and 0.2223/0.3094 m for Random Forest. For New Delhi Mungeshpur Mungeshpur, 173 holdout targets yield MAE/RMSE of 0.073/0.122 m for Persistence, 0.093/0.144 m for Linear Regression, and 0.168/0.309 m for Random Forest. These results are station-specific and do not establish performance across future periods.

Forecasts are an educational prototype. Telemetry values, particularly the large number of zeros and repeated 999 values, require source interpretation before making operational or hydrogeological claims.

## Project layout

- `app.py`: Streamlit user interface and interactive charts.
- `groundwater/data.py`: source loading, station summaries, data-quality indicators, daily aggregation.
- `groundwater/forecasting.py`: leakage-aware features, chronological evaluation, and forecasts.
- `work/evaluate_network.py`: reproducible evaluation across forecast candidates.
- `outputs/model_evaluation_by_station.csv`: station-level holdout metrics for the active CSV.
- `outputs/Delhi_Groundwater_Project_Report.docx`: academic project report.
- `outputs/Delhi_Groundwater_Project_Presentation.pptx`: 14-slide presentation.
- `outputs/VIVA_PREPARATION.md`: viva answers and dashboard demonstration sequence.
- `requirements.txt`: Python package dependencies.
- `PROJECT_STATUS.md`: current progress and known limitations.
- `PROJECT_GUIDE.md`: plain-language project and viva explanations.

## Thapar-area bonus data

`Used dataasets/thapar_area_25km_2021_2025.csv` is a reduced subset of the supplied Punjab telemetry file. It includes all 37 stations within a 25 km straight-line radius of Thapar Institute's published Patiala campus point (30.356883° N, 76.358625° E), plus a calculated distance column. The subset contains 172,752 readings from 1 January 2021 through 22 September 2025 and is about 26 MB. The 776 MB statewide source file is not bundled in the app repository.

The bonus tab reports the subset's station coverage, maps nearby stations, explores station histories, and provides seven-day forecast candidates with chronological holdout results when a station has enough usable data. The campus point is documented in [Thapar's environmental compliance disclosure](https://www.thapar.edu/upload/files/Thapar%20SM%2030.09.2024.pdf). The app retains supplied readings in the subset. For daily analysis it screens values equal to 999 and values below −100 m as candidate anomalies; the source provider's measurement conventions have not been confirmed, so these screens are provisional.
