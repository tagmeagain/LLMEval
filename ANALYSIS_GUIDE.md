# Analysis & Visualization Guide for CXO Presentations

## Overview

The `analysis.py` tool transforms DeepEval evaluation results into **CXO-ready presentations** with:
- ✅ Comprehensive Excel reports with all metrics
- ✅ Professional charts and graphs
- ✅ Executive insights and recommendations
- ✅ Separate output folder for easy sharing

## 🚀 Quick Start

### Step 1: Run Your Evaluation
```bash
python evaluate.py input/your_file.xlsx
```
This creates: `evaluation_result/your_file_results.json`

### Step 2: Generate Analysis
```bash
python analysis.py evaluation_result/your_file_results.json
```

That's it! All outputs will be in `analysis_output/`

---

## 📊 What You Get

### Excel Reports (2 files)

#### 1. Detailed Analysis Excel
**File:** `*_detailed_analysis.xlsx`

Contains **everything** in a single sheet:
- Test Case names
- Initial Conversation (full text)
- User Query
- Model A Response (complete)
- Model B Response (complete)
- Chatbot Role (first 100 words)
- **ALL metrics for Model A** (Score, Pass/Fail, Reason)
- **ALL metrics for Model B** (Score, Pass/Fail, Reason)

**Perfect for:** Deep dive analysis, debugging, understanding specific conversations

#### 2. Executive Summary Excel
**File:** `*_executive_summary.xlsx`

Contains **2 sheets:**

**Sheet 1: Metric Averages**
| Metric | Model A Avg | Model B Avg | Difference (B-A) | Winner |
|--------|-------------|-------------|------------------|--------|
| Coherence | 0.850 | 0.920 | +0.070 | Model B |
| Role Adherence | 0.780 | 0.850 | +0.070 | Model B |

**Sheet 2: All Test Cases**
- Score comparison for each test case across all metrics
- Side-by-side Model A vs Model B

**Perfect for:** CXO presentations, executive reviews

---

### Charts & Graphs (4 files)

All charts saved in `analysis_output/charts/`

#### 1. Metric Comparison Chart
**File:** `metric_comparison.png`

Bar chart comparing Model A vs Model B across all 7 metrics
- Blue bars = Model A
- Green bars = Model B
- Values displayed on each bar
- Easy to see which model performs better

**Use case:** Show overall performance comparison

#### 2. Winner Distribution Pie Chart
**File:** `winner_distribution.png`

Pie chart showing:
- % of metrics where Model B wins
- % of metrics where Model A wins
- % of ties

**Use case:** Quick visual summary of which model is better

#### 3. Metrics Heatmap
**File:** `metrics_heatmap.png`

Two heatmaps side-by-side:
- Left: Model A scores across all test cases and metrics
- Right: Model B scores across all test cases and metrics
- Color-coded: Red (low) → Yellow (medium) → Green (high)

**Use case:** Identify patterns, weak spots, strong areas

#### 4. Improvement Analysis Chart
**File:** `improvement_analysis.png`

Horizontal bar chart showing:
- Green bars = Model B improved over Model A
- Red bars = Model B regressed from Model A
- Sorted by improvement magnitude

**Use case:** Highlight which metrics improved/regressed

---

### Insights Report (1 file)

**File:** `*_insights_report.txt`

Auto-generated text report with:

1. **Overall Performance Stats**
   - Total metrics evaluated
   - Model B wins/losses
   - Win percentages

2. **Top 3 Improvements**
   - Metrics where Model B improved most
   - Exact score differences

3. **Areas Needing Attention**
   - Metrics where Model B underperformed
   - Opportunities for improvement

4. **Key Recommendations**
   - Data-driven recommendations
   - Production deployment guidance

**Perfect for:** Executive summary, email reports, presentations

---

## 💼 CXO Presentation Workflow

### Scenario 1: Quick Executive Review

```bash
# 1. Generate analysis
python analysis.py evaluation_result/results.json

# 2. Share these files:
analysis_output/
├── *_executive_summary.xlsx  ← Share this
├── charts/
│   ├── metric_comparison.png  ← Share this
│   └── winner_distribution.png  ← Share this
└── *_insights_report.txt  ← Share this
```

**Time to prepare:** 30 seconds  
**Impact:** High-level overview with clear recommendations

---

### Scenario 2: Detailed Technical Review

```bash
# Share all files including:
analysis_output/
├── *_detailed_analysis.xlsx  ← Deep dive data
├── *_executive_summary.xlsx  ← Summary
├── charts/
│   ├── metric_comparison.png
│   ├── winner_distribution.png
│   ├── metrics_heatmap.png  ← Pattern analysis
│   └── improvement_analysis.png  ← Detailed improvements
└── *_insights_report.txt
```

**Time to prepare:** 30 seconds  
**Impact:** Complete analysis for decision-making

---

### Scenario 3: Board Presentation

```bash
# 1. Generate analysis
python analysis.py evaluation_result/results.json

# 2. Insert charts into PowerPoint:
- Slide 1: Winner distribution pie chart
- Slide 2: Metric comparison bar chart
- Slide 3: Key insights from insights_report.txt
- Slide 4: Heatmap showing detailed performance
- Slide 5: Improvement analysis
```

**Time to prepare:** 5 minutes  
**Impact:** Professional, data-driven presentation

---

## 🎯 Advanced Usage

### Custom Output Directory
```bash
python analysis.py evaluation_result/results.json my_custom_folder
```
Output will be in: `my_custom_folder/`

