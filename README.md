# DeepEval Multi-Turn Conversation Testing

LLM-as-a-judge evaluation framework for comparing base and finetuned models on multi-turn conversations.

## ✨ Features

✅ **Excel Support** - Load conversations with Model A and Model B responses  
✅ **Excel Format Converter** - Convert custom Excel formats to required format  
✅ **System Prompt Integration** - Load system prompts from separate file  
✅ **Initial Conversation Support** - Include prior conversation context as JSON  
✅ **7 Evaluation Metrics** - Comprehensive multi-turn conversation assessment  
✅ **LLM-as-a-Judge** - Uses GPT-4 (or custom) for nuanced evaluation  
✅ **ConversationalTestCase** - Proper DeepEval format with Turn objects  
✅ **Easy Comparison** - Side-by-side Model A vs Model B evaluation  
✅ **Batch Processing** - Evaluate multiple Excel files at once  
✅ **JSON Results** - Detailed scores, reasoning, and comparisons  

---

## The 7 Metrics

All metrics use **LLM-as-a-judge** evaluation:

### Custom Conversational Metrics

These use DeepEval's **Conversational GEval** framework (designed for multi-turn conversations):

1. **Coherence** - Logical flow and clarity (Custom Conversational GEval)
2. **Contextual Understanding** - Context awareness (Custom Conversational GEval)
3. **Helpfulness** - Practical value (Custom Conversational GEval)

### DeepEval Built-in Multi-Turn Metrics

These are official DeepEval metrics designed specifically for multi-turn conversations:

