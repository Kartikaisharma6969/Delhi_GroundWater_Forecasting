import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const runtimeModules = process.env.RUNTIME_NODE_MODULES;
if (!runtimeModules) throw new Error("RUNTIME_NODE_MODULES must point to the supplied workspace runtime.");
const runtimeRequire = createRequire(path.join(runtimeModules, "__deck_builder__.cjs"));
const { Presentation, PresentationFile } = runtimeRequire("@oai/artifact-tool");

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const outputDir = path.join(root, "presentations");
const tempDir = path.join(root, "work", "deck_tmp");
const draftPath = path.join(tempDir, "Delhi_Groundwater_Showcase_draft.pptx");
const finalPath = path.join(outputDir, "Delhi_Groundwater_Monitoring_Showcase_10min.pptx");
const previewDir = path.join(tempDir, "renders");

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(tempDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const W = 1280;
const H = 720;
const FONT = "Arial";
const C = {
  navy: "#102235",
  navyDeep: "#0B1926",
  ink: "#172A38",
  body: "#314857",
  muted: "#617684",
  teal: "#087F8C",
  tealLight: "#31B8AC",
  aqua: "#DDF3F0",
  paper: "#F5F8FA",
  white: "#FFFFFF",
  line: "#D9E4E9",
  gold: "#D8992E",
  red: "#B8474B",
};

function text(slide, name, value, left, top, width, height, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    typeface: FONT,
    fontSize: `${style.size ?? 18}pt`,
    color: style.color ?? C.ink,
    bold: style.bold ?? false,
    alignment: style.align ?? "left",
    verticalAlignment: style.valign ?? "top",
    wrap: "square",
    autoFit: "none",
    insets: style.insets ?? 0,
  };
  return shape;
}

function rect(slide, name, left, top, width, height, fill, line = "none", radius = 0) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    name,
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 },
    ...(radius ? { borderRadius: radius } : {}),
  });
}

function header(slide, title, section, dark = false) {
  text(slide, "section-label", section.toUpperCase(), 74, 46, 600, 22, {
    size: 11, bold: true, color: dark ? "#79D9CE" : C.teal,
  });
  text(slide, "slide-title", title, 74, 82, 1128, 62, {
    size: 34, bold: true, color: dark ? C.white : C.navy,
  });
}

function footer(slide, page, dark = false) {
  const color = dark ? "#B4C4CE" : C.muted;
  text(slide, "footer-project", "DELHI GROUNDWATER MONITORING AND FORECASTING SYSTEM", 74, 678, 850, 18, {
    size: 9.5, bold: true, color,
  });
  text(slide, "footer-page", `${page} / 10`, 1124, 678, 80, 18, {
    size: 10, bold: true, color, align: "right",
  });
}

function notes(slide, content) {
  slide.speakerNotes.text = content;
  slide.speakerNotes.setVisible(true);
}

function newSlide(presentation, bg = C.paper) {
  const slide = presentation.slides.add({ width: W, height: H });
  slide.background.fill = bg;
  return slide;
}

const deck = Presentation.create({ slideSize: { width: W, height: H } });

// 1. Cover
{
  const slide = newSlide(deck, C.navyDeep);
  text(slide, "cover-kicker", "MCA DATA SCIENCE FOUNDATION PROJECT", 82, 80, 850, 26, {
    size: 13, bold: true, color: "#78D6CC",
  });
  text(slide, "cover-title", "Delhi Groundwater\nMonitoring and Forecasting System", 82, 160, 1040, 180, {
    size: 40, bold: true, color: C.white,
  });
  text(slide, "cover-subtitle", "Station telemetry, data quality, and seven-day forecasts", 84, 372, 930, 42, {
    size: 22, color: "#D5E7EC",
  });
  text(slide, "cover-institution", "Thapar Institute of Engineering and Technology", 84, 504, 850, 30, {
    size: 17, color: "#B6C9D2",
  });
  text(slide, "cover-time", "A 10-minute presentation for two presenters", 84, 551, 690, 28, {
    size: 15, bold: true, color: "#78D6CC",
  });
  footer(slide, 1, true);
  notes(slide, `PRESENTER 1 · 0:25 · OPENING\n\nGood morning. We are presenting our Delhi Groundwater Monitoring and Forecasting System, developed as an MCA Data Science Foundation project. It turns six-hourly station telemetry into a dashboard for network coverage, station history, data quality, and cautious seven-day forecasts. We will show what the data supports, how the models were evaluated, and where interpretation needs care.\n\nSource: Project synopsis and supplied Delhi groundwater telemetry dataset, 2021–2025.`);
}

