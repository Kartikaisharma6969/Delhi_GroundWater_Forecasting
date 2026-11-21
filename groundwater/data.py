from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
import numpy as np

STATION = "Station"
TIME = "Data Acquisition Time"
LEVEL = "Groundwater Level Telemetry 6 Hourly (meter)"
LAT = "Latitude"
LON = "Longitude"
SOURCE_COLUMNS = [STATION, "Agency", "District", LAT, LON, TIME, LEVEL]


@lru_cache(maxsize=3)
def _read_source(path: str, size: int, modified_ns: int) -> pd.DataFrame:
    """Read only fields used by the dashboard; cache by file identity."""
    del size, modified_ns
    frame = pd.read_csv(path, usecols=SOURCE_COLUMNS, low_memory=False)
    frame[TIME] = pd.to_datetime(frame[TIME], format="%d-%m-%Y %H:%M", errors="coerce")
    frame[LEVEL] = pd.to_numeric(frame[LEVEL], errors="coerce")
    frame[STATION] = frame[STATION].astype("string").str.strip()
    return frame


def load_observations(path: str | Path) -> pd.DataFrame:
    source = Path(path).expanduser().resolve()
    stat = source.stat()
    return _read_source(str(source), stat.st_size, stat.st_mtime_ns).copy()


def valid_location(frame: pd.DataFrame) -> pd.Series:
    return frame[LAT].between(6, 38) & frame[LON].between(68, 98)


def station_summary(frame: pd.DataFrame) -> pd.DataFrame:
    summaries = []
    for station, group in frame.groupby(STATION, sort=True, dropna=False):
        levels = group[LEVEL]
        usable = levels.notna() & levels.ne(0) & levels.ne(999) & levels.ge(-100)
        timestamps = group[TIME].dropna().sort_values()
        gaps = timestamps.diff().dt.total_seconds().div(3600).dropna()
        days = timestamps.dt.normalize().nunique()
        calendar_days = (timestamps.max().normalize() - timestamps.min().normalize()).days + 1 if len(timestamps) else 0
        summaries.append({
            STATION: station,
            "District": group["District"].dropna().mode().iat[0] if group["District"].notna().any() else "Unknown",
            "Agency": group["Agency"].dropna().mode().iat[0] if group["Agency"].notna().any() else "Unknown",
            LAT: group[LAT].median(),
            LON: group[LON].median(),
            "Observations": len(group),
            "First observation": group[TIME].min(),
            "Last observation": group[TIME].max(),
            "Observation days": int(days),
            "Calendar coverage (%)": round(days / calendar_days * 100, 1) if calendar_days else 0.0,
            "Typical interval (hours)": float(gaps.mode().iat[0]) if not gaps.empty else np.nan,
            "Positive non-six-hour intervals": int((gaps.gt(0) & gaps.ne(6)).sum()),
            "Zero readings": int(levels.eq(0).sum()),
            "999 readings": int(levels.eq(999).sum()),
            "Extreme readings (< -100 m)": int(levels.lt(-100).sum()),
            "Usable nonzero readings": int(usable.sum()),
            "All readings zero": bool(levels.notna().any() and levels.fillna(0).eq(0).all()),
            "Has mappable coordinates": bool(valid_location(group).all()),
        })
    return pd.DataFrame(summaries)


def daily_series(frame: pd.DataFrame, station: str) -> pd.Series:
    """Daily median for one station; retain zeros and omit 999 candidate codes."""
    selected = frame.loc[frame[STATION].eq(station), [TIME, LEVEL]].dropna()
    # Keep every supplied value in the raw monitoring table. For analytical
    # aggregation, omit the repeated 999 code and the single physically
    # implausible reading below -100 m; both remain visible in quality views.
    selected = selected.loc[selected[LEVEL].ne(999) & selected[LEVEL].ge(-100)].copy()
    if selected.empty:
        return pd.Series(dtype=float, name="Groundwater level (m)")
    daily = selected.set_index(TIME)[LEVEL].resample("D").median()
    daily.name = "Groundwater level (m)"
    return daily


def quality_summary(frame: pd.DataFrame, summaries: pd.DataFrame | None = None) -> dict[str, int | float]:
    repeated = frame.duplicated([STATION, TIME], keep="first")
    location_bad = ~valid_location(frame)
    if summaries is None:
        summaries = station_summary(frame)
    non_six_hour = int(summaries["Positive non-six-hour intervals"].sum())
    return {
        "rows": int(len(frame)),
        "stations": int(frame[STATION].nunique()),
        "districts": int(frame["District"].nunique()),
        "missing timestamps": int(frame[TIME].isna().sum()),
        "missing levels": int(frame[LEVEL].isna().sum()),
        "duplicate station timestamps": int(repeated.sum()),
        "positive non-six-hour intervals": non_six_hour,
        "zero readings": int(frame[LEVEL].eq(0).sum()),
        "999 readings": int(frame[LEVEL].eq(999).sum()),
        "extreme below -100": int(frame[LEVEL].lt(-100).sum()),
        "invalid coordinate rows": int(location_bad.sum()),
        "all-zero stations": int(summaries["All readings zero"].sum()),
    }


def overview_insights(frame: pd.DataFrame, summaries: pd.DataFrame) -> list[str]:
    zero_pct = frame[LEVEL].eq(0).mean() * 100 if len(frame) else 0
    nonzero_stations = int(summaries["Usable nonzero readings"].gt(0).sum())
    date_min, date_max = frame[TIME].min(), frame[TIME].max()
    items = [
        f"The file contains {len(summaries)} monitoring stations; {nonzero_stations} have at least one nonzero reading after the current candidate-anomaly screen.",
        f"{zero_pct:.1f}% of supplied readings are exactly zero. The dashboard retains them and flags stations whose entire series is zero.",
    ]
    if pd.notna(date_min) and pd.notna(date_max):
        items.append(f"Available timestamps run from {date_min:%d %b %Y} to {date_max:%d %b %Y}.")
    return items