4. **Knowledge Retention** ✅ - Remembers information from earlier turns  
   [📚 Official Docs](https://deepeval.com/docs/metrics-knowledge-retention)

5. **Turn Relevancy** ✅ - Each response is relevant to user query  
   [📚 Official Docs](https://deepeval.com/docs/metrics-turn-relevancy)

6. **Role Adherence** ✅ - Maintains consistent role and tone  
   [📚 Official Docs](https://deepeval.com/docs/metrics-role-adherence)

7. **Conversation Completeness** ✅ - All queries addressed, satisfactory conclusion  
   [📚 Official Docs](https://deepeval.com/docs/metrics-conversation-completeness)

> **Note**: Metrics 1-3 use **Conversational GEval** (for multi-turn conversations). Metrics 4-7 are built-in DeepEval metrics. All 7 metrics are proper **conversational metrics** designed to evaluate `ConversationalTestCase` objects as per [DeepEval documentation](https://deepeval.com/docs/evaluation-multiturn-test-cases).

---

## 🚀 Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp env_template.txt .env
# Add your OPENAI_API_KEY to .env

# 3. Run
python3 evaluate.py input/example_conversation_template.xlsx
```

## Features

- ✅ **Two Modes**: Generate responses on-the-fly OR use pre-recorded responses
- ✅ **7 Metrics**: Coherence, Contextual Understanding, Helpfulness, Knowledge Retention, Turn Relevancy, Role Adherence, Conversation Completeness
- ✅ **Clean Outputs**: JSON metrics, markdown summaries
- ✅ **Flexible**: Change models, judge, system prompts easily

## Excel Format

### Option 1: Standard Format (Ready to Use)

For pre-recorded mode (responses already in Excel):

| Initial Conversation | User Query | Model A Response | Model B Response | Chatbot Role |
|---------------------|------------|------------------|------------------|--------------|
| `[{"role": "assistant", "content": "Hello!"}]` | I can't log in | Sorry to hear that... | I understand your frustration... | Support agent |

For generate mode (model generates responses):

| User Query | Chatbot Role | Scenario |
|------------|--------------|----------|
| I can't log in | Professional support agent | Login issue |

### Option 2: Custom Format (Needs Conversion)

If your Excel has custom columns like:

| test_id | conversation_history | query | response_A | response_B |
|---------|---------------------|-------|------------|------------|
| 1 | assistant: Hello user: Hi | What are hours? | 9-5 | 24/7 |

**Convert it first:**

```bash
python convert_excel_format.py input/your_file.xlsx
```

This will create `input/your_file_converted.xlsx` in the standard format. See `CONVERSION_GUIDE.md` for details.

## Usage

### Basic

```bash
# Auto-detect mode
python3 evaluate.py input/test.xlsx

# Force generate mode
python3 evaluate.py input/test.xlsx --mode generate

# Force pre-recorded mode
python3 evaluate.py input/test.xlsx --mode prerecorded
```

### Advanced

```bash
# Change judge model
python3 evaluate.py input/test.xlsx --judge gpt-4

# Use only 4 built-in metrics (faster/cheaper)
python3 evaluate.py input/test.xlsx --metrics builtin

# Custom system prompt
python3 evaluate.py input/test.xlsx --system-prompt my_prompt.txt

# Multiple files
python3 evaluate.py file1.xlsx file2.xlsx file3.xlsx
```

## Change Models

Edit `config.py`:

```python
# Base Model
BASE_MODEL = {
    "name": "gpt-4.1-nano",  # ← Change this
    "api_key": OPENAI_API_KEY,
    "temperature": 0.7,
    "max_tokens": 500
}

# Finetuned Model  
FINETUNED_MODEL = {
    "name": "ft:gpt-3.5-turbo:org:model:id",  # ← Change this
    "api_key": OPENAI_API_KEY,
    "temperature": 0.7,
    "max_tokens": 500
}
```

Judge model: Use `--judge` flag or edit `.env`

## Outputs

For each evaluation, creates:
- `*_results.json` - Full DeepEval output
- `*_metrics_only.json` - Clean scores (Model A vs B)
- `*_summary.md` - Human-readable markdown
- `*_with_responses.xlsx` - Excel with generated responses (generate mode only)

## Metrics

### Custom ConversationalGEval Metrics (3)
1. **Coherence** - Logical flow and structure
2. **Contextual Understanding** - Builds on previous responses
3. **Helpfulness** - Practical and actionable

### Built-in DeepEval Metrics (4)
4. **Knowledge Retention** - Remembers conversation history
5. **Turn Relevancy** - Each turn is relevant
6. **Role Adherence** - Stays in character
7. **Conversation Completeness** - Addresses user needs

## Project Structure

```
DeepEval/
├── evaluate.py              # Main entry point
├── config.py                # Model configuration
├── excel_loader.py          # Excel → DeepEval test cases
├── multi_turn_testing.py    # Evaluation framework
├── model_wrapper.py         # Model API calls
├── create_clean_output.py   # Output formatter
├── system_prompt.txt        # Default system prompt
├── .env                     # API keys (not in git)
├── input/                   # Input Excel files
│   └── example_conversation_template.xlsx
└── evaluation_result/       # Output files
```

## FAQ

**Q: How do I use my finetuned model?**  
A: Edit `config.py`, change `FINETUNED_MODEL["name"]` to your finetuned model ID

**Q: Can I use a different judge model?**  
A: Yes! Use `--judge gpt-4` or edit `.env` to set `JUDGE_MODEL=gpt-4`

**Q: Which mode should I use?**  
A: Use `--mode generate` to generate responses on-the-fly. Use `--mode prerecorded` if you already have responses in Excel.

**Q: How do I reduce costs?**  
A: Use `--metrics builtin` to use only 4 metrics instead of 7 (skips custom GEval)

**Q: Can I customize the system prompt?**  
A: Yes! Edit `system_prompt.txt` or create your own and use `--system-prompt my_prompt.txt`

## Support

See `TECHNICAL_ARCHITECTURE.md` for technical details.

# 3. Multiple files with custom judge
python3 evaluate.py input/test1.xlsx input/test2.xlsx --judge gpt-4

# 4. All options
python3 evaluate.py input/test.xlsx -m generate -j gpt-4 -s custom.txt --metrics all -v
```

**Ready to test!** 

MIT