### Multiple Evaluations
```bash
# Run for multiple results
python analysis.py evaluation_result/test1_results.json analysis_test1
python analysis.py evaluation_result/test2_results.json analysis_test2

# Compare folders side-by-side
```

### Batch Processing
```bash
# Create shell script
for file in evaluation_result/*_results.json; do
    python analysis.py "$file"
done
```

---

## 📋 Excel Column Mapping

### Detailed Analysis Excel Columns:

1. `Test Case` - Name/ID of the test case
2. `Initial Conversation` - Full conversation history
3. `User Query` - The user's question
4. `Model A Response` - Complete response from Model A
5. `Model B Response` - Complete response from Model B
6. `Chatbot Role (100 words)` - First 100 words of system prompt/role

**For each metric (7 total):**
- `Model A - [Metric] Score` - Numerical score (0-1)
- `Model A - [Metric] Pass` - True/False
- `Model A - [Metric] Reason` - Detailed reasoning from judge
- `Model B - [Metric] Score` - Numerical score (0-1)
- `Model B - [Metric] Pass` - True/False
- `Model B - [Metric] Reason` - Detailed reasoning from judge

**Total columns:** ~50 columns (comprehensive!)

---

## 🎨 Chart Customization

Charts use professional styling:
- **Colors:**
  - Model A: Blue (#3498db)
  - Model B: Green (#2ecc71)
  - Positive: Green (#2ecc71)
  - Negative: Red (#e74c3c)

- **Format:**
  - High DPI (300 dpi) for print quality
  - PNG format for universal compatibility
  - Whitegrid style for readability

- **Size:**
  - Standard charts: 12x6 inches
  - Heatmaps: 18x8 inches
  - Large enough for presentations

---

## 🔧 Troubleshooting

### "No module named 'matplotlib'"
```bash
pip install matplotlib seaborn numpy
# Or
pip install -r requirements.txt
```

### "File not found" error
```bash
# Make sure the results file exists
ls -la evaluation_result/*_results.json

# Use full path
python analysis.py evaluation_result/your_file_results.json
```

### Charts look blurry in presentation
- Charts are saved at 300 DPI (print quality)
- Use PNG files directly in PowerPoint/Google Slides
- Don't resize too much - use original size

### Excel columns too narrow
- Columns auto-adjust to content
- Capped at 100 characters width for readability
- Manually adjust in Excel if needed

---

## 💡 Best Practices

### 1. Run Analysis Immediately After Evaluation
```bash
# Right after evaluation
python evaluate.py input/file.xlsx
python analysis.py evaluation_result/file_results.json
```

### 2. Use Descriptive Names
```bash
# Name your input files descriptively
input/customer_support_v1.xlsx
input/customer_support_v2.xlsx

# Analysis outputs will have matching names
```

### 3. Archive Analysis Results
```bash
# Create dated folders
mkdir analysis_2025_01_15
python analysis.py evaluation_result/results.json analysis_2025_01_15
```

### 4. Share Complete Package
```bash
# Zip the analysis folder
zip -r analysis_results.zip analysis_output/

# Share via email/cloud
```

---

## 📊 Example Output Structure

```
analysis_output/
├── charts/
│   ├── metric_comparison.png          (14x8 inches, 300 DPI)
│   ├── winner_distribution.png        (10x8 inches, 300 DPI)
│   ├── metrics_heatmap.png            (18x8 inches, 300 DPI)
│   └── improvement_analysis.png       (14x8 inches, 300 DPI)
├── file_results_detailed_analysis.xlsx     (~5-50 MB depending on data)
├── file_results_executive_summary.xlsx     (~100-500 KB)
└── file_results_insights_report.txt        (~2-5 KB, plain text)
```

---

## 🎓 Understanding the Metrics

### Scores Range: 0.0 to 1.0
- **0.0 - 0.3**: Poor performance
- **0.3 - 0.5**: Below average
- **0.5 - 0.7**: Average/Acceptable
- **0.7 - 0.9**: Good performance
- **0.9 - 1.0**: Excellent performance

### Difference Interpretation
- **+0.10 or more**: Significant improvement
- **+0.05 to +0.10**: Moderate improvement
- **±0.05**: Marginal difference
- **-0.05 to -0.10**: Moderate regression
- **-0.10 or less**: Significant regression

---

## ✅ Complete Workflow Example

```bash
# 1. Setup (one time)
pip install -r requirements.txt
cp env_template.txt .env
# Edit .env with your API key

# 2. Prepare your data
python convert_excel_format.py input/my_tests.xlsx

# 3. Run evaluation
python evaluate.py input/my_tests_converted.xlsx --judge gpt-4

# 4. Generate CXO analysis
python analysis.py evaluation_result/my_tests_converted_results.json

# 5. Review outputs
open analysis_output/  # On Mac
explorer analysis_output\  # On Windows
xdg-open analysis_output/  # On Linux

# 6. Share with CXOs
zip -r cxo_presentation.zip analysis_output/
```

---

## 🎯 Key Takeaways

✅ **One command** generates complete CXO-ready analysis  
✅ **No code changes** - separate tool, doesn't affect evaluations  
✅ **Professional visualizations** - publication-quality charts  
✅ **Comprehensive Excel** - all data in organized format  
✅ **Auto-generated insights** - data-driven recommendations  
✅ **Separate folder** - easy to share, archive, present  

**Perfect for:** Executive reviews, board presentations, decision-making, progress tracking

---

## Support

For technical details about the evaluation: See `README.md`  
For conversion help: See `CONVERSION_GUIDE.md`  
For architecture: See `TECHNICAL_ARCHITECTURE.md`

