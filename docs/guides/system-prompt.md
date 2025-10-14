# System Prompt - Complete Explanation

## Quick Answer

**Q: What is the system prompt used for?**  
**A:** It serves TWO purposes:
1. **During Generation**: Tells models how to behave and respond
2. **During Evaluation**: Helps judge determine if responses match expected behavior

**Q: Is it already being checked?**  
**A:** ✅ **YES!** Metrics like Contextual Understanding, Role Adherence, and Helpfulness all consider your system prompt.

---

## How System Prompt Flows Through Your Code

### Step 1: Loading (evaluate.py)

```python
# Default location: system_prompt.txt
# Can override: --system-prompt custom.txt

system_prompt = ""
if os.path.exists(args.system_prompt):
    with open(args.system_prompt) as f:
        system_prompt = f.read().strip()
```

**Your current system_prompt.txt contains:**
```
You are a professional customer support agent for TechCorp...
- Be empathetic and professional in all interactions
- Always verify user identity before discussing account details
- Escalate complex issues to appropriate teams
...
```

---

### Step 2: During Generation (--mode generate)

**Code Location:** `evaluate.py`, line ~160

```python
full_conversation = []
if system_prompt:
    full_conversation.append({"role": "system", "content": system_prompt})

# Add initial conversation
# Add user query
# Send to OpenAI API
```

**What happens:**
```
┌────────────────────────────────────────────────────────────┐
│ Sent to OpenAI API:                                        │
│                                                             │
│ [                                                           │
│   {                                                         │
│     "role": "system",                                       │
│     "content": "You are a professional support agent..."   │
│   },                                                        │
│   {"role": "user", "content": "Hi, I need help"},          │
│   {"role": "assistant", "content": "Hello!"},              │
│   {"role": "user", "content": "I can't log in"}            │
│ ]                                                           │
│                                                             │
│ Model sees system prompt → Generates response following it │
└────────────────────────────────────────────────────────────┘
```

---

### Step 3: During Evaluation (Both Modes)

**Code Location:** `evaluate.py`, lines ~183, 189

```python
model_a_test_case = ConversationalTestCase(
    turns=base_turns,
    context=[system_prompt],  # ← Passed to DeepEval
    chatbot_role=chatbot_role,
    scenario=scenario
)
```

**What DeepEval receives:**
```
┌────────────────────────────────────────────────────────────┐
│ ConversationalTestCase:                                    │
│                                                             │
│ turns = [                                                   │
│   {"role": "user", "content": "I can't log in"},           │
│   {"role": "assistant", "content": "Let me help..."}       │
│ ]                                                           │
│                                                             │
│ context = [                                                 │
│   "You are a professional support agent..."  ← SYSTEM      │
│ ]                                                  PROMPT   │
│                                                             │
│ chatbot_role = "Professional customer support agent"       │
│ scenario = "Login issue"                                    │
└────────────────────────────────────────────────────────────┘
```

---

## Which Metrics Use System Prompt?

### ✅ Direct Usage (Explicitly Checks)

#### 1. Contextual Understanding
**How it uses system prompt:**
- Judge model sees the context
- Checks if response aligns with system prompt instructions
- Evaluates if assistant builds on previous turns appropriately

**Example:**
- System prompt: "Always verify user identity before discussing account details"
- User: "What's my account balance?"
- Response A: "$1,234.56" → **LOW score** (violated system prompt)
- Response B: "I can help. Can you verify your email first?" → **HIGH score** (followed system prompt)

#### 2. Role Adherence
**How it uses system prompt:**
- Compares responses against `chatbot_role` (which comes from system prompt)
- Checks if assistant stays in character
- Identifies out-of-character responses

**Example:**
- Chatbot role: "Professional customer support agent"
- Response: "Yo dude, just reset ur password lol" → **LOW score** (not professional)
- Response: "I'd be happy to assist you with resetting your password" → **HIGH score** (professional)

#### 3. Helpfulness
**How it uses system prompt:**
- Uses context to judge what "helpful" means
- If system prompt says "be empathetic", judge expects empathy
- If system prompt says "provide clear steps", judge expects actionable advice

**Example:**
- System prompt includes: "Be empathetic and professional"
- Response A: "Reset your password." → **MEDIUM score** (helpful but not empathetic)
- Response B: "I understand this is frustrating. Let me help you reset your password..." → **HIGH score** (helpful AND empathetic)

---

### ⚪ Indirect Usage (Influenced By)

#### 4. Coherence
- Context helps judge evaluate logical flow
- System prompt sets expectations for conversation style

#### 5. Conversation Completeness
- Context defines what "complete" means
- System prompt guides what should be addressed

---

### ⚪ Minimal Usage

#### 6. Knowledge Retention
- Focuses on conversation memory
- Checks if assistant remembers previous turns
- Less dependent on system prompt

#### 7. Turn Relevancy
- Focuses on turn-to-turn relevance
- Checks if each response is relevant to user message
- Less dependent on system prompt

---

## Concrete Example from Your Results

### Your System Prompt Says:
```
"Always verify user identity before discussing account details"
```

