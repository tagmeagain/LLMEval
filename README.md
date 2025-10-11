# DeepEval Multi-Turn Conversation Testing with Excel Support

Test and compare Base vs Finetuned models using multi-turn conversations loaded from Excel files. Uses DeepEval's built-in LLM-as-a-judge metrics for comprehensive evaluation.

## ✨ Features

✅ **Excel Support** - Load conversations with Model A and Model B responses  
✅ **System Prompt Integration** - Load system prompts from separate file  
✅ **Initial Conversation Support** - Include prior conversation context as JSON  
✅ **7 Evaluation Metrics** - Comprehensive multi-turn conversation assessment  
✅ **LLM-as-a-Judge** - Uses GPT-4 (or custom) for nuanced evaluation  
✅ **ConversationalTestCase** - Proper DeepEval format with Turn objects  
✅ **Easy Comparison** - Side-by-side Model A vs Model B evaluation  
✅ **Batch Processing** - Evaluate multiple Excel files at once  
✅ **JSON Results** - Detailed scores, reasoning, and comparisons  

---

## 📊 The 7 Metrics

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

## 🚀 Quick Start (3 Minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up API Key

```bash
cp env_template.txt .env
nano .env  # Add: OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Create System Prompt

```bash
cat > system_prompt.txt << 'EOF'
You are a professional customer support agent for TechCorp.
Be helpful, empathetic, and professional.
EOF
```

### Step 4: Organize Your Excel Files

```bash
# Create input folder
mkdir -p input

# Place your Excel files in input/
# Move your test files to input/ folder
```

### Step 5: Run Evaluation

```bash
python3 run_evaluation.py
```

**That's it!** ✅

Results will be in `evaluation_result/` folder:
- `*_results.json` - Evaluation scores
- `*_with_responses.xlsx` - Excel with generated responses (if applicable)
- `summary.json` - Combined summary

---

## 🎯 How It Works

The script **automatically detects** what to do:

```
┌─────────────────────────────────────────┐
│ Excel has Model A & B Response columns? │
└────────────┬────────────────────────────┘
             │
        ┌────┴────┐
        │         │
       YES       NO
        │         │
        ↓         ↓
   Pre-recorded   Generate
    responses     on-the-fly
        │         │
        ↓         ↓
   Evaluate    Call models
    directly    → Evaluate
        │         │
        └────┬────┘
             ↓
    Save to evaluation_result/
