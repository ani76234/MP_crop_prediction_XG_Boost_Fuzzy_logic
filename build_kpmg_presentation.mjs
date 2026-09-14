import fs from 'node:fs/promises';
import { FileBlob, Presentation, PresentationFile } from '@oai/artifact-tool';

const OUT = 'KPMG_Internship_Wheat_Yield_Prediction_Presentation.pptx';
const ASSETS = 'report_assets';
const W = 1280, H = 720;
const BLUE = '#00338D', NAVY = '#001C4D', SKY = '#6DCBF4', PALE = '#EAF2FB', INK = '#102A43', MUTED = '#516579', WHITE = '#FFFFFF', GREEN = '#00843D', AMBER = '#F6C453';

async function writeBlob(path, blob) { await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer())); }
function box(slide, left, top, width, height, fill='transparent', radius='rect', line='transparent') {
  return slide.shapes.add({ geometry: radius, position:{left,top,width,height}, fill, line:{style:'solid',fill:line,width:line==='transparent'?0:1} });
}
function text(slide, value, left, top, width, height, fontSize=22, color=INK, bold=false, align='left') {
  const s = box(slide,left,top,width,height,'transparent','textbox'); s.text=value;
  s.text.style={fontFace:'Aptos',fontSize,color,bold,alignment:align,marginLeft:0,marginRight:0,marginTop:0,marginBottom:0}; return s;
}
function title(slide, index, label, heading, sub='') {
  text(slide,label.toUpperCase(),56,30,360,24,12,BLUE,true);
  text(slide,heading,56,60,1120,50,34,NAVY,true);
  if(sub) text(slide,sub,56,111,1120,32,17,MUTED,false);
  box(slide,56,151,1168,2,BLUE);
  text(slide,`KPMG Internship Project  |  ${String(index).padStart(2,'0')}`,56,682,420,18,11,MUTED,false);
  text(slide,'High-Resolution Wheat Yield Prediction',876,682,348,18,11,MUTED,false,'right');
}
async function image(slide,path,left,top,width,height,fit='contain') { const blob=new Blob([await fs.readFile(path)],{type:'image/png'}); const img=slide.images.add({blob,fit,alt:path}); img.position={left,top,width,height}; return img; }
function bullet(slide, content, x, y, w, color=INK) { text(slide,'•',x,y,w?18:18,28,24,BLUE,true); text(slide,content,x+22,y,w-22,44,18,color,false); }
function metric(slide,value,label,x,y,color=BLUE) { box(slide,x,y,210,120,WHITE,'roundRect','#D8E4F0'); text(slide,value,x+16,y+19,178,43,31,color,true,'center'); text(slide,label,x+14,y+68,182,29,14,MUTED,true,'center'); }
function source(slide,s) { text(slide,s,56,655,1130,17,10,MUTED,false); }

