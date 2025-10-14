# Metric Calculation Flow - What Data Is Used

## 📊 Overview: What Gets Evaluated

When you run an evaluation, here's **exactly** what data each metric sees:

---

## 🔍 The Complete Test Case Structure

Each `ConversationalTestCase` sent to the metrics contains:

```python
ConversationalTestCase(
    turns=[
        # Initial conversation (if provided in Excel)
        Turn(role="user", content="Hi, I need help"),
        Turn(role="assistant", content="Hello! How can I help?"),
        
        # Current interaction (from Excel row)
        Turn(role="user", content="I can't log in"),  # User Query
        Turn(role="assistant", content="Let me help you...")  # Model Response
    ],
    context=[system_prompt],  # From system_prompt.txt
    chatbot_role="Customer support agent",  # From Excel or system_prompt
    scenario="Login issue",  # From Excel (optional)
    expected_outcome="User gets help"  # From Excel (optional)
)
```

---

## 📝 What Each Metric Sees & Evaluates

### 1️⃣ Coherence [Conversational GEval]

**Inputs to the Metric:**
- ✅ **All turns** (entire conversation)
- ✅ **Context** (system prompt)
- ❌ Does NOT use: chatbot_role, scenario

**What It Evaluates:**
- Flow between ALL turns (not just last one)
- Checks transitions from initial conversation through final response
- Evaluates structure of the ENTIRE conversation

**Example:**
```python
Turns evaluated:
1. user: "Hi" 
2. assistant: "Hello!"  ← Evaluates this transition
3. user: "I can't log in"  ← Evaluates this transition
4. assistant: "Let me help..."  ← Evaluates ALL turns together for flow
```

**Focus:** The **entire conversation flow**, with emphasis on how the **last response** fits the conversation.

---

### 2️⃣ Contextual Understanding [Conversational GEval]

**Inputs to the Metric:**
- ✅ **All turns** (entire conversation)
- ✅ **Context** (system prompt)
- ❌ Does NOT use: chatbot_role, scenario

**What It Evaluates:**
- Does the assistant understand FULL conversation context?
- Does the last response build on previous turns?
- Is awareness maintained across ALL turns?

**Example:**
```python
Initial: user: "My name is Sarah"
Initial: assistant: "Hi Sarah!"
Current: user: "My order is late"
Current: assistant: "Let me check that for you, Sarah"
                    ↑
                    Checks if it remembered "Sarah" from earlier
```

**Focus:** How well the **last response** demonstrates understanding of **all prior context**.

---

### 3️⃣ Helpfulness [Conversational GEval]

**Inputs to the Metric:**
- ✅ **All turns** (entire conversation)
- ✅ **Context** (system prompt)
- ❌ Does NOT use: chatbot_role, scenario

**What It Evaluates:**
- Is the FINAL response helpful given the conversation history?
- Does it provide actionable information?
- Does it address the user's need from the last query?

**Example:**
```python
User query: "How do I reset my password?"
Model response: "Click 'Forgot Password' on login page..."
                ↑
                Judges if THIS response is helpful for THIS query
```

**Focus:** Primarily the **last assistant response** and how helpful it is.

---

### 4️⃣ Knowledge Retention

**Inputs to the Metric:**
- ✅ **All turns** (entire conversation)
- ❌ Does NOT use: context, chatbot_role, scenario

**What It Evaluates:**
- Extracts "knowledge" from each turn (facts, entities, info)
- Checks if later turns "forget" earlier knowledge
- Counts attritions (forgotten facts)

**Example:**
```python
Turn 1: user: "Order #12345, name Sarah"
        → Knowledge: {order: "12345", name: "Sarah"}
        
Turn 2: assistant: "Thanks Sarah, checking #12345"
        → Retention check: Did it remember? ✅

Turn 3: user: "When will it ship?"
        
Turn 4: assistant: "What's your order number?"
        → Retention check: Forgot #12345? ❌ ATTRITION!
```

**Focus:** Checks **all turns** to see if information is retained throughout.

---

### 5️⃣ Turn Relevancy

**Inputs to the Metric:**
- ✅ **All turns** (using sliding window)
- ❌ Does NOT use: context, chatbot_role, scenario

**What It Evaluates:**
- For EACH assistant response, is it relevant to corresponding user message?
- Uses sliding window (size=10) to check context

**Example:**
```python
Window 1: [user: "Hi", assistant: "Hello!"]
          → Is "Hello!" relevant to "Hi"? ✅

Window 2: [user: "Hi", assistant: "Hello!", user: "I can't log in", assistant: "Let me help"]
          → Is "Let me help" relevant to "I can't log in"? ✅
```

**Focus:** **Each assistant turn** is checked for relevancy to its corresponding user turn.

---

### 6️⃣ Role Adherence

