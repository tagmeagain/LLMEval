# DeepEval Metrics Guide

## Overview
This guide explains all 8 metrics used to evaluate conversational AI models in this framework. Each metric is calculated using DeepEval's LLM-as-a-judge approach, where a powerful LLM (like GPT-4) evaluates the quality of responses.

---

## 📊 Metrics Summary

| Metric | Type | Threshold | Purpose |
|--------|------|-----------|---------|
| **Coherence** | Conversational GEval | 0.5 | Measures logical flow and structure |
| **Contextual Understanding** | Conversational GEval | 0.5 | Evaluates context awareness |
| **Helpfulness** | Conversational GEval | 0.5 | Assesses practical value |
| **Human Tonality** | Conversational GEval | 0.5 | Evaluates natural, human-like communication |
| **Knowledge Retention** | Multi-turn | 0.5 | Tracks information memory |
| **Turn Relevancy** | Multi-turn | 0.5 | Checks response relevance |
| **Role Adherence** | Multi-turn | 0.5 | Verifies role consistency |
| **Conversation Completeness** | Multi-turn | 0.5 | Ensures full resolution |

---

## 1️⃣ Coherence [Conversational GEval]

### What It Measures
How logically and smoothly the conversation flows from one turn to the next.

### How It's Calculated
The judge model evaluates:
1. **Logical Flow**: Does each response follow naturally from previous turns?
2. **Structure**: Are responses well-organized and easy to follow?
3. **Transitions**: Are topic changes smooth or abrupt?
4. **Consistency**: Does the conversation maintain coherent thread throughout?

### Evaluation Criteria
```
- Evaluate whether the conversation flows logically from one turn to the next
- Check if responses are well-structured and easy to follow
- Assess if there are smooth transitions between topics
- Identify any abrupt changes or confusing sequences that disrupt coherence
```

### Score Interpretation
- **0.9 - 1.0**: Excellent flow, perfectly structured
- **0.7 - 0.9**: Good coherence, minor issues
- **0.5 - 0.7**: Acceptable but noticeable flow problems
- **< 0.5**: Poor coherence, confusing conversation flow

### Example
**High Coherence (0.95)**:
```
User: "My order is late"
Assistant: "I understand your concern about the delayed order. Let me look that up for you."
User: "When will it arrive?"
Assistant: "Based on the tracking info, your order will arrive tomorrow by 5 PM."
```

**Low Coherence (0.40)**:
```
User: "My order is late"
Assistant: "We have many products available."
User: "When will it arrive?"
Assistant: "Have you tried our mobile app?"
```

---

## 2️⃣ Contextual Understanding [Conversational GEval]

### What It Measures
How well the assistant understands and maintains awareness of the full conversation context.

### How It's Calculated
The judge model evaluates:
1. **Context Comprehension**: Does the assistant understand the full situation?
2. **Building on Previous Turns**: Do responses appropriately reference prior exchanges?
3. **Thread Awareness**: Is the assistant tracking the overall conversation goal?
4. **No Misunderstandings**: Are there instances where context is ignored or misunderstood?

### Evaluation Criteria
```
- Check if the assistant understands the full context of the conversation
- Verify that responses build appropriately on previous turns
- Identify any instances where context is misunderstood or ignored
- Assess whether the assistant maintains awareness of the overall conversation thread
```

### Score Interpretation
- **0.9 - 1.0**: Perfect context awareness throughout
- **0.7 - 0.9**: Good understanding, minor gaps
- **0.5 - 0.7**: Partial understanding, some context missed
- **< 0.5**: Poor context awareness, frequent misunderstandings

### Example
**High Contextual Understanding (0.90)**:
```
User: "I can't log in"
Assistant: "I'll help you with that. First, let me verify your account."
User: "It's john@example.com"
Assistant: "Thanks John. I see your account. Let me send a password reset link to john@example.com."
```

**Low Contextual Understanding (0.45)**:
```
User: "I can't log in"
Assistant: "We have great products!"
User: "It's john@example.com"
Assistant: "What would you like to buy today?"
```

---

## 3️⃣ Helpfulness [Conversational GEval]

### What It Measures
How practical, actionable, and useful the assistant's responses are to the user.

### How It's Calculated
The judge model evaluates:
1. **Practical Information**: Does the response provide actionable guidance?
2. **Need Fulfillment**: Does it address the user's actual needs?
3. **Clarity**: Are explanations clear and useful?
4. **Depth**: Does it go beyond surface-level responses?

