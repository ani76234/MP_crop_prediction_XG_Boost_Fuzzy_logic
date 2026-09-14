from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE

OUT = 'KPMG_Internship_Wheat_Yield_Prediction_Report_Final.docx'

doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(0.85); sec.bottom_margin = Inches(0.8)
sec.left_margin = Inches(0.9); sec.right_margin = Inches(0.9)

styles = doc.styles
normal = styles['Normal']; normal.font.name = 'Aptos'; normal._element.rPr.rFonts.set(qn('w:eastAsia'), 'Aptos'); normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(7); normal.paragraph_format.line_spacing = 1.15
for level, size, color in [(1,15,'17365D'),(2,12.5,'1F4E79'),(3,11,'1F4E79')]:
    s=styles[f'Heading {level}']; s.font.name='Aptos Display'; s._element.rPr.rFonts.set(qn('w:eastAsia'),'Aptos Display'); s.font.size=Pt(size); s.font.bold=True; s.font.color.rgb=RGBColor.from_string(color)
    s.paragraph_format.space_before=Pt(14 if level==1 else 10); s.paragraph_format.space_after=Pt(6); s.paragraph_format.keep_with_next=True
caption=styles['Caption']; caption.font.name='Aptos'; caption.font.size=Pt(9); caption.font.italic=True; caption.font.color.rgb=RGBColor(89,89,89)

def field(paragraph, instruction):
    run=paragraph.add_run(); fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),instruction); run._r.addnext(fld)
def shade(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); tcPr.append(shd)
def set_cell_text(cell, text, bold=False):
    cell.text=''; p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(2); r=p.add_run(text); r.bold=bold; r.font.size=Pt(9); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
