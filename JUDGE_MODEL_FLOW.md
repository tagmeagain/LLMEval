# Judge Model Flow - Complete Technical Trace

## Overview

The judge model is the LLM used for LLM-as-a-judge evaluation. It's passed through the entire system and ultimately used by DeepEval to evaluate conversations.

---

## 🔄 Complete Flow

### Step 1: Entry Point (evaluate.py)

```python
# evaluate.py, line ~94
parser.add_argument(
    '--judge', '-j',
    default='gpt-4.1-nano',  # Default judge model
    help='Judge model for evaluation'
)

# User runs:
# python3 evaluate.py input/test.xlsx --judge gpt-4.1-nano
#                                              ↑
#                                        Judge model specified
```

### Step 2: Passed to evaluate_single_file() (run_evaluation.py)

```python
# evaluate.py, line ~260
result = evaluate_single_file(
    excel_path=excel_file,
    system_prompt=system_prompt,
    output_dir=args.output,
    use_all_metrics=use_all_metrics,
    judge_model=args.judge  # ← Passed here
)
```

```python
# run_evaluation.py, line ~50
def evaluate_single_file(
    excel_path: str,
    system_prompt: str,
    output_dir: str = "evaluation_result",
    use_all_metrics: bool = True,
    judge_model: str = "gpt-4.1-nano"  # ← Received here
):
```

### Step 3: Passed to MultiTurnTester() (multi_turn_testing.py)

```python
# run_evaluation.py, line ~60
tester = MultiTurnTester(
    BASE_MODEL,
    FINETUNED_MODEL,
    judge_model=judge_model,  # ← Passed to tester
    use_all_metrics=use_all_metrics
)
```

```python
# multi_turn_testing.py, line ~33
def __init__(self, base_model_config: dict, finetuned_model_config: dict, 
             judge_model: str = "gpt-4", use_all_metrics: bool = True):
    self.base_model = ModelWrapper(base_model_config)
    self.finetuned_model = ModelWrapper(finetuned_model_config)
    self.judge_model = judge_model  # ← STORED as instance variable
    self.use_all_metrics = use_all_metrics
    self.results = []
```

### Step 4: Used in create_conversational_metrics()

```python
# multi_turn_testing.py, line ~129
metrics = self.create_conversational_metrics(
    judge_model=self.judge_model,  # ← Retrieved from instance
    use_all_metrics=self.use_all_metrics
)
```

### Step 5: Passed to Each Metric (DeepEval Integration)

```python
# multi_turn_testing.py, lines ~69-106
def create_conversational_metrics(self, judge_model: str = "gpt-4", use_all_metrics: bool = True):
    if use_all_metrics:
        return [
            # Custom ConversationalGEval metrics
            ConversationalGEval(
                name="Coherence",
                evaluation_steps=[...],
                evaluation_params=[TurnParams.CONTENT],
                model=judge_model,  # ← PASSED TO DEEPEVAL METRIC
            ),
            ConversationalGEval(
                name="Contextual Understanding",
                evaluation_steps=[...],
                model=judge_model,  # ← PASSED TO DEEPEVAL METRIC
            ),
            ConversationalGEval(
                name="Helpfulness",
                evaluation_steps=[...],
                model=judge_model,  # ← PASSED TO DEEPEVAL METRIC
            ),
            # DeepEval's built-in multi-turn metrics
            KnowledgeRetentionMetric(threshold=0.5, model=judge_model),  # ← PASSED
            TurnRelevancyMetric(threshold=0.5, model=judge_model),       # ← PASSED
            RoleAdherenceMetric(threshold=0.5, model=judge_model),       # ← PASSED
            ConversationCompletenessMetric(threshold=0.5, model=judge_model),  # ← PASSED
        ]
```

### Step 6: DeepEval Uses the Model Internally

When DeepEval metrics are initialized with `model=judge_model`, they:

```python
# Inside DeepEval library (conceptual - actual implementation)

class ConversationalGEval:
    def __init__(self, name, evaluation_steps, evaluation_params, model):
        self.model = model  # Store the judge model name
        # ...
    
    def measure(self, test_case):
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(test_case)
        
        # Call OpenAI API with the specified judge model
        import openai
        response = openai.chat.completions.create(
            model=self.model,  # ← Uses "gpt-4.1-nano"
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        # Parse response for score and reasoning
        return self._parse_response(response)
```

---

## 📊 Visual Flow Diagram

