#!/usr/bin/env python3
"""
Main Evaluation Script - DeepEval Multi-Turn Conversation Testing

Usage:
    # Auto-detect mode
    python3 evaluate.py input/test.xlsx
    
    # Force generate mode
    python3 evaluate.py input/test.xlsx --mode generate
    
    # Force pre-recorded mode  
    python3 evaluate.py input/test.xlsx --mode prerecorded
    
    # Custom options
    python3 evaluate.py input/test.xlsx --judge gpt-4 --metrics builtin
"""

import argparse
import sys
import os
import glob
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List

# Import our modules
from multi_turn_testing import MultiTurnTester
from excel_loader import ExcelConversationLoader
from config import BASE_MODEL, FINETUNED_MODEL


def ensure_directories():
    """Create necessary directories"""
    os.makedirs("input", exist_ok=True)
    os.makedirs("evaluation_result", exist_ok=True)


def detect_mode(excel_path: str) -> str:
    """
    Detect evaluation mode based on Excel columns
    
    Returns:
        'prerecorded' if Model A/B Response columns exist
        'generate' if only User Query exists
    """
    df = pd.read_excel(excel_path)
    has_model_a = "Model A Response" in df.columns
    has_model_b = "Model B Response" in df.columns
    
    if has_model_a and has_model_b:
        return "prerecorded"
    else:
        return "generate"