// 2. Problem and objective
{
  const slide = newSlide(deck);
  header(slide, "Project problem and objective", "01  Project purpose");
  text(slide, "problem-statement", "Groundwater telemetry is useful only when station coverage, data quality, and forecast performance can be explored together.", 84, 178, 1080, 112, {
    size: 27, bold: true, color: C.navy,
  });
  rect(slide, "purpose-rule", 84, 315, 70, 5, C.teal);
  text(slide, "purpose-one", "Monitor the supplied Delhi network across all stations.", 84, 352, 1030, 38, {
    size: 21, color: C.body,
  });
  text(slide, "purpose-two", "Inspect historical observations and data-quality flags without changing source records.", 84, 414, 1030, 55, {
    size: 21, color: C.body,
  });
  text(slide, "purpose-three", "Compare station-level seven-day forecasts with a persistence baseline.", 84, 492, 1030, 40, {
    size: 21, color: C.body,
  });
  footer(slide, 2);
  notes(slide, `PRESENTER 1 · 0:55\n\nThe project focuses on a practical problem: telemetry files are large and stations can have very different coverage. Looking at one well alone would miss the network context. The dashboard keeps all 96 supplied Delhi stations in monitoring and quality views, then makes forecasts only for series with enough usable data. The aim is not to issue an operational warning. It is to make the observations, screening decisions, and model comparisons easier to inspect.\n\nThe three goals shown here are reflected in separate dashboard views. We first look at the actual file, then explain the processing and evaluation choices.`);
}

// 3. Dataset scope
{
  const slide = newSlide(deck, C.white);
  header(slide, "Delhi telemetry at a glance", "02  Supplied dataset");
  text(slide, "dataset-size", "173,132", 84, 180, 470, 82, { size: 48, bold: true, color: C.navy });
  text(slide, "dataset-size-label", "observation records", 86, 264, 430, 32, { size: 18, color: C.muted });
  text(slide, "station-count", "96", 660, 180, 260, 82, { size: 48, bold: true, color: C.teal });
  text(slide, "station-count-label", "monitoring stations", 662, 264, 430, 32, { size: 18, color: C.muted });
  text(slide, "district-count", "8", 84, 382, 280, 82, { size: 48, bold: true, color: C.teal });
  text(slide, "district-count-label", "districts represented", 86, 466, 430, 32, { size: 18, color: C.muted });
  text(slide, "coverage-dates", "2021 to 2025", 660, 382, 470, 82, { size: 38, bold: true, color: C.navy });
  text(slide, "coverage-date-label", "1 January 2021 to 14 October 2025", 662, 466, 500, 32, { size: 17, color: C.muted });
  rect(slide, "dataset-rule", 84, 555, 1112, 1, C.line);
  text(slide, "dataset-cadence", "Six-hourly telemetry is the stated cadence. Actual station intervals vary.", 84, 580, 1080, 38, {
    size: 18, color: C.body,
  });
  footer(slide, 3);
  notes(slide, `PRESENTER 1 · 1:05\n\nThe current Delhi CSV contains 173,132 records across 96 stations and eight districts. Its timestamps begin on 1 January 2021 and end on 14 October 2025. The source describes six-hourly telemetry, while the station-level checks identify irregular intervals in the supplied records. We use the actual file dimensions here, rather than the earlier approximate figures in the synopsis. All stations remain available in the monitoring views, including stations that are not eligible for forecasting.\n\nSource: Supplied Delhi CSV and the project's station summary. Source record: https://nwdp.nwic.gov.in/dataset/ground-water-level-telemetry-hourly-delhi-surface-water-and-ground-water-departments/resource/14c48913-600c-4e2c-9c77-8ef2e92e59e6`);
}

