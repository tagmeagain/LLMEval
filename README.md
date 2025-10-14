# DeepEval - Multi-Turn Conversational AI Testing Framework

Automated evaluation system for comparing LLM chatbot models using 7 comprehensive quality metrics.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your Models
Edit `config.py`:
```python
BASE_MODEL = {
    "name": "gpt-4o-mini",
    "api_key": "your-api-key"
}

FINETUNED_MODEL = {
    "name": "your-finetuned-model",
    "api_key": "your-api-key"
}
```

### 3. Set Your System Prompt
Edit `system_prompt.txt` with your chatbot's role definition.

### 4. Prepare Test Cases
Create Excel file in `input/` with these columns:

**For Pre-recorded Responses:**
- `Initial Conversation` (JSON format, optional)
- `User Query` (required)
- `Model A Response` (required)
- `Model B Response` (required)
- `Chatbot Role` (optional)

**For On-the-fly Generation:**
- `Initial Conversation` (JSON format, optional)
- `User Query` (required)
- `Chatbot Role` (optional)

### 5. Run Evaluation
```bash
python evaluate.py input/your_test.xlsx
```

### 6. Analyze Results
```bash
python analysis.py evaluation_result/your_test_results.json
```

---

## 📊 The 7 Metrics

Each conversation is evaluated on:

1. **Coherence** - Logical flow and structure
2. **Contextual Understanding** - Context awareness
3. **Helpfulness** - Practical value
4. **Knowledge Retention** - Memory tracking
5. **Turn Relevancy** - Response relevance
6. **Role Adherence** - Character consistency
7. **Conversation Completeness** - Full resolution

Threshold: **0.5** for all metrics (Pass/Fail)

---

## 📁 Output Files

After evaluation, you get:

**Results:**
- `evaluation_result/test_results.json` - Full evaluation data
- `evaluation_result/test_metrics_only.json` - Clean metrics summary
- `evaluation_result/test_summary.md` - Markdown summary

**Analysis (after running analysis.py):**
- Excel reports (detailed + executive summary)
- Charts (metric comparison, heatmaps, improvement analysis)
- Insights report (recommendations)

---

## 📚 Documentation

### User Guides
- **[Metrics Guide](docs/guides/metrics-guide.md)** - Understanding each metric
- **[Metric Calculation](docs/guides/metric-calculation.md)** - How metrics are calculated
- **[System Prompt Guide](docs/guides/system-prompt.md)** - Using system prompts
- **[Analysis Guide](docs/guides/analysis-guide.md)** - Analyzing results

### Reference
- **[Commands Reference](docs/reference/commands.md)** - All CLI commands
- **[Excel Conversion](docs/reference/conversion.md)** - Format conversion guide

### Advanced
- **[Technical Architecture](docs/advanced/technical-architecture.md)** - System internals

---

## 💡 Common Use Cases

### Compare Base vs Fine-tuned Model
```bash
# Use pre-recorded responses
python evaluate.py input/comparison_test.xlsx
python analysis.py evaluation_result/comparison_test_results.json
```

### Generate Responses and Evaluate
```bash
# Models generate responses on-the-fly
python evaluate.py input/queries.xlsx --mode generate
```

### Custom Judge Model
```bash
python evaluate.py input/test.xlsx --judge gpt-4
```

### With Logging
```bash
python run_evaluation_with_log.py input/test.xlsx
python run_analysis_with_log.py evaluation_result/test_results.json
```

---

## 🎯 Key Features

✅ **Automated Testing** - No manual evaluation needed  
✅ **Comprehensive Metrics** - 7 quality dimensions  
✅ **Model Comparison** - Side-by-side base vs fine-tuned  
✅ **Batch Processing** - Test multiple conversations at once  
✅ **Rich Analysis** - Charts, Excel reports, insights  
✅ **Flexible** - Pre-recorded or generated responses  

---

## 📖 Learn More

- [Metrics Guide](docs/guides/metrics-guide.md) - Understand the 7 metrics
- [Metric Calculation Flow](docs/guides/metric-calculation.md) - See what data is evaluated
- [Commands Reference](docs/reference/commands.md) - Complete command guide

---

## 🛠️ Requirements

- Python 3.8+
- OpenAI API key (or compatible LLM provider)
- Dependencies: `pip install -r requirements.txt`

---

## 📞 Support

For detailed documentation, see the `docs/` directory.

**Quick Help:**
- Installation issues? Check `requirements.txt`
- Excel format? See [Conversion Guide](docs/reference/conversion.md)
- Understanding metrics? See [Metrics Guide](docs/guides/metrics-guide.md)
- System architecture? See [Technical Architecture](docs/advanced/technical-architecture.md)

---

**Last Updated:** October 14, 2025