def evaluate_file(
    excel_path: str,
    mode: str,
    system_prompt: str,
    judge_model: str,
    use_all_metrics: bool,
    output_dir: str
) -> Dict:
    """
    Evaluate a single Excel file
    
    Args:
        excel_path: Path to Excel file
        mode: 'generate' or 'prerecorded'
        system_prompt: System prompt content
        judge_model: Judge model name
        use_all_metrics: Use all 7 metrics or just 4
        output_dir: Output directory
    
    Returns:
        Results dictionary
    """
    filename = os.path.basename(excel_path)
    print(f"\n{'='*80}")
    print(f"EVALUATING: {filename}")
    print(f"{'='*80}\n")
    print(f"Mode: {mode.upper()}")
    print()
    
    # Initialize tester
    tester = MultiTurnTester(
        BASE_MODEL,
        FINETUNED_MODEL,
        judge_model=judge_model,
        use_all_metrics=use_all_metrics
    )
    
    if mode == "prerecorded":
        # Use Excel responses
        print("✓ Using pre-recorded responses from Excel\n")
        
        loader = ExcelConversationLoader(excel_path)
        model_a_test_case, model_b_test_case = loader.parse_conversation_from_excel()
        
        # Add system prompt as context
        if system_prompt:
            model_a_test_case.context = [system_prompt]
            model_b_test_case.context = [system_prompt]
        
        print(f"Loaded {len(model_a_test_case.turns)} turns\n")
        
    else:  # generate mode
        # Generate responses on-the-fly
        print("✓ Generating responses on-the-fly\n")
        
        # Parse Excel
        df = pd.read_excel(excel_path)
        
        # Extract user queries
        user_queries = []
        for idx, row in df.iterrows():
            if "User Query" in df.columns and pd.notna(row["User Query"]):
                query = str(row["User Query"]).strip()
                if query:
                    user_queries.append(query)
        
        print(f"Extracted {len(user_queries)} user queries\n")
        
        # Build conversation
        full_conversation = []
        if system_prompt:
            full_conversation.append({"role": "system", "content": system_prompt})
        
        for query in user_queries:
            full_conversation.append({"role": "user", "content": query})
        
        # Generate responses
        print("🤖 Calling models to generate responses...\n")
        base_conv, finetuned_conv = tester.generate_conversations(full_conversation)
        
        # Convert to test cases
        from deepeval.test_case import ConversationalTestCase, Turn
        
        # Filter out system messages
        base_turns = [Turn(role=t["role"], content=t["content"]) for t in base_conv if t["role"] in ["user", "assistant"]]
        finetuned_turns = [Turn(role=t["role"], content=t["content"]) for t in finetuned_conv if t["role"] in ["user", "assistant"]]
        
        # Get optional metadata from Excel
        chatbot_role = None
        scenario = None
        if "Chatbot Role" in df.columns and pd.notna(df.iloc[0]["Chatbot Role"]):
            chatbot_role = str(df.iloc[0]["Chatbot Role"]).strip()
        if "Scenario" in df.columns and pd.notna(df.iloc[0]["Scenario"]):
            scenario = str(df.iloc[0]["Scenario"]).strip()
        
        model_a_test_case = ConversationalTestCase(
            turns=base_turns,
            context=[system_prompt] if system_prompt else None,
            chatbot_role=chatbot_role,
            scenario=scenario
        )
        
        model_b_test_case = ConversationalTestCase(
            turns=finetuned_turns,
            context=[system_prompt] if system_prompt else None,
            chatbot_role=chatbot_role,
            scenario=scenario
        )
        
        # Save generated responses to Excel
        output_excel_data = df.copy()
        model_a_responses = [t.content for t in base_turns if t.role == "assistant"]
        model_b_responses = [t.content for t in finetuned_turns if t.role == "assistant"]
        output_excel_data["Model A Response"] = pd.Series(model_a_responses[:len(output_excel_data)])
        output_excel_data["Model B Response"] = pd.Series(model_b_responses[:len(output_excel_data)])
        
        excel_out_path = os.path.join(output_dir, filename.replace('.xlsx', '_with_responses.xlsx'))
        output_excel_data.to_excel(excel_out_path, index=False)
        print(f"✓ Saved Excel with responses: {excel_out_path}\n")
    
    # Evaluate
    print("📊 Evaluating with all metrics...\n")
    result = tester.evaluate_from_excel_test_cases(
        model_a_test_case,
        model_b_test_case,
        filename
    )
    
    # Save results
    result_data = {
        "file": filename,
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "results": result
    }
    
    json_path = os.path.join(output_dir, filename.replace('.xlsx', '_results.json'))
    with open(json_path, 'w') as f:
        json.dump(result_data, f, indent=2, default=str)
    
    print(f"\n✅ Results saved: {json_path}")
    
    # Create clean outputs
    try:
        from create_clean_output import process_result_file
        process_result_file(json_path)
    except:
        pass
    
    return result_data


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='DeepEval Multi-Turn Conversation Evaluation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s input/test.xlsx
  %(prog)s input/test.xlsx --mode generate
  %(prog)s input/test.xlsx --judge gpt-4
  %(prog)s test1.xlsx test2.xlsx --metrics builtin
        '''
    )
    
    parser.add_argument('excel_files', nargs='*', help='Excel file(s) to evaluate')
    parser.add_argument('--mode', '-m', choices=['auto', 'generate', 'prerecorded'], default='auto',
                        help='Evaluation mode (default: auto)')
    parser.add_argument('--system-prompt', '-s', default='system_prompt.txt',
                        help='System prompt file (default: system_prompt.txt)')
    parser.add_argument('--judge', '-j', default='gpt-4.1-nano',
                        help='Judge model (default: gpt-4.1-nano)')
    parser.add_argument('--metrics', choices=['all', 'builtin'], default='all',
                        help='Metrics to use (default: all)')
    parser.add_argument('--output', '-o', default='evaluation_result',
                        help='Output directory (default: evaluation_result)')
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    print("\n" + "="*80)
    print("DEEPEVAL MULTI-TURN EVALUATION")
    print("="*80 + "\n")
    
    ensure_directories()
    
    # Load system prompt
    system_prompt = ""
    if os.path.exists(args.system_prompt):
        with open(args.system_prompt) as f:
            system_prompt = f.read().strip()
        print(f"✓ Loaded system prompt: {args.system_prompt}\n")
    
    # Get Excel files
    excel_files = []
    if args.excel_files:
        for f in args.excel_files:
            if os.path.exists(f):
                excel_files.append(f)
            elif os.path.exists(os.path.join('input', f)):
                excel_files.append(os.path.join('input', f))
    else:
        excel_files = glob.glob("input/*.xlsx")
    
    if not excel_files:
        print("❌ No Excel files found")
        print("\nUsage: python3 evaluate.py input/test.xlsx")
        print("   or: python3 evaluate.py  (processes all in input/)\n")
        return
    
    print(f"📂 Files to process: {len(excel_files)}")
    for f in excel_files:
        print(f"   - {os.path.basename(f)}")
    print()
    
    # Configuration
    use_all_metrics = (args.metrics == 'all')
    print(f"⚙️  Configuration:")
    print(f"   Judge Model: {args.judge}")
    print(f"   Metrics: {'All 7' if use_all_metrics else 'Only 4 built-in'}")
    print(f"   Mode: {args.mode.upper()}")
    
    # Process each file
    for excel_file in excel_files:
        try:
            # Determine mode
            if args.mode == 'auto':
                mode = detect_mode(excel_file)
            else:
                mode = args.mode
            
            # Evaluate
            evaluate_file(
                excel_file,
                mode,
                system_prompt,
                args.judge,
                use_all_metrics,
                args.output
            )
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue
    
    print("\n" + "="*80)
    print("✅ EVALUATION COMPLETE")
    print("="*80)
    print(f"\nResults in: {args.output}/\n")


if __name__ == "__main__":
    main()
