# Logging Guide - DeepEval

## Overview
This guide explains how to capture all evaluation and analysis output to timestamped log files.

---

## 📝 Quick Start

### Option 1: Using Log Wrapper Scripts (Recommended)

**For Evaluation:**
```bash
python run_evaluation_with_log.py input/test.xlsx
```

**For Analysis:**
```bash
python run_analysis_with_log.py evaluation_result/test_results.json
```

### Option 2: Manual Redirect (Shell)

**For Evaluation:**
```bash
# Bash/Zsh
python evaluate.py input/test.xlsx 2>&1 | tee logs/evaluation_$(date +%Y%m%d_%H%M%S).log
```

**For Analysis:**
```bash
# Bash/Zsh
python analysis.py evaluation_result/test_results.json 2>&1 | tee logs/analysis_$(date +%Y%m%d_%H%M%S).log
```

---

## 🎯 Log Wrapper Scripts

### run_evaluation_with_log.py

**What it does:**
- Runs `evaluate.py` with your arguments
- Captures ALL output (stdout + stderr)
- Saves to timestamped log file in `logs/` directory
- Shows output in console AND saves to file simultaneously
- Adds header/footer with timestamps

**Usage:**
```bash
# Basic usage
python run_evaluation_with_log.py input/test.xlsx

# With options
python run_evaluation_with_log.py input/test.xlsx --judge gpt-4o-mini --metrics all

# Multiple files
python run_evaluation_with_log.py input/test1.xlsx input/test2.xlsx
```

**Output:**
```
📝 Starting evaluation...
📁 Log file: logs/evaluation_20251014_143025.log
🔄 Running: python evaluate.py input/test.xlsx

================================================================================
OUTPUT:
================================================================================

[... evaluation output shown here AND saved to log ...]

================================================================================
✅ Evaluation complete!
📁 Full log saved to: logs/evaluation_20251014_143025.log
================================================================================
```

### run_analysis_with_log.py

**What it does:**
- Runs `analysis.py` with your arguments
- Captures ALL output
- Saves to timestamped log file in `logs/` directory
- Shows output in console AND saves to file simultaneously

**Usage:**
```bash
# Basic usage
python run_analysis_with_log.py evaluation_result/test_results.json

# Custom output directory
python run_analysis_with_log.py evaluation_result/test_results.json custom_output
```

---

## 📂 Log File Structure

### Log Directory
```
logs/
├── evaluation_20251014_120000.log
├── evaluation_20251014_130000.log
├── analysis_20251014_120500.log
└── analysis_20251014_130500.log
```

### Log File Format
```
================================================================================
DeepEval Evaluation Log
Timestamp: 2025-10-14 14:30:25
Command: python evaluate.py input/test.xlsx --judge gpt-4o-mini
================================================================================

[... all evaluation output ...]

================================================================================
Evaluation completed with exit code: 0
End time: 2025-10-14 14:35:42
================================================================================
```

---

## 🔧 Advanced Usage

### File-Only Logging (No Console Output)

**Evaluation:**
```bash
python evaluate.py input/test.xlsx > logs/evaluation_$(date +%Y%m%d_%H%M%S).log 2>&1
```

**Analysis:**
```bash
python analysis.py evaluation_result/test_results.json > logs/analysis_$(date +%Y%m%d_%H%M%S).log 2>&1
```

### Separate Error Logs

```bash
# Save output and errors to separate files
python evaluate.py input/test.xlsx \
    > logs/evaluation_output.log \
    2> logs/evaluation_errors.log
```

### Append to Existing Log

```bash
python evaluate.py input/test.xlsx >> logs/combined.log 2>&1
```

---

## 📊 Log Analysis

### View Latest Log

**Latest Evaluation Log:**
```bash
# Linux/Mac
cat logs/evaluation_*.log | tail -1

# Or use:
ls -t logs/evaluation_*.log | head -1 | xargs cat
```

**Latest Analysis Log:**
```bash
ls -t logs/analysis_*.log | head -1 | xargs cat
```

### Search Logs

**Find Errors:**
```bash
grep -i error logs/*.log
grep -i "❌" logs/*.log
```

**Find Specific Metric:**
```bash
grep -i "coherence" logs/evaluation_*.log
```

**Check Pass/Fail:**
```bash
grep -i "pass rate" logs/*.log
```

### Monitor Live Log

```bash
# In one terminal - run with logging
python run_evaluation_with_log.py input/test.xlsx

# In another terminal - monitor the log
tail -f logs/evaluation_*.log
```

---

## 🎨 Log File Features

### Included in Logs:

✅ **Full Command** - Exact command that was run  
✅ **Timestamp** - Start and end times  
✅ **All Output** - Every print statement and message  
✅ **Errors** - stderr captured along with stdout  
✅ **Exit Code** - Success/failure status  
✅ **Unicode Support** - Emojis and special characters  

### Log Contains:

- Configuration details
- File processing progress
- Metric evaluation results
- Error messages and warnings
- Summary statistics
- Output file locations
- Execution time

---

## 🧹 Log Management

### Clean Old Logs

**Delete logs older than 7 days:**
```bash
find logs/ -name "*.log" -mtime +7 -delete
```

**Keep only last 10 logs:**
```bash
ls -t logs/*.log | tail -n +11 | xargs rm
```

**Archive old logs:**
```bash
tar -czf logs_archive_$(date +%Y%m%d).tar.gz logs/*.log
rm logs/*.log
```

### View Log Size

```bash
du -sh logs/
ls -lh logs/
```

---

## 💡 Tips & Best Practices

### 1. Use Descriptive Names

Add test name to log filename:
```bash
python evaluate.py input/customer_support_test.xlsx \
    > logs/evaluation_customer_support_$(date +%Y%m%d_%H%M%S).log 2>&1
```

### 2. Separate Test Runs

Create subdirectories for different test suites:
```bash
mkdir -p logs/production_tests
mkdir -p logs/experimental_tests

python run_evaluation_with_log.py input/prod_test.xlsx
# Then move: mv logs/evaluation_*.log logs/production_tests/
```

### 3. Include Git Commit Info

Add version info to logs:
```bash
(
  echo "Git commit: $(git rev-parse HEAD)"
  echo "Branch: $(git rev-parse --abbrev-ref HEAD)"
  echo "Date: $(date)"
  echo "===================="
  python evaluate.py input/test.xlsx
) > logs/evaluation_with_version.log 2>&1
```

### 4. Email Logs on Completion

```bash
python run_evaluation_with_log.py input/test.xlsx
mail -s "Evaluation Complete" your@email.com < logs/evaluation_*.log
```

### 5. Continuous Integration

For CI/CD pipelines:
```bash
#!/bin/bash
set -e

LOG_FILE="logs/ci_evaluation_$(date +%Y%m%d_%H%M%S).log"

python evaluate.py input/test.xlsx > "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Tests passed"
    cat "$LOG_FILE" | grep "SUMMARY"
else
    echo "❌ Tests failed"
    cat "$LOG_FILE"
    exit 1
fi
```

---

## 🔍 Troubleshooting

### Log File Not Created

**Issue:** No log file appears  
**Solution:** Check logs/ directory exists
```bash
mkdir -p logs
```

### Permission Denied

**Issue:** Can't write to logs/  
**Solution:** Fix permissions
```bash
chmod 755 logs/
```

### Incomplete Logs

**Issue:** Log cuts off early  
**Solution:** Ensure script completes, use `tee` for live viewing
```bash
python evaluate.py input/test.xlsx 2>&1 | tee logs/evaluation.log
```

### Unicode Characters Missing

**Issue:** Emojis show as `?`  
**Solution:** Ensure UTF-8 encoding
```bash
export PYTHONIOENCODING=utf-8
python run_evaluation_with_log.py input/test.xlsx
```

---

## 📋 Summary

| Method | Console Output | File Output | Timestamp | Ease of Use |
|--------|---------------|-------------|-----------|-------------|
| `run_evaluation_with_log.py` | ✅ Yes | ✅ Yes | ✅ Auto | ⭐⭐⭐⭐⭐ Easy |
| `> file.log` redirect | ❌ No | ✅ Yes | ⚠️ Manual | ⭐⭐⭐ Medium |
| `tee file.log` | ✅ Yes | ✅ Yes | ⚠️ Manual | ⭐⭐⭐⭐ Easy |

**Recommendation:** Use `run_evaluation_with_log.py` and `run_analysis_with_log.py` for best experience! 

---

## 🚀 Quick Commands

```bash
# Run evaluation with logging
python run_evaluation_with_log.py input/test.xlsx

# Run analysis with logging
python run_analysis_with_log.py evaluation_result/test_results.json

# View latest evaluation log
cat $(ls -t logs/evaluation_*.log | head -1)

# View latest analysis log
cat $(ls -t logs/analysis_*.log | head -1)

# Find errors in all logs
grep -i error logs/*.log

# Clean old logs (7+ days)
find logs/ -name "*.log" -mtime +7 -delete
```

---

**Last Updated:** October 14, 2025  
**Framework:** DeepEval Multi-Turn Conversation Testing

