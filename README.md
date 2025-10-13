# DeepEval Multi-Turn Conversation Testing

LLM-as-a-judge evaluation framework for comparing Model A vs Model B on multi-turn conversations.

## ✨ Key Features

✅ **Excel-Based Testing** - Load test cases from Excel files  
✅ **Excel Format Converter** - Convert your custom Excel format automatically  
✅ **Auto-Mode Detection** - Automatically detects prerecorded vs generate mode  
✅ **System Prompt Integration** - Uses system_prompt.txt as chatbot role  
✅ **7 Evaluation Metrics** - ALL parameters configured with reasoning included  
✅ **LLM-as-a-Judge** - Configurable judge model (GPT-4, GPT-3.5, etc.)  
✅ **Verbose Mode** - See intermediate calculation steps for debugging  
✅ **Batch Processing** - Evaluate multiple Excel files at once  
✅ **Comprehensive Results** - JSON, Markdown, and Excel outputs  

---

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
# Copy template
cp env_template.txt .env

# Edit .env and add your keys:
OPENAI_API_KEY=sk-your-key-here
JUDGE_MODEL=gpt-4
```

### 3. Run Evaluation
```bash
# If you have custom Excel format, convert it first
python convert_excel_format.py input/your_file.xlsx

# Run evaluation (auto-detects prerecorded mode)
python evaluate.py input/your_file_converted.xlsx
```

---

## 📊 The 7 Metrics

All metrics use **LLM-as-a-judge** evaluation with **ALL parameters configured**:

### Custom Conversational Metrics (3)
1. **Coherence** - Logical flow and clarity
2. **Contextual Understanding** - Context awareness and building on previous turns
3. **Helpfulness** - Practical, actionable information

### DeepEval Built-in Multi-Turn Metrics (4)
4. **Knowledge Retention** - Remembers information from earlier turns  
   [📚 Docs](https://deepeval.com/docs/metrics-knowledge-retention)

5. **Turn Relevancy** - Each response is relevant to user query  
   [📚 Docs](https://deepeval.com/docs/metrics-turn-relevancy)

6. **Role Adherence** - Maintains consistent role (uses system_prompt.txt)  
   [📚 Docs](https://deepeval.com/docs/metrics-role-adherence)

7. **Conversation Completeness** - All queries addressed, satisfactory conclusion  
   [📚 Docs](https://deepeval.com/docs/metrics-conversation-completeness)

**All metrics include:**
- ✅ `include_reason=True` - Detailed reasoning for scores
- ✅ `strict_mode=False` - Gradual scores (0-1)
- ✅ `async_mode=True` - Concurrent execution for speed
- ✅ `verbose_mode` - Optional debug output

---

## 📝 Excel Format

### Option 1: Convert Your Custom Format (Recommended)

If you have columns like: `test_id`, `conversation_history`, `query`, `response_A`, `response_B`

```bash
# Convert to required format
python convert_excel_format.py input/your_file.xlsx

# Output: input/your_file_converted.xlsx
```

**Conversion features:**
- ✅ Converts text conversation_history to JSON format
- ✅ Handles Unicode properly (emojis, special characters)
- ✅ Adds default "Chatbot Role" column
- ✅ Maps all columns correctly

See `CONVERSION_GUIDE.md` for details.

### Option 2: Standard Format (Already Correct)

| Initial Conversation | User Query | Model A Response | Model B Response | Chatbot Role |
|---------------------|------------|------------------|------------------|--------------|
| `[{"role":"assistant","content":"Hello"}]` | I can't log in | Sorry to hear... | I understand... | customer support agent |

**Column descriptions:**
- `Initial Conversation` - Prior conversation turns in JSON format (can be empty: `[]`)
- `User Query` - The user's question/message
- `Model A Response` - Base model's response
- `Model B Response` - Finetuned/comparison model's response
- `Chatbot Role` - Role description (auto-uses system_prompt.txt if empty)

---

## 🎮 Usage Examples

### Basic Usage
```bash
# Auto-detect mode and run
python evaluate.py input/your_file.xlsx
```

### With Custom Judge Model
```bash
# Use GPT-4 as judge
python evaluate.py input/file.xlsx --judge gpt-4

# Use GPT-3.5 (cheaper)
python evaluate.py input/file.xlsx --judge gpt-3.5-turbo
```

### With Verbose Mode (See Intermediate Steps)
```bash
# Enable debug output
python evaluate.py input/file.xlsx --verbose

# Short flag
python evaluate.py input/file.xlsx -v
```

### Only 4 Metrics (Cost Savings)
```bash
# Skip custom GEval metrics (use only built-in 4)
python evaluate.py input/file.xlsx --metrics builtin
```

### Multiple Files
```bash
# Batch process
python evaluate.py input/file1.xlsx input/file2.xlsx input/file3.xlsx
```

### All Options Combined
```bash
python evaluate.py input/file.xlsx \
  --judge gpt-4 \
  --metrics all \
  --verbose \
  --mode prerecorded \
  --system-prompt custom_prompt.txt
```

---

## ⚙️ Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=sk-your-key-here
JUDGE_MODEL=gpt-4  # Default judge model
```

