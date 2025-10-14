# Technical Architecture & Internal Flow

## Overview

This framework evaluates multi-turn LLM conversations using DeepEval's LLM-as-a-judge methodology. It compares two models (Base vs Finetuned) by analyzing their responses in multi-turn conversations.

**Key Features**:
- Unified evaluation script (`run_evaluation.py`) that auto-detects processing mode
- Supports both pre-recorded responses and on-the-fly generation
- Organized input/output structure
- Comprehensive LLM-as-a-judge evaluation with 7 metrics

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      INPUT LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  input/                      system_prompt.txt                   │
│  ├── test1.xlsx              "You are a professional            │
│  ├── test2.xlsx               customer support agent..."         │
│  └── test3.xlsx                                                  │
│                                                                   │
│  Excel can have:                                                 │
│  - User Query (required)                                         │
│  - Model A/B Response (optional - for pre-recorded)             │
│  - Initial Conversation (optional - JSON)                        │
│  - Scenario, Chatbot Role, Expected Outcome (optional)          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                  UNIFIED RUNNER (run_evaluation.py)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Find all Excel files in input/ folder                       │
│  2. Load system_prompt.txt                                      │
│  3. For each Excel file:                                        │
│     ├─ Detect mode (pre-recorded vs generate)                  │
│     ├─ Branch to appropriate processing path                   │
│     └─ Save results to evaluation_result/                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
                    ┌────────┴─────────┐
                    │                  │
            ┌───────▼──────┐    ┌─────▼────────┐
            │ Pre-Recorded │    │  Generate    │
            │    Mode      │    │   Mode       │
            └───────┬──────┘    └─────┬────────┘
                    │                 │
                    ↓                 ↓
┌─────────────────────────────┐   ┌──────────────────────────────┐
│ PARSING LAYER               │   │ GENERATION LAYER             │
│                             │   │                              │
│ excel_loader.py             │   │ 1. Parse user queries        │
│ - Parse Excel               │   │ 2. Build conversation        │
│ - Create Turn objects       │   │ 3. Call Model A → responses  │
│ - Build ConversationalTC    │   │ 4. Call Model B → responses  │
│                             │   │ 5. Create ConversationalTC   │
└─────────────┬───────────────┘   └──────────────┬───────────────┘
              │                                   │
              └────────────────┬──────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              DEEPEVAL TEST CASE FORMAT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ConversationalTestCase (DeepEval Standard Format)              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ turns: [                                                │    │
│  │   Turn(role="user", content="Hello"),                  │    │
│  │   Turn(role="assistant", content="Hi there!"),         │    │
│  │   Turn(role="user", content="I need help"),            │    │
│  │   Turn(role="assistant", content="How can I help?")    │    │
│  │ ]                                                       │    │
│  │                                                         │    │
│  │ context: ["System prompt from system_prompt.txt"]      │    │
│  │ scenario: "Customer support" (from Excel)               │    │
│  │ chatbot_role: "Support agent" (from Excel)              │    │
│  │ expected_outcome: "Issue resolved" (from Excel)         │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Creates TWO test cases: one for Model A, one for Model B       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                     EVALUATION LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  multi_turn_testing.py                                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ MultiTurnTester                                        │    │
│  │                                                         │    │
│  │ evaluate_from_excel_test_cases()                       │    │
│  │   ├─ evaluate_conversation(Model A)                    │    │
│  │   │   └─ create_conversational_metrics()               │    │
│  │   │       ├─ 3 ConversationalGEval metrics             │    │
│  │   │       └─ 4 Built-in DeepEval metrics               │    │
│  │   │                                                     │    │
│  │   └─ evaluate_conversation(Model B)                    │    │
│  │       └─ Same 7 metrics                                │    │
│  │                                                         │    │
│  │ deepeval.evaluate() ← Core DeepEval function           │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    METRICS EVALUATION LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  7 Metrics (all use LLM-as-a-judge with GPT-4)                  │
│                                                                   │
│  Custom ConversationalGEval (3):          Built-in (4):         │
│  ┌──────────────────────────┐           ┌────────────────────┐ │
│  │ 1. Coherence             │           │ 4. Knowledge       │ │
│  │ 2. Contextual Understand │           │    Retention       │ │
│  │ 3. Helpfulness           │           │ 5. Turn Relevancy  │ │
│  └──────────────────────────┘           │ 6. Role Adherence  │ │
│                                          │ 7. Completeness    │ │
│                                          └────────────────────┘ │
│                                                                   │
│  Each metric:                                                    │
│  1. Formats conversation                                         │
│  2. Builds evaluation prompt                                     │
│  3. Sends to GPT-4 (judge model)                                │
│  4. Receives score (0-1) + reasoning                            │
│  5. Returns result                                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                       OUTPUT LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  evaluation_result/                                              │
│  ├── test1_results.json           ← Scores & reasoning          │
│  ├── test1_with_responses.xlsx    ← Excel with responses        │
│  ├── test2_results.json                                         │
│  ├── test2_with_responses.xlsx                                  │
│  └── summary.json                 ← Combined summary            │
│                                                                   │
│  JSON Format:                                                    │
│  {                                                               │
│    "model_a_evaluation": {                                       │
│      "metrics": {                                                │
│        "Coherence": {score: 0.75, reason: "..."},               │
│        "Helpfulness": {score: 0.80, ...}                        │
│      }                                                           │
│    },                                                            │
│    "model_b_evaluation": { ... }                                │
│  }                                                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Execution Flow