// 4. Data quality
{
  const slide = newSlide(deck);
  header(slide, "Data quality decisions", "03  Preserve first, screen for analysis");
  const rows = [
    ["64.98%", "112,496 exact-zero readings are retained. All-zero series are flagged for forecast eligibility."],
    ["1,319", "Readings equal 999 are shown as placeholder candidates and omitted from daily analytical medians."],
    ["1", "Reading below −100 m is flagged and omitted from the analytical daily series."],
    ["0", "Duplicate station and timestamp keys were found in the inspected Delhi file."],
  ];
  let y = 174;
  for (let i = 0; i < rows.length; i++) {
    const [figure, explanation] = rows[i];
    text(slide, `quality-figure-${i + 1}`, figure, 88, y, 205, 52, {
      size: 30, bold: true, color: i === 2 ? C.red : (i === 1 ? C.gold : C.teal),
    });
    text(slide, `quality-description-${i + 1}`, explanation, 330, y + 2, 820, 54, {
      size: 17, color: C.body,
    });
    if (i < rows.length - 1) rect(slide, `quality-divider-${i + 1}`, 88, y + 68, 1060, 1, C.line);
    y += 91;
  }
  text(slide, "quality-caveat", "Screening rules do not alter the source CSV. Measurement conventions for zero and 999 still need confirmation.", 88, 560, 1080, 52, {
    size: 15, bold: true, color: C.navy,
  });
  footer(slide, 4);
  notes(slide, `PRESENTER 1 · 1:10\n\nThe file has a high share of exact-zero readings: 112,496, or 64.98 percent. We retain them in monitoring and flag all-zero stations so they do not become misleading forecast candidates. The repeated value 999 is treated as a candidate placeholder for daily analysis, and one value below minus 100 metres is screened from the analytical series. The original records remain available. We found no duplicate station and timestamp keys.\n\nThese are transparent screening rules, not a claim that the provider has confirmed the physical meaning of zero or 999. That source confirmation remains an important limitation.`);
}

// 5. Architecture and workflow
{
  const slide = newSlide(deck, C.white);
  header(slide, "Analysis pipeline", "04  Reproducible workflow");
  const stages = [
    ["01", "Source CSV", "Read the supplied telemetry fields"],
    ["02", "Quality profile", "Check coverage, timestamps, and candidates"],
    ["03", "Daily series", "Aggregate available values by station and day"],
    ["04", "Model", "Build seven-day forecasts and test chronologically"],
    ["05", "Dashboard", "Explore network, station, quality, and model views"],
  ];
  const boxes = [];
  const x0 = 68;
  const boxW = 208;
  const gap = 20;
  for (let i = 0; i < stages.length; i++) {
    const x = x0 + i * (boxW + gap);
    const box = rect(slide, `workflow-stage-${i + 1}`, x, 238, boxW, 194, i % 2 === 0 ? C.paper : "#EAF5F4", C.line, 16);
    boxes.push(box);
    text(slide, `workflow-number-${i + 1}`, stages[i][0], x + 18, 258, 60, 24, { size: 12, bold: true, color: C.teal });
    text(slide, `workflow-title-${i + 1}`, stages[i][1], x + 18, 300, boxW - 36, 42, { size: 19, bold: true, color: C.navy });
    text(slide, `workflow-copy-${i + 1}`, stages[i][2], x + 18, 350, boxW - 36, 65, { size: 14.5, color: C.body });
  }
  for (let i = 0; i < boxes.length - 1; i++) {
    slide.shapes.connect(boxes[i], boxes[i + 1], {
      kind: "straight", fromSide: "right", toSide: "left",
      line: { style: "solid", fill: C.teal, width: 2 },
      tail: { type: "arrow", width: "sm", length: "sm" },
    });
  }
  text(slide, "workflow-detail", "The raw source stays intact. Only analytical daily series apply the documented candidate-anomaly screen.", 84, 494, 1100, 44, {
    size: 17, color: C.body,
  });
  footer(slide, 5);
  notes(slide, `PRESENTER 1 · 1:25 · HANDOFF AT 5:00\n\nThis is the path from source file to dashboard. The loader reads only the fields needed for station analysis and caches the parsed file by its identity. We profile data quality before aggregation. For each station, available readings are summarized to a daily median; missing calendar days are not interpolated. The forecasting module builds a seven-day target, trains candidate models, and evaluates them using later dates. Streamlit presents those outputs in interactive views.\n\nThe source data stays unchanged, and screening applies to analytical series only. I will hand over to Presenter 2 to explain the forecast design and what the evaluation found.\n\nImplementation references: app.py, groundwater/data.py, and groundwater/forecasting.py.`);
}

