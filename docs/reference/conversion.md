# Excel Format Conversion Guide

## Overview

If you have an Excel file with custom columns, you can convert it to the format required by the DeepEval testing framework.

## Your Input Format

Your Excel should have these columns:
- `test_id` - Unique identifier for each test case
- `conversation_history` - Prior conversation in text format (e.g., "assistant: Hello user: Hi assistant: How can I help?")
- `query` - The user's query/question
- `response_A` - Model A's response (e.g., base model)
- `response_B` - Model B's response (e.g., finetuned model)
- `chatbot_role` - (Optional) The chatbot's role (e.g., "customer support agent", "technical assistant")
  - If not provided, defaults to "helpful AI assistant"

### Example Input Format

| test_id | conversation_history | query | response_A | response_B |
|---------|---------------------|-------|------------|------------|
| 1 | assistant: Hello! How can I help? user: I need support | What are your hours? | We're open 9-5 | We're available 24/7 for your convenience! |

## Required Output Format

The testing framework expects:
- `Initial Conversation` - JSON format: `[{"role": "assistant", "content": "..."}, {"role": "user", "content": "..."}]`
- `User Query` - The user's question
- `Model A Response` - Response from Model A
- `Model B Response` - Response from Model B
- `Chatbot Role` - Role description (e.g., "customer support agent", "helpful AI assistant")
  - **Required** for the Role Adherence metric to work
  - Auto-set to "helpful AI assistant" if not provided

## How to Convert

### Step 1: Run the Conversion Script

```bash
# Basic usage (auto-generates output filename)
python convert_excel_format.py input/your_file.xlsx

# Specify output filename
python convert_excel_format.py input/your_file.xlsx input/converted_file.xlsx
```

### Step 2: Verify the Output

The script will:
1. Read your input Excel
2. Convert `conversation_history` from text to JSON format
3. Map columns correctly:
   - `conversation_history` → `Initial Conversation` (JSON)
   - `query` → `User Query`
   - `response_A` → `Model A Response`
   - `response_B` → `Model B Response`
   - `chatbot_role` → `Chatbot Role` (defaults to "helpful AI assistant" if not provided)
4. Save the converted Excel

### Step 3: Use with Testing Framework

Once converted, you can use the standard testing pipeline:

```bash
# Run evaluation on converted file
python evaluate.py --input-file input/converted_file.xlsx
```

## Conversation History Format

The converter supports flexible text formats for `conversation_history`:

### Supported Formats

1. **With colons**: `assistant: Hello user: Hi assistant: How are you?`
2. **Without colons**: `assistant Hello user Hi assistant How are you?`
3. **Mixed**: Any combination of the above

### Output JSON Format

All formats are converted to:
```json
[
  {"role": "assistant", "content": "Hello"},
  {"role": "user", "content": "Hi"},
  {"role": "assistant", "content": "How are you?"}
]
```

**Unicode Support**: The converter properly handles Unicode characters (emojis, special characters, non-English text) without escaping them as `\uXXXX` sequences. Characters like emojis 😊, accented letters café, or other languages 你好 are preserved in their original form.

## Notes

- Empty or missing `conversation_history` will be converted to `[]` (empty array)
- The `test_id` column will be preserved in the output as `Test ID`
- Make sure your `response_A` and `response_B` were generated using the appropriate system prompt
- The converter does NOT change any existing code in the framework

## Troubleshooting

### Issue: Conversation history not parsing correctly

**Solution**: Check that your text uses "assistant" and "user" keywords. The parser looks for these role markers.

### Issue: Empty responses in output

**Solution**: Verify that your input columns are named exactly as: `query`, `response_A`, `response_B`, `conversation_history`

### Issue: Column mismatch error

**Solution**: Make sure your input Excel has all required columns. Missing columns will result in empty values in the output.

## Example Workflow

```bash
# 1. Place your Excel file in the input directory
# 2. Run conversion
python convert_excel_format.py input/my_tests.xlsx

# 3. Output will be created at input/my_tests_converted.xlsx
# 4. Run evaluation
python evaluate.py --input-file input/my_tests_converted.xlsx

# 5. Check results in evaluation_result/ directory
```

## System Prompt

If your `response_A` and `response_B` were generated using a system prompt:
- The system prompt is stored in `system_prompt.txt`
- This is used by the model wrapper when generating responses
- For pre-recorded responses (like yours), this is just for reference
- The evaluation framework will evaluate the responses as-is, regardless of how they were generated