### Evaluation Criteria
```
- Determine if the responses provide practical, actionable information
- Assess whether the assistant addresses the user's needs effectively
- Check if explanations are clear and useful for the user
- Evaluate if the assistant goes beyond surface-level responses to truly help
```

### Score Interpretation
- **0.9 - 1.0**: Extremely helpful, comprehensive guidance
- **0.7 - 0.9**: Helpful with good practical advice
- **0.5 - 0.7**: Somewhat helpful, lacks depth
- **< 0.5**: Not helpful, vague or irrelevant

### Example
**High Helpfulness (0.92)**:
```
User: "How do I reset my password?"
Assistant: "I can help you reset your password. Please click on the 'Forgot Password' 
link on the login page, enter your email, and follow the instructions sent to your email. 
The reset link expires in 24 hours. Let me know if you need any additional assistance."
```

**Low Helpfulness (0.35)**:
```
User: "How do I reset my password?"
Assistant: "You can reset it."
```

---

## 4️⃣ Human Tonality [Conversational GEval]

### What It Measures
How natural, warm, and human-like the assistant's responses sound, with specific focus on Indian English communication patterns.

### How It's Calculated
The judge model evaluates:
1. **Natural Language**: Does it sound like a real person speaking, not a robot?
2. **Warmth & Relatability**: Is the tone warm and personally engaged?
3. **Indian English Patterns**: Does it use natural Indian English expressions and communication styles?
4. **Authenticity**: Absence of mechanical, templated, or overly scripted phrases
5. **Personal Touch**: Feels like genuine human interaction
6. **Natural Variation**: Uses varied sentence structures and vocabulary

### Evaluation Criteria
```
- Evaluate if the response sounds natural and conversational, like how a real person would speak
- Check if the tone is warm, relatable, and has a human touch rather than robotic or overly formal
- Assess if the language style matches natural Indian English conversation patterns 
  (e.g., use of 'actually', 'na', 'yaar' when appropriate, or empathetic expressions 
  common in Indian communication)
- Identify any stilted, mechanical, or overly templated phrases that feel artificial
- Verify the response feels personally engaged rather than auto-generated or scripted
- Check for natural variations in sentence structure and vocabulary that humans typically use
```

### Score Interpretation
- **0.9 - 1.0**: Extremely natural and human-like
- **0.7 - 0.9**: Good human touch, minor robotic elements
- **0.5 - 0.7**: Somewhat natural, noticeable artificial phrases
- **< 0.5**: Robotic, stilted, lacks human warmth

### Example
**High Human Tonality (0.95)**:
```
User: "I can't access my account"
Assistant: "Oh no! I totally understand how frustrating that must be. Don't worry, 
I'll help you sort this out right away. Let me just quickly check your account 
details, and we'll get you back in, okay?"
```
✅ Natural flow, empathetic, conversational  
✅ Uses phrases like "Oh no!", "totally understand", "sort this out"  
✅ Warm and relatable tone

**Low Human Tonality (0.35)**:
```
User: "I can't access my account"
Assistant: "Your access issue has been noted. Please provide account credentials 
for verification purposes. Standard protocol dictates identity confirmation 
before proceeding with troubleshooting procedures."
```
❌ Robotic and formal  
❌ Uses stiff phrases like "noted", "protocol dictates", "procedures"  
❌ Lacks warmth and personal engagement

### Indian English Patterns
**Natural Indian English expressions that score higher:**
- "Actually, let me check that for you"
- "Don't worry na, I'll help you"
- "Totally understand your concern"
- "Let me quickly do this for you"
- "Will be done soon, promise!"
- Empathetic expressions: "Arey!", "Oh my!", "So sorry to hear that"

**Overly formal (non-Indian) that scores lower:**
- "Kindly provide the aforementioned details"
- "As per company policy..."
- "Your request has been duly noted"

---

## 5️⃣ Knowledge Retention

### What It Measures
Whether the assistant remembers and retains information established earlier in the conversation.

### How It's Calculated
The metric tracks:
1. **Knowledge Extraction**: What facts/entities are mentioned in each turn
2. **Retention Check**: Does the assistant "forget" previously mentioned information?
3. **Attrition Count**: Number of times the assistant loses track of established knowledge

### Calculation Formula
```
Score = 1 - (Number of Attritions / Total Knowledge Items)

Where:
- Attrition = Forgetting or contradicting previously established knowledge
- Score ranges from 0.0 to 1.0
```

