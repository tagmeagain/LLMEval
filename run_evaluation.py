"""
Unified Evaluation Script
Automatically detects if model responses exist or generates them on-the-fly

Input: Excel files in input/ folder
Output: Results in evaluation_result/ folder (JSON + Excel)

Usage:
    python3 run_evaluation.py
"""

import os
import glob
import json
import pandas as pd
from datetime import datetime
from multi_turn_testing import MultiTurnTester
from excel_loader import ExcelConversationLoader
from config import BASE_MODEL, FINETUNED_MODEL


def ensure_directories():
    """Create input and output directories if they don't exist"""
    os.makedirs("input", exist_ok=True)
    os.makedirs("evaluation_result", exist_ok=True)


def detect_excel_mode(df):
    """
    Detect if Excel has pre-recorded responses or just queries
    
    Returns:
        "pre_recorded" if Model A/B Response columns exist
        "generate" if only User Query exists
    """
    has_model_a = "Model A Response" in df.columns
    has_model_b = "Model B Response" in df.columns
    
    if has_model_a and has_model_b:
        return "pre_recorded"
    else:
        return "generate"


def evaluate_single_file(
    excel_path: str,
    system_prompt: str,
    output_dir: str = "evaluation_result",
    use_all_metrics: bool = True,
    judge_model: str = "gpt-4"
):
    """
    Evaluate a single Excel file - auto-detects mode
    
    Args:
        excel_path: Path to Excel file
        system_prompt: System prompt content
        output_dir: Output directory for results
        use_all_metrics: Use all 7 metrics or just 4
        judge_model: Judge model to use
    
    Returns:
        Dictionary with results
    """
    filename = os.path.basename(excel_path)
    file_base = os.path.splitext(filename)[0]
    
    print("\n" + "="*80)
    print(f"PROCESSING: {filename}")
    print("="*80 + "\n")
    
    # Load Excel to detect mode
    df = pd.read_excel(excel_path)
    mode = detect_excel_mode(df)
    
    print(f"📊 Excel loaded: {len(df)} rows")
    print(f"🔍 Detection: {mode.upper()} mode")
    print()
    
    # Initialize tester
    tester = MultiTurnTester(
        BASE_MODEL,
        FINETUNED_MODEL,
        judge_model=judge_model,
        use_all_metrics=use_all_metrics
    )
    
    if mode == "pre_recorded":
        # Mode 1: Use pre-recorded responses from Excel
        print("✓ Found Model A Response and Model B Response columns")
        print("  Using pre-recorded responses from Excel\n")
        
        # Load using excel_loader
        loader = ExcelConversationLoader(excel_path)
        model_a_test_case, model_b_test_case = loader.parse_conversation_from_excel()
        
        # Add system prompt as context
        if system_prompt:
            model_a_test_case.context = [system_prompt]
            model_b_test_case.context = [system_prompt]
        
        print(f"✓ Loaded {len(model_a_test_case.turns)} turns from Excel")
        
        # Evaluate
        print("\n📊 Evaluating with all metrics...")
        result = tester.evaluate_from_excel_test_cases(
            model_a_test_case,
            model_b_test_case,
            f"Evaluation: {filename}"
        )
        
        # Prepare output data
        output_data = {
            "file": filename,
            "mode": "pre_recorded",
            "timestamp": datetime.now().isoformat(),
            "evaluation": result
        }
        
        # Excel output (same as input since responses already exist)
        output_excel_data = df.copy()
        
    else:
        # Mode 2: Generate responses on-the-fly
        print("✓ No Model A/B Response columns found")
        print("  Generating responses on-the-fly from both models\n")
        
        # Parse initial conversation and metadata
        initial_conversation = []
        scenario = None
        expected_outcome = None
        chatbot_role = None
        
        if "Initial Conversation" in df.columns and pd.notna(df.iloc[0]["Initial Conversation"]):
            initial_conv_str = str(df.iloc[0]["Initial Conversation"]).strip()
            if initial_conv_str:
                try:
                    initial_conversation = json.loads(initial_conv_str)
                    print(f"✓ Parsed initial conversation: {len(initial_conversation)} turns")
                except (json.JSONDecodeError, ValueError):
                    print("⚠️  Could not parse Initial Conversation as JSON")
        
        if "Scenario" in df.columns and pd.notna(df.iloc[0]["Scenario"]):
            scenario = str(df.iloc[0]["Scenario"]).strip()
        
        if "Expected Outcome" in df.columns and pd.notna(df.iloc[0]["Expected Outcome"]):
            expected_outcome = str(df.iloc[0]["Expected Outcome"]).strip()
        
        if "Chatbot Role" in df.columns and pd.notna(df.iloc[0]["Chatbot Role"]):
            chatbot_role = str(df.iloc[0]["Chatbot Role"]).strip()
        
        # Extract user queries
        user_queries = []
        for idx, row in df.iterrows():
            if "User Query" in df.columns and pd.notna(row["User Query"]):
                query = str(row["User Query"]).strip()
                if query:
                    user_queries.append(query)
        
        print(f"✓ Extracted {len(user_queries)} user queries\n")
        
        # Build full conversation
        full_conversation = []
        
        if system_prompt:
            full_conversation.append({"role": "system", "content": system_prompt})
        
        for turn in initial_conversation:
            full_conversation.append({
                "role": turn.get("role", "user"),
                "content": turn.get("content", "")
            })
        
        for query in user_queries:
            full_conversation.append({"role": "user", "content": query})
        
        print(f"📝 Full conversation: {len(full_conversation)} turns")
        if system_prompt:
            print(f"   - System prompt: 1 turn")
        if initial_conversation:
            print(f"   - Initial conversation: {len(initial_conversation)} turns")
        print(f"   - User queries: {len(user_queries)} turns")
        print()
        
        # Generate responses from both models
        print("🤖 Generating responses from both models...")
        print("   This may take a minute...\n")
        
        base_conversation, finetuned_conversation = tester.generate_conversations(full_conversation)
        
        print("✓ Responses generated\n")
        
        # Preview responses
        print("-"*80)
        print("GENERATED RESPONSES PREVIEW")
        print("-"*80)
        response_count = 0
        for turn in base_conversation:
            if turn["role"] == "assistant":
                response_count += 1
                if response_count <= 2:  # Show first 2
                    preview = turn["content"][:150] + "..." if len(turn["content"]) > 150 else turn["content"]
                    print(f"\nBase Model Response {response_count}:")
                    print(f"  {preview}")
        print()
        
        # Convert to ConversationalTestCase for evaluation
        from deepeval.test_case import ConversationalTestCase, Turn
        
        base_turns = [Turn(role=t["role"], content=t["content"]) for t in base_conversation]
        finetuned_turns = [Turn(role=t["role"], content=t["content"]) for t in finetuned_conversation]
        
        base_test_case = ConversationalTestCase(
            turns=base_turns,
            context=[system_prompt] if system_prompt else None,
            scenario=scenario,
            expected_outcome=expected_outcome,
            chatbot_role=chatbot_role
        )
        
        finetuned_test_case = ConversationalTestCase(
            turns=finetuned_turns,
            context=[system_prompt] if system_prompt else None,
            scenario=scenario,
            expected_outcome=expected_outcome,
            chatbot_role=chatbot_role
        )
        
        # Evaluate
        print("📊 Evaluating with all metrics...")
        result = tester.evaluate_from_excel_test_cases(
            base_test_case,
            finetuned_test_case,
            f"Generated Evaluation: {filename}"
        )
        
        # Prepare output data
        output_data = {
            "file": filename,
            "mode": "generated",
            "timestamp": datetime.now().isoformat(),
            "system_prompt": system_prompt,
            "scenario": scenario,
            "expected_outcome": expected_outcome,
            "chatbot_role": chatbot_role,
            "evaluation": result
        }
        
        # Create Excel with generated responses
        output_excel_data = df.copy()
        
        # Extract just the user queries and responses
        model_a_responses = []
        model_b_responses = []
        
        for turn in base_conversation:
            if turn["role"] == "assistant":
                model_a_responses.append(turn["content"])
        
        for turn in finetuned_conversation:
            if turn["role"] == "assistant":
                model_b_responses.append(turn["content"])
        
        # Add response columns
        output_excel_data["Model A Response"] = pd.Series(model_a_responses[:len(output_excel_data)])
        output_excel_data["Model B Response"] = pd.Series(model_b_responses[:len(output_excel_data)])
    
    # Save JSON results
    json_output_path = os.path.join(output_dir, f"{file_base}_results.json")
    with open(json_output_path, "w") as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\n✅ JSON results saved: {json_output_path}")
    
    # Save Excel with responses (if generated)
    if mode == "generate":
        excel_output_path = os.path.join(output_dir, f"{file_base}_with_responses.xlsx")
        output_excel_data.to_excel(excel_output_path, index=False)
        print(f"✅ Excel with responses saved: {excel_output_path}")
    
    print()
    
    return output_data