### Entry Point: run_evaluation.py

**What happens when you run `python3 run_evaluation.py`**:

```python
"""
PHASE 1: INITIALIZATION
"""
1. Create directories if they don't exist
   os.makedirs("input", exist_ok=True)
   os.makedirs("evaluation_result", exist_ok=True)

2. Load system prompt from system_prompt.txt
   with open("system_prompt.txt") as f:
       system_prompt = f.read()

3. Find all Excel files in input/ folder
   excel_files = glob.glob("input/*.xlsx")
   # Found: input/test1.xlsx, input/test2.xlsx

"""
PHASE 2: MODE DETECTION (for each Excel file)
"""
4. Load Excel and detect mode
   df = pd.read_excel("input/test1.xlsx")
   
   if "Model A Response" in df.columns and "Model B Response" in df.columns:
       mode = "pre_recorded"  # Use existing responses
   else:
       mode = "generate"      # Generate responses on-the-fly

"""
PHASE 3A: PRE-RECORDED MODE
"""
5a. If pre-recorded:
    - Use ExcelConversationLoader
    - Parse Excel → ConversationalTestCase (with existing responses)
    - Add system prompt as context
    - Evaluate directly
    - Save results only (no Excel output needed)

"""
PHASE 3B: GENERATION MODE
"""
5b. If generate:
    - Parse user queries from Excel
    - Parse Initial Conversation JSON (if present)
    - Build conversation: system prompt + initial conversation + user queries
    - Call Model A → generate responses
    - Call Model B → generate responses
    - Create ConversationalTestCase for both
    - Evaluate both
    - Save results AND Excel with generated responses

"""
PHASE 4: EVALUATION (same for both modes)
"""
6. For each model (A and B):
   - Create 7 metrics
   - Run deepeval.evaluate()
   - Each metric calls GPT-4 (judge)
   - Collect scores and reasoning

"""
PHASE 5: OUTPUT
"""
7. Save to evaluation_result/
   - {filename}_results.json           (scores, reasoning)
   - {filename}_with_responses.xlsx    (if generated)
   - summary.json                      (all results combined)
```

---

## 🔀 Mode Detection Logic

### How the System Decides

```python
def detect_excel_mode(df):
    """
    Checks Excel columns to determine processing mode
    """
    has_model_a = "Model A Response" in df.columns
    has_model_b = "Model B Response" in df.columns
    
    if has_model_a and has_model_b:
        return "pre_recorded"  # Use existing responses
    else:
        return "generate"      # Generate new responses
```

### Mode Comparison