// 6. Forecast and evaluation method
{
  const slide = newSlide(deck);
  header(slide, "Forecast design and evaluation", "05  Station-level time series");
  text(slide, "forecast-target-label", "FORECAST TARGET", 84, 174, 280, 22, { size: 11, bold: true, color: C.teal });
  text(slide, "forecast-target", "Daily median groundwater level seven calendar days after the feature date.", 84, 207, 485, 82, {
    size: 21, bold: true, color: C.navy,
  });
  text(slide, "features-label", "FEATURES AVAILABLE BY THAT DATE", 84, 332, 440, 22, { size: 11, bold: true, color: C.teal });
  text(slide, "features-copy", "Lagged levels at 1, 7, 14, and 28 days\nTrailing means over 7 and 28 days\nAnnual calendar sine and cosine terms", 84, 365, 500, 130, {
    size: 17, color: C.body,
  });
  text(slide, "models-label", "MODELS COMPARED", 670, 174, 280, 22, { size: 11, bold: true, color: C.teal });
  text(slide, "models-copy", "Persistence baseline\nLinear Regression\nRandom Forest Regression", 670, 207, 390, 115, {
    size: 19, color: C.navy, bold: true,
  });
  text(slide, "split-label", "CHRONOLOGICAL HOLDOUT", 670, 362, 360, 22, { size: 11, bold: true, color: C.teal });
  const train = rect(slide, "training-window", 670, 410, 355, 58, C.navy, "none", 6);
  text(slide, "training-window-text", "Earlier examples  ·  80%", 682, 425, 330, 28, { size: 16, bold: true, color: C.white, align: "center", valign: "middle" });
  rect(slide, "purge-window", 1033, 410, 16, 58, C.gold, "none", 0);
  const test = rect(slide, "test-window", 1057, 410, 140, 58, C.teal, "none", 6);
  text(slide, "test-window-text", "Later 20%", 1063, 425, 130, 28, { size: 14, bold: true, color: C.white, align: "center", valign: "middle" });
  text(slide, "split-caption", "A seven-day purge prevents training labels from crossing into the first test date.", 670, 486, 526, 54, { size: 15, color: C.body });
  text(slide, "metrics-label", "Scored with MAE and RMSE. No random time-series split and no invented confidence intervals.", 84, 566, 1100, 38, {
    size: 15, bold: true, color: C.navy,
  });
  footer(slide, 6);
  notes(slide, `PRESENTER 2 · 1:10\n\nThe target is the station's daily median level seven calendar days after a feature date. The features use observations available at that date: lags at 1, 7, 14, and 28 days, trailing means, and annual calendar terms. We compare Persistence, Linear Regression, and Random Forest.\n\nEvaluation is chronological. Earlier examples are used for training and later examples for testing. A seven-day purge removes training cases whose targets would not yet have been observed at the first test feature date. We report MAE and RMSE. Missing calendar days are not filled, and the dashboard does not display made-up confidence intervals.\n\nImplementation reference: groundwater/forecasting.py.`);
}

