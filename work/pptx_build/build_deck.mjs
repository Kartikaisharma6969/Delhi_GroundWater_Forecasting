import fs from 'node:fs/promises';
import path from 'node:path';
import { Presentation, PresentationFile } from 'file:///C:/Program%20Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..').replaceAll('\\', '/');
const WORK = `${ROOT}/work/pptx_build`;
const OUT = `${ROOT}/outputs`;
const RESULTS = await fs.readFile(`${OUT}/model_evaluation_by_station.csv`, 'utf8');
const lines = RESULTS.trim().split(/\r?\n/);
const headers = lines[0].split(',');
const records = lines.slice(1).map(line => {
  const vals = line.split(','); const o={}; headers.forEach((h,i)=>o[h]=vals[i]); return o;
});
const evaluated = records.filter(r => r.Evaluated === 'True');
const median = key => {
  const vals=evaluated.map(r=>Number(r[key])).sort((a,b)=>a-b);
  return vals[Math.floor(vals.length/2)];
};
const metrics = [
  {name:'Persistence', mae:median('Persistence MAE (m)'), rmse:median('Persistence RMSE (m)'), wins:evaluated.filter(r=>r['Best by MAE']==='Persistence').length},
  {name:'Linear regression', mae:median('Linear Regression MAE (m)'), rmse:median('Linear Regression RMSE (m)'), wins:evaluated.filter(r=>r['Best by MAE']==='Linear Regression').length},
  {name:'Random forest', mae:median('Random Forest MAE (m)'), rmse:median('Random Forest RMSE (m)'), wins:evaluated.filter(r=>r['Best by MAE']==='Random Forest').length},
];