def table(headers, rows, widths=None):
    t=doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.style='Table Grid'
    for i,h in enumerate(headers): set_cell_text(t.rows[0].cells[i],h,True); shade(t.rows[0].cells[i],'D9EAF7')
    for row in rows:
        cells=t.add_row().cells
        for i,v in enumerate(row): set_cell_text(cells[i],str(v))
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Inches(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
    return t
def p(text, style=None): return doc.add_paragraph(text, style)
def bullet(text): return doc.add_paragraph(text, style='List Bullet')
def figure(label, text):
    q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER; q.paragraph_format.space_before=Pt(8); q.paragraph_format.space_after=Pt(4)
    r=q.add_run('[ '+text+' ]'); r.italic=True; r.font.color.rgb=RGBColor(100,100,100)
    c=doc.add_paragraph(label, style='Caption'); c.alignment=WD_ALIGN_PARAGRAPH.CENTER
def imagefig(path, label, width=6.1):
    q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER; q.paragraph_format.space_before=Pt(8); q.paragraph_format.space_after=Pt(3)
    q.add_run().add_picture(path, width=Inches(width))
    c=doc.add_paragraph(label, style='Caption'); c.alignment=WD_ALIGN_PARAGRAPH.CENTER
def eq(text):
    q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER; q.paragraph_format.space_before=Pt(5); q.paragraph_format.space_after=Pt(5); r=q.add_run(text); r.bold=True; r.font.name='Cambria Math'; r.font.size=Pt(11)
def h(text, level=1): doc.add_heading(text, level=level)

# Cover
doc.add_paragraph().paragraph_format.space_after=Pt(52)
t=doc.add_paragraph(); t.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=t.add_run('HIGH-RESOLUTION WHEAT YIELD\nPREDICTION SYSTEM'); r.bold=True; r.font.name='Aptos Display'; r.font.size=Pt(25); r.font.color.rgb=RGBColor(0,51,141)
s=doc.add_paragraph('Using XGBoost and Google Earth Engine', style='Subtitle'); s.alignment=WD_ALIGN_PARAGRAPH.CENTER
brand=doc.add_paragraph('KPMG Internship Project Report'); brand.alignment=WD_ALIGN_PARAGRAPH.CENTER; brand.runs[0].bold=True; brand.runs[0].font.size=Pt(14); brand.runs[0].font.color.rgb=RGBColor(0,51,141)
doc.add_paragraph().paragraph_format.space_after=Pt(45)
meta=table(['Project documentation report','Submission details'], [['Engagement context','KPMG Internship Project'],['Degree programme','Bachelor of Technology'],['Project domain','Remote sensing, machine learning and geospatial analytics'],['Study region','Madhya Pradesh, India'],['Prepared by','[Student Name / Roll Number]'],['KPMG mentor','[Mentor Name]'],['Academic guide','[Faculty Guide Name]'],['Institution','[College / Department Name]']], [2.7,3.7])
doc.add_paragraph('Academic Year: [Insert Academic Year]').alignment=WD_ALIGN_PARAGRAPH.CENTER
doc.add_page_break()

h('Abstract',1)
p('This report presents a high-resolution wheat yield prediction framework for Madhya Pradesh, India. The framework first estimates district-level wheat yield with an Extreme Gradient Boosting (XGBoost) model trained on historical agricultural statistics and seasonally aggregated satellite-derived environmental features. It then translates the district prediction to a 500 x 500 m spatial grid through a Relative Productivity Index (RPI) derived from local vegetation, rainfall and soil-moisture conditions. This two-stage design is intended to retain the statistical reliability of district-level yield records while revealing meaningful within-district environmental variability.')
p('Google Earth Engine supports consistent extraction of Rabi-season indicators for 2015-2023, while district-wise yield records provide the supervised learning target. Lagged and rolling variables allow a tree-based learner to represent temporal persistence and departures from normal conditions without requiring a recurrent neural network. Under walk-forward validation, the final model attained R-squared = 0.431, RMSE = 0.728, MAE = 0.493 and MAPE = 18.22%. The final procedure produces approximately 1.6 million grid-level estimates, preserves each district prediction in expectation, and supports interpretable mapping of productivity variation.')
h('Keywords',2); p('Wheat yield prediction; XGBoost; Google Earth Engine; NDVI; EVI; soil moisture; spatial disaggregation; Relative Productivity Index; Madhya Pradesh.')
h('Table of Contents',1)
toc_rows = [
['1. Introduction','3'],['2. Objectives','3'],['3. Study Area','4'],['4. Data Collection','4'],['5. Data Preprocessing and Feature Engineering','5'],['6. District-Level Wheat Yield Prediction using XGBoost','7'],['7. Generation of the 500 x 500 m Grid','8'],['8. Grid-Level Environmental Feature Extraction','9'],['9. Relative Productivity Index Methodology','9'],['10. Grid-Level Yield Estimation','11'],['11. Visualization of Predicted Yield','11'],['12. Advantages and Limitations','12'],['13. Future Scope','13'],['14. Conclusion','13'],['15. References','14']]
contents = doc.add_table(rows=0, cols=2); contents.alignment=WD_TABLE_ALIGNMENT.CENTER
for title, page in toc_rows:
    cells=contents.add_row().cells; set_cell_text(cells[0],title); set_cell_text(cells[1],page); cells[1].paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.RIGHT
for row in contents.rows:
    row.cells[0].width=Inches(5.7); row.cells[1].width=Inches(0.5)
doc.add_paragraph('The page references above are the intended report layout. A Word TOC field is included below for automatic refresh after any edits.', style='Caption')
toc=doc.add_paragraph(); field(toc,'TOC \\o "1-3" \\h \\z \\u')
doc.add_page_break()

h('1. Introduction')
p('Wheat is a strategic Rabi-season crop whose yield responds to crop vigor, moisture availability, rainfall timing and management conditions. Conventional reporting systems commonly provide yield at district scale. Such estimates are valuable for planning, but they mask substantial variation across fields and landscapes within the same district. A district can contain irrigated and rain-fed zones, contrasting soils, and different crop-condition trajectories; assigning one value everywhere obscures this heterogeneity.')
p('The present system addresses that scale mismatch through a linked prediction and spatial-distribution workflow. It learns the district-level yield signal from historical outcomes and environmental observations, then distributes the predicted district value according to relative local environmental productivity. This separation is deliberate: the machine-learning model is trained where dependable labels exist, while the grid stage uses satellite observations to express local contrasts without claiming unavailable plot-level yield measurements.')
h('1.1 End-to-end workflow',2)
flow = ['GADM Boundary','Google Earth Engine','District Satellite Features (2015-2023)','Historical Yield Data (DESAGRI)','Dataset Construction','Time-Series Feature Engineering','XGBoost District Yield Prediction','500 x 500 m Grid Generation','Grid-Level Satellite Features','Weighted Productivity Index','Relative Productivity Index','Grid-Level Yield Allocation','High-Resolution Wheat Yield Map']
flow_table=doc.add_table(rows=0, cols=1); flow_table.alignment=WD_TABLE_ALIGNMENT.CENTER
for idx, item in enumerate(flow):
    cell=flow_table.add_row().cells[0]; set_cell_text(cell, item, True if idx in (0,len(flow)-1) else False); cell.paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER; shade(cell, 'D9EAF7' if idx in (0,len(flow)-1) else 'F3F7FB')
    if idx < len(flow)-1:
        connector=flow_table.add_row().cells[0]; set_cell_text(connector, '↓'); connector.paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph('Figure 1. End-to-end workflow for district prediction and grid-level yield allocation.', style='Caption').alignment=WD_ALIGN_PARAGRAPH.CENTER

h('2. Objectives')
table(['Objective','Purpose and contribution'],[
['Develop district-level yield estimates','Create a statistically supervised baseline using district yield records and seasonally relevant predictors.'],
['Represent temporal behavior','Use lags, rolling summaries and anomalies so XGBoost can learn persistence and change across crop years.'],
['Generate a 500 x 500 m grid','Provide a consistent spatial unit for local environmental extraction across Madhya Pradesh.'],
['Construct a Relative Productivity Index','Convert local environmental differences into a normalized multiplier that preserves district totals.'],
['Visualize high-resolution predictions','Support interpretation of within-district yield variation for monitoring and planning.']],[2.0,4.4])

h('3. Study Area')
p('The study area is Madhya Pradesh, a large central Indian state with extensive wheat cultivation and considerable agro-climatic variation. Its scale and diversity make it a useful test bed: a single district average cannot fully describe differences in rainfall, crop greenness and soil-water conditions across the state. Wheat production is economically important in the Rabi season, when crop development broadly spans November to May.')
p('Administrative boundaries were obtained from the Global Administrative Areas (GADM) dataset. GADM was selected because it provides a commonly used, machine-readable and spatially consistent administrative hierarchy. District boundaries are essential because historical yield observations are reported by district, and the model must aggregate environmental observations to the same reporting unit before a valid supervised learning dataset can be built. The boundary layer also constrains grid generation and final map display.')
imagefig('report_assets/gadm_source.png','Figure 2. GADM version 4.1 India administrative boundary dataset selection used as the source for district boundary extraction.',5.6)

h('4. Data Collection')
h('4.1 Satellite-derived environmental data',2)
p('Google Earth Engine (GEE) was used to acquire and summarize environmental variables for crop years 2015-2023. GEE was chosen over manual scene-by-scene downloading because its catalog, cloud computation and geospatial reducers support reproducible extraction over many districts and grid points. Only November-May observations were used. Annual averages would combine the wheat growth cycle with monsoon and fallow conditions, diluting the crop-relevant signal; seasonal aggregation focuses the features on the period when wheat canopy development and water stress affect output.')
table(['Variable','Meaning and relevance to wheat','Reason for seasonal summary'],[
['Mean NDVI','Normalized Difference Vegetation Index; a proxy for green biomass and canopy vigor.','Mean captures sustained crop condition over the season.'],
['Peak NDVI','Maximum seasonal NDVI; indicative of the strongest canopy state.','Peak captures maximum greenness that an average can conceal.'],
['Mean EVI','Enhanced Vegetation Index; improves sensitivity in denser canopies and moderates some background effects.','Mean reflects typical vegetation activity during wheat growth.'],
['Peak EVI','Maximum seasonal EVI; complementary measure of peak canopy development.','Peak distinguishes districts reaching different canopy maxima.'],
['Mean rainfall','Average precipitation during the Rabi window; affects soil-water recharge and crop stress.','Seasonal mean represents water supply during the production period.'],
['Mean soil moisture','Average near-surface moisture condition; a direct proxy for plant-available water conditions.','Seasonal mean represents persistent moisture adequacy or deficit.']],[1.25,3.5,1.65])
p('Mean values were retained because yield is affected by cumulative and persistent conditions rather than a single observation. Peak values were additionally retained for NDVI and EVI because crop yield can respond to the attainment of a healthy maximum canopy; two seasons with similar means may differ in their peak biomass and phenological trajectory.')
h('4.2 Historical agricultural statistics',2)
p('District-wise wheat area, production and yield were collected from the Department of Agriculture and Farmers Welfare Crop Area, Production and Yield report portal (DESAGRI: https://data.desagri.gov.in/website/crops-apy-report-web). Yield is the supervised learning target, while area and production provide valuable consistency checks because yield should correspond to production divided by area after unit harmonization. Historical yield data is indispensable: it provides observed outcomes from which a model can learn the relationship between past environmental and temporal conditions and realized district yield.')

h('5. Data Preprocessing and Feature Engineering')
h('5.1 Dataset construction and quality controls',2)
p('The analytical dataset was built by joining district-level seasonal environmental summaries with the historical agricultural table on a standardized district identifier and crop year. District-name normalization is necessary because punctuation, spelling, suffixes and administrative naming can differ between sources. Before modeling, the workflow checks duplicate keys, missing values, invalid yield units, non-positive area or production records, and consistency between reported yield and the production-area ratio. Records are sorted within each district by crop year before lagged features are created, preventing future information from entering past rows.')
h('5.1.1 Data construction pipeline',3)
pipeline = doc.add_table(rows=0, cols=1); pipeline.alignment=WD_TABLE_ALIGNMENT.CENTER
def pipe_box(text, fill='F3F7FB', bold=False):
    cell=pipeline.add_row().cells[0]; set_cell_text(cell,text,bold); cell.paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER; shade(cell,fill)
def pipe_arrow():
    cell=pipeline.add_row().cells[0]; set_cell_text(cell,'↓'); cell.paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER
pipe_box('GADM Administrative Boundaries\n(District Map of India)','D9EAF7',True); pipe_arrow()
pipe_box('Filter Madhya Pradesh Districts'); pipe_arrow()
pipe_box('Google Earth Engine (2015-2023)\nNovember-May (Rabi Season)','D9EAF7',True); pipe_arrow()
branch=pipeline.add_row().cells[0]; branch_table=branch.add_table(rows=1, cols=2); branch_table.alignment=WD_TABLE_ALIGNMENT.CENTER
set_cell_text(branch_table.cell(0,0),'Mean / Peak NDVI',True); shade(branch_table.cell(0,0),'F3F7FB'); set_cell_text(branch_table.cell(0,1),'Mean / Peak EVI',True); shade(branch_table.cell(0,1),'F3F7FB')
pipe_arrow(); pipe_box('Mean Rainfall'); pipe_arrow(); pipe_box('Mean Soil Moisture'); pipe_arrow()
pipe_box('District-wise Satellite Feature Dataset','D9EAF7',True); pipe_arrow()
pipe_box('Historical Wheat Yield Dataset (DESAGRI)\nArea | Production | Yield','F3F7FB',True); pipe_arrow()
pipe_box('Merge on District + Crop Year','D9EAF7',True); pipe_arrow()
pipe_box('Data Cleaning & Validation\nMissing-value handling | District-name matching | Feature-consistency checks'); pipe_arrow()
pipe_box('Time-Series Feature Engineering\nYield lags (1, 2, 3) | Rolling means | Rolling standard deviation | Previous yield change\nEnvironmental lags | Environmental rolling means | Environmental anomalies | Year-to-year changes','F3F7FB'); pipe_arrow()
pipe_box('Final Machine Learning Dataset','D9EAF7',True); pipe_arrow(); pipe_box('XGBoost Model Training','D9EAF7',True); pipe_arrow(); pipe_box('District-Level Wheat Yield Prediction','D9EAF7',True)
doc.add_paragraph('Figure 3. Data construction pipeline for the district-level wheat yield prediction dataset.', style='Caption').alignment=WD_ALIGN_PARAGRAPH.CENTER
h('5.2 Rationale for feature engineering',2)
p('A raw annual table does not explicitly tell a tree ensemble how the present season relates to earlier seasons. Feature engineering converts ordered observations into tabular predictors that expose persistence, momentum, variability and departures from normal. This allows XGBoost to learn time-series-like behavior using structured columns, avoiding the data and architecture demands of recurrent neural networks while preserving model transparency and suitability for modest district-year sample sizes.')
table(['Feature family','Feature','Purpose in the model'],[
['Yield history','Previous Year Yield','Captures immediate persistence in district productivity.'],['Yield history','Yield Lag-2 and Yield Lag-3','Represent multi-year memory and delayed effects.'],['Yield history','Rolling Mean (2 and 3 years)','Provides a smoothed local baseline less sensitive to a single unusual year.'],['Yield history','Rolling Standard Deviation','Represents recent yield instability and risk.'],['Yield history','Previous Yield Change','Captures momentum: improvement or decline relative to the prior year.'],['Environment','Lag-1 and Lag-2','Represent delayed environmental conditions and serial dependence.'],['Environment','Rolling Mean','Supplies a recent climatological/crop-condition baseline.'],['Environment','Anomaly vs Previous Mean','Measures whether the current condition is unusually favorable or adverse.'],['Environment','Change from Previous Year','Highlights abrupt year-to-year environmental shifts.']],[1.15,2.0,3.25])
p('For a generic environmental variable X at year t, representative transformations are X(t-1), X(t-2), mean[X(t-1), ..., X(t-k)], X(t) - mean[X(t-1), ..., X(t-k)], and X(t) - X(t-1). These features are calculated within district only, then initial rows lacking sufficient history are handled consistently through exclusion or an explicitly documented imputation policy.')

h('6. District-Level Wheat Yield Prediction using XGBoost')
h('6.1 Model rationale',2)
p('A decision tree partitions predictor space into interpretable rules, such as different responses under high vegetation vigor and low soil moisture. Gradient boosting builds trees sequentially: each new tree focuses on residual errors from the preceding ensemble. XGBoost is an efficient, regularized implementation of gradient-boosted trees that can model nonlinear relations and feature interactions, while controlling complexity through shrinkage, tree depth and regularization.')
p('XGBoost was selected over linear regression because yield responses to vegetation, rainfall and moisture are rarely linear or independent. It was preferred to a Random Forest baseline because boosting explicitly corrects residual error sequentially and commonly performs strongly on structured prediction tasks with engineered features. The final choice should nevertheless be validated using a time-aware comparison on the project dataset, not assumed solely from general model properties.')
h('6.2 Training, prediction and evaluation',2)
p('The input matrix contains current seasonal variables, their engineered historical transformations, and eligible historical yield features. The target variable is district-level wheat yield for the corresponding crop year. Training and validation should respect chronology: model fitting must use only earlier crop years when predicting a later period. Hyperparameters are tuned within the training period, and the untouched final time window is used for reporting performance.')
table(['Metric','Equation / interpretation','Walk-forward result'],[
['MAE','(1/n) sum |y - yhat|; average absolute error in yield units.','0.493'],['RMSE','sqrt((1/n) sum (y - yhat)^2); penalizes larger errors.','0.728'],['MAPE','(100/n) sum |(y - yhat)/y|; relative error, used only where y is valid and non-zero.','18.22%'],['R-squared','1 - sum(y-yhat)^2 / sum(y-ybar)^2; variance explained against the evaluation baseline.','0.431']],[1.0,4.5,1.0])
imagefig('report_assets/predicted_vs_actual.png','Figure 4. Walk-forward predicted versus actual district wheat yield (Trial 2).',5.55)
imagefig('report_assets/walk_forward_residuals.png','Figure 5. Walk-forward residuals (actual minus predicted) for Trial 2.',5.55)
imagefig('report_assets/feature_importance.png','Figure 6. Gain-based feature importance from the final XGBoost model (Trial 2).',5.5)
h('6.3 Interpretation of model accuracy and error',2)
p('The walk-forward R-squared of 0.431 indicates modest-to-moderate explanatory power: the model captures approximately 43% of the variation in held-out district-year yield, but a substantial share remains unexplained. The MAE of 0.493 and RMSE of 0.728 are expressed in the target yield unit; the RMSE being larger than the MAE indicates that a smaller number of larger misses materially affects error. MAPE of 18.22% means that the typical proportional deviation is meaningful for an operational forecasting use case, so the output should be interpreted as a decision-support estimate rather than a precise field measurement.')
p('Several design realities explain this result. First, 2015-2023 provides only a short time series, and lag/rolling features reduce the number of usable early observations further. Second, the evaluation is walk-forward: every prediction is made on a future period not available during fitting, which is more realistic and usually less optimistic than random train-test splitting. Third, reported district yield is affected by factors not included in the feature set, including irrigation, fertilizer, seed variety, pests, diseases, planting and harvest timing, prices and management practice.')
p('The charts support this interpretation. Predictions are compressed toward the central range: high observed yields tend to be under-predicted and low observed yields can be over-predicted. The residual plot also contains several sizeable outliers, which inflate RMSE. Feature importance is led by three-year rolling yield, district identity and year, while environmental features contribute smaller incremental gains. This suggests that historical and location-specific structure is informative, but the available seasonal environmental summaries do not fully explain shocks or management-driven yield differences. Seasonal means and peaks also compress important within-season timing information, such as a short heat or moisture-stress event.')
p('Appropriate improvements include adding crop masks and irrigation/fertilizer proxies, daily weather and heat-stress variables, phenology-aware time-series features, consistent yield-unit verification, longer historical coverage, and uncertainty intervals. These improvements should be tested through the same walk-forward protocol; they should not be assumed to improve accuracy without out-of-time evidence.')

h('7. Generation of the 500 x 500 m Grid')
p('District-level prediction is insufficient when users need to understand local variation for targeting, monitoring or prioritization. A regular 500 x 500 m grid was generated within each Madhya Pradesh district in GEE. This resolution offers a practical balance: it is sufficiently fine to reveal broad within-district contrasts while remaining computationally manageable across the state. Approximately 1.6 million grid points were generated.')
p('Centroid coordinates were stored rather than complete cell polygons because point-based extraction and tabular storage are substantially lighter for a large grid. Each centroid acts as the representative sampling location for a 500 m cell. Cell geometries can be reconstructed for visualization when needed, while centroids reduce transfer size and simplify repeated GEE reduction operations.')

h('8. Grid-Level Environmental Feature Extraction')
p('For every grid centroid, the same Rabi-season definitions were used to calculate mean rainfall, mean soil moisture, mean NDVI, peak NDVI, mean EVI and peak EVI. Reusing the district-model definitions preserves semantic consistency between stages. Environmental conditions vary within a district because of irrigation access, soils, elevation, local rainfall, land cover and crop establishment differences. District averages therefore cannot identify locally favorable or unfavorable areas.')
p('Grid-level extraction is not a second supervised model. Instead, it provides the local evidence used to distribute a district prediction proportionately. This distinction prevents the method from overstating the availability of ground-truth yield labels at grid scale.')

h('9. Relative Productivity Index Methodology')
h('9.1 Normalization and weighted scoring',2)
p('The six grid-level variables have different units and ranges. They are normalized before combination so that rainfall does not dominate merely because of its numeric scale and vegetation indices are comparable across locations. A min-max form may be used within an appropriate reference domain: z(i,j) = [x(i,j) - min(x(j))] / [max(x(j)) - min(x(j))]. The reference domain and handling of outliers must be documented because these choices affect comparability.')
p('For grid i, a wheat-specific productivity score is calculated as a weighted combination of normalized variables:')
eq('P(i) = w1 z_NDVI_mean(i) + w2 z_NDVI_peak(i) + w3 z_EVI_mean(i) + w4 z_EVI_peak(i) + w5 z_Rain(i) + w6 z_SoilMoisture(i)')
p('The weights w1...w6 express agronomic importance and should sum to one. Their values are project parameters, not universal constants; they should be justified through agronomic literature, expert consultation, sensitivity analysis or calibrated validation. Weighted scoring is preferred to an unweighted average because the indicators do not contribute equally to wheat productivity and because the method must make its assumptions explicit.')
h('9.2 Relative Productivity Index',2)
p('The Relative Productivity Index converts the score into a district-relative multiplier:')
eq('RPI(i) = P(i) / mean_d[P(i)]')
p('For a district d with N grid cells, the district average of RPI is exactly one (subject to consistent computation):')
eq('(1/N) sum_i RPI(i) = (1/N) sum_i P(i) / mean_d[P(i)] = mean_d[P(i)] / mean_d[P(i)] = 1')
p('This property is essential. It means the RPI expresses relative spatial redistribution rather than creating or destroying a district’s predicted yield level. Cells above one are environmentally more favorable than the district average; cells below one are less favorable. A small positive denominator safeguard and a documented fallback should be used if a district’s mean score is zero or undefined.')
table(['Methodological decision','Reason'],[['Normalize before weighting','Ensures units do not determine influence.'],['Use crop-specific weights','Encodes the comparative importance of wheat-relevant signals.'],['Divide by district mean score','Anchors the multiplier at one within every district.'],['Retain RPI as a relative index','Avoids implying grid-scale ground-truth calibration where labels are absent.']],[2.3,4.2])

h('10. Grid-Level Yield Estimation')
p('The district prediction is spatially distributed using the RPI:')
eq('Grid Yield(i) = District Predicted Yield(d) x RPI(i)')
p('This formulation preserves the modeled district yield while introducing within-district variation guided by local environmental conditions. Taking the average over all N cells in district d gives:')
eq('mean_d[Grid Yield] = District Predicted Yield(d) x mean_d[RPI] = District Predicted Yield(d)')
p('The conservation property is the key control: the grid map refines the district prediction rather than contradicting it. If area-weighted averages are required, the same proof applies when the productivity normalization and aggregation use matching cell-area weights.')

h('11. Visualization of Predicted Yield')
p('The final grid-level estimates are visualized within the Madhya Pradesh administrative boundary using an ordered color gradient, with a clearly labelled yield unit and legend. A perceptually ordered palette should map lower predicted yield to lighter or cooler tones and higher yield to darker or warmer tones, while retaining sufficient contrast for print and screen use. District boundaries may be overlaid lightly to maintain administrative context without obscuring the grid signal.')
p('Approximately 1.6 million grid cells form the final visualization. Rendering should be optimized using tiled layers, aggregation at smaller map scales, or server-side visualization so that the map remains responsive. The map is an analytical communication product; legend breaks, missing-data treatment and projection must be stated with the exported figure.')
imagefig('report_assets/final_yield_map.png','Figure 7. Grid-level predicted wheat yield map for Madhya Pradesh at 500 m resolution.',5.85)

h('12. Advantages and Limitations')
h('12.1 Advantages',2)
table(['Advantage','Practical significance'],[['High spatial resolution','Reveals environmental variability that district averages conceal.'],['Satellite-enabled','Uses consistent, repeatable observations across a large region.'],['Automation through GEE','Supports scalable extraction and repeatable annual updates.'],['Hybrid design','Combines observed district yield supervision with local spatial evidence.'],['Conservation-aware distribution','RPI preserves district predictions while allowing local differentiation.']],[2.0,4.5])
h('12.2 Limitations',2)
p('The system depends on the quality, coverage and comparability of historical yield records. It does not directly include fertilizer application, cultivar, pest and disease incidence, irrigation operations, soil nutrients or farm management, each of which can materially affect yield. Satellite indicators can be affected by cloud contamination, temporal sampling, mixed pixels and imperfect correspondence between canopy signal and harvested output. Finally, RPI weights and the assumption that environmental productivity can proportionately distribute district yield are modeling assumptions that require sensitivity assessment and cautious interpretation.')

h('13. Future Scope')
p('Future work can improve spatial and temporal fidelity by incorporating Sentinel-2 imagery, which offers higher-resolution optical observations where cloud-free coverage is available. Daily weather variables, growing-degree days, heat stress and rainfall timing could distinguish beneficial and harmful precipitation patterns that a seasonal mean cannot capture. Field- or survey-level yield data would enable direct calibration of grid-scale estimates.')
p('Methodologically, sequence models or hybrid deep-learning approaches may be evaluated when longer and denser time series are available. Explainable AI techniques such as SHAP can make district-model behavior more transparent to stakeholders. A real-time prediction pipeline and web dashboard could expose current-season indicators, uncertainty layers and district summaries to decision makers, subject to appropriate validation and governance.')

h('14. Conclusion')
p('This project establishes a coherent methodology for high-resolution wheat yield prediction in Madhya Pradesh. It begins with seasonally relevant satellite observations and historical district yield data, creates time-aware features, and uses XGBoost to estimate district-level wheat yield. It then generates a 500 x 500 m grid, extracts local environmental conditions, and constructs a Relative Productivity Index that measures each cell against its district mean.')
p('By design, multiplying district predictions by the RPI produces local variation without changing the district average prediction. The result is a high-resolution yield map grounded in observed district statistics and local satellite-derived conditions. The framework is scalable and interpretable, while its limitations make clear that grid-level estimates are environmentally informed spatial allocations rather than substitutes for field-measured yield. Further validation, added agronomic data and uncertainty analysis are the appropriate next steps before operational deployment.')

h('15. References')
p('Department of Agriculture and Farmers Welfare, Government of India. Crop Area, Production and Yield Report portal (DESAGRI). Available at: https://data.desagri.gov.in/website/crops-apy-report-web (accessed [insert date]).')
p('GADM. Global Administrative Areas database. Available at: https://gadm.org/ (accessed [insert date]).')
p('Google Earth Engine. Earth Engine Data Catalog and developer documentation. Available at: https://developers.google.com/earth-engine (accessed [insert date]).')
p('Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 785-794.')
p('Huete, A. et al. (2002). Overview of the radiometric and biophysical performance of the MODIS vegetation indices. Remote Sensing of Environment, 83(1-2), 195-213.')
p('Tucker, C. J. (1979). Red and photographic infrared linear combinations for monitoring vegetation. Remote Sensing of Environment, 8(2), 127-150.')

# Header/footer
for section in doc.sections:
    header=section.header.paragraphs[0]; header.text='KPMG Internship Project | High-Resolution Wheat Yield Prediction System'; header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    header.runs[0].font.size=Pt(8); header.runs[0].font.color.rgb=RGBColor(89,89,89)
    footer=section.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER; footer.add_run('Page '); field(footer,'PAGE')

doc.core_properties.title='High-Resolution Wheat Yield Prediction System using XGBoost and Google Earth Engine'
doc.core_properties.subject='B.Tech Project Documentation Report'
doc.core_properties.author='[Student Name]'
doc.save(OUT)
print(OUT)