// 7. Model results
{
  const slide = newSlide(deck, C.white);
  header(slide, "Evaluation favors the persistence baseline", "06  Results from actual holdouts");
  text(slide, "network-result-label", "NETWORK RESULT", 78, 164, 500, 26, { size: 11, bold: true, color: C.teal });
  text(slide, "example-result-label", "ONE STATION EXAMPLE", 680, 164, 500, 26, { size: 11, bold: true, color: C.teal });
  slide.charts.add("bar", {
    position: { left: 60, top: 205, width: 560, height: 340 },
    title: "Stations where each model had lowest MAE",
    titleTextStyle: { typeface: FONT, fontSize: "14pt", bold: true, fill: C.navy },
    categories: ["Persistence", "Linear Regression", "Random Forest"],
    series: [{ name: "Stations", values: [26, 3, 0], fill: C.teal }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 75 },
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd", textStyle: { typeface: FONT, fontSize: "13pt", bold: true, fill: C.ink } },
    xAxis: { min: 0, max: 30, majorUnit: 10, textStyle: { typeface: FONT, fontSize: "11pt", fill: C.body }, majorGridlines: { style: "solid", fill: C.line, width: 1 } },
    yAxis: { textStyle: { typeface: FONT, fontSize: "11pt", fill: C.body }, majorGridlines: null },
    chartFill: "none", chartLine: { style: "solid", fill: "none", width: 0 }, plotAreaFill: "none", plotAreaLine: { style: "solid", fill: "none", width: 0 },
  });
  slide.charts.add("bar", {
    position: { left: 662, top: 205, width: 555, height: 340 },
    title: "New Delhi Mungeshpur MAE (m)",
    titleTextStyle: { typeface: FONT, fontSize: "14pt", bold: true, fill: C.navy },
    categories: ["Persistence", "Linear Regression", "Random Forest"],
    series: [{ name: "MAE (m)", values: [0.073, 0.093, 0.168], fill: C.teal }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 75 },
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd", numberFormatCode: "0.000", textStyle: { typeface: FONT, fontSize: "12pt", bold: true, fill: C.ink } },
    xAxis: { min: 0, max: 0.2, majorUnit: 0.05, numberFormatCode: "0.00", textStyle: { typeface: FONT, fontSize: "10pt", fill: C.body }, majorGridlines: { style: "solid", fill: C.line, width: 1 } },
    yAxis: { textStyle: { typeface: FONT, fontSize: "10pt", fill: C.body }, majorGridlines: null },
    chartFill: "none", chartLine: { style: "solid", fill: "none", width: 0 }, plotAreaFill: "none", plotAreaLine: { style: "solid", fill: "none", width: 0 },
  });
  text(slide, "result-caveat", "29 of 30 candidates had enough dated holdout examples. Results are station-specific; machine learning did not outperform persistence most often.", 82, 568, 1110, 48, {
    size: 15, color: C.body,
  });
  footer(slide, 7);
  notes(slide, `PRESENTER 2 · 1:30\n\nAcross 29 evaluated Delhi stations, Persistence had the lowest MAE at 26. Linear Regression was best at three. Random Forest was not best at any of the 29 stations. One of the 30 forecast candidates did not have enough dated examples for holdout evaluation. The honest result is that the simple baseline performed best most often. We do not claim machine learning improved the forecasts.\n\nFor New Delhi Mungeshpur Mungeshpur, the holdout contains 173 test targets. Its MAE was 0.073 metres for Persistence, 0.093 for Linear Regression, and 0.168 for Random Forest. These figures describe this station and test period only.\n\nSource: outputs/model_evaluation_by_station.csv and the project's verified network evaluation summary.`);
}