**Inputs to the Metric:**
- ✅ **All turns** (entire conversation)
- ✅ **chatbot_role** (from Excel or system prompt)
- ❌ Does NOT use: context, scenario

**What It Evaluates:**
- Are ALL assistant responses "in character"?
- Checks each assistant turn against the defined role
- Identifies out-of-character responses

**Example:**
```python
Chatbot Role: "Professional customer support agent"

Turn 1: assistant: "I'm here to help!" ✅ In character
Turn 2: assistant: "Yo dude, sup?" ❌ Out of character
```

**Focus:** **Every assistant response** is checked against the chatbot_role.

---

### 7️⃣ Conversation Completeness

**Inputs to the Metric:**
- ✅ **All turns** (entire conversation)
- ❌ Does NOT use: context, chatbot_role, scenario

**What It Evaluates:**
- Extracts user's intentions from all user messages
- Checks if the FINAL assistant response addresses all intentions
- Looks for gaps or incomplete answers

**Example:**
```python
User intention: "Reset password"
Final response: "Click forgot password link and follow email instructions"
                ↑
                Does this FULLY address the intention? ✅
```

**Focus:** The **last assistant response** and whether it completely addresses **all user intentions** from the conversation.

---

## 🎯 Summary Table

| Metric | Uses Initial Conversation | Uses System Prompt | Uses Chatbot Role | Evaluates All Turns | Focus on Last Response |
|--------|---------------------------|-------------------|-------------------|---------------------|----------------------|
| **Coherence** | ✅ Yes | ✅ Yes (context) | ❌ No | ✅ Yes | ⚠️ Primarily |
| **Contextual Understanding** | ✅ Yes | ✅ Yes (context) | ❌ No | ✅ Yes | ⚠️ Primarily |
| **Helpfulness** | ✅ Yes | ✅ Yes (context) | ❌ No | ✅ Yes | ✅ Yes |
| **Knowledge Retention** | ✅ Yes | ❌ No | ❌ No | ✅ Yes | ✅ All equally |
| **Turn Relevancy** | ✅ Yes | ❌ No | ❌ No | ✅ Yes | ✅ All equally |
| **Role Adherence** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | ✅ All equally |
| **Conversation Completeness** | ✅ Yes | ❌ No | ❌ No | ✅ Yes | ✅ Last response |

---

## 📋 Detailed Flow: From Excel to Evaluation

### Step 1: Excel Row Processing

**Your Excel:**
```
| Initial Conversation | User Query | Model A Response |
|---------------------|------------|------------------|
| [{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}] | "I can't log in" | "Let me help..." |
```

### Step 2: Turn Construction

```python
# System builds this:
turns = [
    Turn(role="user", content="Hi"),                    # From Initial Conversation
    Turn(role="assistant", content="Hello!"),           # From Initial Conversation
    Turn(role="user", content="I can't log in"),        # From User Query
    Turn(role="assistant", content="Let me help...")    # From Model A Response
]
```

### Step 3: Test Case Creation

```python
test_case = ConversationalTestCase(
    turns=turns,                      # ALL 4 turns above
    context=[system_prompt],          # From system_prompt.txt
    chatbot_role=system_prompt,       # From Excel OR system_prompt.txt
    scenario="Login issue"            # From Excel (optional)
)
```

### Step 4: Metric Evaluation

Each metric receives the **COMPLETE test case** with:
- All conversation history (initial + current)
- System prompt as context
- Chatbot role
- All metadata

### Step 5: Judge LLM Analysis

The judge model (GPT-4o-mini) sees:
```
Context: [system prompt text]
Chatbot Role: "Professional customer support agent"

Conversation:
user: Hi
assistant: Hello!
user: I can't log in
assistant: Let me help you with that...

Evaluate: [specific metric criteria]
```

---

## 🎯 Key Points

### ✅ YES - Metrics Evaluate:

1. **System Prompt** → Used as `context` by GEval metrics
2. **Initial Conversation** → Part of the turn history
3. **User Query** → Added as a user turn
4. **Model Response** → Added as assistant turn (the one being judged)
5. **ALL Turns Together** → Full conversation evaluated as a whole

### ⚠️ Focus Areas:

**For Conversational GEval (Coherence, Contextual Understanding, Helpfulness):**
- Evaluates **entire conversation**
- But focuses on how well the **last response** fits
- Considers all prior context

**For Multi-Turn Metrics (Retention, Relevancy, Role, Completeness):**
- Checks **each turn** individually
- Then aggregates for final score
- Example: Knowledge Retention checks if turn 4 remembers info from turn 1

---

## 🔬 Detailed Example

### Your Excel Input:

```
Initial Conversation: [{"role":"user","content":"My name is Sarah"}]
User Query: "My order #12345 is late"
Model A Response: "I'll check your order for you"
System Prompt: "You are a professional support agent..."
```

### What Each Metric Sees:

**Complete conversation sent to all metrics:**
```python
turns = [
    Turn(role="user", content="My name is Sarah"),           # Turn 0
    Turn(role="user", content="My order #12345 is late"),    # Turn 1  
    Turn(role="assistant", content="I'll check your order for you")  # Turn 2
]
context = ["You are a professional support agent..."]
chatbot_role = "You are a professional support agent..."
```

### How Each Metric Uses This:

**Coherence:**
- Analyzes: Turn 0 → Turn 1 → Turn 2 flow
- Checks: Does response (Turn 2) flow logically from Turn 1?
- Considers: Initial context from Turn 0

**Knowledge Retention:**
- Turn 0: Extracts knowledge = {name: "Sarah"}
- Turn 1: Extracts knowledge = {order: "#12345"}
- Turn 2: Checks if response remembers Sarah and #12345
- If it says "What's your name?" → ATTRITION!

**Role Adherence:**
- Compares ALL assistant responses against chatbot_role
- Turn 2 response must match the defined role
- Checks professional tone, appropriate language, etc.

**Conversation Completeness:**
- Extracts user intention from Turn 1: "Check order status"
- Checks if Turn 2 response fully addresses this intention
- Looks for gaps: Did it offer to check? Did it ask for details?

---

## 💡 Important Clarifications

### Q: Does it only evaluate the last response?

**A:** No and Yes:
- **NO**: All turns are considered for context and history
- **YES**: The **last assistant response** is the primary one being scored
- But it's scored **in the context of** the entire conversation

### Q: Does it use the system prompt?

**A:** Yes, in two ways:
1. **As `context`**: Helps metrics understand expected behavior
2. **As `chatbot_role`**: For Role Adherence metric specifically

### Q: What about initial conversation?

**A:** Yes, included:
- Initial conversation becomes the first N turns
- Metrics see the FULL history
- Example: Knowledge Retention tracks info from initial conversation

### Q: Is each row evaluated separately?