### Model Configuration (config.py)
```python
# Base Model
BASE_MODEL = {
    "name": "gpt-4.1-nano",
    "api_key": OPENAI_API_KEY,
    "temperature": 0.7,
    "max_tokens": 500
}

# Finetuned Model
FINETUNED_MODEL = {
    "name": "ft:gpt-3.5-turbo:org:model:id",  # Your finetuned model
    "api_key": OPENAI_API_KEY,
    "temperature": 0.7,
    "max_tokens": 500
}
```

### System Prompt (system_prompt.txt)
The system prompt is **automatically used as the chatbot_role** for Role Adherence metric.

Example:
```
You are a professional customer support agent for TechCorp.
Your responsibilities:
- Be empathetic and professional
- Solve issues efficiently
...
```

---

## 📤 Outputs

For each evaluation, you get:

| File | Description |
|------|-------------|
| `*_results.json` | Full DeepEval output with all metrics |
| `*_metrics_only.json` | Clean scores comparison (Model A vs B) |
| `*_summary.md` | Human-readable markdown summary |
| `*_with_responses.xlsx` | Excel with responses (generate mode only) |

**Example output structure:**
```json
{
  "metric": "Role Adherence",
  "score": 0.85,
  "reason": "The assistant consistently maintained a professional...",
  "pass": true
}
```

---

## 🎯 Command Line Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--mode` | `-m` | Evaluation mode: auto, generate, prerecorded | `auto` |
| `--judge` | `-j` | Judge model (gpt-4, gpt-3.5-turbo, etc.) | From `.env` or `gpt-4.1-nano` |
| `--metrics` | | Metrics to use: all, builtin | `all` |
| `--system-prompt` | `-s` | System prompt file path | `system_prompt.txt` |
| `--output` | `-o` | Output directory | `evaluation_result` |
| `--verbose` | `-v` | Enable verbose mode (shows intermediate steps) | `False` |

---

## 📁 Project Structure

```
DeepEval/
├── evaluate.py                 # Main entry point
├── convert_excel_format.py     # Excel format converter
├── config.py                   # Model configuration
├── excel_loader.py             # Excel → DeepEval test cases
├── multi_turn_testing.py       # Evaluation framework with all metrics
├── model_wrapper.py            # Model API wrapper
├── create_clean_output.py      # Output formatting
├── system_prompt.txt           # Default system prompt (used as chatbot_role)
├── .env                        # API keys and configuration
├── env_template.txt            # Template for .env
├── requirements.txt            # Python dependencies
├── CONVERSION_GUIDE.md         # Excel conversion guide
├── TECHNICAL_ARCHITECTURE.md   # Technical documentation
├── input/                      # Input Excel files
│   └── test_multiple_conversations.xlsx
└── evaluation_result/          # Output files
    └── *.json, *.md, *.xlsx
```

---

## 💡 FAQ

**Q: How do I convert my custom Excel format?**  
A: Run `python convert_excel_format.py input/your_file.xlsx` - See `CONVERSION_GUIDE.md`

**Q: Why am I not getting reasons for metrics?**  
A: Updated! All metrics now include `include_reason=True` parameter.

**Q: How do I change the judge model?**  
A: Set `JUDGE_MODEL=gpt-4` in `.env` or use `--judge gpt-4` flag.

**Q: How do I use my finetuned model?**  
A: Edit `config.py` and change `FINETUNED_MODEL["name"]` to your model ID.

**Q: What if I don't have conversation history?**  
A: Use empty array `[]` in "Initial Conversation" column.

**Q: How do I reduce costs?**  
A: Use `--metrics builtin` (4 metrics instead of 7) or use cheaper judge like `gpt-3.5-turbo`.

**Q: What does verbose mode show?**  
A: Intermediate calculation steps for each metric (useful for debugging).

**Q: Can I test a single model?**  
A: Yes, just use the same model for both Model A and Model B responses.

---

## 🔧 Troubleshooting

### "chatbot_role cannot be empty"
✅ Fixed! System prompt is now automatically used as chatbot_role.

### "No valid conversations found"
- Check that "User Query" column exists
- Ensure cells have content

### "Invalid JSON in Initial Conversation"
- Validate JSON format: `[{"role":"user","content":"..."}]`
- Use the converter if your format is text-based

### Missing reasons in output
✅ Fixed! All metrics now include reasoning.

---

## 📚 Documentation

- `CONVERSION_GUIDE.md` - Excel format conversion guide
- `TECHNICAL_ARCHITECTURE.md` - Technical details and architecture
- `RUN_CODES.md` - Comprehensive usage examples
- `SYSTEM_PROMPT_EXPLAINED.md` - System prompt documentation

---

## 🚀 Complete Workflow Example

```bash
# 1. Convert your custom Excel
python convert_excel_format.py input/my_tests.xlsx
# Output: input/my_tests_converted.xlsx

# 2. Run evaluation
python evaluate.py input/my_tests_converted.xlsx --judge gpt-4 --verbose

# 3. Check results
ls -la evaluation_result/
# my_tests_converted_results.json
# my_tests_converted_metrics_only.json  
# my_tests_converted_summary.md
```

---

## License

MIT

---

## Support

For technical details, see `TECHNICAL_ARCHITECTURE.md`  
For conversion help, see `CONVERSION_GUIDE.md`  
For examples, see `RUN_CODES.md`
