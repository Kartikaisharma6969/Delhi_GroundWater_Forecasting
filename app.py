from __future__ import annotations

import os
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from groundwater.data import (
    LAT, LEVEL, LON, STATION, TIME, daily_series, load_observations,
    overview_insights, quality_summary, station_summary, valid_location,
)
from groundwater.forecasting import evaluate_station, forecast_station

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = os.environ.get(
    "DELHI_GW_CSV",
    str(PROJECT_ROOT / "Used dataasets" / "gwl_tel_6_hourly_delhi_sw_gw_dl_2021_2025.csv"),
)
DEFAULT_THAPAR_CSV = os.environ.get(
    "THAPAR_GW_CSV",
    str(PROJECT_ROOT / "Used dataasets" / "thapar_area_25km_2021_2025.csv"),
)
THAPAR_LAT = 30 + 21 / 60 + 24.78 / 3600
THAPAR_LON = 76 + 21 / 60 + 31.05 / 3600
THAPAR_RADIUS_KM = 25
NWIC_DATASET_URL = "https://nwdp.nwic.gov.in/dataset/ground-water-level-telemetry-hourly-delhi-surface-water-and-ground-water-departments/resource/14c48913-600c-4e2c-9c77-8ef2e92e59e6"
STATION_SUMMARY_CACHE_VERSION = 2