| Aspect | Pre-Recorded Mode | Generate Mode |
|--------|------------------|---------------|
| **Excel Columns** | User Query, Model A Response, Model B Response | User Query only |
| **Model Calls** | None (uses Excel responses) | Yes (calls both models) |
| **API Calls** | Only judge model (14 calls) | Models + judge (varies) |
| **Output** | JSON results only | JSON + Excel with responses |
| **Speed** | Faster (no generation) | Slower (waits for models) |
| **Requirements** | None | Configured models in config.py |

---

## 🔄 Detailed Internal Flow

### Step 1: Input Processing (run_evaluation.py)

**File**: `excel_loader.py`  
**Class**: `ExcelConversationLoader`

```python
# What happens internally:

1. Load Excel file using pandas
   df = pd.read_excel(excel_path)

2. Check for Initial Conversation (JSON)
   - If present: Parse as JSON array
   - Create Turn objects for prior conversation
   
3. For each row in Excel:
   - Extract user query
   - Extract Model A response
   - Extract Model B response
   - Create Turn objects:
     * Turn(role="user", content=user_query)
     * Turn(role="assistant", content=model_a_response)
   
4. Build ConversationalTestCase for each model:
   ConversationalTestCase(
     turns=[...],           # List of Turn objects
     context=[...],         # System prompt
     scenario="...",        # From Excel
     chatbot_role="...",    # From Excel
     expected_outcome="..." # From Excel
   )

5. Return two ConversationalTestCase objects
   - One for Model A (with Model A's responses)
   - One for Model B (with Model B's responses)
```

**Key Code**:
```python
# Creating Turn objects
model_a_turns.append(Turn(role="user", content=user_query))
model_a_turns.append(Turn(role="assistant", content=model_a_response))

# Building test case
model_a_test_case = ConversationalTestCase(
    turns=model_a_turns,
    context=[system_prompt],
    scenario=scenario,
    chatbot_role=chatbot_role
)
```

---

### Step 2: System Prompt Integration (evaluate_with_system_prompt.py)

**What happens**:

```python
1. Read system_prompt.txt
   with open("system_prompt.txt") as f:
       system_prompt = f.read()

2. Add to ConversationalTestCase
   model_a_test_case.context = [system_prompt]
   model_b_test_case.context = [system_prompt]
   
   # Context is used by metrics to understand expected behavior
```

---

### Step 3: Metric Creation (multi_turn_testing.py)

**File**: `multi_turn_testing.py`  
**Method**: `create_conversational_metrics()`

```python
def create_conversational_metrics(judge_model="gpt-4", use_all_metrics=True):
    """
    Creates 7 metric objects that will evaluate conversations
    
    Internal process:
    1. Each metric is initialized with:
       - evaluation_steps: What to check
       - evaluation_params: What data to use (TurnParams.CONTENT)
       - model: Which LLM to use as judge (GPT-4)
    
    2. Metrics are configured but NOT executed yet
    """
    
    return [
        # Custom ConversationalGEval metrics
        ConversationalGEval(
            name="Coherence",
            evaluation_steps=[
                "Evaluate whether conversation flows logically",
                "Check if responses are well-structured",
                ...
            ],
            evaluation_params=[TurnParams.CONTENT],
            model=judge_model  # GPT-4
        ),
        # ... 6 more metrics
    ]
```

**Key Point**: Metrics are just configured at this stage, not executed.

---

### Step 4: Evaluation Execution (DeepEval Framework)

**File**: `multi_turn_testing.py`  
**Method**: `evaluate_conversation()`

```python
def evaluate_conversation(test_case, model_name):
    """
    Internal flow:
    
    1. Get all 7 metrics (already configured)
    2. Pass test_case to DeepEval's evaluate() function
    3. DeepEval iterates through each metric
    4. For each metric:
       a. Metric extracts conversation turns
       b. Formats prompt for judge model
       c. Sends to GPT-4 with evaluation criteria
       d. GPT-4 returns score + reasoning
       e. Metric processes response
    5. Return all metric results
    """
    
    metrics = self.create_conversational_metrics(...)
    
    # DeepEval's evaluate function
    results = evaluate(
        test_cases=[test_case],  # ConversationalTestCase
        metrics=metrics,          # List of 7 metrics
        print_results=False
    )
    
    return results
```