### Test Scenario:
**User Query:** "I can't log into my account"

### Model A Response:
```
"I'm sorry to hear you're having trouble logging in. 
Can you verify your email address?"
```

### Model B Response:
```
"I understand your frustration. To assist you better, 
could you please verify your name or email address?"
```

### Evaluation Results:

```json
{
  "Contextual Understanding": {
    "Model A": 0.7930,
    "Model B": 0.8036,
    "Reason for B": "The assistant demonstrates understanding of the 
                     conversation context by responding appropriately 
                     and building on previous exchanges."
  },
  "Role Adherence": {
    "Model A": 1.0,
    "Model B": 1.0,
    "Reason": "All responses are consistent with the role of a 
               professional customer support agent."
  },
  "Helpfulness": {
    "Model A": 0.7292,
    "Model B": 0.7795,
    "Reason for B": "The assistant provides practical steps by 
                     requesting verification details and expressing 
                     empathy."
  }
}
```

**Analysis:**
- Both models followed the system prompt (asked for verification) ✅
- Model B scored higher on Helpfulness because it added empathy ("I understand your frustration") which aligns with system prompt's "Be empathetic" instruction ✅
- Role Adherence scored 1.0 for both because they stayed in character ✅

**This proves the system prompt IS being used in evaluation!**

---

## How to Verify System Prompt is Working

### Method 1: Check Scores
Look at these metrics in your results:
- **Contextual Understanding**: Higher = Better alignment with system prompt
- **Role Adherence**: Higher = Better adherence to defined role
- **Helpfulness**: Higher = Better following of helpful guidelines

### Method 2: Test with Violations
Create a test where you INTENTIONALLY violate system prompt:

**System Prompt:** "Always verify user identity"  
**Test Response (Manual):** "Your account balance is $1,234.56" (no verification)

You should see:
- Lower "Contextual Understanding" score
- Lower "Helpfulness" score
- Reason might mention not following guidelines

### Method 3: Compare Different System Prompts
Run same conversations with different system prompts:
- Formal vs. Casual tone
- With vs. Without specific instructions
- Compare metric scores across runs

You'll see differences in scores based on how well responses match each system prompt!

---

## Summary: Your Questions Answered

### Q1: What is the use of system_prompt which I am passing?
**A:** 
1. **During Generation**: Instructs models on how to behave, what tone to use, and what rules to follow
2. **During Evaluation**: Provides context to judge model so it can evaluate if responses match expected behavior

### Q2: Where will my system_prompt be used?
**A:**
1. **Generation** (`evaluate.py` line ~160): Added as system message before sending to OpenAI
2. **Evaluation** (`evaluate.py` lines ~183, 189): Passed as "context" to DeepEval test case

### Q3: How is the code picking it up?
**A:**
1. Read from file: `system_prompt.txt` (default) or custom file via `--system-prompt`
2. Loaded in memory: `evaluate.py` line ~293-296
3. Used throughout: Generation and evaluation

### Q4: Can I use system_prompt itself to check if metrics are measured against it?
**A:** ✅ **YES! It's already happening!**

**Which metrics check it:**
- ✅ Contextual Understanding (directly)
- ✅ Role Adherence (directly)
- ✅ Helpfulness (directly)
- ⚪ Coherence (indirectly)
- ⚪ Conversation Completeness (indirectly)
- ⚪ Knowledge Retention (minimal)
- ⚪ Turn Relevancy (minimal)

### Q5: Is it doing it already?
**A:** ✅ **YES! No changes needed!**

Your current setup is correct. The system prompt is:
- ✅ Being read from file
- ✅ Passed to models during generation
- ✅ Passed to DeepEval during evaluation
- ✅ Considered by judge model when scoring
- ✅ Reflected in metric scores (especially Contextual Understanding, Role Adherence, Helpfulness)

---

## What You Can Do

### To See the Effect More Clearly:

1. **Experiment with Different System Prompts**
   ```bash
   # Create different prompts
   echo "Be extremely formal and technical" > prompt_formal.txt
   echo "Be casual and friendly" > prompt_casual.txt
   
   # Run with each
   python3 evaluate.py test.xlsx --system-prompt prompt_formal.txt
   python3 evaluate.py test.xlsx --system-prompt prompt_casual.txt
   
   # Compare scores!
   ```

2. **Add Specific Rules to Test**
   ```txt
   In system_prompt.txt, add:
   "Always ask for order number before discussing orders"
   "Never discuss pricing without manager approval"
   "Always offer alternative solutions"
   ```
   
   Then check if models follow these rules in their scores!

3. **Monitor These Metrics Specifically**
   - Contextual Understanding → Shows alignment with system prompt
   - Role Adherence → Shows role consistency
   - Helpfulness → Shows if helpful according to your guidelines

---

## No Code Changes Needed!

✅ Your system is working correctly  
✅ System prompt is being used as intended  
✅ Metrics are checking against it  
✅ You can verify by looking at scores  

🎯 **Just keep using it!** The system prompt is doing exactly what it should be doing.
