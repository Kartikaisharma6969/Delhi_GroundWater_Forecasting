from pathlib import Path
import csv
import json
import math

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Used dataasets" / "gwl_tel_6_hourly_delhi_sw_gw_dl_2021_2025.csv"
OUT = ROOT / "outputs"
WORK = ROOT / "work"
RESULTS = pd.read_csv(OUT / "model_evaluation_by_station.csv")
EVAL = RESULTS[RESULTS["Evaluated"].astype(str).str.lower().eq("true")].copy()

try:
    FONT = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
    SMALL = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
    BOLD = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
except OSError:
    FONT = ImageFont.load_default()
    SMALL = FONT
    BOLD = FONT

def chart_base(title, subtitle=""):
    im = Image.new("RGB", (1500, 780), "white")
    d = ImageDraw.Draw(im)
    d.text((70, 42), title, font=BOLD, fill="#12343b")
    if subtitle:
        d.text((70, 82), subtitle, font=SMALL, fill="#536a70")
    return im, d

def save_monthly_chart():
    usecols = ["Data Acquisition Time", "Groundwater Level Telemetry 6 Hourly (meter)"]
    data = pd.read_csv(DATA, usecols=usecols, low_memory=False)
    data[usecols[0]] = pd.to_datetime(data[usecols[0]], format="%d-%m-%Y %H:%M", errors="coerce")
    level = pd.to_numeric(data[usecols[1]], errors="coerce")
    keep = level.notna() & level.ne(0) & level.ne(999) & level.ge(-100)
    month_counts = data.loc[keep].dropna(subset=usecols[:1]).groupby(data.loc[keep, usecols[0]].dt.to_period("M")).size()
    im, d = chart_base("Screened readings by month", "Supplied six-hourly records excluding zero, 999 candidate values and one value below −100 m")
    x0, y0, x1, y1 = 105, 165, 1430, 670
    d.line((x0, y0, x0, y1, x1, y1), fill="#536a70", width=2)
    if not month_counts.empty:
        values = month_counts.to_list()
        maxv = max(values) or 1
        n = len(values)
        bw = max(2, (x1-x0)//n-3)
        step = (x1-x0)/n
        for i, v in enumerate(values):
            h = (y1-y0-35) * v / maxv
            x = x0 + int(i*step)+2
            d.rectangle((x, y1-h, x+bw, y1), fill="#0a8791")
        for i in range(0, n, max(1, n//8)):
            label = str(month_counts.index[i])
            x = x0 + int(i*step)
            d.text((x-5, y1+14), label, font=SMALL, fill="#314c53")
        d.text((x0, y0-4), f"Peak month: {month_counts.idxmax()} ({maxv:,})", font=SMALL, fill="#314c53")
    d.text((x0, 715), "Month", font=SMALL, fill="#314c53")
    im.save(WORK / "monthly_screened_readings.png")

def save_model_chart():
    med = {m: float(EVAL[f"{m} MAE (m)"].median()) for m in ["Persistence", "Linear Regression", "Random Forest"]}
    im, d = chart_base("Median station holdout MAE", "29 eligible stations · seven-calendar-day target · chronological holdout · lower is better")
    x0, y0, x1, y1 = 140, 180, 1410, 640
    maximum = max(med.values()) * 1.18
    d.line((x0, y1, x1, y1), fill="#536a70", width=2)
    colors = ["#087f8c", "#4299a5", "#7bb9be"]
    for i, (model, val) in enumerate(med.items()):
        x = x0 + 115 + i*400
        h = (y1-y0)*val/maximum
        d.rectangle((x, y1-h, x+210, y1), fill=colors[i])
        d.text((x, y1-h-39), f"{val:.4f} m", font=BOLD, fill="#12343b")
        d.text((x, y1+20), model, font=FONT, fill="#314c53")
    d.text((x0, y0-25), f"Best by MAE: Persistence at 26 stations, Linear Regression at 3, Random Forest at 0", font=SMALL, fill="#314c53")
    im.save(WORK / "median_holdout_mae.png")

def save_quality_chart():
    vals = [("All-zero station series", "65 stations", "#bd5660"), ("999 candidate values", "1,319 readings", "#d78a2e"), ("Below −100 m", "1 reading", "#a53f4b"), ("Suspect coordinate records", "4,733 rows", "#c7a02b")]
    im, d = chart_base("Data-quality findings", "Counts are labeled in their own units; bar lengths are decorative and do not compare categories")
    y = 175
    for label, value, color in vals:
        d.ellipse((105,y+4,135,y+34),fill=color)
        d.text((165,y), label, font=FONT, fill="#173c43")
        d.rectangle((610,y+7,1040,y+31), fill="#e6f0ef")
        d.rectangle((610,y+7,900,y+31), fill=color)
        d.text((1110,y), value, font=FONT, fill="#173c43")
        y += 105
    im.save(WORK / "quality_findings.png")

def shade(cell, color):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    pr.append(shd)

def set_cell(cell, text, bold=False, color="17343A", size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = "Aptos"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

def table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Light Shading Accent 1"
    for i,h in enumerate(headers):
        set_cell(t.rows[0].cells[i], h, True, "FFFFFF", 9)
        shade(t.rows[0].cells[i], "0B626C")
    for row in rows:
        cells=t.add_row().cells
        for i,val in enumerate(row):
            set_cell(cells[i], val, False, "17343A", 9)
            if len(t.rows)%2==0: shade(cells[i], "EAF4F2")
    if widths:
        for row in t.rows:
            for cell,w in zip(row.cells,widths): cell.width=Inches(w)
    doc.add_paragraph()
    return t

def para(doc, text, style=None):
    p=doc.add_paragraph(style=style)
    p.paragraph_format.space_after=Pt(6)
    p.add_run(text)
    return p

def heading(doc, text, level=1):
    return doc.add_heading(text, level=level)

def figure(doc, path, caption, width=6.4):
    p=doc.add_paragraph()
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width))
    cp=doc.add_paragraph(caption)
    cp.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for r in cp.runs:
        r.italic=True; r.font.size=Pt(9); r.font.color.rgb=RGBColor(85,105,110)

def build():
    OUT.mkdir(exist_ok=True)
    save_monthly_chart(); save_model_chart(); save_quality_chart()
    q=json.loads((OUT/"model_evaluation_metadata.json").read_text(encoding="utf-8"))
    metrics=[]
    for m in ["Persistence","Linear Regression","Random Forest"]:
        metrics.append([m, f"{EVAL[f'{m} MAE (m)'].median():.4f}", f"{EVAL[f'{m} RMSE (m)'].median():.4f}"])
    wins=EVAL["Best by MAE"].value_counts().to_dict()
    doc=Document()
    sec=doc.sections[0]
    sec.top_margin=Inches(.7); sec.bottom_margin=Inches(.7); sec.left_margin=Inches(.8); sec.right_margin=Inches(.8)
    styles=doc.styles
    styles["Normal"].font.name="Aptos"; styles["Normal"].font.size=Pt(10.5); styles["Normal"].font.color.rgb=RGBColor(35,55,61)
    for name,size,color in [("Title",30,"12343B"),("Heading 1",19,"0B626C"),("Heading 2",13,"0B626C")]:
        styles[name].font.name="Aptos Display"; styles[name].font.size=Pt(size); styles[name].font.bold=True; styles[name].font.color.rgb=RGBColor.from_string(color)
    p=doc.add_paragraph(style="Title"); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run("Delhi Groundwater Monitoring and Forecasting System")
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run("Academic Project Report"); r.bold=True; r.font.size=Pt(17); r.font.color.rgb=RGBColor.from_string("087F8C")
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Data Science Foundation Laboratory\nMCA Programme\nThapar Institute of Engineering & Technology\n\nTeam members: To be completed by the students\nAcademic year: 2026–27").font.size=Pt(12)
    doc.add_page_break()

    heading(doc,"Abstract")
    para(doc,"This project develops a local interactive dashboard for monitoring historical groundwater telemetry across all stations present in a user-supplied Delhi CSV. The application combines station coverage, map visualization, data-quality review, daily station histories, seven-calendar-day forecasting, and chronological model evaluation. The inspected file contains 173,132 observations from 96 stations in 8 districts, spanning 1 January 2021 to 14 October 2025. Data screening found 112,496 zero readings, 1,319 readings equal to 999, one reading below −100 m, and coordinate issues affecting 4,733 rows. All 96 stations remain available for monitoring; 30 meet the project’s screened-reading forecast-candidate threshold, and 29 yield a chronological holdout evaluation. Across those 29 stations, persistence has the lowest MAE at 26 stations, while linear regression wins at 3. Median station MAE is 0.0644 m for persistence, 0.2341 m for linear regression, and 0.2223 m for random forest. The results support an educational monitoring prototype, not operational groundwater decisions. The meanings of zero and 999 remain unverified, and no hydrogeological depletion or recharge claim is made.")
    para(doc,"Keywords: groundwater telemetry, time-series forecasting, data quality, Streamlit, Delhi")

    heading(doc,"1 Introduction")
    para(doc,"Groundwater monitoring produces repeated measurements at distributed locations, but the records must be explored alongside their coverage and quality limitations. This project organizes the supplied Delhi station data into an interactive analytical workflow. Users can inspect the complete station network, compare time coverage, examine individual histories, and test short-horizon forecasts against simple and machine-learning baselines.")
    heading(doc,"1.1 Problem statement",2)
    para(doc,"A collection of telemetry records is difficult to interpret without station-level summaries, quality flags, consistent temporal aggregation, and time-aware evaluation. The project addresses this usability problem while avoiding unsupported interpretations of groundwater conditions.")
    heading(doc,"1.2 Objectives",2)
    for x in ["Retain every supplied station in monitoring and quality views.","Summarize timestamps, coverage, repeated values, suspect coordinates, and sampling irregularity.","Aggregate station observations to daily medians without filling missing calendar days.","Compare persistence, linear regression, and random forest for a seven-calendar-day target.","Present actual results in an interactive local dashboard and explain limitations."]:
        para(doc,x,"List Bullet")
    heading(doc,"2 Dataset")
    para(doc,"The active file is gwl_tel_6_hourly_delhi_sw_gw_dl_2021_2025.csv, supplied locally by the project team. Its filename suggests six-hourly observations; actual time differences are checked rather than assumed. Earlier synopsis estimates described approximately 257,361 rows and 91 stations, but the inspected file differs. Results in this report use the actual supplied file summarized below.")
    table(doc,["Property","Observed value"],[
        ["Observation rows","173,132"],["Source columns","21 (7 loaded for dashboard analysis)"],["Stations / districts","96 / 8"],["Timestamp range","1 Jan 2021 19:00 to 14 Oct 2025 12:00"],["Missing selected timestamps / levels","0 / 0"],["Duplicate station–timestamp keys","0"],["Rows with out-of-bounds coordinates","4,733; 94 stations pass map bounds"],
    ])
    para(doc,"The dashboard loads station, agency, district, latitude, longitude, acquisition time, and groundwater level. It reads the source file without modifying it. The source provider’s measurement and sentinel documentation was not available in the supplied materials.")

    heading(doc,"3 Data quality and preprocessing")
    para(doc,"The dashboard reports file- and station-level indicators. Positive intervals different from six hours total 3,208 across station histories. This count describes intervals between sorted timestamps and does not prove that each gap is an error. Coordinates are screened against broad Delhi-region bounds for map display; a station with suspect coordinates remains present elsewhere in the app.")
    figure(doc,WORK/"quality_findings.png","Figure 1. Selected data-quality counts. Categories use different units and should not be summed.")
    para(doc,"Exactly 112,496 readings (64.98%) are zero, and 65 station series contain only zeros. The file also has 1,319 values equal to 999, including 1,318 at Bakhtawarpur Village, and one value of −847.345 m at New Delhi Bakkarwala Bakkarwala. The dashboard labels 999 as a candidate code and flags the extreme value for review. Both remain visible in raw station histories and quality indicators. They are omitted from daily analytical aggregation; zeros are retained. These handling rules are transparent but should be revisited when the source defines the values.")
    para(doc,"Daily values use the median of available readings for each station and calendar date. Empty dates remain missing. The analytical series omits 999 candidate values and readings below −100 m, while preserving the original CSV. This screening is a cautious prototype decision, not confirmation that the source values are invalid.")

    heading(doc,"4 Exploratory analysis")
    para(doc,"The dashboard provides station mapping, monthly telemetry coverage, station observation histories, daily medians, and station comparisons. The following monthly chart counts nonzero values after excluding 999 and readings below −100 m. It reflects the supplied record count by month and is not a measure of groundwater volume or a complete sampling-rate correction.")
    figure(doc,WORK/"monthly_screened_readings.png","Figure 2. Monthly screened telemetry records across the network. Gaps and changes in counts describe availability, not aquifer change.")
    para(doc,"The Insights tab displays the stations with the largest number of screened readings, a distribution of station calendar coverage, monthly screened counts, and the selected station’s monthly median. All stations remain visible in station selection and coverage summaries. Forecast eligibility is presented separately from network inclusion.")

    heading(doc,"5 Forecasting methodology")
    para(doc,"The target is a station’s daily median groundwater level seven calendar days after the feature date. The feature set contains values at lags of 1, 7, 14, and 28 days, trailing 7- and 28-day means calculated from prior observations, and annual sine/cosine calendar terms. No missing days are interpolated. Candidate models are persistence, linear regression, and random forest regression. Persistence predicts the value at the feature date.")
    para(doc,"For station-specific evaluation, eligible examples are ordered by feature date and divided into an earlier training segment and a later test segment. A seven-day purge prevents training labels whose target date falls after the first test feature date from entering model fitting. Metrics are calculated on a common chronological test set for each station. The network evaluation includes stations with at least 100 screened nonzero readings; stations that cannot produce at least 60 dated training examples and 20 test examples after lag and horizon construction are marked unavailable.")
    para(doc,"MAE reports the mean absolute difference between predicted and observed values in meters. RMSE also uses meters and gives larger errors greater influence. Lower values indicate smaller errors for that station and test period. The app does not generate confidence intervals.")

    heading(doc,"6 Results")
    table(doc,["Model","Median station MAE (m)","Median station RMSE (m)","Stations with lowest MAE"],[
        [m, f"{EVAL[f'{m} MAE (m)'].median():.4f}", f"{EVAL[f'{m} RMSE (m)'].median():.4f}",str(int(wins.get(m,0)))] for m in ["Persistence","Linear Regression","Random Forest"]
    ])
    figure(doc,WORK/"median_holdout_mae.png","Figure 3. Median of station-level chronological holdout MAE. Each station contributes one metric.")
    para(doc,"Thirty stations pass the candidate threshold. Twenty-nine have enough dated examples for model evaluation; New Delhi Hiranki Hiranki 13500 has only 49 examples after target and lag construction and is unavailable under the stated minimum. Persistence has the lowest MAE for 26 evaluated stations; linear regression has the lowest MAE for 3; random forest has the lowest for none. The model medians summarize station errors and do not imply identical station behavior.")
    para(doc,"The dashboard’s live Forecast Lab fits candidate models to the chosen station’s eligible history and shows predictions seven calendar days after the latest usable observation. Since the file ends in October 2025, the displayed date is retrospective relative to the current project date. A forecast is a model output, not a warning or certainty interval.")

    heading(doc,"7 System architecture and implementation")
    table(doc,["Component","Responsibility"],[
        ["app.py","Streamlit tabs, controls, metrics, Plotly charts, tables and downloads"],["groundwater/data.py","Selected-field loading, caching, station summaries, quality indicators, daily medians"],["groundwater/forecasting.py","Seven-day features, persistence baseline, regression models, evaluation and forecasts"],["work/evaluate_network.py","Reproducible per-station evaluation CSV and source-file metadata"],["outputs/","Station evaluation results and academic deliverables"],
    ])
    para(doc,"The app is built with Python, Pandas, NumPy, Scikit-learn, Plotly, and Streamlit. It runs on localhost. The source path can be changed in the sidebar, and cached results use file path, size, and modification time. The six dashboard tabs are Overview, Station Explorer, Forecast Lab, Model Evaluation, Data Quality, and Insights.")

    heading(doc,"8 Limitations and ethical interpretation")
    for x in [
        "The source provider and measurement conventions for zero, 999, units, and datum are not established in the supplied project materials.",
        "A high share of zero readings limits the set of series with usable nonzero variation; all-zero station series cannot support meaningful regression forecasts.",
        "One extreme reading is flagged and omitted from analytical daily aggregation pending review; its measurement context is unknown.",
        "The simple candidate models use univariate station histories and calendar features. They do not include rainfall, pumping, geology, land use, or aquifer properties.",
        "Metrics are station- and period-specific. A network median does not validate operational use or guarantee future performance.",
        "The dashboard is an educational prototype. It does not infer depletion, recharge, safe pumping, groundwater volume, or risk thresholds.",
        "The Thapar-area bonus section is not included because its separate dataset has not yet been analyzed.",
    ]: para(doc,x,"List Bullet")

    heading(doc,"9 Future scope")
    for x in [
        "Obtain source documentation for units, datum, missing-value codes, zero values, and station metadata.",
        "Add the Thapar-area dataset after verifying its schema, geographic coverage, date range, and measurement comparability.",
        "Test rolling-origin evaluation and additional seasonal baselines after the core pipeline is reviewed.",
        "Add user-selectable date ranges and explicit coverage statistics for each selected station.",
        "Deploy to a managed hosting platform only after data rights, configuration, and resource requirements are established.",
    ]: para(doc,x,"List Bullet")

    heading(doc,"10 Conclusion")
    para(doc,"The project delivers an interactive local monitoring and forecasting prototype using all 96 stations in the supplied Delhi file. It pairs station histories and data-quality findings with a seven-day evaluation that includes a persistence baseline and a leakage-aware chronological split. In the evaluated subset, persistence performed best by MAE for most stations. The implementation makes uncertainty about source codes and measurement context visible and keeps its claims within the evidence available from this telemetry file.")

    heading(doc,"References")
    refs=[
        "Project team. User-supplied CSV: gwl_tel_6_hourly_delhi_sw_gw_dl_2021_2025.csv. Local project copy. Original provider metadata was not included.",
        "Pandas documentation. Series.resample. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.resample.html",
        "Scikit-learn documentation. mean_absolute_error. https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html",
        "Scikit-learn documentation. RandomForestRegressor. https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html",
        "Streamlit documentation. https://docs.streamlit.io/",
    ]
    for x in refs: para(doc,x,"List Number")
    docx=OUT/"Delhi_Groundwater_Project_Report.docx"
    doc.save(docx)
    print(json.dumps({"report":str(docx),"figures":[str(WORK/x) for x in ["quality_findings.png","monthly_screened_readings.png","median_holdout_mae.png"]],"source_size":q["source_size"]},indent=2))

if __name__=="__main__": build()