### Score Interpretation
- **1.0**: Perfect retention, no information lost
- **0.8 - 0.9**: Minor lapses in memory
- **0.6 - 0.8**: Some information forgotten
- **< 0.6**: Significant memory issues

### Example
**Perfect Retention (1.0)**:
```
User: "My name is Sarah and my order is #12345"
Assistant: "Thanks Sarah. I've found order #12345."
User: "When will it ship?"
Assistant: "Sarah, order #12345 will ship tomorrow."
```

**Poor Retention (0.5)**:
```
User: "My name is Sarah and my order is #12345"
Assistant: "Thanks! I've found your order."
User: "When will it ship?"
Assistant: "Could you please provide your order number?"  ← Forgot #12345
```

---

## 6️⃣ Turn Relevancy

### What It Measures
Whether each assistant response is relevant to the corresponding user message.

### How It's Calculated
The metric uses a sliding window approach:
1. **Window Analysis**: Examines conversation in chunks (size=10 turns)
2. **Relevancy Check**: For each assistant message, determines if it's relevant to user's message
3. **Verdict**: "yes" = relevant, "no" = irrelevant

### Calculation Formula
```
Score = Number of Relevant Responses / Total Number of Assistant Responses
```

### Score Interpretation
- **1.0**: All responses perfectly relevant
- **0.8 - 0.9**: Mostly relevant, minor off-topic moments
- **0.6 - 0.8**: Several irrelevant responses
- **< 0.6**: Frequently off-topic

### Example
**Perfect Relevancy (1.0)**:
```
User: "What's your return policy?"
Assistant: "Our return policy allows returns within 30 days of purchase."  ✓ Relevant

User: "Do I need a receipt?"
Assistant: "Yes, you'll need the original receipt or order confirmation."  ✓ Relevant
```

**Poor Relevancy (0.5)**:
```
User: "What's your return policy?"
Assistant: "We have a mobile app available."  ✗ Irrelevant

User: "Do I need a receipt?"
Assistant: "Yes, you'll need the original receipt."  ✓ Relevant
```

---

## 7️⃣ Role Adherence

### What It Measures
Whether the assistant consistently maintains its assigned role throughout the conversation.

### How It's Calculated
The metric evaluates:
1. **Role Definition**: Uses the `chatbot_role` or system prompt
2. **Character Check**: Identifies "out-of-character" responses
3. **Consistency**: Verifies all responses align with the defined role

### Calculation Formula
```
Score = 1 - (Number of Out-of-Character Responses / Total Responses)
```

### Score Interpretation
- **1.0**: Perfect role adherence
- **0.8 - 0.9**: Minor deviations from role
- **0.6 - 0.8**: Some inconsistencies
- **< 0.6**: Frequently breaks character

### Example
**Perfect Role Adherence (1.0)** - Customer Support Agent:
```
User: "I need help"
Assistant: "I'm here to assist you. Could you please describe the issue?"  ✓ In character

User: "What do you think about politics?"
Assistant: "I'm here to help with your account and orders. How can I assist you today?"  ✓ Stays in role
```

**Poor Role Adherence (0.4)** - Customer Support Agent:
```
User: "I need help"
Assistant: "Sure! I love helping people. By the way, did you see the game last night?"  ✗ Too casual

User: "My order is late"
Assistant: "Ugh, shipping is always slow. I hate waiting too."  ✗ Unprofessional
```

---

## 8️⃣ Conversation Completeness

### What It Measures
Whether the assistant fully addresses the user's intentions without leaving gaps or omissions.

### How It's Calculated
The metric:
1. **Intention Extraction**: Identifies what the user is trying to accomplish
2. **Completeness Check**: Evaluates if the response fully addresses each intention
3. **Gap Detection**: Finds any omissions or incomplete information

### Calculation Formula
```
Score = Number of Fully Addressed Intentions / Total User Intentions
```

### Score Interpretation
- **1.0**: All user intentions completely addressed
- **0.8 - 0.9**: Most intentions met, minor gaps
- **0.6 - 0.8**: Some intentions partially addressed
- **< 0.6**: Many intentions unaddressed

### Example
**Complete (1.0)**:
```
User Intention: "Learn how to reset password"
Assistant: "I can help you reset your password. Please click on the 'Forgot Password' 
link on the login page, and follow the instructions sent to your email."
✓ Fully addresses how to reset password
```

**Incomplete (0.5)**:
```
User Intention: "Learn how to reset password"
Assistant: "You can reset it on the login page."
✗ Doesn't explain specific steps or process
```

---