---

### Step 5: LLM-as-a-Judge Process (How Each Metric Works)

This is the most important part - **how metrics actually evaluate**:

#### For ConversationalGEval Metrics (Coherence, Helpfulness, etc.)

```python
"""
Internal flow for ONE metric evaluation:

1. METRIC RECEIVES TEST CASE
   test_case.turns = [
     Turn(role="user", content="Hello"),
     Turn(role="assistant", content="Hi there!"),
     Turn(role="user", content="I need help"),
     Turn(role="assistant", content="How can I help?")
   ]

2. METRIC FORMATS CONVERSATION
   conversation_text = '''
   USER: Hello
   ASSISTANT: Hi there!
   USER: I need help
   ASSISTANT: How can I help?
   '''

3. METRIC CONSTRUCTS PROMPT FOR JUDGE
   prompt = f'''
   You are evaluating a conversation for Coherence.
   
   Evaluation Steps:
   1. Evaluate whether conversation flows logically
   2. Check if responses are well-structured
   3. Assess if there are smooth transitions
   
   Conversation:
   {conversation_text}
   
   Rate the conversation on a scale of 0 to 1.
   Provide reasoning for your score.
   
   Return JSON:
   {{
     "score": 0.85,
     "reason": "The conversation flows naturally..."
   }}
   '''

4. SEND TO GPT-4 (Judge Model)
   response = openai.chat.completions.create(
     model="gpt-4",
     messages=[{"role": "user", "content": prompt}],
     temperature=0
   )

5. PARSE GPT-4 RESPONSE
   result = json.loads(response.choices[0].message.content)
   score = result["score"]      # e.g., 0.85
   reason = result["reason"]    # "The conversation flows naturally..."

6. RETURN METRIC RESULT
   return {
     "score": 0.85,
     "pass": True if score >= threshold else False,
     "reason": "The conversation flows naturally..."
   }
"""
```

#### For Built-in Metrics (Knowledge Retention, Turn Relevancy, etc.)

These work similarly but have specialized logic:

**Knowledge Retention**:
```python
"""
1. Extract all information mentioned in early turns
   - Names, dates, order numbers, preferences, etc.

2. Check if information is used in later turns
   - Does assistant reference earlier info?
   - Is information retained correctly?

3. Calculate score:
   score = (retained_info_count / total_info_count)

4. Send to judge model for verification
   - Judge confirms if retention is appropriate
"""
```

**Turn Relevancy**:
```python
"""
1. For each assistant turn:
   - Get previous context (sliding window)
   - Get current user query
   - Get assistant response

2. Ask judge: "Is this response relevant to user query?"

3. Calculate score:
   score = (relevant_turns / total_turns)
"""
```

**Role Adherence**:
```python
"""
1. Get chatbot_role from test case
   chatbot_role = "Professional customer support agent"

2. For each assistant turn:
   - Check if response matches role
   - Verify tone, language, behavior

3. Ask judge: "Does this follow the role?"

4. Calculate score based on consistency
"""
```

**Conversation Completeness**:
```python
"""
1. Extract user intentions from all user turns
   intentions = ["Get refund", "Know timeline", "Confirm email"]

2. Check if each intention was satisfied
   - Did assistant address it?
   - Was resolution provided?

3. Calculate score:
   score = (satisfied_intentions / total_intentions)
"""
```

---

### Step 6: Results Aggregation

**What happens after all metrics evaluate**:

```python
# For Model A
model_a_results = {
    "Coherence": {score: 0.75, reason: "...", pass: True},
    "Contextual Understanding": {score: 0.70, ...},
    "Helpfulness": {score: 0.72, ...},
    "Knowledge Retention": {score: 0.68, pass: True, ...},
    "Turn Relevancy": {score: 0.75, pass: True, ...},
    "Role Adherence": {score: 0.70, pass: True, ...},
    "Conversation Completeness": {score: 0.73, pass: True, ...}
}

# Same for Model B
model_b_results = { ... }

# Combine into final result
final_result = {
    "test_case_name": "Excel Test",
    "model_a_evaluation": model_a_results,
    "model_b_evaluation": model_b_results
}

# Save to JSON
with open("results.json", "w") as f:
    json.dump(final_result, f, indent=2)
```

