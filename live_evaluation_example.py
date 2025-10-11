"""
Live Evaluation from Excel
Load user queries from Excel, generate model responses on-the-fly, and evaluate

Excel Format:
- Column: "Initial Conversation" (optional, JSON format, first row only)
- Column: "User Query" (required)
- Optional columns: Scenario, Expected Outcome, Chatbot Role

Usage:
    python3 live_evaluation_example.py your_file.xlsx
    
Or programmatically:
    from live_evaluation_example import evaluate_from_excel_live
    evaluate_from_excel_live("your_file.xlsx", "system_prompt.txt")
"""

import pandas as pd
import json
import sys
import os
from multi_turn_testing import MultiTurnTester
from config import BASE_MODEL, FINETUNED_MODEL


def evaluate_from_excel_live(
    excel_path: str,
    system_prompt_path: str = "system_prompt.txt",
    test_name: str = None,
    use_all_metrics: bool = True,
    judge_model: str = "gpt-4"
):
    """
    Load user queries from Excel, generate responses on-the-fly, and evaluate
    
    Args:
        excel_path: Path to Excel file with user queries
        system_prompt_path: Path to system prompt file
        test_name: Name for this test (default: Excel filename)
        use_all_metrics: Use all 7 metrics or just 4 built-in (default: True)
        judge_model: LLM to use as judge (default: gpt-4)
    
    Excel Format:
        Required columns:
        - "User Query": User questions
        
        Optional columns:
        - "Initial Conversation": JSON array of prior conversation (first row only)
          Example: [{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]
        - "Scenario": Test scenario description
        - "Expected Outcome": Expected result
        - "Chatbot Role": Role the chatbot should play
    
    Returns:
        Dictionary with evaluation results
    """
    
    print("\n" + "="*80)
    print("LIVE EVALUATION FROM EXCEL")
    print("="*80 + "\n")
    
    # 1. Load system prompt
    system_prompt = None
    if os.path.exists(system_prompt_path):
        print(f"📄 Loading system prompt from: {system_prompt_path}")
        with open(system_prompt_path, "r") as f:
            system_prompt = f.read().strip()
        print(f"✓ System prompt loaded ({len(system_prompt)} characters)\n")
    else:
        print(f"⚠️  System prompt file not found: {system_prompt_path}")
        print("   Continuing without system prompt...\n")
    
    # 2. Load Excel file
    print(f"📊 Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    print(f"✓ Excel loaded with {len(df)} rows\n")
    
    # 3. Parse initial conversation (if present)
    initial_conversation = []
    if "Initial Conversation" in df.columns and pd.notna(df.iloc[0]["Initial Conversation"]):
        initial_conv_str = str(df.iloc[0]["Initial Conversation"]).strip()
        if initial_conv_str:
            try:
                initial_conversation = json.loads(initial_conv_str)
                print(f"✓ Found initial conversation with {len(initial_conversation)} turns")
            except (json.JSONDecodeError, ValueError):
                print(f"⚠️  Could not parse Initial Conversation as JSON, skipping...")
    
    # 4. Extract optional metadata
    scenario = None
    expected_outcome = None
    chatbot_role = None
    
    if "Scenario" in df.columns and pd.notna(df.iloc[0]["Scenario"]):
        scenario = str(df.iloc[0]["Scenario"]).strip()
        print(f"✓ Scenario: {scenario}")
    
    if "Expected Outcome" in df.columns and pd.notna(df.iloc[0]["Expected Outcome"]):
        expected_outcome = str(df.iloc[0]["Expected Outcome"]).strip()
        print(f"✓ Expected Outcome: {expected_outcome}")
    
    if "Chatbot Role" in df.columns and pd.notna(df.iloc[0]["Chatbot Role"]):
        chatbot_role = str(df.iloc[0]["Chatbot Role"]).strip()
        print(f"✓ Chatbot Role: {chatbot_role}")
    
    print()
    
    # 5. Extract user queries
    if "User Query" not in df.columns:
        raise ValueError("Excel file must have 'User Query' column")
    
    user_queries = []
    for idx, row in df.iterrows():
        if pd.notna(row["User Query"]):
            query = str(row["User Query"]).strip()
            if query:
                user_queries.append(query)
    
    print(f"✓ Extracted {len(user_queries)} user queries:")
    for i, query in enumerate(user_queries, 1):
        preview = query[:80] + "..." if len(query) > 80 else query
        print(f"  {i}. {preview}")
    print()
    
    # 6. Build full conversation for generation
    full_conversation = []
    
    # Add system prompt
    if system_prompt:
        full_conversation.append({"role": "system", "content": system_prompt})
    
    # Add initial conversation
    for turn in initial_conversation:
        full_conversation.append({
            "role": turn.get("role", "user"),
            "content": turn.get("content", "")
        })
    
    # Add user queries
    for query in user_queries:
        full_conversation.append({"role": "user", "content": query})
    
    print(f"📝 Total conversation length: {len(full_conversation)} turns")
    if system_prompt:
        print(f"   - System prompt: 1 turn")
    if initial_conversation:
        print(f"   - Initial conversation: {len(initial_conversation)} turns")
    print(f"   - User queries: {len(user_queries)} turns")
    print()
    
    # 7. Initialize tester
    print("🔧 Initializing evaluator...")
    print(f"   - Base Model: {BASE_MODEL.get('name', 'configured model')}")
    print(f"   - Finetuned Model: {FINETUNED_MODEL.get('name', 'configured model')}")
    print(f"   - Judge Model: {judge_model}")
    print(f"   - Metrics: {'All 7 metrics' if use_all_metrics else 'Only 4 built-in metrics'}")
    print()
    
    tester = MultiTurnTester(
        BASE_MODEL,
        FINETUNED_MODEL,
        judge_model=judge_model,
        use_all_metrics=use_all_metrics
    )
    
    print("✓ Evaluator initialized\n")
    
    # 8. Generate responses from both models
    print("="*80)
    print("🤖 GENERATING RESPONSES FROM BOTH MODELS (On-the-Fly)")
    print("="*80)
    print("This will call your models to generate responses in real-time...")
    print("Please wait, this may take a minute...\n")
    
    base_conversation, finetuned_conversation = tester.generate_conversations(full_conversation)
    
    print("✓ Responses generated successfully!\n")
    
    # 9. Preview generated responses
    print("-"*80)
    print("PREVIEW: Base Model Responses")
    print("-"*80)
    response_count = 0
    for turn in base_conversation:
        if turn["role"] == "assistant":
            response_count += 1
            preview = turn["content"][:200] + "..." if len(turn["content"]) > 200 else turn["content"]
            print(f"\nResponse {response_count}:")
            print(f"  {preview}")
    
    print("\n" + "-"*80)
    print("PREVIEW: Finetuned Model Responses")
    print("-"*80)
    response_count = 0
    for turn in finetuned_conversation:
        if turn["role"] == "assistant":
            response_count += 1
            preview = turn["content"][:200] + "..." if len(turn["content"]) > 200 else turn["content"]
            print(f"\nResponse {response_count}:")
            print(f"  {preview}")
    
    print()
    
    # 10. Evaluate both conversations
    print("="*80)
    print("📊 EVALUATING WITH ALL METRICS")
    print("="*80)
    print("This will evaluate both conversations using LLM-as-a-judge...")
    print()
    
    print("Evaluating Base Model...")
    base_eval = tester.evaluate_conversation(base_conversation, "Base Model (Generated)")
    
    print("Evaluating Finetuned Model...")
    finetuned_eval = tester.evaluate_conversation(finetuned_conversation, "Finetuned Model (Generated)")
    
    # 11. Save results
    test_case_name = test_name or f"Live Evaluation: {os.path.basename(excel_path)}"
    
    results = {
        "test_case_name": test_case_name,
        "excel_file": excel_path,
        "system_prompt": system_prompt,
        "scenario": scenario,
        "expected_outcome": expected_outcome,
        "chatbot_role": chatbot_role,
        "initial_conversation": initial_conversation,
        "user_queries": user_queries,
        "base_model": {
            "config": BASE_MODEL.get("name", "configured"),
            "conversation": [{"role": t["role"], "content": t["content"]} for t in base_conversation],
            "evaluation": base_eval
        },
        "finetuned_model": {
            "config": FINETUNED_MODEL.get("name", "configured"),
            "conversation": [{"role": t["role"], "content": t["content"]} for t in finetuned_conversation],
            "evaluation": finetuned_eval
        }
    }
    
    output_filename = f"live_results_{os.path.basename(excel_path).replace('.xlsx', '')}.json"
    with open(output_filename, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*80)
    print("✅ EVALUATION COMPLETE")
    print("="*80)
    print(f"\nResults saved to: {output_filename}")
    print("\nSummary:")
    print(f"  - Generated responses from both models")
    print(f"  - Evaluated with {'7 metrics' if use_all_metrics else '4 metrics'}")
    print(f"  - Total conversation turns: {len(base_conversation)}")
    print()
    
    return results


def main():
    """Main function - command line interface"""
    
    if len(sys.argv) < 2:
        print("\n" + "="*80)
        print("LIVE EVALUATION FROM EXCEL - Usage")
        print("="*80 + "\n")
        
        print("This script loads user queries from Excel, generates model responses")
        print("on-the-fly, and evaluates them with all 7 metrics.\n")
        
        print("Usage:")
        print("  python3 live_evaluation_example.py <excel_file> [system_prompt_file]\n")
        
        print("Examples:")
        print("  python3 live_evaluation_example.py queries.xlsx")
        print("  python3 live_evaluation_example.py queries.xlsx prompts/system.txt\n")
        
        print("Excel Format:")
        print("  Required column:")
        print("    - User Query: Your test questions\n")
        
        print("  Optional columns:")
        print("    - Initial Conversation: JSON array of prior conversation (first row only)")
        print("      Example: [{\"role\":\"user\",\"content\":\"Hi\"},{\"role\":\"assistant\",\"content\":\"Hello!\"}]")
        print("    - Scenario: Test scenario description")
        print("    - Expected Outcome: Expected result")
        print("    - Chatbot Role: Role the chatbot should play\n")
        
        print("Example Excel:")
        print("  | Initial Conversation | User Query | Scenario | Chatbot Role |")
        print("  |---------------------|------------|----------|--------------|")
        print("  | [{\"role\":\"user\",\"content\":\"Hi\"}] | I need help | Support | Agent |")
        print("  |                     | How do I reset? | | |")
        print("  |                     | Thanks | | |\n")
        
        print("What happens:")
        print("  1. Load system prompt and Excel file")
        print("  2. Extract user queries and optional metadata")
        print("  3. Generate responses from BOTH models (Base & Finetuned)")
        print("  4. Evaluate both conversations with 7 metrics")
        print("  5. Save results to JSON\n")
        
        print("Requirements:")
        print("  - Configure BASE_MODEL and FINETUNED_MODEL in config.py")
        print("  - Set OPENAI_API_KEY in .env file")
        print("  - Create system_prompt.txt (optional but recommended)\n")
        
        return
    
    # Get arguments
    excel_file = sys.argv[1]
    system_prompt_file = sys.argv[2] if len(sys.argv) > 2 else "system_prompt.txt"
    
    # Validate Excel file exists
    if not os.path.exists(excel_file):
        print(f"\n❌ Error: Excel file not found: {excel_file}\n")
        return
    
    try:
        # Run evaluation
        evaluate_from_excel_live(
            excel_path=excel_file,
            system_prompt_path=system_prompt_file,
            use_all_metrics=True,
            judge_model="gpt-4"
        )
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print("Make sure:")
        print("  1. Excel file has 'User Query' column")
        print("  2. BASE_MODEL and FINETUNED_MODEL are configured in config.py")
        print("  3. OPENAI_API_KEY is set in .env file")
        print("  4. All dependencies are installed (pip install -r requirements.txt)\n")
        raise


if __name__ == "__main__":
    main()