## 🎯 Pass/Fail Determination

Each metric has a **threshold of 0.5**:
- **✅ PASS**: Score ≥ 0.5
- **❌ FAIL**: Score < 0.5

### Overall Test Case Pass/Fail
A conversation **PASSES** only if **ALL 7 metrics pass** their individual thresholds.

---

## 🔍 How the Evaluation Works

### 1. LLM-as-a-Judge
All metrics use GPT-4 or similar models as evaluators:
```
Judge Model: gpt-4o-mini (default)
Configurable via: --judge-model flag
```

### 2. Evaluation Process
```
1. Test Case Created → Conversation with turns
2. Metrics Applied → Each metric analyzes the conversation
3. LLM Evaluates → Judge model scores each metric
4. Results Compiled → Scores, reasons, and verdicts generated
5. Pass/Fail Determined → Based on 0.5 threshold
```

### 3. Scoring Scale
```
All metrics use: 0.0 to 1.0 scale
- 0.0 = Worst possible
- 0.5 = Threshold (minimum passing)
- 1.0 = Perfect score
```

---

## 📊 Metric Output Structure

Each metric provides:

```json
{
  "name": "Coherence [Conversational GEval]",
  "score": 0.8816,
  "success": true,
  "threshold": 0.5,
  "reason": "The conversation flows logically...",
  "evaluation_model": "gpt-4o-mini",
  "evaluation_cost": 0.000092,
  "verbose_logs": "Criteria:\n...\nEvaluation Steps:\n...\nVerdicts:\n..."
}
```

### Fields Explained
- **score**: Numerical score (0.0 - 1.0)
- **success**: Pass/Fail (true if score ≥ threshold)
- **threshold**: Minimum score needed to pass (0.5)
- **reason**: Explanation of the score
- **verbose_logs**: Detailed evaluation steps and verdicts

---

## 🎓 Best Practices

### 1. Understanding Low Scores
- **< 0.3**: Critical issues, fundamental problems
- **0.3 - 0.5**: Needs improvement, just below passing
- **0.5 - 0.7**: Passing but room for enhancement
- **0.7 - 0.9**: Good performance
- **0.9 - 1.0**: Excellent performance

### 2. Metric Relationships
- **Coherence + Contextual Understanding**: Often correlate
- **Helpfulness + Completeness**: Related but distinct
- **Knowledge Retention**: Independent, tracks memory
- **Turn Relevancy**: Basic requirement for all others
- **Role Adherence**: Independent behavioral check

### 3. Improving Scores

**For Coherence**: 
- Ensure logical response flow
- Use transition phrases
- Maintain consistent topic progression

**For Contextual Understanding**:
- Reference previous conversation elements
- Build on established context
- Track user's goals

**For Helpfulness**:
- Provide specific, actionable steps
- Include relevant details
- Go beyond surface-level responses

**For Knowledge Retention**:
- Explicitly reference previously mentioned facts
- Maintain entity consistency (names, numbers, etc.)

**For Turn Relevancy**:
- Directly address user's question
- Stay on topic
- Avoid tangents

**For Role Adherence**:
- Maintain consistent tone
- Follow role constraints
- Use appropriate language for the role

**For Conversation Completeness**:
- Address all parts of user's request
- Provide comprehensive answers
- Offer follow-up support

---

## 📖 Additional Resources

- **DeepEval Documentation**: https://docs.confident-ai.com/
- **GEval Paper**: Understanding LLM-based evaluation
- **System Prompt**: `system_prompt.txt` defines the chatbot role
- **Technical Architecture**: See `TECHNICAL_ARCHITECTURE.md` for implementation details

---

## ❓ FAQ

### Q: Why use LLM-as-a-judge?
**A**: LLMs can understand nuance, context, and intent better than rule-based metrics. They provide more human-like evaluation.

### Q: Are the scores deterministic?
**A**: No, LLM evaluations can vary slightly between runs due to the probabilistic nature of LLMs. However, they're generally consistent.

### Q: Can I adjust thresholds?
**A**: Yes, modify the threshold values in `multi_turn_testing.py` where metrics are defined.

### Q: What if a metric fails?
**A**: The entire test case fails. Check the `reason` field to understand why and improve the response.

### Q: How much does evaluation cost?
**A**: Depends on the judge model and conversation length. Using `gpt-4o-mini` costs approximately $0.001-0.002 per conversation.

---

**Last Updated**: October 14, 2025
**Framework**: DeepEval Multi-Turn Conversation Testing