```
evaluate.py
    ↓
    judge_model = "gpt-4.1-nano" (from --judge or default)
    ↓
run_evaluation.py::evaluate_single_file(judge_model=...)
    ↓
MultiTurnTester.__init__(judge_model=...)
    ↓
    self.judge_model = "gpt-4.1-nano"  [STORED]
    ↓
MultiTurnTester.create_conversational_metrics(judge_model=self.judge_model)
    ↓
    [Creates 7 metrics, each gets model=judge_model]
    ↓
    ┌─────────────────────────────────────────┐
    │ ConversationalGEval(                    │
    │     name="Coherence",                   │
    │     model="gpt-4.1-nano"  ← STORED      │
    │ )                                       │
    └─────────────────────────────────────────┘
    ↓
deepeval.evaluate(test_cases=[...], metrics=[...])
    ↓
    For each metric:
        metric.measure(test_case)
        ↓
        DeepEval internally:
        ┌────────────────────────────────────┐
        │ openai.chat.completions.create(   │
        │     model="gpt-4.1-nano",  ← USED │
        │     messages=[evaluation_prompt]   │
        │ )                                  │
        └────────────────────────────────────┘
        ↓
        Returns: {"score": 0.93, "reason": "..."}
```

---

## 🔍 Actual Code Locations

### Location 1: evaluate.py (Line ~94)

```python
parser.add_argument(
    '--judge', '-j',
    default='gpt-4.1-nano',
    help='Judge model for evaluation (default: gpt-4.1-nano)'
)

# User command:
# python3 evaluate.py test.xlsx --judge gpt-4
#                                       ↑
#                                  This value
```

### Location 2: run_evaluation.py (Line ~362)

```python
judge_model = os.getenv("JUDGE_MODEL", "gpt-4.1-nano")

# Can also come from .env:
# JUDGE_MODEL=gpt-4.1-nano
```

### Location 3: multi_turn_testing.py (Line ~36)

```python
def __init__(self, ..., judge_model: str = "gpt-4", ...):
    self.judge_model = judge_model  # ← Stored as instance variable
```

### Location 4: multi_turn_testing.py (Lines ~78, 89, 100, 103-106)

```python
# Each metric initialization
ConversationalGEval(
    name="Coherence",
    model=judge_model,  # ← Passed to DeepEval metric
)

KnowledgeRetentionMetric(threshold=0.5, model=judge_model)  # ← Passed
TurnRelevancyMetric(threshold=0.5, model=judge_model)       # ← Passed
RoleAdherenceMetric(threshold=0.5, model=judge_model)       # ← Passed
ConversationCompletenessMetric(threshold=0.5, model=judge_model)  # ← Passed
```

---

## 🎯 How DeepEval Library Uses It

### DeepEval's Internal Process

When you pass `model="gpt-4.1-nano"` to a DeepEval metric:

1. **Metric Initialization**:
   ```python
   metric = ConversationalGEval(
       name="Coherence",
       evaluation_steps=[...],
       model="gpt-4.1-nano"  # Stored in metric
   )
   ```

2. **During Evaluation** (`metric.measure(test_case)`):
   ```python
   # DeepEval internally (simplified):
   def measure(self, test_case):
       # Format conversation
       conversation_text = self._format_conversation(test_case.turns)
       
       # Build evaluation prompt
       prompt = f"""
       Evaluate this conversation for {self.name}.
       
       Evaluation Steps:
       {self.evaluation_steps}
       
       Conversation:
       {conversation_text}
       
       Rate from 0 to 1.
       """
       
       # Call OpenAI with judge model
       response = openai.chat.completions.create(
           model=self.model,  # ← "gpt-4.1-nano"
           messages=[{"role": "user", "content": prompt}]
       )
       
       # Parse GPT-4.1-nano's response
       return self._parse_evaluation(response)
   ```

3. **API Call Example**:
   ```json
   POST https://api.openai.com/v1/chat/completions
   {
     "model": "gpt-4.1-nano",
     "messages": [{
       "role": "user",
       "content": "Evaluate this conversation for Coherence..."
     }],
     "temperature": 0
   }
   ```

4. **Response from gpt-4.1-nano**:
   ```json
   {
     "choices": [{
       "message": {
         "content": "{\"score\": 0.93, \"reason\": \"The conversation flows logically...\"}"
       }
     }]
   }
   ```

5. **DeepEval Parses and Returns**:
   ```python
   MetricData(
       name="Coherence",
       score=0.93,
       reason="The conversation flows logically...",
       evaluation_model="gpt-4.1-nano"  # ← Recorded which model judged
   )
   ```

---

## 🔗 Key Integration Points

### 1. DeepEval Metric Classes Accept `model` Parameter

All DeepEval metrics that use LLM-as-a-judge accept a `model` parameter:

