# Project Status

## Current phase

MVP, network evaluation, project documentation, report, presentation, and viva preparation are complete for the supplied Delhi CSV. The dashboard is running locally; public deployment and the Thapar-area extension remain future work.

## Completed

- Inspected the supplied CSV schema and full record coverage.
- Confirmed 173,132 rows, 96 stations, 8 districts, and timestamps from 2021-01-01 to 2025-10-14.
- Confirmed no duplicate station/timestamp keys.
- Identified zero-only stations, repeated 999 values, one extreme low reading, and two invalid coordinate groups.
- Added a read-only data loader with a process-level cache keyed by file size and modified time.
- Added Streamlit caches for station summaries, daily series, forecasts, and model evaluation keyed to the source-file version.
- Added station coverage and quality summaries.
- Added per-station day coverage and positive non-six-hour interval counts.
- Added a plain-language project guide and a viva question-and-answer guide with verified data facts and a dashboard demonstration sequence.
- Added all-station overview, station history, map, coverage chart, forecast lab, model evaluation, data-quality, and insights dashboard tabs.
- Added persistence, Linear Regression, and Random Forest methods for a seven-calendar-day target.
- Added chronological holdout evaluation with MAE/RMSE and a seven-calendar-day purge at the train/test boundary so training labels are known at the first test feature date.
- Included the persistence baseline in forecast outputs and show the lowest-MAE model for the selected station.
- Added local setup instructions.
- Installed the project dependencies in a local .venv.
- Launched the local Streamlit app and visually confirmed the overview, station map, and monthly coverage chart render in the browser.
- Bound the retained demo session to localhost and redirected Streamlit configuration into the project folder.
- Evaluated 30 network forecast candidates; 29 produced enough dated examples. Persistence has the lowest MAE at 26 evaluated stations, Linear Regression at 3, and Random Forest at none.
- Added an academic report with actual dataset statistics, model results, tables, and three generated data figures.
- Added a 14-slide presentation and visually reviewed its rendered slides.
- Added a viva guide with 27 likely questions and answers.
- Added a Thapar-area bonus dashboard tab with a 25 km station map, station-level monitoring, data-quality indicators, seven-day forecast candidates, and chronological holdout evaluation.
- Filtered the Punjab source into a 37-station, 172,752-row app-ready subset spanning 1 January 2021 through 22 September 2025; the original statewide CSV remains outside the repository.
- Fixed the missing NumPy import in station summaries and guarded the status table against a missing extreme-reading column.
- Confirmed the Streamlit app responds at `http://127.0.0.1:8502/` with HTTP 200.

## Data decisions in the current MVP

- Every station remains in the dashboard and station tables.
- Zero readings remain visible. Stations whose entire series is zero are not presented as forecast-ready.
- The repeated value 999 is flagged as a candidate placeholder and omitted from analytical daily aggregation.
- The lone reading below −100 m is flagged and omitted from analytical daily aggregation.
- Suspect coordinates suppress only map placement, not the station record.
- No missing calendar days are interpolated.

## Pending

- Confirm with the dataset source what zero and 999 represent, if possible.
- Confirm Punjab telemetry conventions for 999 and readings below −100 m before interpreting them as placeholders or invalid values.
- Publicly deploy only after hosting, resource, and data access requirements are decided.

## Known limitations

- Streamlit and Plotly are installed in the project-local .venv; the app is intended to run locally and is not publicly deployed.
- The supplied file differs from earlier handoff estimates (173,132 rows / 96 stations; the handoff mentioned about 257,361 / 91).
- A high share of zeros and one station dominated by 999 limit the scientifically defensible forecast population.
- Model metrics are station-specific and should not be generalized to all Delhi stations.
- Word or LibreOffice is not installed in this environment, so the DOCX report could not be rendered to page images for visual layout review. Its structure, tables, and embedded figures were generated and checked programmatically.
- The slides use actual evaluation results and editable shapes, but do not include a live dashboard screenshot because browser screenshot automation was unavailable in this session.
