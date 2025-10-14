# Quick Reference Guide

## ⚡ Essential Commands

### Run Evaluation
```bash
# Basic evaluation
python evaluate.py input/test.xlsx

# With logging
python run_evaluation_with_log.py input/test.xlsx

# Custom judge model
python evaluate.py input/test.xlsx --judge gpt-4o

# Generate mode (on-the-fly responses)
python evaluate.py input/queries.xlsx --mode generate
```

### Analyze Results
```bash
# Basic analysis
python analysis.py evaluation_result/test_results.json

# With logging
python run_analysis_with_log.py evaluation_result/test_results.json

# Custom output directory
python analysis.py evaluation_result/test_results.json custom_output
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