```

**You don't need to choose** - the script figures it out! 🎉

---

## 📋 Excel File Format

### Required Columns

| Column Name | Required | Description | Example |
|-------------|----------|-------------|---------|
| **Turn** | Yes | Turn number (1, 2, 3, ...) | 1, 2, 3, 4 |
| **User Query** | Yes | What the user asked | "I can't log into my account" |
| **Model A Response** | Yes | Base model's actual response | "Have you tried resetting your password?" |
| **Model B Response** | Yes | Finetuned model's actual response | "I understand you're frustrated. Let me help..." |

### Optional Columns

| Column Name | Required | Description | Example |
|-------------|----------|-------------|---------|
| **Initial Conversation** | Optional | Prior conversation as JSON array (first row only) | `[{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]` |
| **Scenario** | Optional | Test scenario description | "Frustrated user asking for refund" |
| **Expected Outcome** | Optional | Expected result | "User successfully resets password" |
| **Chatbot Role** | Optional | Role the chatbot should play | "Professional support agent" |

### Example 1: Simple Excel (Minimal)

| Turn | User Query | Model A Response | Model B Response |
|------|------------|------------------|------------------|
| 1 | I can't log into my account | Have you tried resetting your password? | I understand you're unable to access your account. This must be frustrating. Let's get this resolved. Have you tried using the 'Forgot Password' feature? |
| 2 | Yes, I didn't get the reset email | Can you check your spam folder? | Let me check a few things. First, can you confirm you've checked your spam/junk folder? |
| 3 | I checked spam, nothing there | What email is your account registered with? | Since you've confirmed it's not in spam, could you provide the email address registered with your account? |
| 4 | It's john@example.com | I'll send you a reset link | Perfect! I've just manually triggered a password reset for john@example.com. You should receive it within 2-3 minutes. Is there anything else I can help you with? |

### Example 2: With Initial Conversation (Advanced)

| Turn | Initial Conversation | User Query | Model A Response | Model B Response | Scenario | Chatbot Role |
|------|---------------------|------------|------------------|------------------|----------|--------------|
| 1 | `[{"role":"user","content":"Hello"},{"role":"assistant","content":"Hi! How can I help?"}]` | I need a refund | Sure, order number? | I'd be happy to help with your refund. Could you provide your order number? | Customer requesting refund | Professional support agent |
| 2 | | Order #12345 | Processing... | Thank you! I've located order #12345. The refund is being processed now. | | |
| 3 | | How long? | 5-7 days | Refunds typically process within 5-7 business days. You'll receive confirmation via email. | | |

> **Note**: The **Initial Conversation** column contains a JSON array representing prior conversation turns that happened before your test turns. This is useful for testing conversations that have context.

---

## 📖 Detailed Usage Scenarios

### Scenario A: You Have Pre-Recorded Responses in Excel

**Use this when**: You already collected Model A and Model B responses and have them in Excel

**Excel columns needed**: Turn, User Query, Model A Response, Model B Response

**Steps**:

1. **Prepare files**:
   ```bash
   # Create system_prompt.txt (optional)
   cat > system_prompt.txt << 'EOF'
   You are a professional customer support agent.
   Be helpful, friendly, and professional.
   EOF
   
   # Your Excel has: Turn | User Query | Model A Response | Model B Response
   ```

2. **Run evaluation**:
   ```bash
   python3 evaluate_with_system_prompt.py your_conversations.xlsx
   ```

3. **View results**:
   ```bash
   cat results_your_conversations.json
   ```

**What happens**:
- ✅ Loads pre-recorded responses from Excel
- ✅ Evaluates both with 7 metrics
- ✅ No model inference calls needed
- ✅ Only judge model (GPT-4) is called for evaluation

---

### Scenario B: You Want to Generate Responses On-the-Fly

**Use this when**: You only have user queries and want models to generate responses in real-time

**Excel columns needed**: User Query (optional: Initial Conversation)

**Steps**:

1. **Prepare files**:
   ```bash
   # Create system_prompt.txt
   cat > system_prompt.txt << 'EOF'
   You are a professional customer support agent for TechCorp.
   Be helpful, empathetic, and professional.
   EOF
   
   # Your Excel only has: User Query column
   ```

2. **Configure your models** in `config.py`:
   ```python
   BASE_MODEL = {
       "name": "gpt-3.5-turbo",  # Your base model
       "api_key": OPENAI_API_KEY,
       "temperature": 0.7,
       "max_tokens": 500
   }
   
   FINETUNED_MODEL = {
       "name": "ft:gpt-3.5-turbo:your-org:model:id",  # Your finetuned model
       "api_key": OPENAI_API_KEY,
       "temperature": 0.7,
       "max_tokens": 500
   }
   ```

3. **Run live evaluation**:
   ```bash
   python3 live_evaluation_example.py your_queries.xlsx
   ```

4. **View results**:
   ```bash
   cat live_results_your_queries.json
   ```

**What happens**:
- ✅ Loads user queries from Excel
- ✅ Loads system prompt from `system_prompt.txt`
- ✅ Calls Model A to generate responses
- ✅ Calls Model B to generate responses
- ✅ Evaluates both with 7 metrics
- ✅ Saves responses + scores to JSON

---

### Scenario C: Batch Process Multiple Excel Files

**Use this when**: You have multiple test files to evaluate

**Steps**:

1. **Organize your files**:
   ```bash
   test_cases/
   ├── test1.xlsx
   ├── test2.xlsx
   └── test3.xlsx
   ```

2. **Create batch script** `run_batch.py`:
   ```python
   from evaluate_with_system_prompt import batch_evaluate
   import glob
   
   # Get all Excel files
   excel_files = glob.glob("test_cases/*.xlsx")
   
   # Batch evaluate
   batch_evaluate(
       excel_files=excel_files,
       system_prompt_path="system_prompt.txt",
       use_all_metrics=True,
       judge_model="gpt-4"
   )
   ```

3. **Run batch**:
   ```bash
   python3 run_batch.py
   ```

---

## 💻 Usage

### Method 1: Simple Evaluation (Recommended)

**Use this when**: You have pre-recorded responses in Excel

```bash
# With system prompt (recommended)
python3 evaluate_with_system_prompt.py conversations.xlsx

# With custom system prompt location
python3 evaluate_with_system_prompt.py conversations.xlsx prompts/system.txt
```

**What it does**:
- ✅ Loads system prompt from `system_prompt.txt`
- ✅ Loads conversations from Excel
- ✅ Handles initial conversation JSON automatically
- ✅ Evaluates with all 7 metrics
- ✅ Saves results to JSON
- ✅ Prints summary

### Method 2: Programmatic Evaluation

**Use this when**: You need more control or want to integrate into your own scripts

```python
from evaluate_with_system_prompt import load_and_evaluate

# Single file evaluation
load_and_evaluate(
    excel_path="conversations.xlsx",
    system_prompt_path="system_prompt.txt",
    test_name="Customer Support Test",
    use_all_metrics=True,    # All 7 metrics
    judge_model="gpt-4"      # Judge model
)
```

### Method 3: Batch Evaluation

**Use this when**: You have multiple Excel files to test

```python
from evaluate_with_system_prompt import batch_evaluate

# Evaluate multiple files with same system prompt
batch_evaluate(
    excel_files=[
        "customer_support_tests.xlsx",
        "sales_tests.xlsx",
        "technical_support_tests.xlsx"
    ],
    system_prompt_path="system_prompt.txt",
    use_all_metrics=True,
    judge_model="gpt-4"
)
```

### Method 4: Manual Control (Advanced)

**Use this when**: You need complete control over the evaluation process

```python
from excel_loader import ExcelConversationLoader
from multi_turn_testing import MultiTurnTester
from config import BASE_MODEL, FINETUNED_MODEL

# 1. Load system prompt
with open("system_prompt.txt", "r") as f:
    system_prompt = f.read()

# 2. Load test cases from Excel
loader = ExcelConversationLoader("your_file.xlsx")
model_a_test_case, model_b_test_case = loader.parse_conversation_from_excel()

# 3. Add system prompt to test cases
model_a_test_case.context = [system_prompt]
model_b_test_case.context = [system_prompt]

# 4. Initialize tester with all 7 metrics
tester = MultiTurnTester(
    BASE_MODEL,
    FINETUNED_MODEL,
    judge_model="gpt-4",
    use_all_metrics=True  # Use all 7 metrics
)

# 5. Evaluate
result = tester.evaluate_from_excel_test_cases(
    model_a_test_case,
    model_b_test_case,
    "My Test Case Name"
)

# 6. Save and view results
tester.save_results("results.json")
tester.print_summary()
```

### What Gets Created

The `ConversationalTestCase` follows [DeepEval's format](https://deepeval.com/docs/evaluation-multiturn-test-cases):

```python
from deepeval.test_case import ConversationalTestCase, Turn

ConversationalTestCase(
    turns=[
        Turn(role="user", content="I can't log in"),
        Turn(role="assistant", content="Let me help..."),
        Turn(role="user", content="Still not working"),
        Turn(role="assistant", content="Try this...")
    ],
    context=["Optional system context"],
    scenario="Optional scenario description",
    expected_outcome="Optional expected outcome",
    chatbot_role="Optional role description"
)
```

Custom metrics use [Conversational GEval](https://deepeval.com/docs/metrics-conversational-g-eval):

```python
from deepeval.metrics import ConversationalGEval
from deepeval.test_case import TurnParams

ConversationalGEval(
    name="Coherence",
    evaluation_steps=["Step 1", "Step 2", ...],
    evaluation_params=[TurnParams.CONTENT],  # Evaluates turn content
    model="gpt-4"
)
```

---

## 📖 Detailed Usage Guide

### Step-by-Step: Complete Workflow

#### Step 1: Prepare Your Data Files

**A. Create `system_prompt.txt`**

This file contains your system prompt that was used to generate the model responses:

```txt
You are a professional customer support agent for TechCorp.

Guidelines:
- Be friendly and professional
- Solve customer issues efficiently
- Always verify user identity before discussing account details
- Escalate to manager for complex billing issues
- Use customer's name when known
```

**B. Create your Excel file**

Create `my_test.xlsx` with your actual conversations:

| Turn | Initial Conversation | User Query | Model A Response | Model B Response | Scenario | Chatbot Role |
|------|---------------------|------------|------------------|------------------|----------|--------------|
| 1 | `[{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello! How can I help?"}]` | I need a refund for my order | What's your order number? | I'd be happy to help with your refund request. Could you please provide your order number so I can look into this? | Customer requesting refund | Professional support agent |
| 2 | | It's order #12345 | Let me check. Found it. Refund will be processed. | Thank you! I've located order #12345 from March 15th. I'll process the refund right away. You should see it in 5-7 business days. | | |
| 3 | | Can I get it faster? | No expedited processing available. | I understand you'd like it sooner. We can offer expedited processing which reduces the time to 1-2 business days. Would you like me to proceed with that? | | |

**Key points**:
- Each row is one turn of the conversation
- Model A = Base model responses
- Model B = Finetuned model responses
- Initial Conversation (optional) = Prior context as JSON
- Fill optional columns only in first row

#### Step 2: Run the Evaluation

```bash
python3 evaluate_with_system_prompt.py my_test.xlsx
```

You'll see:
```
================================================================================
DEEPEVAL MULTI-TURN CONVERSATION EVALUATION
================================================================================

📄 Loading system prompt from: system_prompt.txt
✓ System prompt loaded (245 characters)

📊 Loading conversations from Excel: my_test.xlsx
✓ Loaded test case with 8 turns
  - Initial conversation: 2 prior turns
  - Scenario: Customer requesting refund
  - Chatbot Role: Professional support agent
✓ System prompt added to test cases as context

--------------------------------------------------------------------------------
PREVIEW - Model A (Base Model)
--------------------------------------------------------------------------------
  Turn 1 [user]: Hi
  Turn 2 [assistant]: Hello! How can I help?
  Turn 3 [user]: I need a refund for my order
  Turn 4 [assistant]: What's your order number?
  Turn 5 [user]: It's order #12345
  Turn 6 [assistant]: Let me check. Found it. Refund will be processed.
  ... and 2 more turns

================================================================================
RUNNING EVALUATION: Excel Test: my_test.xlsx
================================================================================

Evaluating Model A (Base)...
Evaluating Model B (Finetuned)...

✅ EVALUATION COMPLETE
Results saved to: results_my_test.json
```

#### Step 3: Review Results

The results are saved in `results_my_test.json`:

```json
{
  "test_case_name": "Excel Test: my_test.xlsx",
  "model_a_evaluation": {
    "model": "Model A (Base)",
    "metrics": {
      "Coherence": {"score": 0.75, "reason": "..."},
      "Contextual Understanding": {"score": 0.70, "reason": "..."},
      "Helpfulness": {"score": 0.65, "reason": "..."},
      "Knowledge Retention": {"score": 0.60, "pass": true, "reason": "..."},
      "Turn Relevancy": {"score": 0.72, "pass": true, "reason": "..."},
      "Role Adherence": {"score": 0.68, "pass": true, "reason": "..."},
      "Conversation Completeness": {"score": 0.70, "pass": true, "reason": "..."}
    }
  },
  "model_b_evaluation": {
    "model": "Model B (Finetuned)",
    "metrics": {
      "Coherence": {"score": 0.90, "reason": "..."},
      "Contextual Understanding": {"score": 0.88, "reason": "..."},
      "Helpfulness": {"score": 0.92, "reason": "..."},
      "Knowledge Retention": {"score": 0.85, "pass": true, "reason": "..."},
      "Turn Relevancy": {"score": 0.89, "pass": true, "reason": "..."},
      "Role Adherence": {"score": 0.91, "pass": true, "reason": "..."},
      "Conversation Completeness": {"score": 0.87, "pass": true, "reason": "..."}
    }
  }
}
```

---

## ⚙️ Configuration Options

### Use Only Built-in Metrics

```python
# Use only 4 built-in DeepEval metrics (no custom ConversationalGEval metrics)
load_and_evaluate(
    excel_path="conversations.xlsx",
    use_all_metrics=False  # Only 4 built-in metrics
)
```

### Change Judge Model

```python
# Use GPT-3.5 instead of GPT-4 (faster but potentially less accurate)
load_and_evaluate(
    excel_path="conversations.xlsx",
    judge_model="gpt-3.5-turbo"  # Alternative judge model
)
```

### Custom Column Names

If your Excel has different column names:

```python
loader = ExcelConversationLoader("your_file.xlsx")
model_a, model_b = loader.parse_conversation_from_excel(
    turn_col="Turn Number",
    user_query_col="Customer Question",
    model_a_col="Base Model Answer",
    model_b_col="Finetuned Answer",
    context_col="Initial Conversation",  # For JSON initial conversation
    scenario_col="Test Scenario",
    expected_outcome_col="Expected Result",
    chatbot_role_col="Agent Role"
)
```

### Test Multiple Files

```python
import glob

# Get all Excel files in a directory
excel_files = glob.glob("test_cases/*.xlsx")

# Batch evaluate
from evaluate_with_system_prompt import batch_evaluate
batch_evaluate(
    excel_files=excel_files,
    system_prompt_path="system_prompt.txt"
)
```

---

## 📊 Results Format

### JSON Output

```json
{
  "test_case_name": "My Test Case",
  "model_a_evaluation": {
    "model": "Model A (Base)",
    "metrics": {
      "Coherence": {"score": 0.75, "reason": "..."},
      "Contextual Understanding": {"score": 0.70, "reason": "..."},
      "Helpfulness": {"score": 0.80, "reason": "..."},
      "Knowledge Retention": {"score": 0.65, "pass": true, "reason": "..."},
      "Turn Relevancy": {"score": 0.72, "pass": true, "reason": "..."},
      "Role Adherence": {"score": 0.78, "pass": true, "reason": "..."},
      "Conversation Completeness": {"score": 0.68, "pass": true, "reason": "..."}
    }
  },
  "model_b_evaluation": {
    "model": "Model B (Finetuned)",
    "metrics": { /* same structure with different scores */ }
  }
}
```

### Score Interpretation

- **0.9 - 1.0**: Excellent ⭐⭐⭐
- **0.8 - 0.9**: Good ⭐⭐
- **0.7 - 0.8**: Acceptable ⭐
- **0.6 - 0.7**: Needs improvement ⚠️
- **Below 0.6**: Poor ❌

---

## 📁 Project Structure

```
DeepEval/
├── README.md                    # This file
├── config.py                    # Model configurations
├── requirements.txt             # Dependencies
├── excel_loader.py              # Excel → ConversationalTestCase converter
├── multi_turn_testing.py        # Main evaluation framework
├── example_excel_testing.py     # Example usage + template generator
├── model_wrapper.py             # Model API wrapper
└── test_cases.py                # Pre-built test scenarios
```

---

## 🔍 Metric Definitions

### 1. Coherence (Conversational GEval)
**Type**: Custom conversational metric using **Conversational GEval**  
**Definition**: The collective quality of all sentences in the conversation  
**Evaluates**: Logical flow, smooth transitions, overall clarity  
**Example**: Does the conversation make sense as a whole?

### 2. Contextual Understanding (Conversational GEval)
**Type**: Custom conversational metric using **Conversational GEval**  
**Definition**: Assistant's ability to understand and maintain context  
**Evaluates**: Context awareness, building on previous information  
**Example**: Does the assistant understand the full situation?

### 3. Helpfulness (Conversational GEval)
**Type**: Custom conversational metric using **Conversational GEval**  
**Definition**: How helpful and actionable the responses are  
**Evaluates**: Practical value, usefulness, problem-solving  
**Example**: Does the response actually help the user?

### 4. Knowledge Retention ✅
**Definition**: Remembers and references earlier information  
**Evaluates**: Memory of details, consistency across turns  
**Example**: If user says "My name is Alex" in turn 1, assistant uses it in turn 3  
**Formula**: (Satisfied Intentions) / (Total Intentions)  
[📚 Official Docs](https://deepeval.com/docs/metrics-knowledge-retention)

### 5. Turn Relevancy ✅
**Definition**: Each response is relevant to the query  
**Evaluates**: On-topic responses, no irrelevant tangents  
**Example**: Does each turn address what the user just asked?  
**Formula**: (Relevant Turns) / (Total Assistant Turns)  
[📚 Official Docs](https://deepeval.com/docs/metrics-turn-relevancy)

### 6. Role Adherence ✅
**Definition**: Maintains consistent role, tone, personality  
**Evaluates**: Consistent behavior, no out-of-character responses  
**Example**: If assistant is "professional agent," stays professional throughout  
**Formula**: Checks if each turn adheres to specified chatbot role  
[📚 Official Docs](https://deepeval.com/docs/metrics-role-adherence)

### 7. Conversation Completeness ✅
**Definition**: All queries addressed, satisfactory conclusion  
**Evaluates**: Complete answers, no unresolved issues  
**Example**: Are all user's concerns resolved by the end?  
**Formula**: (Satisfied User Intentions) / (Total User Intentions)  
[📚 Official Docs](https://deepeval.com/docs/metrics-conversation-completeness)

---

## 🛠️ Advanced Usage

### Multiple Excel Sheets

```python
loader = ExcelConversationLoader("tests.xlsx")
conversations = loader.load_multiple_conversations(
    sheet_names=["Test 1", "Test 2", "Test 3"]
)

for idx, (model_a, model_b) in enumerate(conversations, 1):
    tester.evaluate_from_excel_test_cases(model_a, model_b, f"Test {idx}")

tester.print_summary()
```

### Multiple Excel Files

```python
import glob

for file_path in glob.glob("test_cases/*.xlsx"):
    loader = ExcelConversationLoader(file_path)
    model_a, model_b = loader.parse_conversation_from_excel()
    tester.evaluate_from_excel_test_cases(model_a, model_b, file_path)

tester.print_summary()
```

### Generate New Responses

```python
# Extract only user queries from Excel
loader = ExcelConversationLoader("user_queries.xlsx")
user_turns = loader.extract_user_turns_only()

# Generate fresh responses from both models
tester = MultiTurnTester(BASE_MODEL, FINETUNED_MODEL)
base_conv, finetuned_conv = tester.generate_conversations(user_turns)

# Evaluate
result = tester.evaluate_from_excel_test_cases(base_conv, finetuned_conv, "Fresh Test")
```

---

## ❓ FAQ

### General Questions

**Q: Do I need to configure BASE_MODEL and FINETUNED_MODEL?**  
A: No! If you already have Model A and Model B responses in your Excel file, you don't need to configure these. They're only needed if you want to generate new responses.

**Q: Do I need API keys for both models if I have pre-recorded responses in Excel?**  
A: No! If using pre-recorded responses, you only need the API key for the judge model (GPT-4 by default).

**Q: What's the Initial Conversation column for?**  
A: It lets you include prior conversation context before your test turns. Format it as a JSON array like: `[{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]`

**Q: What's the difference between system prompt and Initial Conversation?**  
A: 
- **System prompt** (from `system_prompt.txt`): Instructions to the AI about its role and behavior
- **Initial Conversation**: Actual prior conversation turns that happened before your test

### Excel Questions

**Q: Can I use my own Excel format?**  
A: Yes! Use custom column mappings in `parse_conversation_from_excel()`. See [Custom Column Names](#custom-column-names) section.

**Q: What if my conversation has more than 4 turns?**  
A: No problem! The metrics work with any number of turns. You can have 2, 10, 50+ turns.

**Q: Can I test multiple conversations in one Excel file?**  
A: Use separate sheets for separate conversations, or create multiple Excel files and use batch evaluation.

### Performance

**Q: How many API calls does evaluation make?**  
A: With GPT-4 as judge:
- 14 API calls per test case (7 metrics × 2 models)
- If generating responses: Additional model API calls for each user query

**Q: How can I optimize for speed?**  
A: 
1. Use `use_all_metrics=False` (4 metrics instead of 7)
2. Use pre-recorded responses (no model generation needed)
3. Test with smaller batches initially

### Technical Questions

**Q: Can I use local models as judges?**  
A: Yes! Pass a custom `DeepEvalBaseLLM` model to the `judge_model` parameter.

**Q: What format are the results in?**  
A: JSON format with detailed scores, reasons, and pass/fail for each metric.

**Q: Can I integrate this into CI/CD?**  
A: Yes! Run `python3 evaluate_with_system_prompt.py test.xlsx` in your pipeline. Check exit code and parse JSON results.

---

## 🎯 Complete Example Workflow

### Real-World Example: Customer Support Chatbot

**Scenario**: You're testing a finetuned customer support chatbot against the base model.

#### Step 1: Prepare System Prompt

Create `system_prompt.txt`:
```
You are a professional customer support agent for TechCorp, a SaaS company.

Your role:
- Be empathetic and professional
- Resolve customer issues efficiently
- Always verify user identity before accessing account details
- Escalate complex billing issues to managers
- Use customer's name when available
- Provide clear next steps

Communication style:
- Friendly but professional
- Use complete sentences
- Avoid technical jargon unless necessary
- Acknowledge customer frustration when present
```

#### Step 2: Create Excel Test File

Create `customer_support_test.xlsx`:

| Turn | Initial Conversation | User Query | Model A Response | Model B Response | Scenario | Expected Outcome | Chatbot Role |
|------|---------------------|------------|------------------|------------------|----------|------------------|--------------|
| 1 | | I've been charged twice for my subscription | Can you provide your account email? | I'm sorry to hear you've been charged twice. That's definitely frustrating. Let me help you resolve this right away. Could you please provide your account email address? | Billing issue - duplicate charge | Issue acknowledged and resolved | Professional support agent |
| 2 | | sarah@example.com | Let me check. I see duplicate charges. | Thank you, Sarah. I've pulled up your account and can confirm there are indeed two duplicate charges on March 15th. I'll process a refund for one of these right now. | | | |
| 3 | | How long will the refund take? | 5-7 business days | The refund will be processed immediately on our end, and you should see it back in your account within 5-7 business days. I'll also send you a confirmation email with the refund details and a reference number. Is there anything else I can help you with today? | | | |

#### Step 3: Run Evaluation

```bash
python3 evaluate_with_system_prompt.py customer_support_test.xlsx
```

#### Step 4: Review Results

Open `results_customer_support_test.json`:

**Model A Scores**:
- Coherence: 0.75
- Contextual Understanding: 0.70
- Helpfulness: 0.72
- Knowledge Retention: 0.68
- Turn Relevancy: 0.75
- Role Adherence: 0.70
- Conversation Completeness: 0.73

**Model B Scores**:
- Coherence: 0.92
- Contextual Understanding: 0.90
- Helpfulness: 0.94
- Knowledge Retention: 0.88
- Turn Relevancy: 0.91
- Role Adherence: 0.93
- Conversation Completeness: 0.90

**Analysis**:
- Model B shows 20-25% improvement across all metrics
- Particularly strong in Helpfulness (+30%) and Role Adherence (+33%)
- Knowledge Retention improved (remembers customer name)
- More empathetic and complete responses

#### Step 5: Iterate

Based on results:
1. ✅ Model B handles empathy well
2. ✅ Model B provides more complete information
3. 🔄 Could improve response times in training data
4. 🔄 Add more edge cases (complex refund scenarios, frustrated customers)

Create more test cases and repeat!

---

## 🔧 How It Works (Technical Overview)

### High-Level Flow

```
Excel File → Parse → ConversationalTestCase → Evaluate → Results JSON
```

### Detailed Process

1. **Excel Parsing** (`excel_loader.py`)
   - Reads Excel file with pandas
   - Parses Initial Conversation JSON (if present)
   - Creates `Turn` objects for each row
   - Builds two `ConversationalTestCase` objects (Model A & Model B)

2. **System Prompt Integration** (`evaluate_with_system_prompt.py`)
   - Loads `system_prompt.txt`
   - Adds as `context` to test cases
   - Context used by metrics for evaluation

3. **Metric Configuration** (`multi_turn_testing.py`)
   - Creates 7 metric objects
   - Each configured with evaluation steps and judge model
   - Metrics are ConversationalGEval (custom) or built-in DeepEval

4. **Evaluation Execution** (DeepEval framework)
   - For each metric on each model:
     - Format conversation as text
     - Build prompt with evaluation criteria
     - Send to GPT-4 (judge model)
     - GPT-4 returns score (0-1) + reasoning
     - Parse and store results

5. **Results Aggregation**
   - Collect all 7 metric scores for both models
   - Save to JSON with detailed reasoning
   - Print summary statistics

### LLM-as-a-Judge Process

Each metric works like this:

```python
# 1. Receive conversation
conversation = [
  Turn(role="user", content="Hello"),
  Turn(role="assistant", content="Hi there!")
]

# 2. Format for judge
text = "USER: Hello\nASSISTANT: Hi there!"

# 3. Build prompt
prompt = f"""
Evaluate this conversation for Coherence.
Steps:
1. Check logical flow
2. Assess transitions
3. Rate 0-1

Conversation:
{text}

Return JSON: {{"score": 0.85, "reason": "..."}}
"""

# 4. Send to GPT-4
response = gpt4(prompt)

# 5. Parse result
{"score": 0.85, "reason": "Natural flow...", "pass": True}
```

### Why This Works

- **Proper Format**: Uses DeepEval's `ConversationalTestCase` (not plain dicts)
- **LLM-as-a-Judge**: GPT-4 evaluates like a human would
- **Multi-Turn Aware**: Metrics see full conversation context
- **Standardized**: Follows official DeepEval documentation

### API Usage Model

- **Per Test Case**: 14 GPT-4 API calls (7 metrics × 2 models)
- **Formula**: 7 metrics × 2 models × number of test cases
- **Additional**: If generating responses, add model API calls per user query

**📖 For complete technical details, see**: [`TECHNICAL_ARCHITECTURE.md`](TECHNICAL_ARCHITECTURE.md)

---

## 📚 Additional Resources

- [DeepEval Documentation](https://deepeval.com/docs/)
- [Multi-Turn Test Cases](https://deepeval.com/docs/evaluation-multiturn-test-cases)
- [Conversational GEval](https://deepeval.com/docs/metrics-conversational-g-eval)
- [Knowledge Retention Metric](https://deepeval.com/docs/metrics-knowledge-retention)
- [Turn Relevancy Metric](https://deepeval.com/docs/metrics-turn-relevancy)
- [Role Adherence Metric](https://deepeval.com/docs/metrics-role-adherence)
- [Conversation Completeness Metric](https://deepeval.com/docs/metrics-conversation-completeness)

---

## ✅ Summary

- ✅ **Excel support ready** - Load conversations directly
- ✅ **Proper DeepEval format** - Uses `ConversationalTestCase` with `Turn` objects
- ✅ **All 7 metrics** - Knowledge Retention, Turn Relevancy, Role Adherence, Conversation Completeness + 3 more
- ✅ **Built-in metrics** - Using DeepEval's official multi-turn metrics
- ✅ **LLM-as-a-judge** - GPT-4 provides nuanced evaluation
- ✅ **Production ready** - JSON outputs, comprehensive results

---

## 📁 Project Files & When to Use Them

| File | Purpose | When to Use |
|------|---------|-------------|
| **`run_evaluation.py`** | **🌟 MAIN SCRIPT - Use This!** | Auto-detects mode, processes all files in input/ |
| `evaluate_with_system_prompt.py` | Evaluate pre-recorded responses | Advanced: Single file with pre-recorded responses |
| `live_evaluation_example.py` | Generate responses on-the-fly | Advanced: Single file, generate responses |
| `excel_loader.py` | Loads Excel → ConversationalTestCase | Internal - called by scripts |
| `multi_turn_testing.py` | Core evaluation framework | Internal - evaluation engine |
| `config.py` | Model configurations | Edit to set your model IDs (if generating) |
| `system_prompt.txt` | System prompt | Create this with your prompt |
| `requirements.txt` | Python dependencies | Install with pip |
| `README.md` | This file - User guide | Documentation |
| `TECHNICAL_ARCHITECTURE.md` | Technical documentation | For engineering team |
| `example_excel_testing.py` | Creates Excel template | Run to create template |

### Recommended Workflow

**90% of users should just use**: `run_evaluation.py`

It automatically:
- ✅ Finds all Excel files in `input/` folder
- ✅ Detects if responses exist or need generation
- ✅ Handles system prompt and initial conversation
- ✅ Saves everything to `evaluation_result/` folder

---

## 🚀 Quick Commands Cheat Sheet

### Initial Setup (One Time)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup API key
cp env_template.txt .env
nano .env  # Add your OPENAI_API_KEY

# 3. Create directories and system prompt
mkdir -p input evaluation_result
cat > system_prompt.txt << 'EOF'
You are a professional customer support agent for TechCorp.
Be helpful, friendly, and professional.
EOF

# 4. (Optional) Configure models in config.py if generating responses
```

### Running Evaluations (Recommended)

```bash
# 1. Place Excel files in input/ folder
cp your_test.xlsx input/

# 2. Run evaluation (auto-detects everything!)
python3 run_evaluation.py

# 3. View results
ls evaluation_result/
cat evaluation_result/*_results.json
```

### Alternative: Individual Scripts

```bash
# Pre-recorded responses only
python3 evaluate_with_system_prompt.py input/conversations.xlsx

# Generate responses on-the-fly only  
python3 live_evaluation_example.py input/queries.xlsx

# Create Excel template
python3 example_excel_testing.py
```

### Help Commands

```bash
# View main script help
python3 run_evaluation.py --help

# View results
cat evaluation_result/summary.json
cat evaluation_result/*_results.json
```

---

## ✅ Pre-Flight Checklist

### Using run_evaluation.py (Recommended)

- [ ] ✅ Installed dependencies: `pip install -r requirements.txt`
- [ ] ✅ Created `.env` with `OPENAI_API_KEY=sk-...`
- [ ] ✅ Created `system_prompt.txt`
- [ ] ✅ Created `input/` folder: `mkdir -p input`
- [ ] ✅ Placed Excel files in `input/` folder
- [ ] ✅ Excel has at minimum:
  - [ ] User Query column
  - [ ] Optional: Model A Response, Model B Response (if pre-recorded)
  - [ ] Optional: Initial Conversation (JSON format)
- [ ] ✅ (Only if generating) Configured models in `config.py`

**Run**: 
```bash
python3 run_evaluation.py                    # All files in input/
python3 run_evaluation.py my_test.xlsx       # Specific file
```

**Results**: Check `evaluation_result/` folder

---

## 🎯 Which Script Should I Use?

### 🌟 Recommended: `run_evaluation.py` (90% of use cases)

**Use this script for most cases** - it automatically handles everything:

```bash
# Process all files in input/ folder
python3 run_evaluation.py

# OR process specific file(s)
python3 run_evaluation.py test1.xlsx
python3 run_evaluation.py test1.xlsx test2.xlsx
python3 run_evaluation.py input/my_test.xlsx
```

**Automatically detects**:
- ✅ If responses exist → uses them
- ✅ If responses missing → generates them
- ✅ Processes all files in input/ OR specified files
- ✅ Saves to evaluation_result/

---

### Alternative Scripts (Advanced)

| Script | Use Case |
|--------|----------|
| `evaluate_with_system_prompt.py` | Single file with pre-recorded responses only |
| `live_evaluation_example.py` | Single file with live generation only |

**Most users should use `run_evaluation.py` instead** ✅

---

## 📂 Directory Structure

After setup, your project should look like this:

```
DeepEval/
├── input/                          ← Place Excel files here
│   ├── test1.xlsx
│   ├── test2.xlsx
│   └── test3.xlsx
├── evaluation_result/              ← Results saved here (auto-created)
│   ├── test1_results.json
│   ├── test1_with_responses.xlsx   (if generated)
│   ├── test2_results.json
│   ├── test2_with_responses.xlsx
│   └── summary.json
├── system_prompt.txt               ← Your system prompt
├── .env                            ← Your API key
├── config.py                       ← Model configs
├── run_evaluation.py               ← 🌟 MAIN SCRIPT
└── ...
```

**Ready to test!** 🚀