st.set_page_config(
    page_title="Delhi Groundwater Monitoring & Forecasting System",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
:root { --ink:#172a33; --muted:#60747d; --teal:#087f8c; --mint:#e5f4f0; --line:#dce8e8; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
@keyframes heroReveal {from {opacity:0; transform:translateY(14px) scale(.992);} to {opacity:1; transform:translateY(0) scale(1);}}
@keyframes sectionReveal {from {opacity:0; transform:translateY(10px);} to {opacity:1; transform:translateY(0);}}
@keyframes lensGlide {0% {left:0; top:2.5rem; opacity:0;} 14% {opacity:.86;} 82% {opacity:.72;} 100% {left:calc(100% - 4.35rem); top:calc(100% - 7rem); opacity:0;}}
@keyframes lensHandleGlide {0% {left:0; top:6.05rem; opacity:0;} 14% {opacity:.86;} 82% {opacity:.72;} 100% {left:calc(100% - 4.35rem); top:calc(100% - 3.45rem); opacity:0;}}
.block-container { padding-top:1.4rem; padding-bottom:2rem; max-width:1500px; }
.hero { background:linear-gradient(115deg,#0d3440,#087f8c); border-radius:18px; padding:1.7rem 2rem; color:white; margin-bottom:1rem; overflow-wrap:anywhere; animation:heroReveal .68s cubic-bezier(.2,.72,.25,1) both; }
.hero h1 {font-family:'Manrope',sans-serif; margin:0; font-size:clamp(1.75rem,4vw,2.15rem); line-height:1.14; color:white;}
.hero p {margin:.55rem 0 0; color:#d8eeee; font-size:1rem; line-height:1.55;}
.metric-card {background:#fff; border:1px solid var(--line); border-radius:14px; padding:1rem 1.1rem; min-height:112px; box-shadow:0 3px 12px #153e4a0b;}
.metric-label {font-size:.82rem; color:var(--muted); font-weight:600;}
.metric-value {font-family:'Manrope',sans-serif; font-size:1.65rem; font-weight:800; margin-top:.2rem; color:#173742;}
.metric-note {font-size:.75rem; color:var(--muted); margin-top:.15rem;}
.section-title {font-family:'Manrope',sans-serif; font-size:1.2rem; font-weight:800; margin:.5rem 0 .3rem;}
.nwic-source-card {display:block; margin:.35rem 0 .65rem; padding:1rem; border-radius:16px; color:#fff !important; text-decoration:none !important; background:linear-gradient(135deg,#0d3440 0%,#087f8c 58%,#10a58b 100%); border:1px solid #72c5bc80; box-shadow:0 8px 22px #001d2545; transition:transform .18s ease, box-shadow .18s ease;}
.nwic-source-card:hover {transform:translateY(-2px); box-shadow:0 12px 26px #001d255c; border-color:#a4eee1;}
.nwic-source-kicker {display:block; margin-bottom:.45rem; color:#b9f1e7; font-size:.67rem; font-weight:800; letter-spacing:.12em;}
.nwic-source-title {display:block; color:#fff; font-family:'Manrope',sans-serif; font-size:1.03rem; font-weight:800; line-height:1.25;}
.nwic-source-detail {display:block; margin-top:.45rem; color:#e1f8f4; font-size:.78rem; line-height:1.4;}
div[data-testid="stMetric"] {
  background:linear-gradient(135deg,#f2fbfa,#e2f3f0) !important;
  border:1px solid #79c4bb !important;
  padding:14px;
  border-radius:12px;
  box-shadow:0 4px 14px #00394320;
}
div[data-testid="stMetric"] [data-testid="stMetricLabel"],
div[data-testid="stMetric"] [data-testid="stMetricLabel"] *,
div[data-testid="stMetric"] [data-testid="stMetricValue"],
div[data-testid="stMetric"] [data-testid="stMetricValue"] *,
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
  color:#123c45 !important;
  opacity:1 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
  font-weight:700 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
  font-weight:800 !important;
}
.stTabs [data-baseweb="tab-list"] {gap:8px; max-width:100%; overflow-x:auto; flex-wrap:nowrap; scrollbar-width:thin; scrollbar-color:#79c4bb transparent;}
.stTabs [data-baseweb="tab"] {height:46px; flex:0 0 auto; position:relative; border-radius:10px 10px 0 0;padding:0 18px; white-space:nowrap; transition:background-color .2s ease, color .2s ease, transform .2s ease;}
.stTabs [data-baseweb="tab"]:hover {background:#eaf7f5; transform:translateY(-1px);}
.stTabs [data-baseweb="tab"][aria-selected="true"] {color:#087f8c !important;}
.stTabs [data-baseweb="tab"]::after {content:""; position:absolute; left:16px; right:16px; bottom:0; height:3px; border-radius:3px 3px 0 0; background:linear-gradient(90deg,#087f8c,#39b89e); transform:scaleX(0); transform-origin:center; transition:transform .24s ease;}
.stTabs [data-baseweb="tab"][aria-selected="true"]::after {transform:scaleX(1);}
.stTabs [role="tabpanel"] {position:relative; animation:sectionReveal .42s cubic-bezier(.2,.72,.25,1) both;}
.stTabs [role="tabpanel"]::before {content:""; position:absolute; z-index:9; left:0; top:2.5rem; width:4.35rem; height:4.35rem; border:1px solid #ffffffc9; border-radius:50%; background:radial-gradient(circle at 31% 27%,#ffffffa6 0%,#d9fffa72 25%,#36c4b638 67%,#087f8c1c 100%); box-shadow:0 0 0 5px #16a89520,0 0 26px #30cfbd70,inset 0 0 10px #ffffffa1; backdrop-filter:brightness(1.08) saturate(1.22); pointer-events:none; animation:lensGlide 1.12s cubic-bezier(.2,.72,.25,1) .05s both;}
.stTabs [role="tabpanel"]::after {content:""; position:absolute; z-index:8; left:0; top:6.05rem; margin-left:2.95rem; width:.62rem; height:2.15rem; border:1px solid #d8fffa; border-radius:999px; background:linear-gradient(180deg,#e9fffb,#087f8c); box-shadow:0 3px 12px #087f8c55; transform:rotate(-43deg); transform-origin:top center; pointer-events:none; animation:lensHandleGlide 1.12s cubic-bezier(.2,.72,.25,1) .05s both;}
.stTabs [data-baseweb="tab"] button p {white-space:nowrap;}
@media (max-width: 760px) {
  html, body {max-width:100%; overflow-x:hidden;}
  .block-container {width:100%; min-width:0; padding:1rem .8rem 1.5rem !important;}
  .hero {border-radius:15px; padding:1.25rem 1.1rem; margin-bottom:.75rem;}
  .hero h1 {font-size:clamp(1.6rem,6vw,2rem); line-height:1.12;}
  .hero p {font-size:.94rem; line-height:1.5;}
  .stTabs [data-baseweb="tab-list"] {gap:3px; padding-bottom:2px; -webkit-overflow-scrolling:touch;}
  .stTabs [data-baseweb="tab"] {height:44px; padding:0 .7rem;}
  .stTabs [data-baseweb="tab"] button p {font-size:.82rem;}
  .metric-card {min-height:92px; padding:.8rem .9rem;}
  .metric-value {font-size:clamp(1.15rem,5vw,1.5rem); overflow-wrap:anywhere;}
  .metric-note {line-height:1.35;}
  div[data-testid="stMetric"] {padding:10px !important; min-width:0;}
  div[data-testid="stMetric"] [data-testid="stMetricLabel"] {font-size:.8rem !important; line-height:1.3;}
  div[data-testid="stMetric"] [data-testid="stMetricValue"] {font-size:clamp(1.1rem,5vw,1.45rem) !important; line-height:1.2;}
  div[data-testid="stDataFrame"], div[data-testid="stTable"], div[data-testid="stPlotlyChart"] {max-width:100%; min-width:0;}
  div[data-testid="stDataFrame"] {overflow-x:auto;}
  .stMarkdown, .stAlert {overflow-wrap:anywhere;}
}
@media (max-width: 420px) {
  .block-container {padding-left:.65rem !important; padding-right:.65rem !important;}
  .hero {padding:1.1rem .9rem;}
  .hero h1 {font-size:1.58rem;}
  .stTabs [data-baseweb="tab"] {padding:0 .55rem;}
  .stTabs [data-baseweb="tab"] button p {font-size:.78rem;}
}
@media (prefers-reduced-motion: reduce) {
  .hero, .stTabs [role="tabpanel"] {animation:none !important;}
  .stTabs [role="tabpanel"]::before, .stTabs [role="tabpanel"]::after {display:none !important; animation:none !important;}
  .stTabs [data-baseweb="tab"], .stTabs [data-baseweb="tab"]::after, .nwic-source-card {transition:none !important;}
}
</style>
""", unsafe_allow_html=True)


def metric(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def cached_station_summaries(path: str, size: int, modified_ns: int, schema_version: int) -> pd.DataFrame:
    del schema_version
    return station_summary(load_observations(path))


@st.cache_data(show_spinner=False)
def cached_daily_series(path: str, size: int, modified_ns: int, station: str) -> pd.Series:
    frame = load_observations(path)
    return daily_series(frame, station)


@st.cache_data(show_spinner=False)
def cached_forecast(path: str, size: int, modified_ns: int, station: str):
    return forecast_station(cached_daily_series(path, size, modified_ns, station))


@st.cache_data(show_spinner=False)
def cached_evaluation(path: str, size: int, modified_ns: int, station: str):
    return evaluate_station(cached_daily_series(path, size, modified_ns, station))


@st.cache_data(show_spinner=False)
def cached_network_evaluation(path: str, size: int, modified_ns: int) -> pd.DataFrame:
    root = PROJECT_ROOT
    meta_path = root / "outputs" / "model_evaluation_metadata.json"
    result_path = root / "outputs" / "model_evaluation_by_station.csv"
    if not meta_path.exists() or not result_path.exists():
        return pd.DataFrame()
    try:
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        if (
            metadata.get("source_path") != path
            or metadata.get("source_size") != size
            or metadata.get("source_modified_ns") != modified_ns
        ):
            return pd.DataFrame()
        return pd.read_csv(result_path)
    except (OSError, ValueError, pd.errors.ParserError):
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def cached_thapar_distances(path: str, size: int, modified_ns: int) -> pd.DataFrame:
    del size, modified_ns
    frame = pd.read_csv(path, usecols=[STATION, "Distance from Thapar Campus (km)"])
    frame[STATION] = frame[STATION].astype("string").str.strip()
    return frame.groupby(STATION, as_index=False)["Distance from Thapar Campus (km)"].median()


def show_station_chart(frame: pd.DataFrame, station: str) -> None:
    subset = frame.loc[frame[STATION].eq(station)].copy()
    subset["Reading status"] = "Supplied reading"
    subset.loc[subset[LEVEL].eq(999), "Reading status"] = "999 placeholder candidate"
    subset.loc[subset[LEVEL].lt(-100), "Reading status"] = "Extreme value flagged"
    fig = px.scatter(
        subset, x=TIME, y=LEVEL, color="Reading status",
        color_discrete_map={
            "Supplied reading": "#087f8c",
            "999 placeholder candidate": "#e2a03f",
            "Extreme value flagged": "#b43b48",
        },
        title=f"Supplied six-hourly readings · {station}",
        labels={TIME: "Observation time", LEVEL: "Groundwater level (m)"},
        render_mode="webgl",
    )
    fig.update_layout(template="plotly_white", height=380, margin=dict(l=10, r=10, t=55, b=10), legend_title_text="")
    st.plotly_chart(fig, width="stretch")


st.sidebar.markdown("## Project controls")
csv_path = DEFAULT_CSV
st.sidebar.markdown(
    f'<a class="nwic-source-card" href="{NWIC_DATASET_URL}" target="_blank" rel="noopener noreferrer" aria-label="Open the Delhi groundwater telemetry dataset on the National Water Data Portal">'
    '<span class="nwic-source-kicker">OFFICIAL DATA SOURCE</span>'
    '<span class="nwic-source-title">Delhi Groundwater Telemetry</span>'
    '<span class="nwic-source-detail">Browse the National Water Data Portal record&nbsp; ↗</span>'
    '</a>',
    unsafe_allow_html=True,
)
st.sidebar.caption("The dashboard currently analyzes its bundled CSV snapshot. The card opens the NWIC source record.")

st.markdown(
    '<div class="hero"><h1>Delhi Groundwater Monitoring & Forecasting System</h1>'
    '<p>Explore telemetry coverage, station histories, data quality, and cautious seven-day forecasts.</p></div>',
    unsafe_allow_html=True,
)

if not Path(csv_path).expanduser().is_file():
    st.error("The CSV path does not exist. Enter the full path to the supplied groundwater CSV in the sidebar.")
    st.stop()

try:
    with st.spinner("Loading and indexing station observations…"):
        source = Path(csv_path).expanduser().resolve()
        source_stat = source.stat()
        cache_key = (str(source), source_stat.st_size, source_stat.st_mtime_ns)
        data = load_observations(source)
        stations = cached_station_summaries(*cache_key, STATION_SUMMARY_CACHE_VERSION)
except Exception as exc:
    st.error(f"Could not read the dataset: {exc}")
    st.stop()

quality = quality_summary(data, stations)
date_min, date_max = data[TIME].min(), data[TIME].max()
date_span = f"{date_min:%d %b %Y} – {date_max:%d %b %Y}" if pd.notna(date_min) and pd.notna(date_max) else "Unavailable"
good_for_forecast = stations.loc[stations["Usable nonzero readings"].ge(100), STATION].tolist()
all_station_names = stations[STATION].tolist()
preferred_demo_station = "New Delhi Mungeshpur Mungeshpur"
if preferred_demo_station not in good_for_forecast:
    preferred_demo_station = good_for_forecast[0] if good_for_forecast else all_station_names[0]

tabs = st.tabs(["Overview", "Station Explorer", "Forecast Lab", "Model Evaluation", "Data Quality", "Insights", "Thapar Area (Bonus)"])

with tabs[0]:
    st.markdown('<div class="section-title">Delhi monitoring network</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    with cols[0]: metric("Stations", f"{quality['stations']}", "All stations retained")
    with cols[1]: metric("Observations", f"{quality['rows']:,}", "Six-hourly telemetry rows")
    with cols[2]: metric("Coverage", date_span, "First to last timestamp")
    with cols[3]: metric("Districts", f"{quality['districts']}", "Represented in the file")
    with cols[4]: metric("Forecast-ready candidates", f"{len(good_for_forecast)}", "At least 100 usable nonzero readings")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown('<div class="section-title">Station locations</div>', unsafe_allow_html=True)
        mapped = stations.loc[stations.apply(lambda row: 6 <= row[LAT] <= 38 and 68 <= row[LON] <= 98, axis=1)].copy()
        if not mapped.empty:
            fig = px.scatter_map(
                mapped, lat=LAT, lon=LON, color="Usable nonzero readings",
                size="Observations", hover_name=STATION,
                hover_data={"District": True, "Observations": True, "Usable nonzero readings": True, LAT: False, LON: False},
                color_continuous_scale="Teal", zoom=9, height=490,
                title="Monitoring stations with valid Delhi-region coordinates",
            )
            fig.update_layout(map_style="carto-positron", margin=dict(l=0, r=0, t=45, b=0))
            st.plotly_chart(fig, width="stretch")
        st.caption(f"{len(mapped)} of {len(stations)} stations have coordinates within the Delhi-region screening bounds.")
    with right:
        st.markdown('<div class="section-title">Network coverage</div>', unsafe_allow_html=True)
        monthly = data.dropna(subset=[TIME]).assign(Month=lambda x: x[TIME].dt.to_period("M").dt.to_timestamp()).groupby("Month").size().rename("Observations").reset_index()
        fig = px.bar(monthly, x="Month", y="Observations", color_discrete_sequence=["#087f8c"], title="Records by month")
        fig.update_layout(template="plotly_white", height=270, margin=dict(l=5, r=5, t=45, b=5))
        st.plotly_chart(fig, width="stretch")
        st.markdown("**Data-led notes**")
        for insight in overview_insights(data, stations):
            st.write(f"• {insight}")
        st.info(f"{quality['all-zero stations']} stations have all-zero series. They remain part of network monitoring; the forecasting page explains why constant series cannot produce a meaningful model.")

with tabs[1]:
    station = st.selectbox("Choose a monitoring station", all_station_names, index=all_station_names.index(preferred_demo_station), key="station_explorer")
    row = stations.loc[stations[STATION].eq(station)].iloc[0]
    a, b, c, d = st.columns(4)
    with a: st.metric("District", row["District"])
    with b: st.metric("Supplied observations", f"{int(row['Observations']):,}")
    with c: st.metric("Usable nonzero readings", f"{int(row['Usable nonzero readings']):,}")
    with d: st.metric("Coverage", f"{row['First observation']:%d %b %Y} – {row['Last observation']:%d %b %Y}")
    show_station_chart(data, station)
    daily = cached_daily_series(*cache_key, station)
    if not daily.empty:
        fig = px.line(daily.rename_axis("Date").reset_index(), x="Date", y="Groundwater level (m)", title="Daily median (999 and the single value below −100 m omitted from analytical aggregation)")
        fig.update_traces(line_color="#087f8c")
        fig.update_layout(template="plotly_white", height=330, margin=dict(l=5, r=5, t=50, b=5))
        st.plotly_chart(fig, width="stretch")
        st.caption("Daily medians use available readings only. Missing calendar days are not interpolated.")
    else:
        st.warning("No readings remain after excluding 999 candidate codes and the one extreme value flagged for review.")

with tabs[2]:
    station = st.selectbox("Station to forecast", all_station_names, index=all_station_names.index(preferred_demo_station), key="forecast_station_v2")
    row = stations.loc[stations[STATION].eq(station)].iloc[0]
    st.caption("Forecast target: the station’s groundwater level seven calendar days after its latest usable observation. All 96 stations are selectable.")
    if row["All readings zero"] or int(row["Usable nonzero readings"]) < 100:
        st.warning("This station is not forecast-ready. Its complete series is zero or it has too few nonzero readings for a defensible training set. It remains visible in monitoring and quality views.")
    else:
        daily = cached_daily_series(*cache_key, station)
        forecast, message = cached_forecast(*cache_key, station)
        if message:
            st.warning(message)
        else:
            st.markdown("### Candidate model forecasts")
            st.dataframe(forecast, hide_index=True, width="stretch")
            st.caption("These are model outputs, not certainty intervals. Select the best model using the held-out chronological results below; the dashboard does not claim the forecast is reliable without that evidence.")
            context = daily.dropna().tail(120).rename_axis("Date").reset_index()
            fig = px.line(context, x="Date", y="Groundwater level (m)", title="Recent observations and seven-day-ahead candidates")
            for _, prediction in forecast.iterrows():
                fig.add_trace(go.Scatter(x=[prediction["Forecast date"]], y=[prediction["Forecast (m)"]], mode="markers+text", name=prediction["Model"], text=[prediction["Model"]], textposition="top center", marker=dict(size=11, symbol="diamond")))
            fig.update_layout(template="plotly_white", height=380, margin=dict(l=5, r=5, t=50, b=5))
            st.plotly_chart(fig, width="stretch")
    with st.expander("How this forecast is made"):
        st.write("Daily median observations are used to build lag (1, 7, 14, 28 days), trailing-average, and seasonal calendar features. A seven-day target is learned from historical examples. Forecast eligibility requires at least 100 usable observations and 60 dated training examples. The 999 candidate code and one reading below −100 m are omitted from analytical series but shown in data-quality views.")

with tabs[3]:
    station = st.selectbox("Station for model evaluation", all_station_names, index=all_station_names.index(preferred_demo_station), key="evaluation_station_v2")
    row = stations.loc[stations[STATION].eq(station)].iloc[0]
    if row["All readings zero"] or int(row["Usable nonzero readings"]) < 100:
        st.warning("This station has no useful variation or too few nonzero readings for model evaluation. It remains included in station coverage and data quality.")
    else:
        metrics, predictions, message = cached_evaluation(*cache_key, station)
        if message:
            st.warning(message)
        else:
            st.caption("Chronological holdout: earliest 80% of eligible examples for training, latest 20% for testing, with a seven-day purge so training labels are known by the first test feature date. The target is seven days after each feature date.")
            st.dataframe(metrics, hide_index=True, width="stretch")
            best = metrics.iloc[0]
            st.info(
                f"For {station}, {best['Model']} had the lowest holdout MAE "
                f"({best['MAE (m)']:.3f} m) over {int(best['Test observations'])} test targets. "
                "This result applies to this station and period only."
            )
            chosen = st.selectbox("Show actual versus predicted", metrics["Model"].tolist())
            graph = predictions.loc[predictions["Model"].eq(chosen)]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=graph["Date"], y=graph["Actual"], mode="lines+markers", name="Actual", line=dict(color="#173742")))
            fig.add_trace(go.Scatter(x=graph["Date"], y=graph["Predicted"], mode="lines+markers", name="Predicted", line=dict(color="#e2a03f")))
            fig.update_layout(template="plotly_white", title=f"{chosen}: held-out seven-day predictions", xaxis_title="Target date", yaxis_title="Groundwater level (m)", height=420)
            st.plotly_chart(fig, width="stretch")
            st.caption("MAE is average absolute error in meters; RMSE penalizes larger errors more. Compare both with persistence before interpreting performance.")
    with st.expander("Model definitions"):
        st.write("Persistence predicts the latest available daily value. Linear Regression and Random Forest use lagged levels, trailing means, and day-of-year sine/cosine features. The split follows time order; a random split is not used.")

with tabs[4]:
    st.markdown("### File-level quality indicators")
    qcols = st.columns(4)
    for index, (label, value) in enumerate([
        ("Missing timestamps", quality["missing timestamps"]),
        ("Missing level values", quality["missing levels"]),
        ("Duplicate station/times", quality["duplicate station timestamps"]),
        ("Positive intervals not 6 hours", quality["positive non-six-hour intervals"]),
        ("Zero readings", f"{quality['zero readings']:,}"),
        ("999 candidate readings", f"{quality['999 readings']:,}"),
        ("Readings below −100 m", quality["extreme below -100"]),
        ("Rows with suspect coordinates", f"{quality['invalid coordinate rows']:,}"),
        ("Stations entirely zero", quality["all-zero stations"]),
    ]):
        with qcols[index % 4]:
            st.metric(label, value)
    st.markdown("### Station-by-station coverage")
    display = stations.rename(columns={
        STATION: "Station", "Usable nonzero readings": "Nonzero readings (excluding 999)",
        "First observation": "First timestamp", "Last observation": "Last timestamp",
    })
    def status_for_station(row: pd.Series) -> str:
        flags = []
        if row["All readings zero"]:
            flags.append("ALL ZERO · forecast unavailable")
        if row["999 readings"] > 0:
            flags.append("999 CANDIDATE")
        if row.get("Extreme readings (< -100 m)", 0) > 0:
            flags.append("EXTREME VALUE")
        if not row["Has mappable coordinates"]:
            flags.append("LOCATION FLAG")
        if row["Positive non-six-hour intervals"] > 0:
            flags.append("IRREGULAR INTERVALS")
        return " · ".join(flags) if flags else "COVERAGE PRESENT · no current flags"

    display["Data status"] = stations.apply(status_for_station, axis=1).values
    def quality_cell_style(row: pd.Series) -> list[str]:
        styles = ["background-color: #edf8f7; color: #173d43;"] * len(row)
        columns = list(row.index)
        status_index = columns.index("Data status")
        status = row["Data status"]
        if "ALL ZERO" in status:
            styles[status_index] = "background-color: #fbe5e7; color: #8d2531; font-weight: 700;"
        elif "EXTREME VALUE" in status:
            styles[status_index] = "background-color: #f9dddd; color: #8d2531; font-weight: 700;"
        elif "999 CANDIDATE" in status or "LOCATION FLAG" in status:
            styles[status_index] = "background-color: #fff0d6; color: #7c4a08; font-weight: 700;"
        elif "IRREGULAR INTERVALS" in status:
            styles[status_index] = "background-color: #fff8d7; color: #705900; font-weight: 700;"
        else:
            styles[status_index] = "background-color: #dff3e8; color: #1d6544; font-weight: 700;"
        for column, color in [
            ("Zero readings", "#fff4cf"),
            ("999 readings", "#ffe7c2"),
            ("Extreme readings (< -100 m)", "#f9dddd"),
        ]:
            if column in columns and row[column] > 0:
                styles[columns.index(column)] = f"background-color: {color}; color: #6b3d12; font-weight: 700;"
        if "Has mappable coordinates" in columns and not row["Has mappable coordinates"]:
            styles[columns.index("Has mappable coordinates")] = "background-color: #fbe5e7; color: #8d2531; font-weight: 700;"
        return styles

    styled_display = (
        display.style
        .set_table_styles([
            {"selector": "th", "props": [("background-color", "#0b626c"), ("color", "#ffffff"), ("font-weight", "700"), ("border-color", "#c8dedb")]},
            {"selector": "td", "props": [("border-color", "#d6e8e5")]},
        ])
        .apply(quality_cell_style, axis=1)
    )
    st.caption("Status colors: 🔴 all-zero series or extreme reading · 🟠 999 candidate or coordinate issue · 🟡 irregular sampling · 🟢 no flags from the current screen. These colors describe review status, not the validity of groundwater measurements.")
    st.dataframe(styled_display, hide_index=True, width="stretch", height=430)
    st.download_button("Download station coverage table", display.to_csv(index=False).encode("utf-8"), "delhi_station_coverage.csv", "text/csv")
    st.info("Data policy: the dashboard preserves the supplied rows in its monitoring and quality views. The repeated 999 value and the single reading below −100 m are treated as candidate anomalies only for the analytical daily series; they are not removed from the source file. Zero readings are retained and all-zero stations are flagged.")

with tabs[5]:
    st.markdown("### Network coverage and station patterns")
    st.caption("These summaries describe data availability and observed values. They do not establish groundwater depletion, recharge, or safe pumping.")
    model_results = cached_network_evaluation(*cache_key)
    evaluated = model_results.loc[model_results["Evaluated"].eq(True)].copy() if not model_results.empty else pd.DataFrame()
    candidate_count = len(good_for_forecast)
    evaluated_count = len(evaluated)
    columns = st.columns(4)
    with columns[0]: st.metric("Stations in file", len(stations))
    with columns[1]: st.metric("Stations with all-zero series", quality["all-zero stations"])
    with columns[2]: st.metric("Forecast candidates", candidate_count, "At least 100 screened readings")
    with columns[3]: st.metric("Stations with holdout results", evaluated_count, f"out of {candidate_count} candidates")

    left, right = st.columns(2)
    with left:
        top = stations.sort_values("Usable nonzero readings", ascending=False).head(12).sort_values("Usable nonzero readings")
        fig = px.bar(top, x="Usable nonzero readings", y=STATION, orientation="h", color_discrete_sequence=["#087f8c"], title="Stations with the most screened readings")
        fig.update_layout(template="plotly_white", height=470, margin=dict(l=5, r=10, t=50, b=5), yaxis_title="")
        st.plotly_chart(fig, width="stretch")
    with right:
        coverage = px.histogram(stations, x="Calendar coverage (%)", nbins=12, color_discrete_sequence=["#3e9b88"], title="Calendar span with at least one telemetry record")
        coverage.update_layout(template="plotly_white", height=470, margin=dict(l=5, r=10, t=50, b=5), xaxis_title="Calendar span covered (%)", yaxis_title="Stations")
        st.plotly_chart(coverage, width="stretch")

    usable = data.loc[data[LEVEL].notna() & data[LEVEL].ne(0) & data[LEVEL].ne(999) & data[LEVEL].ge(-100)].copy()
    usable["Month"] = usable[TIME].dt.to_period("M").dt.to_timestamp()
    monthly_counts = usable.dropna(subset=["Month"]).groupby("Month").size().rename("Usable readings").reset_index()
    count_fig = px.line(monthly_counts, x="Month", y="Usable readings", title="Screened nonzero readings by month", markers=True, color_discrete_sequence=["#087f8c"])
    count_fig.update_layout(template="plotly_white", height=320, margin=dict(l=5, r=5, t=50, b=5))
    st.plotly_chart(count_fig, width="stretch")

    station = st.selectbox("Station for monthly pattern", good_for_forecast or all_station_names, index=(good_for_forecast or all_station_names).index(preferred_demo_station), key="insights_station_v1")
    daily = cached_daily_series(*cache_key, station)
    monthly_median = daily.dropna().resample("MS").median().rename_axis("Month").reset_index()
    if not monthly_median.empty:
        trend = px.line(monthly_median, x="Month", y="Groundwater level (m)", markers=True, title=f"Monthly median at {station}")
        trend.update_traces(line_color="#087f8c")
        trend.update_layout(template="plotly_white", height=360, margin=dict(l=5, r=5, t=50, b=5))
        st.plotly_chart(trend, width="stretch")
    else:
        st.info("No screened daily values are available for this station.")

    if evaluated_count:
        wins = evaluated["Best by MAE"].value_counts()
        model_rows = []
        for model in ["Persistence", "Linear Regression", "Random Forest"]:
            model_rows.append({
                "Model": model,
                "Stations with lowest MAE": int(wins.get(model, 0)),
                "Median station MAE (m)": float(evaluated[f"{model} MAE (m)"].median()),
                "Median station RMSE (m)": float(evaluated[f"{model} RMSE (m)"].median()),
            })
        st.markdown("### Chronological holdout results across eligible stations")
        st.dataframe(pd.DataFrame(model_rows), hide_index=True, width="stretch")
        st.caption("The medians summarize station-specific errors across stations with enough holdout examples. Each station keeps its own time-ordered train/test split.")

with tabs[6]:
    st.markdown("### Thapar-area groundwater monitoring and forecasting")
    st.caption(
        "Bonus study area: all monitoring stations within 25 km straight-line distance of Thapar Institute's published campus location in Patiala. "
        "These are surrounding-area stations, not measurements from Thapar campus wells."
    )
    st.caption(
        f"Campus reference point: {THAPAR_LAT:.6f}° N, {THAPAR_LON:.6f}° E. "
        "Location is from the [Thapar environmental compliance disclosure](https://www.thapar.edu/upload/files/Thapar%20SM%2030.09.2024.pdf)."
    )
    thapar_path = Path(DEFAULT_THAPAR_CSV).expanduser()
    if not thapar_path.is_file():
        st.warning("The Thapar-area dataset is not available. Add thapar_area_25km_2021_2025.csv to the project's Used dataasets folder.")
    else:
        try:
            with st.spinner("Loading nearby Punjab monitoring stations…"):
                thapar_source = thapar_path.resolve()
                thapar_stat = thapar_source.stat()
                thapar_cache_key = (str(thapar_source), thapar_stat.st_size, thapar_stat.st_mtime_ns)
                thapar_data = load_observations(thapar_source)
                thapar_stations = cached_station_summaries(*thapar_cache_key, STATION_SUMMARY_CACHE_VERSION)
                thapar_distances = cached_thapar_distances(*thapar_cache_key)
                thapar_stations = thapar_stations.merge(thapar_distances, on=STATION, how="left").sort_values("Distance from Thapar Campus (km)")
            thapar_quality = quality_summary(thapar_data, thapar_stations)
            thapar_date_min, thapar_date_max = thapar_data[TIME].min(), thapar_data[TIME].max()
            thapar_date_span = (
                f"{thapar_date_min:%d %b %Y} – {thapar_date_max:%d %b %Y}"
                if pd.notna(thapar_date_min) and pd.notna(thapar_date_max) else "Unavailable"
            )
            thapar_candidates = thapar_stations.loc[
                thapar_stations["Usable nonzero readings"].ge(100), STATION
            ].tolist()

            overview = st.columns(4)
            with overview[0]: st.metric("Stations within 25 km", len(thapar_stations))
            with overview[1]: st.metric("Telemetry records", f"{len(thapar_data):,}")
            with overview[2]: st.metric("Coverage", thapar_date_span)
            with overview[3]: st.metric("Forecast candidates", len(thapar_candidates), "At least 100 screened nonzero readings")

            map_stations = thapar_stations.loc[
                thapar_stations[LAT].between(6, 38) & thapar_stations[LON].between(68, 98)
            ].copy()
            if not map_stations.empty:
                map_fig = px.scatter_map(
                    map_stations, lat=LAT, lon=LON, color="Usable nonzero readings",
                    size="Observations", hover_name=STATION,
                    hover_data={
                        "District": True, "Observations": True,
                        "Usable nonzero readings": True,
                        "Distance from Thapar Campus (km)": ":.1f",
                        LAT: False, LON: False,
                    },
                    color_continuous_scale="Teal", zoom=9,
                    center={"lat": THAPAR_LAT, "lon": THAPAR_LON}, height=440,
                    title="Punjab monitoring stations around Thapar",
                )
                map_fig.update_layout(map_style="carto-positron", margin=dict(l=0, r=0, t=45, b=0))
                st.plotly_chart(map_fig, width="stretch")

            st.markdown("### Nearby station analysis")
            st.dataframe(
                thapar_stations[[STATION, "District", "Distance from Thapar Campus (km)", "Observations", "Usable nonzero readings", "First observation", "Last observation"]].rename(columns={
                    STATION: "Station", "Distance from Thapar Campus (km)": "Distance from campus (km)",
                    "Usable nonzero readings": "Usable nonzero readings (screened)",
                }),
                hide_index=True, width="stretch", height=320,
            )

            station_options = thapar_stations[STATION].tolist()
            eligible_nearby = thapar_stations.loc[thapar_stations[STATION].isin(thapar_candidates), STATION].tolist()
            default_station = eligible_nearby[0] if eligible_nearby else station_options[0]
            station = st.selectbox(
                "Station for local trend and forecast", station_options,
                index=station_options.index(default_station), key="thapar_area_station_v1",
            )
            row = thapar_stations.loc[thapar_stations[STATION].eq(station)].iloc[0]
            station_metrics = st.columns(4)
            with station_metrics[0]: st.metric("District", row["District"])
            with station_metrics[1]: st.metric("Distance from campus", f"{row['Distance from Thapar Campus (km)']:.1f} km")
            with station_metrics[2]: st.metric("Supplied observations", f"{int(row['Observations']):,}")
            with station_metrics[3]: st.metric("Usable nonzero readings", f"{int(row['Usable nonzero readings']):,}")

            show_station_chart(thapar_data, station)
            daily = cached_daily_series(*thapar_cache_key, station)
            if not daily.empty:
                monthly = daily.dropna().resample("MS").median().rename_axis("Month").reset_index()
                trend = px.line(
                    monthly, x="Month", y="Groundwater level (m)", markers=True,
                    title=f"Monthly median groundwater level · {station}",
                )
                trend.update_traces(line_color="#087f8c")
                trend.update_layout(template="plotly_white", height=340, margin=dict(l=5, r=5, t=50, b=5))
                st.plotly_chart(trend, width="stretch")
                st.caption("Daily medians retain zero readings. The existing analytical screen omits 999 and values below −100 m; the source rows remain in the area dataset.")
            else:
                st.warning("No dated readings remain for the selected station after the current analytical screen.")

            st.markdown("### Seven-day forecast and holdout evaluation")
            if int(row["Usable nonzero readings"]) < 100 or row["All readings zero"]:
                st.info("This station remains included in monitoring, but it does not meet the current forecast-candidate threshold.")
            else:
                forecast, forecast_message = cached_forecast(*thapar_cache_key, station)
                if forecast_message:
                    st.info(forecast_message)
                else:
                    st.dataframe(forecast, hide_index=True, width="stretch")
                    metrics, predictions, evaluation_message = cached_evaluation(*thapar_cache_key, station)
                    if evaluation_message:
                        st.info(f"Holdout evaluation unavailable: {evaluation_message}")
                    elif not metrics.empty:
                        best = metrics.iloc[0]
                        st.dataframe(metrics, hide_index=True, width="stretch")
                        st.caption(
                            f"Lowest holdout MAE for this station: {best['Model']} "
                            f"({best['MAE (m)']:.3f} m across {int(best['Test observations'])} test targets). "
                            "This station-specific result does not establish reliability for other wells or future periods."
                        )

            st.markdown("### Data quality review")
            qc = st.columns(4)
            with qc[0]: st.metric("Zero readings", f"{thapar_quality['zero readings']:,}")
            with qc[1]: st.metric("999 candidate readings", f"{thapar_quality['999 readings']:,}")
            with qc[2]: st.metric("Readings below −100 m", f"{thapar_quality['extreme below -100']:,}")
            with qc[3]: st.metric("Duplicate station/times", f"{thapar_quality['duplicate station timestamps']:,}")
            st.caption(
                "Values equal to 999 and readings below −100 m are treated as candidate anomalies for daily analysis. "
                "This screening rule is provisional because the source provider's measurement conventions have not been confirmed. "
                "The extracted area file retains the supplied readings."
            )
        except Exception as exc:
            st.error(f"Could not load the Thapar-area dataset: {exc}")

st.sidebar.divider()
st.sidebar.caption("Educational prototype · not an operational warning system.")