---

## 🔢 API Calls Breakdown

### For ONE test case with 4 turns:

**Pre-Recorded Mode** (responses already in Excel):
```
Model A Evaluation:
├─ Metric 1 (Coherence): 1 GPT-4 API call
├─ Metric 2 (Context):   1 GPT-4 API call
├─ Metric 3 (Helpful):   1 GPT-4 API call
├─ Metric 4 (Knowledge): 1 GPT-4 API call
├─ Metric 5 (Relevancy): 1 GPT-4 API call
├─ Metric 6 (Role):      1 GPT-4 API call
└─ Metric 7 (Complete):  1 GPT-4 API call
= 7 API calls

Model B Evaluation:
= 7 API calls

Total: 14 GPT-4 API calls (judge only)
```

**Generation Mode** (responses generated on-the-fly):
```
Model A Generation:
├─ Query 1 → Model A: 1 API call
├─ Query 2 → Model A: 1 API call
├─ Query 3 → Model A: 1 API call
└─ Query 4 → Model A: 1 API call
= 4 API calls

Model B Generation:
= 4 API calls

Evaluation (both models):
= 14 GPT-4 API calls

Total: 22 API calls (8 generation + 14 evaluation)
```

---

## 🎯 Key Design Decisions

### 1. Why ConversationalTestCase?

**Answer**: DeepEval requires this format for multi-turn evaluation. It's specifically designed for conversational AI testing.

```python
# DeepEval's format
ConversationalTestCase(
    turns=[Turn(...), Turn(...)],  # Multi-turn conversation
    context=[...],                   # Ground truth
    scenario="...",                  # Test scenario
    chatbot_role="..."              # Expected role
)

# This format allows metrics to:
# - Access full conversation history
# - Understand expected behavior (role, scenario)
# - Compare against ground truth (context)
```

### 2. Why LLM-as-a-Judge?

**Answer**: Traditional metrics (BLEU, ROUGE) don't work for open-ended conversations.

**Traditional metrics fail because**:
- Can't understand context
- Can't judge helpfulness
- Can't evaluate conversational flow
- Don't understand user intent

**LLM-as-a-judge succeeds because**:
- Understands natural language
- Can judge quality like a human
- Provides reasoning for scores
- Evaluates nuanced aspects

### 3. Why Separate Custom and Built-in Metrics?

**Answer**: 
- **Custom ConversationalGEval**: Flexible, define your own criteria
- **Built-in Metrics**: Specialized algorithms optimized for specific aspects

Example:
```python
# Custom: You define what "good" means
ConversationalGEval(
    name="Empathy",
    evaluation_steps=["Check if assistant shows empathy", ...]
)

# Built-in: Pre-built algorithm for specific task
KnowledgeRetentionMetric()  # Has specialized logic to track info retention
```

---

## 🔧 Technical Components

### Component 1: ExcelConversationLoader

**Purpose**: Parse Excel → ConversationalTestCase

**Key Methods**:
- `load_data()`: Read Excel file
- `parse_conversation_from_excel()`: Main parsing logic
- Handles JSON parsing for Initial Conversation
- Creates Turn objects for each row

**Input**: Excel file  
**Output**: 2× ConversationalTestCase objects

---

### Component 2: MultiTurnTester

**Purpose**: Orchestrate evaluation

**Key Methods**:
- `create_conversational_metrics()`: Initialize metrics
- `evaluate_conversation()`: Run evaluation
- `evaluate_from_excel_test_cases()`: Main entry point
- `save_results()`: Save JSON output

**Input**: ConversationalTestCase objects  
**Output**: JSON results

---

### Component 3: Metrics (7 total)

**Purpose**: Evaluate specific aspects

**Types**:
1. **ConversationalGEval** (Custom)
   - Flexible evaluation criteria
   - Uses GPT-4 to judge based on steps

2. **Built-in Metrics** (DeepEval)
   - Specialized algorithms
   - Optimized for specific tasks

---