// 8. Dashboard components
{
  const slide = newSlide(deck);
  header(slide, "Dashboard components", "07  One interface for network and station work");
  const rows = [
    ["Overview", "Network KPIs, station map, coverage, and data-led notes"],
    ["Station Explorer", "Six-hourly observations and daily history for a selected station"],
    ["Forecast Lab", "Seven-day candidates with model and limitation notes"],
    ["Model Evaluation", "Chronological holdout metrics and actual-versus-predicted plots"],
    ["Data Quality", "Missing values, intervals, duplicates, anomalies, and station coverage"],
    ["Insights", "Network coverage, monthly patterns, and cross-station results"],
    ["Thapar Area (Bonus)", "Stations within 25 km of campus with local analysis and forecasts"],
  ];
  let y = 171;
  for (let i = 0; i < rows.length; i++) {
    text(slide, `dashboard-area-${i + 1}`, rows[i][0], 84, y, 258, 29, {
      size: 16.5, bold: true, color: i === 6 ? C.teal : C.navy,
    });
    text(slide, `dashboard-function-${i + 1}`, rows[i][1], 360, y, 820, 36, {
      size: 16.5, color: C.body,
    });
    if (i < rows.length - 1) rect(slide, `dashboard-rule-${i + 1}`, 84, y + 43, 1096, 1, C.line);
    y += 62;
  }
  text(slide, "dashboard-scope-note", "All 96 Delhi stations remain in monitoring and quality views. Forecast availability depends on data sufficiency.", 84, 620, 1100, 32, {
    size: 14.5, color: C.muted,
  });
  footer(slide, 8);
  notes(slide, `PRESENTER 2 · 1:05\n\nThe dashboard brings the analytical work into seven areas. Overview summarizes the network and map. Station Explorer shows supplied observations and the station's daily history. Forecast Lab presents seven-day candidates. Model Evaluation compares actual and predicted test values with MAE and RMSE. Data Quality exposes coverage and flagged records. Insights summarizes network patterns. The Thapar Area tab adds a bounded regional bonus study.\n\nAll Delhi stations remain visible in monitoring and quality pages. A station that is not forecast-ready is still part of the network; the interface simply explains why its forecast is unavailable. The NWIC link opens the official source record, while current charts use the project's bundled CSV snapshot.`);
}

// 9. Thapar bonus study
{
  const slide = newSlide(deck, C.white);
  header(slide, "Thapar-area bonus study", "08  Punjab telemetry near campus");
  text(slide, "thapar-stations", "37", 84, 174, 250, 70, { size: 46, bold: true, color: C.teal });
  text(slide, "thapar-stations-label", "stations within 25 km", 86, 246, 300, 28, { size: 17, color: C.muted });
  text(slide, "thapar-records", "172,752", 460, 174, 340, 70, { size: 42, bold: true, color: C.navy });
  text(slide, "thapar-records-label", "telemetry records", 462, 246, 300, 28, { size: 17, color: C.muted });
  text(slide, "thapar-coverage", "2021–2025", 890, 174, 300, 70, { size: 36, bold: true, color: C.navy });
  text(slide, "thapar-coverage-label", "through 22 September 2025", 892, 246, 310, 28, { size: 16, color: C.muted });
  rect(slide, "thapar-divider", 84, 308, 1112, 1, C.line);
  text(slide, "thapar-nearest-title", "Closest supplied monitoring points", 84, 342, 1080, 36, { size: 23, bold: true, color: C.navy });
  text(slide, "thapar-kvk-300", "3.85 km", 84, 405, 190, 45, { size: 25, bold: true, color: C.teal });
  text(slide, "thapar-kvk-300-desc", "Krishi Vigyan Kendra, 300 m sensor\n2,444 records", 290, 405, 445, 62, { size: 17, color: C.body });
  text(slide, "thapar-kvk-200", "4.02 km", 710, 405, 190, 45, { size: 25, bold: true, color: C.teal });
  text(slide, "thapar-kvk-200-desc", "Krishi Vigyan Kendra, 200 m sensor\n3,099 records", 910, 405, 320, 62, { size: 16, color: C.body });
  rect(slide, "thapar-note-line", 84, 514, 5, 80, C.gold);
  text(slide, "thapar-campus-note", "The CSV contains surrounding-area stations, not a station named Thapar or an on-campus well.", 108, 525, 1055, 56, {
    size: 19, bold: true, color: C.navy,
  });
  footer(slide, 9);
  notes(slide, `PRESENTER 2 · 0:55\n\nFor a regional bonus, we filtered the supplied statewide Punjab CSV to stations within a 25-kilometre straight-line radius of Thapar's published Patiala campus point. The app-ready subset contains 37 stations and 172,752 records, from 1 January 2021 to 22 September 2025. It supports local station histories and forecasts where data is sufficient.\n\nThe closest supplied stations are two Krishi Vigyan Kendra sensors at about 3.85 and 4.02 kilometres. The source file has no station named Thapar and no measurement identified as an on-campus well. These stations are regional context, not a substitute for campus groundwater monitoring.\n\nCampus location source: https://www.thapar.edu/upload/files/Thapar%20SM%2030.09.2024.pdf\nPunjab telemetry source: statewide CSV supplied for this project; the 25-kilometre subset is bundled with the dashboard.`);
}