def main():
    """
    Main function - processes Excel files
    
    Usage:
        python3 run_evaluation.py                    # Process all files in input/
        python3 run_evaluation.py file1.xlsx         # Process specific file
        python3 run_evaluation.py file1.xlsx file2.xlsx  # Process multiple files
    """
    print("\n" + "="*80)
    print("DEEPEVAL MULTI-TURN EVALUATION - UNIFIED RUNNER")
    print("="*80 + "\n")
    
    # Ensure directories exist
    ensure_directories()
    
    # Load system prompt
    system_prompt_path = "system_prompt.txt"
    system_prompt = None
    
    if os.path.exists(system_prompt_path):
        print(f"📄 Loading system prompt: {system_prompt_path}")
        with open(system_prompt_path, "r") as f:
            system_prompt = f.read().strip()
        print(f"✓ System prompt loaded ({len(system_prompt)} characters)\n")
    else:
        print(f"⚠️  No system_prompt.txt found")
        print("   Continuing without system prompt...\n")
    
    # Determine Excel files to process
    excel_files = []
    
    # Check if files provided as command line arguments
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        # Use files from command line arguments
        for arg in sys.argv[1:]:
            if arg.endswith(".xlsx") or arg.endswith(".xls"):
                # Handle both absolute and relative paths
                if os.path.exists(arg):
                    excel_files.append(arg)
                elif os.path.exists(os.path.join("input", arg)):
                    excel_files.append(os.path.join("input", arg))
                else:
                    print(f"⚠️  File not found: {arg}")
        
        if excel_files:
            print(f"📂 Processing {len(excel_files)} file(s) from arguments:")
            for f in excel_files:
                print(f"   - {f}")
            print()
    else:
        # Find all Excel files in input/ folder
        excel_files = glob.glob("input/*.xlsx") + glob.glob("input/*.xls")
        
        if not excel_files:
            print("❌ No Excel files found in input/ folder\n")
            print("Usage:")
            print("  1. Place Excel files in input/ folder and run:")
            print("     python3 run_evaluation.py\n")
            print("  2. OR pass specific files as arguments:")
            print("     python3 run_evaluation.py file1.xlsx file2.xlsx\n")
            print("  3. OR pass files from input/ folder:")
            print("     python3 run_evaluation.py input/test1.xlsx\n")
            print("Excel file should have:")
            print("  - User Query column (required)")
            print("  - Model A Response + Model B Response (for pre-recorded)")
            print("  - OR just User Query (for live generation)")
            print("  - Initial Conversation column (optional, JSON format)\n")
            return
        
        print(f"📂 Found {len(excel_files)} Excel file(s) in input/ folder:")
        for f in excel_files:
            print(f"   - {os.path.basename(f)}")
        print()
    
    # Configuration
    print("⚙️  Configuration:")
    print(f"   - Judge Model: gpt-4")
    print(f"   - Metrics: All 7 metrics")
    print(f"   - Output Directory: evaluation_result/")
    print()
    
    # Process each file
    all_results = []
    
    for idx, excel_file in enumerate(excel_files, 1):
        print(f"\n{'='*80}")
        print(f"FILE {idx}/{len(excel_files)}")
        print(f"{'='*80}")
        
        try:
            result = evaluate_single_file(
                excel_path=excel_file,
                system_prompt=system_prompt,
                output_dir="evaluation_result",
                use_all_metrics=True,
                judge_model="gpt-4"
            )
            all_results.append(result)
        except Exception as e:
            print(f"\n❌ Error processing {excel_file}: {e}\n")
            continue
    
    # Create summary
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80 + "\n")
    
    print(f"Total files processed: {len(all_results)}/{len(excel_files)}")
    print(f"Pre-recorded: {sum(1 for r in all_results if r['mode'] == 'pre_recorded')}")
    print(f"Generated: {sum(1 for r in all_results if r['mode'] == 'generated')}")
    print()
    
    print("Output files in evaluation_result/:")
    for result in all_results:
        file_base = os.path.splitext(result["file"])[0]
        print(f"  - {file_base}_results.json")
        if result["mode"] == "generated":
            print(f"  - {file_base}_with_responses.xlsx")
    print()
    
    # Save combined summary
    summary_path = os.path.join("evaluation_result", "summary.json")
    with open(summary_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_files": len(excel_files),
            "processed": len(all_results),
            "results": all_results
        }, f, indent=2, default=str)
    
    print(f"✅ Combined summary saved: {summary_path}")
    print()
    
    print("="*80)
    print("✅ ALL EVALUATIONS COMPLETE")
    print("="*80)
    print()