**A:** Yes:
- Each Excel row = One complete conversation
- Each row gets its own evaluation
- Rows are independent (Row 1 doesn't affect Row 2)

---

## 🔄 Visual Flow Diagram

```
Excel Row
─────────────────────────────────────────────────────
| Initial Conv | User Query | Model Response | 
| Turn 0-1     | Turn 2     | Turn 3         |
─────────────────────────────────────────────────────
           │
           ▼
ConversationalTestCase
─────────────────────────────────────────────────────
turns: [Turn 0, Turn 1, Turn 2, Turn 3]  ← ALL TURNS
context: [system_prompt]                  ← CONTEXT
chatbot_role: "Support agent"             ← ROLE
─────────────────────────────────────────────────────
           │
           ▼
Judge Model (GPT-4o-mini)
─────────────────────────────────────────────────────
Sees:
  - Full conversation history (all turns)
  - System prompt for expected behavior
  - Chatbot role for character check
  
Evaluates:
  - How well the LAST response fits
  - Given ALL the prior context
  - Against the defined criteria
─────────────────────────────────────────────────────
           │
           ▼
Metric Score (0.0 - 1.0)
─────────────────────────────────────────────────────
Example: Coherence = 0.85
Reason: "Response flows well from prior conversation..."
```

---

## 🎯 What Gets Evaluated Per Metric

### Coherence
```
Input: ALL turns + context
Evaluation Focus: 
  - Overall conversation flow
  - Last response coherence with prior turns
  - Smooth transitions throughout
Output: Single score for entire conversation
```

### Contextual Understanding
```
Input: ALL turns + context
Evaluation Focus:
  - Does last response show understanding of full context?
  - Does it reference/build on previous turns?
  - Context awareness across entire conversation
Output: Score for contextual awareness
```

### Helpfulness
```
Input: ALL turns + context
Evaluation Focus:
  - Is the LAST response helpful?
  - Given the conversation context
  - Practical value of the final answer
Output: Score for helpfulness of last response
```

### Knowledge Retention
```
Input: ALL turns (no context needed)
Evaluation Process:
  Turn 1: Extract knowledge → {name: "Sarah"}
  Turn 2: Extract knowledge → {order: "12345"}
  Turn 3: Check if remembered Sarah ✅
  Turn 4: Check if remembered #12345 ✅
Output: Score = 1 - (attritions / knowledge_items)
```

### Turn Relevancy
```
Input: ALL turns (sliding window)
Evaluation Process:
  For each assistant turn:
    - Is it relevant to preceding user turn?
    - Check: Turn 2 (assistant) vs Turn 1 (user)
    - Check: Turn 4 (assistant) vs Turn 3 (user)
Output: % of relevant responses
```

### Role Adherence
```
Input: ALL turns + chatbot_role
Evaluation Process:
  For EACH assistant turn:
    - Compare against defined chatbot_role
    - Turn 1 (assistant): In character? ✅
    - Turn 3 (assistant): In character? ✅
Output: % of in-character responses
```

### Conversation Completeness
```
Input: ALL turns
Evaluation Process:
  1. Extract user intentions from ALL user turns
  2. Check if LAST assistant response addresses ALL intentions
  3. Look for gaps or missing information
Output: % of intentions fully addressed
```

---

## 📊 Example: Full Calculation Walkthrough

### Your Excel Row:
```
Initial Conversation: [{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]
User Query: "I can't log into my account"
Model A Response: "Let me help you reset your password"
System Prompt: "You are a professional customer support agent..."
Chatbot Role: [Empty - will use system prompt]
```

### What Gets Built:
```python
turns = [
    Turn(role="user", content="Hi"),                                    # Turn 0
    Turn(role="assistant", content="Hello!"),                           # Turn 1
    Turn(role="user", content="I can't log into my account"),          # Turn 2
    Turn(role="assistant", content="Let me help you reset your password")  # Turn 3
]
context = ["You are a professional customer support agent..."]
chatbot_role = "You are a professional customer support agent..."
```

### What Each Metric Evaluates:

**Coherence:**
```
Sees: All 4 turns + context
Checks: Does Turn 3 (last response) flow well from Turn 2 (user query)?
        Does it maintain coherence with Turn 0-1 (initial greeting)?
Score: 0.85 - "Response flows logically from login issue query..."
```

**Contextual Understanding:**
```
Sees: All 4 turns + context
Checks: Does Turn 3 understand the context (login issue)?
        Does it build on the greeting from Turn 0-1?
Score: 0.78 - "Understands login context but could acknowledge initial greeting..."
```

**Helpfulness:**
```
Sees: All 4 turns + context
Checks: Is Turn 3 helpful for solving the login issue?
        Does it provide actionable guidance?
Score: 0.65 - "Offers to help but lacks specific reset steps..."
```

**Knowledge Retention:**
```
Sees: All 4 turns
Extracts: 
  Turn 0: No specific knowledge
  Turn 1: No specific knowledge  
  Turn 2: Knowledge = {issue: "can't log in"}
  Turn 3: Check if it remembered the issue ✅
Score: 1.0 - "No attritions detected"
```

**Turn Relevancy:**
```
Sees: All 4 turns
Checks:
  Turn 1 relevant to Turn 0? ✅ (greeting response)
  Turn 3 relevant to Turn 2? ✅ (addresses login issue)
Score: 1.0 - "All responses relevant"
```

**Role Adherence:**
```
Sees: All 4 turns + chatbot_role
Checks:
  Turn 1 matches "professional support agent"? ✅
  Turn 3 matches "professional support agent"? ✅
Score: 1.0 - "All responses in character"
```

**Conversation Completeness:**
```
Sees: All 4 turns
Extracts intentions:
  Turn 0: "Greet agent"
  Turn 2: "Get help with login"
Checks if Turn 3 addresses both:
  - Acknowledges user? ⚠️ Partial
  - Helps with login? ✅ Yes
Score: 0.85 - "Addresses main intention but could acknowledge greeting"
```

---

## ⚠️ Common Misconceptions

### ❌ WRONG: "Only the last response is evaluated"
**✅ CORRECT:** The last response is evaluated **in the context** of the entire conversation.

### ❌ WRONG: "Initial conversation is ignored"
**✅ CORRECT:** Initial conversation is part of the turn history and affects scoring.

### ❌ WRONG: "System prompt is just for generation"
**✅ CORRECT:** System prompt is used as **context** for evaluation metrics.

### ❌ WRONG: "Each turn is scored separately"
**✅ CORRECT:** The ENTIRE conversation gets a single score per metric.

---

## 🔍 How to Verify What Data Is Used

Check the `verbose_logs` in your results:

```python
# In verbose_logs you'll see:
"Turns:
[
    {role: 'user', content: 'Hi'},
    {role: 'assistant', content: 'Hello!'},
    {role: 'user', content: 'Login issue'},
    {role: 'assistant', content: 'Let me help'}
]"
```

This shows **exactly** what turns the metric evaluated!

---

## 💡 Key Takeaway

**The metrics see EVERYTHING:**
1. ✅ Initial conversation (all prior turns)
2. ✅ System prompt (as context)
3. ✅ User query (current turn)
4. ✅ Model response (current turn)
5. ✅ Chatbot role (for Role Adherence)
6. ✅ Metadata (scenario, expected outcome)

**They evaluate the COMPLETE conversation holistically, with particular focus on how well the final response:**
- Fits the conversation flow
- Demonstrates context understanding
- Helps the user
- Maintains role consistency
- Completes the user's intention

---

**Last Updated:** October 14, 2025  
**Framework:** DeepEval Multi-Turn Conversation Testing