// 10. Limitations and conclusion
{
  const slide = newSlide(deck, C.navy);
  header(slide, "Interpretation and next steps", "09  What the prototype can support", true);
  text(slide, "closing-main", "A monitoring and model-comparison tool for historical telemetry.", 84, 176, 1060, 72, {
    size: 28, bold: true, color: C.white,
  });
  text(slide, "closing-limit-one", "Measurement meaning for zero, 999, and extreme values still needs source confirmation.", 84, 302, 1050, 42, {
    size: 18, color: "#D5E3E8",
  });
  text(slide, "closing-limit-two", "Forecast metrics are station-specific. Persistence beats the machine-learning models most often.", 84, 365, 1050, 48, {
    size: 18, color: "#D5E3E8",
  });
  text(slide, "closing-limit-three", "The dashboard does not infer depletion, recharge, safe pumping, or groundwater volume.", 84, 438, 1050, 42, {
    size: 18, color: "#D5E3E8",
  });
  rect(slide, "closing-rule", 84, 528, 70, 4, C.tealLight);
  text(slide, "closing-next-step", "Next: confirm measurement conventions, add direct campus measurements if available, and continue seasonal evaluation.", 84, 556, 1040, 54, {
    size: 17, bold: true, color: "#90E0D7",
  });
  text(slide, "closing-thanks", "Thank you", 84, 625, 420, 34, { size: 20, bold: true, color: C.white });
  footer(slide, 10, true);
  notes(slide, `PRESENTER 2 · 0:20 · CLOSE\n\nTo conclude, this prototype makes the supplied station data easier to monitor and compare. Its forecasts are educational and station-specific. Before making stronger hydrogeological interpretations, we need source confirmation for measurement conventions and, for the Thapar study, direct campus measurements if they become available. Thank you.\n\nDo not describe these outputs as groundwater depletion, recharge, safe-pumping, or volume estimates.`);
}

if (deck.slides.items.length !== 10) throw new Error(`Expected 10 slides, found ${deck.slides.items.length}`);

for (const [index, slide] of deck.slides.items.entries()) {
  const filename = `slide-${String(index + 1).padStart(2, "0")}.png`;
  const png = await deck.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(previewDir, filename), new Uint8Array(await png.arrayBuffer()));
}

const pptx = await PresentationFile.exportPptx(deck);
await pptx.save(draftPath);
console.log(JSON.stringify({ draftPath, finalPath, slides: deck.slides.items.length, previewDir }));