if __name__ == "__main__":
    import sys
    
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print("\n" + "="*80)
        print("UNIFIED EVALUATION SCRIPT - Help")
        print("="*80 + "\n")
        
        print("This script automatically:")
        print("  1. Finds Excel files (from input/ or arguments)")
        print("  2. Detects if responses exist or need to be generated")
        print("  3. Evaluates with all 7 metrics")
        print("  4. Saves results to evaluation_result/ folder\n")
        
        print("Usage:")
        print("  # Process all files in input/ folder")
        print("  python3 run_evaluation.py\n")
        
        print("  # Process specific file(s)")
        print("  python3 run_evaluation.py test1.xlsx")
        print("  python3 run_evaluation.py test1.xlsx test2.xlsx")
        print("  python3 run_evaluation.py input/test1.xlsx\n")
        
        print("  # Show this help")
        print("  python3 run_evaluation.py --help\n")
        
        print("Directory Structure:")
        print("  input/                    ← Place your Excel files here")
        print("    ├── test1.xlsx")
        print("    ├── test2.xlsx")
        print("    └── test3.xlsx")
        print("  system_prompt.txt         ← Your system prompt")
        print("  evaluation_result/        ← Results saved here (auto-created)")
        print("    ├── test1_results.json")
        print("    ├── test1_with_responses.xlsx  (if generated)")
        print("    ├── test2_results.json")
        print("    └── summary.json\n")
        
        print("Excel Format:")
        print("  Option 1 - Pre-recorded responses:")
        print("    Columns: User Query, Model A Response, Model B Response")
        print("    Optional: Initial Conversation, Scenario, Chatbot Role\n")
        
        print("  Option 2 - Generate on-the-fly:")
        print("    Columns: User Query only")
        print("    Optional: Initial Conversation, Scenario, Chatbot Role")
        print("    Note: Requires BASE_MODEL and FINETUNED_MODEL in config.py\n")
        
        print("Initial Conversation Format:")
        print('  JSON array: [{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello"}]')
        print("  Place in first row only\n")
        
        print("System Prompt:")
        print("  Create system_prompt.txt in the root directory")
        print("  Will be loaded automatically\n")
        
        print("Requirements:")
        print("  - pip install -r requirements.txt")
        print("  - .env file with OPENAI_API_KEY")
        print("  - config.py with model configurations (if generating)")
        print()
        
        return
    
    # Run main evaluation
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        print("Run with --help for usage information")
        raise

