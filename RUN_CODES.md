# How to Run the Code - Complete Guide

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Input Dataset Format](#input-dataset-format)
3. [Column Specifications](#column-specifications)
4. [Supported Input Formats](#supported-input-formats)
5. [Running the Code](#running-the-code)
6. [Configuration](#configuration)
7. [Understanding Outputs](#understanding-outputs)
8. [Examples](#examples)

---

## Quick Start

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure API key
cp env_template.txt .env
nano .env  # Add your OPENAI_API_KEY

# 3. Prepare your Excel file (see format below)

# 4. Run evaluation
python3 evaluate.py input/your_file.xlsx --mode generate
```

---

## Input Dataset Format

### 🎯 Key Concept: Each ROW = One SEPARATE Conversation

**Important**: Each row in your Excel file represents a **complete, independent conversation** to be evaluated.

### Excel Structure

```
Row 1: Conversation 1
Row 2: Conversation 2  
Row 3: Conversation 3
...
```

Each conversation consists of:
- **Initial Conversation** (optional): Previous conversation turns
- **User Query**: The last user message in this conversation
- **Model Responses** (optional): Pre-recorded responses for evaluation

---

## Column Specifications

### Required Columns

| Column Name | Type | Required | Description |
|-------------|------|----------|-------------|
| `User Query` | String | ✅ YES | The last user message in the conversation. This is what the model needs to respond to. |

### Optional Columns

| Column Name | Type | Required | Description | Example |
|-------------|------|----------|-------------|---------|
| `Initial Conversation` | JSON String | ⭐ Recommended | Prior conversation turns before the user query. Format: JSON array of turn objects. | `[{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]` |
| `Model A Response` | String | For prerecorded mode | Pre-recorded response from base model. If provided, will use this instead of generating. | `I can help you with that...` |
| `Model B Response` | String | For prerecorded mode | Pre-recorded response from finetuned model. If provided, will use this instead of generating. | `I'd be happy to assist...` |
| `Chatbot Role` | String | ⭐ Recommended | Role description for the chatbot. Used by Role Adherence metric. | `Professional customer support agent` |
| `Scenario` | String | Optional | Description of the scenario being tested. | `Login issue - password reset` |
| `Expected Outcome` | String | Optional | What you expect the model to achieve. | `User successfully resets password` |

---

## Supported Input Formats

### Format 1: Generate Mode (On-the-Fly Response Generation)

**Use Case**: You have user queries and want models to generate responses.

**Excel Columns**:
- `User Query` (required)
- `Initial Conversation` (optional, JSON)
- `Chatbot Role` (recommended)
- `Scenario` (optional)

**Example Excel**:

| Initial Conversation | User Query | Chatbot Role | Scenario |
|---------------------|------------|--------------|----------|
| `[{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]` | I can't log into my account | Professional support agent | Login issue |
| `[{"role":"user","content":"My order is late"},{"role":"assistant","content":"Let me check"}]` | When will it arrive? | Professional support agent | Order tracking |
| `` | How do I reset my password? | Professional support agent | Password reset |

**What Happens**:
1. System reads each row as a separate conversation
2. Loads initial conversation turns from JSON (if provided)
3. Adds user query as the last message
4. Calls Model A (base) and Model B (finetuned) to generate responses
5. Evaluates both responses with all 7 metrics
6. Saves responses back to Excel

**Run Command**:
```bash
python3 evaluate.py input/your_file.xlsx --mode generate
```

---

### Format 2: Pre-recorded Mode (Existing Responses)

**Use Case**: You already have model responses and want to evaluate them.

**Excel Columns**:
- `User Query` (required)
- `Model A Response` (required)
- `Model B Response` (required)
- `Initial Conversation` (optional, JSON)
- `Chatbot Role` (recommended)
- `Scenario` (optional)

**Example Excel**:

| Initial Conversation | User Query | Model A Response | Model B Response | Chatbot Role | Scenario |
|---------------------|------------|------------------|------------------|--------------|----------|
| `[{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]` | I can't log in | Sorry to hear that. Can you verify your email? | I understand your frustration. Let me help you... | Support agent | Login issue |
| `` | When will my order arrive? | Let me check the tracking... | I'll look up your order status... | Support agent | Order tracking |

**What Happens**:
1. System reads each row as a separate conversation
2. Loads initial conversation turns from JSON (if provided)
3. Uses the pre-recorded responses from Excel
4. Evaluates both responses with all 7 metrics
5. No model API calls made (cost-effective!)

**Run Command**:
```bash
python3 evaluate.py input/your_file.xlsx --mode prerecorded
```

---

### Format 3: Auto-Detect Mode (Recommended)

**Use Case**: Let the system automatically detect which mode to use.

**Excel Columns**: Any combination from Format 1 or 2

**What Happens**:
- If `Model A Response` and `Model B Response` columns exist with data → Pre-recorded mode
- Otherwise → Generate mode

**Run Command**:
```bash
python3 evaluate.py input/your_file.xlsx
# No --mode flag needed, auto-detects!
```

---

## Column Specifications in Detail

### 1. User Query (Required)

**Type**: String  
**Description**: The user's message that the model needs to respond to.

**Examples**:
```
I can't log into my account
When will my order arrive?
How do I cancel my subscription?
What are your business hours?
```

**Important**: 
- Must be non-empty
- Can be a question or statement
- This is the LAST message in the conversation
- Each row's query is independent

---

### 2. Initial Conversation (Optional but Recommended)

**Type**: JSON String (array of turn objects)  
**Description**: Previous conversation turns that provide context for the user query.

**Format**:
```json
[
  {"role": "user", "content": "Hi, I need help"},
  {"role": "assistant", "content": "Hello! I'm here to help."},
  {"role": "user", "content": "My account is locked"}
]
```

**Rules**:
- Must be valid JSON
- Each turn must have `role` and `content`
- `role` can be: `"user"` or `"assistant"` (NOT "system")
- Turns are in chronological order
- Can be empty string `""` if no initial conversation

**Why Use This**:
- Provides context to the model
- Tests multi-turn understanding
- Makes conversations more realistic
- Enables Knowledge Retention metric

**Example in Excel Cell**:
```json
[{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello! How can I help?"}]
```

---

### 3. Model A Response (Optional - For Pre-recorded Mode)

**Type**: String  
**Description**: Pre-recorded response from your base model.

**When to Use**:
- You already have responses from your base model
- You want to evaluate existing conversations
- You want to avoid API costs for generation

**Example**:
```
I'm sorry to hear you're having trouble logging in. Can you verify your email address?
```

---

### 4. Model B Response (Optional - For Pre-recorded Mode)

**Type**: String  
**Description**: Pre-recorded response from your finetuned model.

**When to Use**:
- You already have responses from your finetuned model
- You want to compare two existing responses
- You want to avoid API costs for generation

**Example**:
```
I understand your frustration with the login issue. Let me help you resolve this quickly. Could you please verify your email address?
```

---

### 5. Chatbot Role (Recommended)

**Type**: String  
**Description**: The role/persona the chatbot should embody.

**Why Important**:
- **Required** for Role Adherence metric
- Helps the model understand expected behavior
- Improves evaluation quality

**Examples**:
```
Professional customer support agent
Medical assistant
Technical support specialist
Friendly sales representative
Banking customer service agent
```

**Where to Put It**:
- Usually in the first row of each conversation
- Can be the same for multiple conversations
- Can be different for different scenarios

---

### 6. Scenario (Optional)

**Type**: String  
**Description**: Brief description of the conversation scenario.

**Examples**:
```
Login issue - password reset
Order tracking and delivery inquiry
Billing question - refund request
Technical troubleshooting - app crash
```

**Benefits**:
- Helps with result organization
- Provides context in evaluation reports
- Useful for categorizing test cases

---

### 7. Expected Outcome (Optional)

**Type**: String  
**Description**: What you expect to achieve in this conversation.

**Examples**:
```
User successfully resets password
Customer receives order tracking information
Issue escalated to technical team
Refund processed within 24 hours
```

**Benefits**:
- Sets evaluation expectations
- Helps with qualitative assessment
- Useful for documentation

---

## Running the Code

### Basic Commands

#### 1. Auto-Detect Mode (Recommended)

```bash
python3 evaluate.py input/your_file.xlsx
```

**What it does**:
- Automatically detects if responses exist in Excel
- Uses pre-recorded if available, otherwise generates
- Evaluates all conversations
- Creates all output files

---

#### 2. Generate Mode (Force Generation)

```bash
python3 evaluate.py input/your_file.xlsx --mode generate
```

**What it does**:
- Forces response generation even if responses exist in Excel
- Calls your configured models (config.py)
- Generates fresh responses for each conversation
- Saves responses back to Excel

**When to use**:
- Testing new models
- You want fresh responses
- Comparing model versions

---

#### 3. Pre-recorded Mode (Force Pre-recorded)

```bash
python3 evaluate.py input/your_file.xlsx --mode prerecorded
```

**What it does**:
- Forces use of Excel responses
- Will ERROR if responses don't exist
- No model API calls
- Cost-effective for re-evaluation

**When to use**:
- You already have responses in Excel
- Re-evaluating with different judge
- Re-evaluating with different metrics
- Testing evaluation logic without API costs

---

### Advanced Commands

#### Change Judge Model

```bash
# Use GPT-4 as judge
python3 evaluate.py input/test.xlsx --judge gpt-4

# Use GPT-3.5 as judge (cheaper)
python3 evaluate.py input/test.xlsx --judge gpt-3.5-turbo
```

#### Use Fewer Metrics (Cost Savings)

```bash
# Only 4 built-in metrics (no custom GEval)
python3 evaluate.py input/test.xlsx --metrics builtin
```

Saves ~60% on judge model costs by using only:
- Knowledge Retention
- Turn Relevancy
- Role Adherence
- Conversation Completeness

#### Custom System Prompt

```bash
# Use custom prompt file
python3 evaluate.py input/test.xlsx --system-prompt prompts/banking_agent.txt
```

#### Custom Output Directory

```bash
# Save results to custom folder
python3 evaluate.py input/test.xlsx --output results/experiment1
```

#### Process Multiple Files

```bash
# Process all files in input/ folder
python3 evaluate.py

# Process specific files
python3 evaluate.py file1.xlsx file2.xlsx file3.xlsx

# Mix of paths
python3 evaluate.py input/test1.xlsx /path/to/test2.xlsx
```

#### Combine All Options

```bash
python3 evaluate.py input/test.xlsx \
  --mode generate \
  --judge gpt-4 \
  --metrics all \
  --system-prompt custom_prompt.txt \
  --output results/run1
```

---

## Configuration

### Change Base and Finetuned Models

Edit `config.py`:

```python
# Base Model (Model A)
BASE_MODEL = {
    "name": "gpt-4.1-nano",  # ← Change this
    "api_key": OPENAI_API_KEY,
    "temperature": 0.7,
    "max_tokens": 500
}

# Finetuned Model (Model B)
FINETUNED_MODEL = {
    "name": "ft:gpt-3.5-turbo:org:model:abc123",  # ← Change this
    "api_key": OPENAI_API_KEY,
    "temperature": 0.7,
    "max_tokens": 500
}
```

**Model Name Examples**:
- `gpt-4.1-nano`
- `gpt-4`
- `gpt-4-turbo`
- `gpt-3.5-turbo`
- `ft:gpt-3.5-turbo:yourorg:modelname:id123` (finetuned model)

### Change Default Judge Model

Edit `.env`:

```bash
OPENAI_API_KEY=sk-your-key-here
JUDGE_MODEL=gpt-4.1-nano  # ← Change this
```

Or use CLI flag: `--judge gpt-4`

---

## Understanding Outputs

For each evaluation, the system creates **5 output files**:

### 1. `*_results.json` (Full DeepEval Output)

**Content**: Complete technical output from DeepEval
- All test cases
- All metric data
- Full reasoning
- Timestamps
- Model details

**Use**: Debugging, full technical details

---

### 2. `*_metrics_only.json` (Clean Metrics)

**Content**: Just the scores in clean format

```json
{
  "test_name": "test.xlsx",
  "total_conversations": 3,
  "conversations": [
    {
      "conversation": "Conversation 1",
      "model_a_metrics": {
        "Coherence": {"score": 0.85, "pass": true},
        "Helpfulness": {"score": 0.92, "pass": true}
      },
      "model_b_metrics": {
        "Coherence": {"score": 0.88, "pass": true},
        "Helpfulness": {"score": 0.95, "pass": true}
      },
      "comparison": {
        "Coherence": "Model B wins",
        "Helpfulness": "Model B wins"
      }
    }
  ]
}
```

**Use**: 
- Easy to parse programmatically
- Quick comparison of models
- Dashboard integration

---

### 3. `*_summary.md` (Human-Readable Summary)

**Content**: Markdown summary with emojis

```markdown
# Evaluation Summary: test.xlsx

**Total Conversations**: 3

## Conversation 1

### Model A Metrics
- ✅ Coherence: 0.8500
- ✅ Helpfulness: 0.9200

### Model B Metrics  
- ✅ Coherence: 0.8800
- ✅ Helpfulness: 0.9500

### Comparison
- Coherence: Model B wins
- Helpfulness: Model B wins
```

**Use**: 
- Share with non-technical team
- Quick visual comparison
- Reports and presentations

---

### 4. `*_with_responses.xlsx` (Excel with Responses)

**Content**: Your original Excel + generated responses

**Columns Added**:
- `Model A Response` (if generate mode)
- `Model B Response` (if generate mode)

**Use**:
- Review model responses
- Manual quality check
- Future pre-recorded evaluations

---

### 5. `.deepeval/` Folder (DeepEval Cache)

**Content**: DeepEval's internal cache and telemetry
- Not meant for direct use
- Automatically managed

---

## Examples

### Example 1: Simple Conversations (No Initial Context)

**Excel**: `input/simple_queries.xlsx`

| User Query | Chatbot Role | Scenario |
|------------|--------------|----------|
| What are your business hours? | Customer service agent | Business inquiry |
| How do I track my order? | Customer service agent | Order tracking |
| Do you offer refunds? | Customer service agent | Refund policy |

**Run**:
```bash
python3 evaluate.py input/simple_queries.xlsx --mode generate
```

**Result**:
- 3 conversations evaluated
- Each gets fresh model responses
- All metrics calculated

---

### Example 2: Multi-Turn Conversations (With Initial Context)

**Excel**: `input/multi_turn_queries.xlsx`

| Initial Conversation | User Query | Chatbot Role | Scenario |
|---------------------|------------|--------------|----------|
| `[{"role":"user","content":"I can't log in"},{"role":"assistant","content":"Have you tried resetting?"}]` | Yes, but I didn't get the email | Support agent | Login issue |
| `[{"role":"user","content":"My order is late"},{"role":"assistant","content":"Let me check for you"}]` | Any updates? | Support agent | Order follow-up |

**Initial Conversation JSON for Row 1**:
```json
[
  {"role": "user", "content": "I can't log in"},
  {"role": "assistant", "content": "Have you tried resetting your password?"}
]
```

**Run**:
```bash
python3 evaluate.py input/multi_turn_queries.xlsx --mode generate
```

**Result**:
- Models see the initial conversation as context
- Generate responses to the user query
- Evaluation includes context awareness

---

### Example 3: Pre-recorded Responses

**Excel**: `input/prerecorded_test.xlsx`

| User Query | Model A Response | Model B Response | Chatbot Role |
|------------|------------------|------------------|--------------|
| I can't log in | Can you verify your email? | I understand this is frustrating. Let me help you reset your password. | Support agent |
| Track my order | Let me check... | I'll look up your order. Can you provide the order number? | Support agent |

**Run**:
```bash
python3 evaluate.py input/prerecorded_test.xlsx --mode prerecorded
```

**Result**:
- No API calls to generate responses
- Fast evaluation
- Cost = only judge model calls

---

### Example 4: Batch Processing

**Folder Structure**:
```
input/
  - customer_support_conversations.xlsx
  - technical_support_conversations.xlsx
  - sales_conversations.xlsx
```

**Run**:
```bash
# Process all files in input/ folder
python3 evaluate.py
```

**Result**:
- All Excel files evaluated
- Separate output files for each
- One command for everything

---

## Creating Your Input Dataset

### Step-by-Step Guide

#### Step 1: Decide Your Test Scenarios

Example scenarios:
- Login issues
- Password reset
- Order tracking
- Billing questions
- Technical troubleshooting

#### Step 2: Create Excel File

1. Open Excel or Google Sheets
2. Create columns (minimum required):
   - `User Query`
   - `Chatbot Role` (recommended)

3. Add optional columns if needed:
   - `Initial Conversation` (for multi-turn)
   - `Scenario`
   - `Expected Outcome`

#### Step 3: Fill in Data

**For each conversation** (each row):

1. **Write the user query** in `User Query` column
2. **Add context** in `Initial Conversation` (if multi-turn)
3. **Specify role** in `Chatbot Role`
4. **Add metadata** in `Scenario` and other columns

#### Step 4: Format Initial Conversation (If Using)

Convert conversation to JSON:

**Conversation**:
```
User: Hi, I need help
Assistant: Hello! I'm here to help.
User: My account is locked
```

**JSON Format** (put this in Excel cell):
```json
[{"role":"user","content":"Hi, I need help"},{"role":"assistant","content":"Hello! I'm here to help."},{"role":"user","content":"My account is locked"}]
```

**Tips**:
- Use online JSON validator to check format
- No line breaks in Excel cell
- Use double quotes for JSON
- Escape quotes if needed: `\"hello\"`

#### Step 5: Save and Run

1. Save as `.xlsx` file
2. Put in `input/` folder
3. Run: `python3 evaluate.py input/your_file.xlsx --mode generate`

---

## Complete Working Example

### Example: Customer Support Testing

**File**: `input/customer_support_test.xlsx`

**Row 1**: Login Issue with Context

| Column | Value |
|--------|-------|
| Initial Conversation | `[{"role":"user","content":"I can't access my account"},{"role":"assistant","content":"I'm here to help. Have you tried resetting your password?"}]` |
| User Query | Yes, but I didn't receive the reset email |
| Chatbot Role | Professional customer support agent for TechCorp |
| Scenario | Login issue - password reset email not received |
| Expected Outcome | User receives reset email or alternative solution |

**Row 2**: Order Tracking

| Column | Value |
|--------|-------|
| Initial Conversation | `` (empty - no context) |
| User Query | Where is my order #12345? |
| Chatbot Role | Professional customer support agent for TechCorp |
| Scenario | Order tracking inquiry |
| Expected Outcome | Customer receives order status and ETA |

**Row 3**: Billing Question

| Column | Value |
|--------|-------|
| Initial Conversation | `[{"role":"user","content":"I was charged twice"},{"role":"assistant","content":"I apologize for the inconvenience. Let me investigate this."}]` |
| User Query | Can I get a refund for the duplicate charge? |
| Chatbot Role | Professional customer support agent for TechCorp |
| Scenario | Billing issue - duplicate charge refund |
| Expected Outcome | Refund initiated or escalation to billing team |

**Run Command**:
```bash
python3 evaluate.py input/customer_support_test.xlsx --mode generate --judge gpt-4.1-nano
```

**Output**:
- 3 conversations evaluated
- Each conversation gets 7 metric scores
- Model A vs Model B comparison for each
- All results in `evaluation_result/` folder

---

## Troubleshooting

### Issue: "No valid conversations found"

**Cause**: Missing `User Query` column or all queries are empty

**Fix**: 
- Ensure column is named exactly `User Query`
- Check that cells contain text

---

### Issue: "chatbot_role cannot be empty for Role Adherence metric"

**Cause**: Missing `Chatbot Role` column

**Fix**:
- Add `Chatbot Role` column
- Fill with role description (e.g., "Professional support agent")

---

### Issue: "Invalid JSON in Initial Conversation"

**Cause**: Malformed JSON in `Initial Conversation` column

**Fix**:
- Validate JSON online (jsonlint.com)
- Ensure proper format: `[{"role":"user","content":"..."}]`
- Check for missing quotes or commas

---

### Issue: Mode detection incorrect

**Cause**: Auto-detect choosing wrong mode

**Fix**:
- Use explicit mode: `--mode generate` or `--mode prerecorded`
- Check Excel has correct columns

---

## Quick Reference

### Minimum Required Excel Format

```
| User Query |
|------------|
| Query 1    |
| Query 2    |
```

Run: `python3 evaluate.py input/file.xlsx --mode generate`

---

### Recommended Excel Format

```
| Initial Conversation | User Query | Chatbot Role | Scenario |
|---------------------|------------|--------------|----------|
| [{"role":"user",...}] | Query 1   | Support agent | Scenario 1 |
| [{"role":"user",...}] | Query 2   | Support agent | Scenario 2 |
```

Run: `python3 evaluate.py input/file.xlsx`

---

### Full Excel Format

```
| Initial Conversation | User Query | Model A Response | Model B Response | Chatbot Role | Scenario | Expected Outcome |
|---------------------|------------|------------------|------------------|--------------|----------|------------------|
| [{"role":"user",...}] | Query 1   | Response A1      | Response B1      | Support      | Login    | User logs in    |
```

Run: `python3 evaluate.py input/file.xlsx --mode prerecorded`

---

## Summary

### To Run an Evaluation:

1. **Prepare Excel** with required columns:
   - Minimum: `User Query`
   - Recommended: + `Chatbot Role`, `Initial Conversation`

2. **Configure models** in `config.py`:
   - `BASE_MODEL["name"]` = your base model
   - `FINETUNED_MODEL["name"]` = your finetuned model

3. **Run command**:
   ```bash
   python3 evaluate.py input/your_file.xlsx --mode generate
   ```

4. **Check outputs** in `evaluation_result/`:
   - `*_metrics_only.json` - Clean scores
   - `*_summary.md` - Visual summary
   - `*_with_responses.xlsx` - Responses

### Key Points:

✅ Each ROW = One conversation  
✅ Initial Conversation = Previous turns (JSON)  
✅ User Query = Last message  
✅ Chatbot Role = Required for Role Adherence metric  
✅ Two modes: Generate (fresh responses) or Prerecorded (existing responses)

---

## Need Help?

- See `README.md` for quick start
- See `TECHNICAL_ARCHITECTURE.md` for technical details
- Check examples in `input/` folder

🚀 You're ready to run evaluations!

