# Usage Examples - All Ways to Run

## 🎯 Quick Reference

| What You Want | Command |
|---------------|---------|
| **Auto-detect everything** | `python3 evaluate.py input/test.xlsx` |
| **Force generate responses** | `python3 evaluate.py input/test.xlsx --mode generate` |
| **Force use Excel responses** | `python3 evaluate.py input/test.xlsx --mode prerecorded` |
| **Process all files** | `python3 evaluate.py` |
| **Multiple specific files** | `python3 evaluate.py test1.xlsx test2.xlsx` |
| **Custom judge model** | `python3 evaluate.py input/test.xlsx --judge gpt-4` |
| **Only built-in metrics** | `python3 evaluate.py input/test.xlsx --metrics builtin` |
| **Custom everything** | `python3 evaluate.py input/test.xlsx -m generate -j gpt-4 -s custom.txt` |

---

## 📖 Detailed Examples

### Example 1: Auto-Detect Mode (Recommended)

**Scenario**: Let the script decide what to do

```bash
# Process single file
python3 evaluate.py input/customer_support.xlsx

# What happens:
# - Checks if Model A/B Response columns exist
# - If YES: Uses pre-recorded responses
# - If NO: Generates responses on-the-fly
# - Evaluates with all 7 metrics
```

---

### Example 2: Force Generate Mode

**Scenario**: You want fresh responses even if Excel has some

```bash
python3 evaluate.py input/queries.xlsx --mode generate

# What happens:
# - Ignores any existing Model A/B responses
# - Calls gpt-5-nano (Model A) to generate responses
# - Calls gpt-5-nano (Model B) to generate responses
# - Evaluates both with all 7 metrics
# - Saves responses to Excel
```

**Excel needed**:
| User Query |
|------------|
| I can't log in |
| I need help |

---

### Example 3: Force Pre-Recorded Mode

**Scenario**: You only want to evaluate existing responses

```bash
python3 evaluate.py input/conversations.xlsx --mode prerecorded

# What happens:
# - Validates Model A/B Response columns exist
# - Errors if columns missing
# - Uses only pre-recorded responses
# - No model generation calls
# - Evaluates with all 7 metrics
```

**Excel needed**:
| User Query | Model A Response | Model B Response |
|------------|------------------|------------------|
| I can't log in | Try resetting | Let me help you... |

---

### Example 4: Multiple Files (Batch)

**Scenario**: Evaluate several test files at once

```bash
# Specific files
python3 evaluate.py input/test1.xlsx input/test2.xlsx input/test3.xlsx

# All files in input/
python3 evaluate.py

# What happens:
# - Processes each file independently
# - Auto-detects mode for each file
# - Saves individual results + combined summary
```

---

### Example 5: Custom Judge Model

**Scenario**: Use different LLM as judge

```bash
# Use GPT-4 as judge
python3 evaluate.py input/test.xlsx --judge gpt-4

# Use GPT-3.5 as judge (faster)
python3 evaluate.py input/test.xlsx --judge gpt-3.5-turbo

# What happens:
# - All 7 metrics use specified judge model
# - Changes evaluation quality/speed
```

---

### Example 6: Select Metrics

**Scenario**: Use fewer metrics

```bash
# Only 4 built-in metrics (faster)
python3 evaluate.py input/test.xlsx --metrics builtin

# All 7 metrics (default)
python3 evaluate.py input/test.xlsx --metrics all

# What happens:
# builtin: Only Knowledge Retention, Turn Relevancy, Role Adherence, Completeness
# all: Above 4 + Coherence, Contextual Understanding, Helpfulness
```

---

### Example 7: Custom System Prompt

**Scenario**: Use different system prompt for different tests

```bash
# Custom location
python3 evaluate.py input/test.xlsx --system-prompt prompts/technical_support.txt

# Short form
python3 evaluate.py input/test.xlsx -s prompts/sales_agent.txt

# What happens:
# - Loads specified prompt file
# - Uses it for model generation (if generate mode)
# - Uses it for evaluation context
```

---

### Example 8: Custom Output Directory

**Scenario**: Save results to specific location

```bash
# Custom output
python3 evaluate.py input/test.xlsx --output results_2024_10_11

# Short form
python3 evaluate.py input/test.xlsx -o my_results

# What happens:
# - Creates specified directory
# - Saves all results there
# - Useful for versioning/organizing
```

---

### Example 9: Verbose Mode

**Scenario**: See detailed processing information

```bash
python3 evaluate.py input/test.xlsx --verbose

# Short form
python3 evaluate.py input/test.xlsx -v

# What happens:
# - Shows detailed logging
# - Displays all intermediate steps
# - Helpful for debugging
```

---

### Example 10: Combined Options (Advanced)

**Scenario**: Maximum control over evaluation

```bash
python3 evaluate.py input/queries.xlsx \
  --mode generate \
  --system-prompt prompts/support_agent.txt \
  --judge gpt-4 \
  --metrics all \
  --output results_$(date +%Y%m%d_%H%M) \
  --verbose

# What happens:
# - Forces generation mode
# - Uses custom system prompt
# - Uses GPT-4 as judge
# - Uses all 7 metrics
# - Saves to timestamped directory
# - Shows verbose output
```

---

### Example 11: Testing Different Configurations

**Scenario**: Compare different judge models

```bash
# Test 1: GPT-4 as judge
python3 evaluate.py input/test.xlsx --judge gpt-4 --output results_gpt4

# Test 2: GPT-3.5 as judge
python3 evaluate.py input/test.xlsx --judge gpt-3.5-turbo --output results_gpt35

# Test 3: Custom model
python3 evaluate.py input/test.xlsx --judge gpt-5-nano --output results_nano

# Compare results
diff results_gpt4/test_results.json results_gpt35/test_results.json
```

---

### Example 12: CI/CD Integration

**Scenario**: Automated testing in pipeline

```bash
#!/bin/bash
# ci_test.sh

# Activate environment
source venv/bin/activate

# Run evaluation
python3 evaluate.py input/regression_tests.xlsx \
  --mode prerecorded \
  --judge gpt-4 \
  --metrics all \
  --output ci_results

# Check if passed
if [ $? -eq 0 ]; then
    echo "✅ Evaluation passed"
    exit 0
else
    echo "❌ Evaluation failed"
    exit 1
fi
```

---

## 🎯 Decision Tree

```
What do you have?
│
├─ Only user queries
│  → python3 evaluate.py input/queries.xlsx --mode generate
│
├─ Queries + Model A/B responses
│  ├─ Want to use existing responses
│  │  → python3 evaluate.py input/conversations.xlsx --mode prerecorded
│  │
│  └─ Want fresh responses
│     → python3 evaluate.py input/conversations.xlsx --mode generate
│
└─ Not sure
   → python3 evaluate.py input/test.xlsx
   (Auto-detect will figure it out!)
```

---

## ✅ Summary

**Primary command** (covers 90% of use cases):
```bash
python3 evaluate.py input/your_file.xlsx
```

**Force specific behavior**:
```bash
# Generate on-the-fly
python3 evaluate.py input/test.xlsx --mode generate

# Use pre-recorded only
python3 evaluate.py input/test.xlsx --mode prerecorded
```

**Customize evaluation**:
```bash
# Different judge
python3 evaluate.py input/test.xlsx --judge gpt-4

# Fewer metrics
python3 evaluate.py input/test.xlsx --metrics builtin

# Custom prompt
python3 evaluate.py input/test.xlsx -s custom.txt
```

**All options available via CLI - no code changes needed!** 🚀