const deck = Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#0D2630',navy2:'#153B46',teal:'#12A3A5',cyan:'#72D2CE',white:'#F4FAFA',muted:'#BCD0D2',gold:'#F0B86D',red:'#EE8A91',green:'#8DD6B2',ink:'#17343A'};
function rect(slide,x,y,w,h,fill,r=0){
  const sh=slide.shapes.add({geometry:r?'roundRect':'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}}); return sh;
}
function text(slide,str,x,y,w,h,opts={}){
  const sh=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  sh.text=String(str); sh.text.style={fontFamily:'Arial',fontSize:opts.size||'20pt',bold:!!opts.bold,color:opts.color||C.white,verticalAlignment:opts.valign||'middle',wrap:true,alignment:opts.align||'left'}; return sh;
}
function base(kicker,title,sub=''){
  const s=deck.slides.add(); s.background.fill=C.navy;
  rect(s,0,0,14,720,C.teal); text(s,kicker.toUpperCase(),70,34,900,24,{size:'11pt',bold:true,color:C.cyan});
  text(s,title,70,72,1140,74,{size:'32pt',bold:true});
  if(sub) text(s,sub,70,145,1120,46,{size:'15pt',color:C.muted});
  rect(s,70,676,1140,1,'#31525A'); text(s,'Delhi Groundwater Monitoring and Forecasting System',70,682,890,20,{size:'9pt',color:C.muted});
  text(s,String(deck.slides.items.length).padStart(2,'0'),1150,682,60,20,{size:'9pt',color:C.cyan,align:'right'});
  return s;
}
function bullet(slide,txt,x,y,w,color=C.cyan,size='19pt'){
  rect(slide,x,y+10,9,9,color,4); text(slide,txt,x+24,y,w-24,54,{size,color:C.white});
}
function stat(slide,x,y,w,value,label,accent=C.cyan){
  text(slide,value,x,y,w,70,{size:'32pt',bold:true,color:accent}); text(slide,label,x,y+67,w,50,{size:'14pt',color:C.muted});
}

// 1 Cover
{
 const s=deck.slides.add(); s.background.fill=C.navy;
 rect(s,0,0,22,720,C.teal); rect(s,860,0,420,720,C.navy2);
 for(let i=0;i<7;i++) rect(s,900+i*42,220+(i%3)*38,18,350-(i%3)*46,['#0E6973','#12868B','#12A3A5','#48BDB8'][i%4],8);
 text(s,'MCA  ·  DATA SCIENCE FOUNDATION LAB',82,74,760,35,{size:'12pt',bold:true,color:C.cyan});
 text(s,'Delhi Groundwater\nMonitoring and\nForecasting System',82,162,760,260,{size:'42pt',bold:true});
 text(s,'A station-wide dashboard for historical telemetry, data quality and seven-day forecast evaluation',84,445,700,100,{size:'20pt',color:C.muted});
 rect(s,84,570,365,4,C.teal); text(s,'Thapar Institute of Engineering & Technology',84,592,700,35,{size:'14pt',color:C.white});
 text(s,'Student names: add before submission',84,632,700,28,{size:'11pt',color:C.muted});
}
// 2 Problem
{
 const s=base('01  Motivation','Why build a monitoring system?','Telemetry is useful only when coverage, measurement quality and model performance are visible together.');
 bullet(s,'Station histories are spread across a large time-series file.',98,238,1080);
 bullet(s,'Irregular coverage and repeated values can change what an apparent trend means.',98,326,1080,C.gold);
 bullet(s,'Forecasting needs a time-ordered test and a simple baseline for comparison.',98,414,1080,C.cyan);
 rect(s,98,528,1080,82,C.navy2,14); text(s,'Project scope',124,543,190,34,{size:'13pt',bold:true,color:C.cyan}); text(s,'An educational decision-support prototype using the supplied Delhi telemetry file.',320,540,810,52,{size:'18pt'});
}
// 3 objectives
{
 const s=base('02  Objectives','What the system delivers','One dashboard, six connected analysis views, and all supplied stations retained for monitoring.');
 const items=[['01','Explore all stations','Map, coverage and history'],['02','Review data quality','Missingness, codes, intervals and coordinates'],['03','Aggregate daily values','Daily median, no gap filling'],['04','Evaluate forecasts','Seven-day target, chronological holdout'],['05','Explain limitations','No unsupported aquifer claims']];
 items.forEach((it,i)=>{let y=226+i*78;text(s,it[0],100,y,70,42,{size:'20pt',bold:true,color:C.cyan});text(s,it[1],190,y,340,44,{size:'18pt',bold:true});text(s,it[2],560,y,600,44,{size:'16pt',color:C.muted});rect(s,190,y+55,940,1,'#31525A');});
}
// 4 dataset
{
 const s=base('03  Dataset','The inspected file differs from the synopsis','Use these measured counts in the presentation. Earlier estimates do not match the active CSV.');
 stat(s,100,236,260,'173,132','observation rows'); stat(s,400,236,240,'96','station names',C.gold); stat(s,690,236,250,'8','districts',C.green); stat(s,990,236,230,'2021–25','date coverage');
 text(s,'1 Jan 2021 19:00 to 14 Oct 2025 12:00',100,392,1070,52,{size:'20pt',bold:true});
 bullet(s,'21 columns in source, 7 fields used by the dashboard.',100,480,1080);
 bullet(s,'The CSV remains read-only; source provider metadata was not included.',100,548,1080,C.gold);
}
// 5 network
{
 const s=base('04  Network coverage','All stations stay in scope','Forecast eligibility is separate from network monitoring.');
 stat(s,110,240,260,'96','stations available in selectors'); stat(s,455,240,260,'94','stations pass map bounds',C.green); stat(s,800,240,260,'65','series contain only zeros',C.gold);
 rect(s,110,416,1050,116,C.navy2,12); text(s,'How to explain this',138,432,280,32,{size:'14pt',bold:true,color:C.cyan});
 text(s,'Every station appears in coverage and quality views. Forecasts require enough screened readings and dated examples to fit and evaluate the models.',138,470,960,45,{size:'17pt'});
 text(s,'Two station locations are screened out of the map by broad coordinate bounds. Their station records remain available.',110,565,1050,48,{size:'15pt',color:C.muted});
}
// 6 quality
{
 const s=base('05  Data quality','Review signals before interpreting values','These are screening flags. Zero and 999 conventions have not been confirmed by the source provider.');
 const vals=[['Zero readings','112,496','64.98% of rows',C.gold],['All-zero stations','65','retained in monitoring',C.red],['999 candidate values','1,319','mostly at Bakhtawarpur Village',C.gold],['Below −100 m','1','flagged for review',C.red],['Suspect coordinate rows','4,733','94 stations pass map bounds',C.cyan],['Duplicate station-times','0','in selected fields',C.green]];
 vals.forEach((a,i)=>{const col=i%3,row=Math.floor(i/3),x=105+col*370,y=245+row*175;text(s,a[1],x,y,330,56,{size:'27pt',bold:true,color:a[3]});text(s,a[0],x,y+57,330,32,{size:'15pt',bold:true});text(s,a[2],x,y+91,330,48,{size:'12pt',color:C.muted});});
 text(s,'Raw values remain visible. The analytical daily series omits 999 and the single value below −100 m; zeros are retained.',105,610,1060,38,{size:'13pt',color:C.muted});
}
// 7 processing
{
 const s=base('06  Processing','From six-hourly rows to daily series','A transparent series of steps preserves the raw CSV and documents analytical screening.');
 const steps=[['01','Load selected columns'],['02','Parse timestamps and numeric levels'],['03','Summarize by station'],['04','Flag 999 and extreme candidate values'],['05','Compute daily median'],['06','Leave missing dates empty']];
 steps.forEach((a,i)=>{let col=i%3,row=Math.floor(i/3),x=105+col*365,y=260+row*180;text(s,a[0],x,y,66,48,{size:'20pt',bold:true,color:C.cyan});rect(s,x,y+55,315,2,'#39717A');text(s,a[1],x,y+75,315,72,{size:'17pt',bold:true});});
 text(s,'No interpolation is used. The median summarizes within-day readings and does not repair missing telemetry.',105,620,1050,34,{size:'14pt',color:C.muted});
}
// 8 forecast
{
 const s=base('07  Forecast method','Predict the level seven calendar days ahead','Station-level models use only features that are available at the forecast origin.');
 const x=100,y=235;
 text(s,'Target',x,y,230,36,{size:'14pt',bold:true,color:C.cyan}); text(s,'Daily median at date t + 7',x,y+40,980,42,{size:'21pt',bold:true});
 text(s,'Inputs',x,y+112,230,36,{size:'14pt',bold:true,color:C.cyan}); text(s,'Lags 1, 7, 14, 28 days · trailing 7 and 28 day means · annual sine/cosine',x,y+151,1040,55,{size:'17pt'});
 text(s,'Models',x,y+240,230,36,{size:'14pt',bold:true,color:C.cyan}); text(s,'Persistence baseline · Linear Regression · Random Forest Regression',x,y+278,1040,50,{size:'17pt'});
 text(s,'Evaluation',x,y+366,230,36,{size:'14pt',bold:true,color:C.cyan}); text(s,'Chronological 80/20 split with a seven-day purge before the test period. Compare MAE and RMSE.',x,y+404,1040,56,{size:'17pt'});
}
// 9 leakage
{
 const s=base('08  Evaluation design','Keep future labels out of model training','For the seven-day target, training examples near the boundary are purged when their labels would not yet be known.');
 const x0=130,x1=1130,y=365;
 rect(s,x0,y,630,78,C.teal,12); text(s,'Earlier training examples',x0+24,y+18,580,45,{size:'18pt',bold:true});
 rect(s,x0+630,y,70,78,C.gold,8); text(s,'7d',x0+642,y+16,46,40,{size:'14pt',bold:true,color:C.navy,align:'center'});
 rect(s,x0+700,y,300,78,'#39717A',12); text(s,'Later test examples',x0+724,y+18,250,45,{size:'18pt',bold:true});
 text(s,'Train labels must be observed on or before the first test feature date.',130,480,1000,42,{size:'18pt',color:C.white});
 text(s,'Metrics are calculated on the same test dates for all three models at each station.',130,540,1000,38,{size:'15pt',color:C.muted});
}
// 10 results
{
 const s=base('09  Network results','Persistence wins most station comparisons','29 of 30 forecast candidates produced enough dated examples for evaluation.');
 const max=Math.max(...metrics.map(m=>m.mae))*1.25;
 metrics.forEach((m,i)=>{const y=245+i*115; text(s,m.name,105,y,245,36,{size:'16pt',bold:true}); rect(s,390,y+3,Math.round(m.mae/max*560),36,[C.teal,'#42A9AD','#83C6C5'][i],8); text(s,`${m.mae.toFixed(4)} m`,975,y,180,36,{size:'16pt',bold:true,color:C.cyan}); text(s,`${m.wins} stations lowest MAE`,390,y+43,550,28,{size:'13pt',color:C.muted});});
 text(s,'Median station MAE · lower is better',105,595,1000,35,{size:'14pt',color:C.muted});
}
// 11 interpretation
{
 const s=base('10  What results mean','Added model complexity did not improve MAE for most stations','Network medians summarize station-level holdouts and should not be treated as one network-wide forecast.');
 metrics.forEach((m,i)=>{const x=105+i*365; text(s,m.name,x,245,320,40,{size:'16pt',bold:true,color:C.cyan}); stat(s,x,300,320,`${m.mae.toFixed(4)} m`,'median station MAE',[C.cyan,C.gold,C.red][i]); text(s,`Median RMSE ${m.rmse.toFixed(4)} m`,x,425,320,35,{size:'14pt',color:C.muted});});
 rect(s,105,520,1080,96,C.navy2,12); text(s,'Interpretation',128,532,225,30,{size:'13pt',bold:true,color:C.cyan}); text(s,'For these historical holdouts, carrying forward the last observed value often beat regression models. Results vary by station and test period.',350,532,800,70,{size:'16pt'});
}
// 12 dashboard
{
 const s=base('11  Application','Six tabs support the analysis workflow','Streamlit and Plotly provide interactive views on a local website.');
 const tabs=['Overview','Station Explorer','Forecast Lab','Model Evaluation','Data Quality','Insights'];
 tabs.forEach((t,i)=>{const x=105+(i%3)*360,y=250+Math.floor(i/3)*155; text(s,String(i+1).padStart(2,'0'),x,y,62,44,{size:'19pt',bold:true,color:C.cyan});text(s,t,x+72,y,260,44,{size:'17pt',bold:true});rect(s,x+72,y+55,260,2,'#39717A');});
 text(s,'The app currently runs at localhost for demonstration. Public deployment has not been configured.',105,590,1050,40,{size:'15pt',color:C.gold});
}
// 13 limitations and future scope
{
 const s=base('12  Limitations and next steps','Use the dashboard as a prototype','Source metadata and contextual measurements are required for stronger hydrogeological conclusions.');
 bullet(s,'Confirm what zero, 999, units and datum represent.',100,235,1070,C.gold,'16pt');
 bullet(s,'Include rainfall, pumping, geology or aquifer context where reliable data exist.',100,315,1070,C.cyan,'16pt');
 bullet(s,'Add Thapar-area monitoring after validating its separate CSV.',100,395,1070,C.green,'16pt');
 bullet(s,'Consider public hosting after data rights and resource needs are reviewed.',100,475,1070,C.cyan,'16pt');
 text(s,'No depletion, recharge, safe-pumping or operational warning claim is made from this file alone.',100,585,1080,45,{size:'15pt',bold:true,color:C.gold});
}
// 14 conclusion
{
 const s=deck.slides.add(); s.background.fill=C.navy;
 rect(s,0,0,14,720,C.teal); text(s,'13  CONCLUSION',78,64,700,30,{size:'12pt',bold:true,color:C.cyan});
 text(s,'A complete view of the supplied Delhi network',78,148,1050,82,{size:'30pt',bold:true});
 text(s,'96 stations monitored',82,290,475,52,{size:'25pt',bold:true,color:C.cyan});
 text(s,'Seven-day forecasts evaluated chronologically',82,370,780,52,{size:'22pt',bold:true,color:C.white});
 text(s,'Persistence performed best by MAE at 26 of 29 evaluated stations.',82,460,850,62,{size:'20pt',color:C.muted});
 rect(s,82,580,780,3,C.teal); text(s,'Questions',82,604,400,52,{size:'22pt',bold:true,color:C.gold});
 text(s,'Delhi Groundwater Monitoring and Forecasting System',78,682,900,20,{size:'9pt',color:C.muted});
 text(s,'14',1150,682,60,20,{size:'9pt',color:C.cyan,align:'right'});
}

await fs.mkdir(`${WORK}/rendered`,{recursive:true}); await fs.mkdir(OUT,{recursive:true});
for(let i=0;i<deck.slides.items.length;i++){
  const png=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});
  await fs.writeFile(`${WORK}/rendered/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await png.arrayBuffer()));
}
const candidate=`${WORK}/Delhi_Groundwater_Project_Report_candidate.pptx`;
await (await PresentationFile.exportPptx(deck)).save(candidate);
const skill='C:/Users/karti/.codex/plugins/cache/openai-primary-runtime/presentations/26.1119.11507/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(`${skill}/container_tools/artifact_tool_utils.mjs`).href);
const finalPath=`${OUT}/Delhi_Groundwater_Project_Presentation_v2.pptx`;
const validation=await finalizePresentation({
  explicitTotalSlideCount:14,
  requiredNativeChartOwnerSlides:[],
  requiredNativeTableOwnerSlides:[],
  workspaceDir:ROOT,
  candidatePath:candidate,
  finalPath,
  pythonExecutable:'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe',
  integrityValidatorPath:`${skill}/container_tools/inspect_presentation_package_integrity.py`,
  layoutValidatorPath:`${skill}/container_tools/inspect_presentation_layout_geometry.py`,
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
  fontPolicy:{basis:'design',families:['Arial']},
  verifyArtifactToolImport:true,
  receiptPath:`${WORK}/rendered/validation.json`,
});
console.log(JSON.stringify({candidate,finalPath,slides:deck.slides.items.length,metrics,validation},null,2));