## 📊 Data Flow Example

Let's trace one complete evaluation:

```
1. INPUT
   Excel row: Turn 1, "Hello", "Hi there!", "Hello! How can I help?"
   
2. PARSE
   Turn(role="user", content="Hello")
   Turn(role="assistant", content="Hi there!")  # Model A
   
3. CREATE TEST CASE
   ConversationalTestCase(turns=[...], context=[system_prompt])
   
4. EVALUATE
   For Coherence metric:
   - Format conversation text
   - Build prompt: "Evaluate coherence..."
   - Call GPT-4
   - Receive: {score: 0.85, reason: "..."}
   
5. AGGREGATE
   {
     "Coherence": {score: 0.85, ...},
     "Helpfulness": {score: 0.90, ...},
     ...
   }
   
6. OUTPUT
   Save to results.json
```

---

## 🎓 Summary for Engineering Team

**What this framework does**:
1. Loads multi-turn conversations from Excel
2. Converts to DeepEval's ConversationalTestCase format
3. Evaluates using 7 metrics (all LLM-as-a-judge)
4. Each metric sends conversation to GPT-4 for scoring
5. Returns detailed scores, reasoning, and pass/fail

**Why it works**:
- Uses proper DeepEval format (ConversationalTestCase)
- Leverages LLM-as-a-judge for nuanced evaluation
- Follows DeepEval's official documentation
- Handles multi-turn context properly

**Key innovation**:
- Excel → ConversationalTestCase bridge
- System prompt integration
- Initial conversation support (JSON)
- Batch processing capability

**Cost model**:
- 14 GPT-4 API calls per test case
- ~$0.50-1.00 per test case
- Can reduce by using fewer metrics or cheaper judge model

---

## 🔍 Debugging & Introspection

To see what's happening internally:

```python
# Enable verbose mode to see prompts sent to GPT-4
metric = ConversationalGEval(
    name="Coherence",
    evaluation_steps=[...],
    verbose_mode=True  # Prints intermediate steps
)

# Measure single metric standalone
metric.measure(test_case)
print(metric.score, metric.reason)

# This shows exactly what prompt was sent to judge
```

---

---

## 🎯 Complete Flow Diagram

### End-to-End Process

```
USER ACTION
    │
    ↓
[1] Place Excel files in input/
[2] Create system_prompt.txt
[3] Run: python3 run_evaluation.py
    │
    ↓
┌───────────────────────────────┐
│  run_evaluation.py STARTS     │
└───────────────┬───────────────┘
                │
                ↓
┌───────────────────────────────┐
│  Load system_prompt.txt       │
│  Find Excel files in input/   │
└───────────────┬───────────────┘
                │
                ↓
        For Each Excel File:
                │
                ↓
┌───────────────────────────────┐
│  Detect Mode                  │
│  ┌─────────────────────────┐ │
│  │ Check for Model A/B     │ │
│  │ Response columns?       │ │
│  └─────────┬───────────────┘ │
└────────────┼─────────────────┘
             │
      ┌──────┴──────┐
      │             │
   [YES]          [NO]
      │             │
      ↓             ↓
┌──────────┐  ┌─────────────┐
│Pre-      │  │Generate     │
│Recorded  │  │Mode         │
└────┬─────┘  └──────┬──────┘
     │               │
     ↓               ↓
[Load Excel]    [Parse Queries]
[Parse to TC]   [Call Model A]
     │          [Call Model B]
     │          [Create TC]
     │               │
     └───────┬───────┘
             ↓
    ┌────────────────┐
    │ Evaluate Both  │
    │ Test Cases     │
    │ (7 metrics ea) │
    └────────┬───────┘
             │
             ↓
    ┌────────────────┐
    │ Save Results   │
    │ to evaluation_ │
    │ result/        │
    └────────┬───────┘
             │
             ↓
    [Next Excel File]
             │
             ↓
┌────────────────────────┐
│  All Files Complete    │
│  Create summary.json   │
└────────────────────────┘
```

---

## 🔍 Data Transformation Examples

### Example 1: Pre-Recorded Mode

