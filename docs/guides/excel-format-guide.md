# Excel Input Format Guide

## 📋 Overview

Your input Excel file can be in **two formats** depending on your testing mode:

1. **Prerecorded Mode** - Test existing responses
2. **Generate Mode** - Generate responses on-the-fly

---

## 📊 Format 1: Prerecorded Mode (Recommended)

### When to Use:
- You have responses already collected
- Testing existing chatbot outputs
- Comparing logged conversations
- Faster evaluation (no API calls to models)

### Required Columns:

| Column Name | Required? | Description | Example |
|-------------|-----------|-------------|---------|
| **Initial Conversation** | Optional | Previous conversation context in JSON format | `[]` or `[{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]` |
| **User Query** | ✅ Required | The user's current message | `"I can't log into my account"` |
| **Model A Response** | ✅ Required | Base model's response | `"Let me help you with that"` |
| **Model B Response** | ✅ Required | Fine-tuned model's response | `"Oh no! Let me help you reset your password"` |
| **Chatbot Role** | Optional | Role for metrics (uses system_prompt.txt if empty) | `"Customer support agent"` |
| **Scenario** | Optional | Test scenario description | `"Login issue"` |
| **Expected Outcome** | Optional | What should happen | `"User gets help resetting password"` |

### ✅ Excel Example (Prerecorded Mode):

```
| Initial Conversation | User Query | Model A Response | Model B Response | Chatbot Role |
|---------------------|------------|------------------|------------------|--------------|
| [] | How do I reset my password? | You can reset your password by clicking forgot password. | Oh no! Let me help you. Just click 'Forgot Password' and you'll get an email with instructions. Super easy! | Customer support agent |
| [{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}] | My order is late | Your order delay has been noted. | So sorry to hear that! Let me quickly check the tracking for you. | Customer support agent |
```

### How to Create This Excel:

**Option 1: Manual Entry in Excel**
1. Open Microsoft Excel or Google Sheets
2. Create headers in Row 1
3. Add your data starting from Row 2

**Option 2: Create from CSV**
```python
import pandas as pd

data = {
    'Initial Conversation': ['[]', '[]'],
    'User Query': ['How do I reset password?', 'My order is late'],
    'Model A Response': ['Click forgot password', 'Delay noted. Provide order number.'],
    'Model B Response': ['Let me help! Click Forgot Password...', 'Oh no! Let me check that...'],
    'Chatbot Role': ['Customer support agent', 'Customer support agent']
}

df = pd.DataFrame(data)
df.to_excel('input/my_test.xlsx', index=False)
```

---

## 📊 Format 2: Generate Mode

### When to Use:
- You want models to generate responses live
- Testing new scenarios
- Don't have pre-collected responses
- Want real-time model comparison

### Required Columns:

| Column Name | Required? | Description | Example |
|-------------|-----------|-------------|---------|
| **Initial Conversation** | Optional | Previous conversation context in JSON format | `[]` or `[{"role":"user","content":"Hi"}]` |
| **User Query** | ✅ Required | The user's current message | `"I can't log into my account"` |
| **Chatbot Role** | Optional | Role for metrics | `"Customer support agent"` |
| **Scenario** | Optional | Test scenario | `"Login issue"` |

### ❌ Do NOT Include:
- ~~Model A Response~~
- ~~Model B Response~~

(These will be generated automatically)

### ✅ Excel Example (Generate Mode):

```
| Initial Conversation | User Query | Chatbot Role | Scenario |
|---------------------|------------|--------------|----------|
| [] | How do I reset my password? | Customer support agent | Password reset |
| [{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}] | My order is late | Customer support agent | Order tracking |
```

---

## 📝 Initial Conversation Format

The **Initial Conversation** column should contain JSON array of previous turns.

### Empty (No Prior Context):
```
[]
```

### Single Prior Exchange:
```json
[
  {"role":"user","content":"Hi, I need help"},
  {"role":"assistant","content":"Hello! Happy to assist you."}
]
```

### Multiple Prior Exchanges:
```json
[
  {"role":"user","content":"Hi"},
  {"role":"assistant","content":"Hello!"},
  {"role":"user","content":"I have a question"},
  {"role":"assistant","content":"Sure, what would you like to know?"}
]
```

### Tips:
- Use **double quotes** in JSON (not single quotes)
- Must be **valid JSON** format
- Can have any number of prior turns
- Only include `user` and `assistant` roles

---

## 🎯 Complete Example Templates

### Template 1: Simple Prerecorded Test

**File: `input/simple_test.xlsx`**