```python
from deepeval.metrics import ConversationalGEval, KnowledgeRetentionMetric

# DeepEval's signature (from their library)
ConversationalGEval(
    name: str,
    criteria: str = None,
    evaluation_steps: List[str] = None,
    evaluation_params: List[TurnParams] = [TurnParams.CONTENT],
    model: str = "gpt-4o",  # ← This is where judge model goes
    threshold: float = 0.5,
    ...
)

KnowledgeRetentionMetric(
    threshold: float = 0.5,
    model: str = "gpt-4o",  # ← And here
    ...
)
```

### 2. DeepEval Uses OpenAI Client Internally

DeepEval has internal integration with OpenAI:

```python
# Inside DeepEval library
import openai

class BaseMetric:
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def _call_llm(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,  # Uses the model you specified
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

### 3. Our Code Bridges to DeepEval

```python
# Our code (multi_turn_testing.py)
def create_conversational_metrics(self, judge_model: str = "gpt-4"):
    # We pass the judge model to DeepEval's metric constructors
    return [
        ConversationalGEval(model=judge_model),      # DeepEval uses this
        KnowledgeRetentionMetric(model=judge_model), # DeepEval uses this
        # etc.
    ]

# DeepEval's metrics then use this model internally
# when they call OpenAI's API
```

---

## 📝 Example Trace: Single Metric Evaluation

Let's trace ONE metric evaluation from start to finish:

```
1. User Command:
   python3 evaluate.py test.xlsx --judge gpt-4.1-nano

2. evaluate.py captures:
   args.judge = "gpt-4.1-nano"

3. Passes to run_evaluation.py:
   evaluate_single_file(..., judge_model="gpt-4.1-nano")

4. Creates tester:
   tester = MultiTurnTester(..., judge_model="gpt-4.1-nano")
   tester.judge_model = "gpt-4.1-nano"  # Stored

5. Creates metrics:
   metrics = [
       ConversationalGEval(model="gpt-4.1-nano"),  # ← Here
       KnowledgeRetentionMetric(model="gpt-4.1-nano"),  # ← Here
       ...
   ]

6. DeepEval evaluates:
   for metric in metrics:
       result = metric.measure(test_case)
       # Internally:
       # - metric builds prompt: "Evaluate for Coherence..."
       # - calls: openai.chat.completions.create(model="gpt-4.1-nano", ...)
       # - returns: score + reasoning

7. Output shows:
   ✨ You're running DeepEval's latest Coherence Metric! 
   (using gpt-4.1-nano, ...)
   ↑
   DeepEval confirms which model it's using
```

---

## 🎯 Why This Matters

### Flexibility

You can change the judge model at runtime:

```bash
# Use GPT-4
python3 evaluate.py test.xlsx --judge gpt-4

# Use GPT-3.5 (faster/cheaper)
python3 evaluate.py test.xlsx --judge gpt-3.5-turbo

# Use custom model
python3 evaluate.py test.xlsx --judge my-custom-model
```

### Consistency

All 7 metrics use the SAME judge model:

```python
# All metrics get the same judge_model
metrics = [
    ConversationalGEval(model="gpt-4.1-nano"),           # Same
    KnowledgeRetentionMetric(model="gpt-4.1-nano"),      # Same
    TurnRelevancyMetric(model="gpt-4.1-nano"),           # Same
    RoleAdherenceMetric(model="gpt-4.1-nano"),           # Same
    ConversationCompletenessMetric(model="gpt-4.1-nano"), # Same
]
```

---

## 🔍 Verification in Output

You can see which judge model was used in the output:

```
✨ You're running DeepEval's latest Coherence [Conversational GEval] Metric! 
(using gpt-4.1-nano, strict=False, async_mode=True)...
        ↑
   This shows the judge model
```

And in the results:

```
MetricData(
    name='Coherence [Conversational GEval]',
    evaluation_model='gpt-4.1-nano',  ← Which model evaluated
    score=0.9257502914212539,
    reason="The conversation flows logically..."
)
```

---

## 🎓 Summary

**The Flow**:
```
CLI (--judge gpt-4.1-nano)
  → evaluate_single_file(judge_model="gpt-4.1-nano")
  → MultiTurnTester(judge_model="gpt-4.1-nano")
  → create_conversational_metrics(judge_model="gpt-4.1-nano")
  → Each Metric(model="gpt-4.1-nano")
  → DeepEval internally calls OpenAI(model="gpt-4.1-nano")
  → GPT-4.1-nano evaluates and returns scores
```

**The Connection to DeepEval**:
- DeepEval metrics accept a `model` parameter in their constructors
- This tells DeepEval which LLM to use for judging
- DeepEval internally calls OpenAI's API with that model
- The judge model evaluates the conversation and returns scores

**Key Point**: 
The `model` parameter in DeepEval metrics is THE judge model. That's how DeepEval knows which LLM to use for evaluation!