**Input Excel** (`input/test1.xlsx`):
| User Query | Model A Response | Model B Response |
|------------|------------------|------------------|
| Hello | Hi | Hello! How can I help? |
| I need help | What with? | I'd be happy to help! What do you need? |

**Transformed to**:
```python
# Model A Test Case
ConversationalTestCase(
    turns=[
        Turn(role="user", content="Hello"),
        Turn(role="assistant", content="Hi"),
        Turn(role="user", content="I need help"),
        Turn(role="assistant", content="What with?"),
    ],
    context=["System prompt from system_prompt.txt"]
)

# Model B Test Case  
ConversationalTestCase(
    turns=[
        Turn(role="user", content="Hello"),
        Turn(role="assistant", content="Hello! How can I help?"),
        Turn(role="user", content="I need help"),
        Turn(role="assistant", content="I'd be happy to help! What do you need?"),
    ],
    context=["System prompt from system_prompt.txt"]
)
```

**Output** (`evaluation_result/test1_results.json`):
```json
{
  "mode": "pre_recorded",
  "model_a_evaluation": {
    "Coherence": {"score": 0.65, "reason": "..."},
    "Helpfulness": {"score": 0.60, "reason": "..."}
  },
  "model_b_evaluation": {
    "Coherence": {"score": 0.90, "reason": "..."},
    "Helpfulness": {"score": 0.95, "reason": "..."}
  }
}
```

---

### Example 2: Generation Mode with Initial Conversation

**Input Excel** (`input/queries.xlsx`):
| Initial Conversation | User Query |
|---------------------|------------|
| `[{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]` | I need a refund |
| | How long will it take? |

**Transformed to**:
```python
# Full conversation for generation
conversation = [
    {"role": "system", "content": "System prompt..."},
    {"role": "user", "content": "Hi"},               # From Initial Conversation
    {"role": "assistant", "content": "Hello!"},      # From Initial Conversation
    {"role": "user", "content": "I need a refund"},  # From User Query
    {"role": "user", "content": "How long will it take?"}
]

# Send to Model A → generates 2 responses
# Send to Model B → generates 2 responses
```

**Output**:
1. `evaluation_result/queries_results.json` - Evaluation scores
2. `evaluation_result/queries_with_responses.xlsx` - Excel with generated responses added

---

## 🎓 Summary for Engineering Team

### What This System Does

**Input**:
- Excel files in `input/` folder
- System prompt in `system_prompt.txt`
- Optional: Initial conversation as JSON in Excel

**Processing**:
1. Auto-detects if responses exist or need generation
2. Converts to DeepEval's ConversationalTestCase format
3. Evaluates using 7 LLM-as-a-judge metrics
4. Each metric sends conversation to GPT-4 for scoring

**Output**:
- JSON results with scores and reasoning
- Excel with generated responses (if generated)
- Combined summary

### Key Technical Decisions

**1. Why ConversationalTestCase?**
- DeepEval's standard format for multi-turn conversations
- Required for conversational metrics
- Supports metadata (scenario, role, expected outcome)

**2. Why LLM-as-a-Judge?**
- Traditional metrics (BLEU, ROUGE) fail for open-ended conversations
- GPT-4 evaluates like a human reviewer
- Provides reasoning for scores
- Understands context and nuance

**3. Why Unified Script?**
- Single entry point for all use cases
- Auto-detection reduces user error
- Organized input/output structure
- Batch processing built-in

**4. Why Separate Modes?**
- Pre-recorded: Faster, cheaper (no model calls)
- Generation: Flexible, tests models directly

### Architecture Benefits

✅ **Modularity**: Each component has single responsibility  
✅ **Extensibility**: Easy to add new metrics or processing modes  
✅ **Automation**: Auto-detection reduces manual configuration  
✅ **Standardization**: Follows DeepEval official documentation  
✅ **Debuggability**: Clear layer separation, verbose logging  

**This architecture enables systematic, automated evaluation of multi-turn LLM conversations using industry-standard methodologies (DeepEval + LLM-as-a-judge).**

---

## 🔄 Detailed Component Flow

### Step 1: Input Processing (run_evaluation.py)


