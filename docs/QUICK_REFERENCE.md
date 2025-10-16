# Quick Reference Guide

## ⚡ Essential Commands

### Run Evaluation
```bash
# Basic evaluation (console output only)
python evaluate.py input/test.xlsx

# With logging to timestamped file (RECOMMENDED)
python run_evaluation_with_log.py input/test.xlsx

# Custom judge model with logging
python run_evaluation_with_log.py input/test.xlsx --judge gpt-4o

# Generate mode with logging
python run_evaluation_with_log.py input/queries.xlsx --mode generate

# Verbose mode with logging
python run_evaluation_with_log.py input/test.xlsx --verbose
```

### Analyze Results
```bash
# Basic analysis (console output only)
python analysis.py evaluation_result/test_results.json

# With logging to timestamped file (RECOMMENDED)
python run_analysis_with_log.py evaluation_result/test_results.json

# Custom output directory with logging
python run_analysis_with_log.py evaluation_result/test_results.json custom_output
```

### View Logs
```bash
# View latest evaluation log
cat $(ls -t logs/evaluation_*.log | head -1)

# View latest analysis log
cat $(ls -t logs/analysis_*.log | head -1)

# List all logs with sizes
ls -lh logs/

# Search logs for errors
grep -i error logs/*.log
```

---

## 📋 Excel Format

### Prerecorded Mode
| Initial Conversation | User Query | Model A Response | Model B Response | Chatbot Role |
|---------------------|------------|------------------|------------------|--------------|
| `[]` or JSON | Required | Required | Required | Optional |

### Generate Mode
| Initial Conversation | User Query | Chatbot Role |
|---------------------|------------|--------------|
| `[]` or JSON | Required | Optional |

---

## 📊 Metrics Summary

| Metric | What It Measures | Threshold |
|--------|------------------|-----------|
| Coherence | Logical flow | 0.5 |
| Contextual Understanding | Context awareness | 0.5 |
| Helpfulness | Practical value | 0.5 |
| Human Tonality | Natural, human-like tone | 0.5 |
| Knowledge Retention | Memory | 0.5 |
| Turn Relevancy | Relevance | 0.5 |
| Role Adherence | Character consistency | 0.5 |
| Conversation Completeness | Full resolution | 0.5 |

---

## 📁 Output Files

### After Evaluation
```
evaluation_result/
├── test_results.json          ← Full results
├── test_metrics_only.json     ← Clean metrics
└── test_summary.md            ← Markdown summary
```

### After Analysis
```
analysis_output/
├── test_results_detailed_analysis.xlsx
├── test_results_executive_summary.xlsx
├── test_results_insights_report.txt
└── charts/
    ├── metric_comparison.png
    ├── performance_distribution.png
    ├── metrics_heatmap.png
    └── improvement_analysis.png
```

---

## 🎯 Score Interpretation

- **0.9-1.0**: Excellent ⭐⭐⭐
- **0.7-0.9**: Good ⭐⭐
- **0.5-0.7**: Acceptable ⭐
- **<0.5**: Needs Improvement ❌

---

## 📚 Full Documentation

See [Documentation Index](README.md) for complete guides.