| Initial Conversation | User Query | Model A Response | Model B Response | Chatbot Role |
|---------------------|------------|------------------|------------------|--------------|
| [] | How do I reset password? | Click forgot password. | Don't worry! Just click 'Forgot Password' and you'll get an email. Easy! | Support agent |
| [] | My order is late | Provide order number. | Oh no! Let me check that for you. What's your order number? | Support agent |
| [] | What's your refund policy? | 30 day returns accepted. | We offer 30 day returns! Just keep the receipt and you're all good. | Support agent |

### Template 2: Multi-Turn Context

**File: `input/multi_turn_test.xlsx`**

| Initial Conversation | User Query | Model A Response | Model B Response |
|---------------------|------------|------------------|------------------|
| `[{"role":"user","content":"My name is Sarah"},{"role":"assistant","content":"Thanks Sarah!"}]` | My order #12345 is late | Checking order status. | Sarah, let me check order #12345 for you! |
| `[{"role":"user","content":"I'm having trouble"},{"role":"assistant","content":"I'll help you"}]` | It's still not working | What is the issue? | Oh no! What exactly isn't working? Let me help! |

### Template 3: Generate Mode

**File: `input/queries.xlsx`**

| Initial Conversation | User Query | Chatbot Role | Scenario |
|---------------------|------------|--------------|----------|
| [] | I forgot my password | Customer support agent | Password reset |
| [] | Track my order | Customer support agent | Order tracking |
| `[{"role":"user","content":"Hi"}]` | What's your return policy? | Sales assistant | Returns inquiry |

---

## ⚠️ Common Mistakes

### ❌ WRONG: Invalid JSON
```
Initial Conversation: {'role':'user','content':'Hi'}
```
**Problem:** Single quotes not valid in JSON  
**Fix:** Use double quotes: `{"role":"user","content":"Hi"}`

### ❌ WRONG: Missing brackets
```
Initial Conversation: {"role":"user","content":"Hi"}
```
**Problem:** Should be an array  
**Fix:** Add brackets: `[{"role":"user","content":"Hi"}]`

### ❌ WRONG: Missing columns
```
Just has: User Query, Model A Response
Missing: Model B Response
```
**Problem:** Prerecorded mode needs both responses  
**Fix:** Add Model B Response column OR use generate mode

### ❌ WRONG: Wrong column names
```
user_query, modelA_response
```
**Problem:** Case-sensitive, needs exact names  
**Fix:** Use: `User Query`, `Model A Response`

---

## ✅ Excel Creation Methods

### Method 1: Manual (Excel/Google Sheets)
1. Open Excel or Google Sheets
2. Add column headers in Row 1
3. Add data starting from Row 2
4. Save as `.xlsx` in `input/` folder

### Method 2: Python Script
```python
import pandas as pd

data = {
    'Initial Conversation': ['[]', '[]'],
    'User Query': [
        'How do I reset my password?',
        'My order is late'
    ],
    'Model A Response': [
        'Click forgot password.',
        'Provide order number for verification.'
    ],
    'Model B Response': [
        'Don\'t worry! Click \'Forgot Password\' and you\'ll get an email.',
        'Oh no! Let me check that for you right away.'
    ],
    'Chatbot Role': ['Support agent', 'Support agent']
}

df = pd.DataFrame(data)
df.to_excel('input/my_test.xlsx', index=False)
print("✅ Created: input/my_test.xlsx")
```

### Method 3: Convert from CSV
```bash
# If you have a CSV
python convert_excel_format.py input/data.csv output/test.xlsx
```

---

## 🎯 Quick Reference

### Prerecorded Mode Columns:
```
✅ Required:
   - User Query
   - Model A Response
   - Model B Response

⚠️ Optional:
   - Initial Conversation
   - Chatbot Role
   - Scenario
   - Expected Outcome
```

### Generate Mode Columns:
```
✅ Required:
   - User Query

⚠️ Optional:
   - Initial Conversation
   - Chatbot Role
   - Scenario
```

---

## 📁 File Location

Save your Excel files in:
```
DeepEval/
└── input/
    ├── your_test.xlsx
    ├── another_test.xlsx
    └── queries.xlsx
```

---

## 🚀 After Creating Excel

Run evaluation:
```bash
# Prerecorded mode
python evaluate.py input/your_test.xlsx

# Generate mode (auto-detected)
python evaluate.py input/queries.xlsx
```

The system will:
1. Auto-detect mode (based on columns)
2. Evaluate all 8 metrics including **Human Tonality**
3. Save results to `evaluation_result/`

---

**Last Updated:** October 14, 2025  
**See Also:** [Commands Reference](../reference/commands.md)

