from __future__ import annotations

from pathlib import Path
import sys
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from groundwater.data import STATION, daily_series, load_observations, station_summary
from groundwater.forecasting import evaluate_station

SOURCE = ROOT / "Used dataasets" / "gwl_tel_6_hourly_delhi_sw_gw_dl_2021_2025.csv"
OUT = ROOT / "outputs" / "model_evaluation_by_station.csv"
META_OUT = ROOT / "outputs" / "model_evaluation_metadata.json"


def main() -> None:
    data = load_observations(SOURCE)
    summaries = station_summary(data)
    eligible = summaries.loc[summaries["Usable nonzero readings"].ge(100), STATION].tolist()
    records: list[dict[str, object]] = []
    for index, station in enumerate(eligible, start=1):
        daily = daily_series(data, station)
        metrics, _, message = evaluate_station(daily)
        if message:
            records.append({"Station": station, "Evaluated": False, "Reason": message})
        else:
            best = metrics.iloc[0]
            record: dict[str, object] = {
                "Station": station,
                "Evaluated": True,
                "Usable daily values": int(daily.notna().sum()),
                "Holdout targets": int(best["Test observations"]),
                "Best by MAE": best["Model"],
                "Best MAE (m)": float(best["MAE (m)"]),
            }
            for _, metric in metrics.iterrows():
                prefix = str(metric["Model"])
                record[f"{prefix} MAE (m)"] = float(metric["MAE (m)"])
                record[f"{prefix} RMSE (m)"] = float(metric["RMSE (m)"])
            records.append(record)
        print(f"{index:02d}/{len(eligible)} {station}: {message or 'evaluated'}", flush=True)
    result = pd.DataFrame(records).sort_values(["Evaluated", "Station"], ascending=[False, True])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT, index=False)
    stat = SOURCE.stat()
    META_OUT.write_text(json.dumps({
        "source_path": str(SOURCE.resolve()),
        "source_size": stat.st_size,
        "source_modified_ns": stat.st_mtime_ns,
    }, indent=2), encoding="utf-8")
    evaluated = result.loc[result["Evaluated"].eq(True)].copy()
    print(f"saved={OUT}")
    print(f"eligible={len(eligible)} evaluated={len(evaluated)} unavailable={len(result)-len(evaluated)}")
    if not evaluated.empty:
        print("best_by_station=")
        print(evaluated["Best by MAE"].value_counts().to_string())
        for model in ["Persistence", "Linear Regression", "Random Forest"]:
            mae = evaluated[f"{model} MAE (m)"]
            rmse = evaluated[f"{model} RMSE (m)"]
            print(f"{model}: median MAE={mae.median():.4f} m; median RMSE={rmse.median():.4f} m")


if __name__ == "__main__":
    main()