async function main(){
 await fs.mkdir('presentation_preview',{recursive:true});
 const p=Presentation.create({slideSize:{width:W,height:H}});
 // 1 cover
 { const s=p.slides.add(); s.background.fill=NAVY; box(s,0,0,515,H,BLUE); box(s,515,0,765,H,'#0A204C');
   await image(s,`${ASSETS}/final_yield_map.png`,625,80,540,540,'contain');
   text(s,'KPMG INTERNSHIP PROJECT',56,64,360,24,14,SKY,true);
   text(s,'High-Resolution\nWheat Yield\nPrediction System',56,128,410,185,47,WHITE,true);
   text(s,'XGBoost + Google Earth Engine\nMadhya Pradesh | 500 m resolution',56,340,385,62,21,'#DCEBFF',false);
   box(s,56,455,255,3,SKY); text(s,'From district forecasts to a spatially detailed decision-support map',56,476,396,62,18,WHITE,false);
   text(s,'Prepared for KPMG leadership review',56,650,300,22,12,'#DCEBFF',false); }
 //2
 { const s=p.slides.add(); s.background.fill=WHITE; title(s,2,'Why this matters','District averages conceal the variation that decisions need');
   text(s,'The challenge',56,196,290,28,21,BLUE,true); text(s,'Agricultural yield data is reliable at district level, but operational planning needs a more local view.',56,233,370,126,24,INK,true);
   box(s,480,195,230,280,PALE,'roundRect'); text(s,'1.6M',510,230,170,50,43,BLUE,true,'center'); text(s,'500 x 500 m\ngrid cells across\nMadhya Pradesh',510,300,170,80,20,INK,true,'center');
   box(s,758,195,410,280,'#F7FAFD','roundRect','#D8E4F0'); text(s,'The response',790,226,230,30,21,BLUE,true); bullet(s,'Train where labels exist: district yield',790,276,330); bullet(s,'Use local satellite conditions to allocate yield',790,335,330); bullet(s,'Preserve the district prediction in the final map',790,394,330); source(s,'Scope: wheat, Madhya Pradesh; seasonal inputs cover the November-May Rabi cycle.'); }
 //3
 { const s=p.slides.add(); s.background.fill='#F8FBFF'; title(s,3,'Approach','A two-stage design separates prediction from spatial allocation');
   const xs=[56,430,804]; const heads=['1 | Predict','2 | Allocate','3 | Visualize']; const bodies=['District-level XGBoost model\ntrained on historical yield\nand seasonal features.','Grid-level satellite conditions\nconverted into a Relative\nProductivity Index (RPI).','500 m yield map exposes\nintra-district productivity\npatterns.']; const colors=[BLUE,'#176B87',GREEN];
   for(let i=0;i<3;i++){ box(s,xs[i],220,320,245,WHITE,'roundRect','#D8E4F0'); box(s,xs[i],220,320,9,colors[i]); text(s,heads[i],xs[i]+26,255,260,32,24,colors[i],true); text(s,bodies[i],xs[i]+26,307,258,105,20,INK,false); if(i<2) text(s,'→',xs[i]+326,316,38,42,32,BLUE,true,'center'); }
   text(s,'Design principle: grid-level values add local differentiation without changing the district-level forecast on average.',56,525,1100,42,24,NAVY,true); }
 //4 data
 { const s=p.slides.add(); s.background.fill=WHITE; title(s,4,'Data foundation','Consistent boundaries, seasonally relevant satellite features, and official yield records');
   await image(s,`${ASSETS}/gadm_source.png`,56,196,415,320,'contain'); box(s,512,196,660,320,'#F7FAFD','roundRect','#D8E4F0');
   text(s,'Boundary and reference data',544,226,300,28,22,BLUE,true); bullet(s,'GADM administrative boundaries → Madhya Pradesh districts',544,271,570); bullet(s,'DESAGRI district-level wheat area, production and yield',544,327,570); bullet(s,'Google Earth Engine: 2015-2023, November-May only',544,383,570); text(s,'Satellite feature set',544,455,220,26,19,BLUE,true); text(s,'Mean & peak NDVI  |  Mean & peak EVI  |  Mean rainfall  |  Mean soil moisture',544,484,580,40,17,INK,false); source(s,'Sources: GADM v4.1; DESAGRI Crop Area, Production and Yield portal; Google Earth Engine.'); }
 //5 pipeline
 { const s=p.slides.add(); s.background.fill='#F8FBFF'; title(s,5,'Data construction','From raw sources to a machine-learning-ready district dataset');
   const steps=['GADM\nDistricts','GEE seasonal\nfeatures','DESAGRI\nyield data','Merge +\nvalidation','Time-series\nfeatures','XGBoost\ntraining'];
   for(let i=0;i<steps.length;i++){ const x=50+i*198; box(s,x,260,156,116,WHITE,'roundRect','#C9D9EA'); text(s,steps[i],x+14,285,128,56,18,i===5?WHITE:INK,true,'center'); if(i===5) box(s,x,260,156,116,BLUE,'roundRect',BLUE); if(i<steps.length-1) text(s,'→',x+160,298,36,32,25,BLUE,true,'center'); }
   text(s,'Quality controls',56,440,160,24,20,BLUE,true); bullet(s,'District-name standardization and duplicate-key checks',56,479,355); bullet(s,'Yield-unit, missing-value and feature-consistency validation',442,479,360); bullet(s,'Chronological sorting before lags and rolling features are built',833,479,355); }
 //6 features
 { const s=p.slides.add(); s.background.fill=WHITE; title(s,6,'Feature engineering','Trees learn temporal behaviour through explicit historical and environmental features');
   const cols=[['Yield memory','Previous-year yield\nLag-2 / Lag-3\n2- and 3-year rolling mean\nRolling standard deviation'],['Environmental memory','Lag-1 / Lag-2\nRolling mean\nAnomaly vs previous mean\nYear-to-year change'],['Why it helps','Captures persistence\nHighlights shocks\nProvides a local baseline\nAvoids use of future data']];
   for(let i=0;i<3;i++){let x=56+i*382; box(s,x,210,340,290, i===2?'#EAF2FB':'#F7FAFD','roundRect','#D8E4F0'); text(s,cols[i][0],x+26,242,285,28,23,BLUE,true); text(s,cols[i][1],x+26,294,280,150,20,INK,false); }
   text(s,'This tabular representation is a practical alternative to recurrent neural networks when the history is short and labelled observations are limited.',56,555,1120,38,22,NAVY,true); }
 //7 model
 { const s=p.slides.add(); s.background.fill='#F8FBFF'; title(s,7,'Model validation','Walk-forward testing evaluates the model on future periods, not random holdouts');
   text(s,'Training principle',56,204,300,28,22,BLUE,true); text(s,'For each forecast window, the model sees only earlier crop years. This is stricter—and more realistic—than randomly mixing years.',56,247,350,125,22,INK,true);
   metric(s,'0.431','R-squared',470,212,BLUE); metric(s,'0.728','RMSE',710,212,'#176B87'); metric(s,'0.493','MAE',950,212,GREEN); metric(s,'18.22%','MAPE',710,370,'#A05A00');
   text(s,'Interpretation',56,455,210,25,22,BLUE,true); text(s,'The model has modest-to-moderate explanatory power. It is suitable as a decision-support estimate, not as a substitute for field-measured yield.',56,493,1080,50,22,NAVY,true); source(s,'Metrics from Trial 2 overall walk-forward evaluation.'); }
 //8 PVA
 { const s=p.slides.add(); s.background.fill=WHITE; title(s,8,'Validation view','Predictions follow the overall yield pattern—but compress the extremes');
   await image(s,`${ASSETS}/predicted_vs_actual.png`,55,182,650,435,'contain'); box(s,753,205,415,315,'#F7FAFD','roundRect','#D8E4F0'); text(s,'What the chart shows',786,235,300,28,22,BLUE,true); bullet(s,'Central observations align with the reference line',786,285,330); bullet(s,'Higher observed yields are often under-predicted',786,355,330); bullet(s,'Lower observed yields can be over-predicted',786,425,330); text(s,'Implication: the model is better at broad directional prediction than at exceptional seasons.',753,560,405,44,18,NAVY,true); }
 //9 residual
 { const s=p.slides.add(); s.background.fill='#F8FBFF'; title(s,9,'Error pattern','A few large misses drive the gap between typical and squared error');
   await image(s,`${ASSETS}/walk_forward_residuals.png`,56,185,635,430,'contain'); box(s,748,214,410,280,WHITE,'roundRect','#D8E4F0'); text(s,'Residual interpretation',782,245,310,28,22,BLUE,true); bullet(s,'Most residuals cluster around zero',782,294,330); bullet(s,'Several outliers are materially larger',782,355,330); bullet(s,'RMSE > MAE confirms sensitivity to those misses',782,416,330); text(s,'Likely missing drivers: irrigation, fertilizer, seed variety, pests, management and short-lived weather stress.',56,555,1060,36,21,NAVY,true); }
 //10 importance
 { const s=p.slides.add(); s.background.fill=WHITE; title(s,10,'What drives the forecast','Historical yield structure carries more predictive signal than any single satellite measure');
   await image(s,`${ASSETS}/feature_importance.png`,55,174,750,460,'contain'); box(s,840,205,330,340,'#F7FAFD','roundRect','#D8E4F0'); text(s,'Top signals',872,236,220,28,22,BLUE,true); text(s,'1  Yield rolling mean (3y)\n2  District\n3  Year\n4  Yield rolling mean (2y)\n5  Rainfall rolling mean',872,285,250,160,20,INK,true); text(s,'The environmental variables add incremental context; they do not fully explain management and shock effects.',872,470,250,50,17,MUTED,false); }
 //11 RPI
 { const s=p.slides.add(); s.background.fill='#F8FBFF'; title(s,11,'Spatial allocation logic','Relative Productivity Index introduces local variation while conserving the district forecast');
   box(s,56,197,508,270,WHITE,'roundRect','#D8E4F0'); text(s,'1. Create a productivity score',88,230,380,26,22,BLUE,true); text(s,'Normalize six local environmental variables and combine them with wheat-specific weights.',88,274,410,60,20,INK,false); text(s,'P(i) = Σ wj · zj(i)',88,365,350,35,26,NAVY,true,'center');
   box(s,620,197,548,270,WHITE,'roundRect','#D8E4F0'); text(s,'2. Allocate without changing the mean',652,230,420,26,22,BLUE,true); text(s,'RPI(i) = P(i) / mean district [P]',652,282,400,32,24,NAVY,true,'center'); text(s,'Grid Yield(i) = District Prediction × RPI(i)',652,347,430,32,24,NAVY,true,'center');
   text(s,'Because the district-average RPI equals 1, the average grid yield equals the district prediction.',56,525,1080,40,23,NAVY,true); }
 //12 map
 { const s=p.slides.add(); s.background.fill=NAVY; text(s,'OUTPUT',56,35,200,20,12,SKY,true); text(s,'High-resolution wheat yield map',56,64,580,42,34,WHITE,true); text(s,'Grid-level estimates at 500 m resolution for Madhya Pradesh',56,110,600,26,18,'#DCEBFF',false); await image(s,`${ASSETS}/final_yield_map.png`,112,145,1000,500,'contain'); text(s,'Interpretation: colour variation represents the environmentally informed spatial allocation of each district forecast.',56,657,1080,18,11,'#DCEBFF',false); }
 //13 close
 { const s=p.slides.add(); s.background.fill=WHITE; title(s,13,'Recommendation','Use the framework as a scalable decision-support layer—and strengthen it through richer agronomic data');
   const recs=[['Ready now','Repeatable district forecasting + 500 m spatial allocation'],['Before operational use','Treat results as estimates; report uncertainty and validate priority areas'],['Next upgrade','Add daily weather, irrigation/fertilizer proxies, crop masks and longer history']];
   for(let i=0;i<3;i++){let x=56+i*382; box(s,x,222,340,225,i===0?'#EAF2FB':'#F7FAFD','roundRect','#D8E4F0'); text(s,recs[i][0],x+25,255,280,27,22,BLUE,true); text(s,recs[i][1],x+25,310,282,90,20,INK,false);}
   text(s,'The core value: a transparent bridge from official district yield records to a high-resolution view of relative productivity.',56,535,1110,44,24,NAVY,true); text(s,'Thank you',56,612,230,36,30,BLUE,true); }
 for (const [i,s] of p.slides.items.entries()) { const png=await p.export({slide:s,format:'png',scale:1}); await writeBlob(`presentation_preview/slide-${String(i+1).padStart(2,'0')}.png`,png); }
 const pptx=await PresentationFile.exportPptx(p); await pptx.save(OUT);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
