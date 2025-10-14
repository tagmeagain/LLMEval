#!/usr/bin/env python3
"""
Main Evaluation Script - DeepEval Multi-Turn Conversation Testing

Each ROW in Excel = One SEPARATE conversation to evaluate

Excel Format:
- Initial Conversation: Prior conversation (JSON format)
- User Query: Last user message
- Model A Response: Base model response (optional for generate mode)
- Model B Response: Finetuned model response (optional for generate mode)
"""

import argparse
import sys
import os
import glob
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List
import logging

# Import our modules
from multi_turn_testing import MultiTurnTester, deepeval_to_dict
from excel_loader import ExcelConversationLoader
from config import BASE_MODEL, FINETUNED_MODEL
from deepeval.test_case import ConversationalTestCase, Turn
from logger_config import setup_logger, log_section, log_subsection


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
        # Check if responses exist
        has_data = False
        for idx, row in df.iterrows():
            if pd.notna(row.get("Model A Response")) and pd.notna(row.get("Model B Response")):
                has_data = True
                break
        return "prerecorded" if has_data else "generate"
    else:
        return "generate"


def evaluate_file(
    excel_path: str,
    mode: str,
    system_prompt: str,
    judge_model: str,
    use_all_metrics: bool,
    output_dir: str,
    verbose_mode: bool = False
) -> Dict:
    """
    Evaluate conversations from Excel file
    Each row = one separate conversation
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
        use_all_metrics=use_all_metrics,
        verbose_mode=verbose_mode
    )
    
    loader = ExcelConversationLoader(excel_path)
    
    if mode == "prerecorded":
        print("✓ Using pre-recorded responses from Excel\n")
        
        # Get all conversations
        test_case_pairs = loader.get_conversations_prerecorded()
        
        if not test_case_pairs:
            print("❌ No valid conversations found in Excel")
            return None
        
        print(f"Loaded {len(test_case_pairs)} conversation(s)\n")
        
        # Evaluate each conversation
        all_results = []
        for idx, (model_a_test_case, model_b_test_case) in enumerate(test_case_pairs, 1):
            print(f"\n{'='*80}")
            print(f"Conversation {idx}/{len(test_case_pairs)}")
            print(f"{'='*80}\n")
            
            # Add system prompt as context and chatbot_role
            if system_prompt:
                model_a_test_case.context = [system_prompt]
                model_b_test_case.context = [system_prompt]
                # Use system prompt as chatbot_role if not already set
                if not model_a_test_case.chatbot_role or model_a_test_case.chatbot_role == "helpful AI assistant":
                    model_a_test_case.chatbot_role = system_prompt
                if not model_b_test_case.chatbot_role or model_b_test_case.chatbot_role == "helpful AI assistant":
                    model_b_test_case.chatbot_role = system_prompt
            
            # Print chatbot role being used
            print(f"📋 Chatbot Role: {model_a_test_case.chatbot_role[:100]}..." if len(model_a_test_case.chatbot_role) > 100 else f"📋 Chatbot Role: {model_a_test_case.chatbot_role}")
            print()
            
            # Evaluate
            result = tester.evaluate_from_excel_test_cases(
                model_a_test_case,
                model_b_test_case,
                f"{filename} - Conversation {idx}"
            )
            all_results.append(result)
        
        # Save combined results
        combined_results = {
            "file": filename,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "system_prompt": system_prompt[:200] if system_prompt else None,
            "total_conversations": len(test_case_pairs),
            "conversations": all_results
        }
        
    else:  # generate mode
        print("✓ Generating responses on-the-fly\n")
        
        # Get conversations for generation
        conversations = loader.get_conversations_for_generation()
        
        if not conversations:
            print("❌ No valid conversations found in Excel")
            return None
        
        print(f"Loaded {len(conversations)} conversation(s)\n")
        
        # Evaluate each conversation
        all_results = []
        generated_data = []
        
        for idx, conv_data in enumerate(conversations, 1):
            print(f"\n{'='*80}")
            print(f"Conversation {idx}/{len(conversations)}")
            print(f"{'='*80}\n")
            
            # Build conversation for generation
            initial_turns = conv_data["initial_turns"]
            user_query = conv_data["user_query"]
            metadata = conv_data["metadata"]
            
            # Build full conversation
            full_conversation = []
            if system_prompt:
                full_conversation.append({"role": "system", "content": system_prompt})
            
            # Add initial conversation
            for turn in initial_turns:
                full_conversation.append(turn)
            
            # Add user query
            full_conversation.append({"role": "user", "content": user_query})
            
            print(f"Initial conversation: {len(initial_turns)} turn(s)")
            print(f"User query: {user_query[:100]}...\n")
            
            # Generate responses
            print("🤖 Generating responses...\n")
            base_conv, finetuned_conv = tester.generate_conversations(full_conversation)
            
            # Convert to test cases (filter out system messages)
            base_turns = [Turn(role=t["role"], content=t["content"]) for t in base_conv if t["role"] in ["user", "assistant"]]
            finetuned_turns = [Turn(role=t["role"], content=t["content"]) for t in finetuned_conv if t["role"] in ["user", "assistant"]]
            
            # Create test cases
            model_a_test_case = ConversationalTestCase(
                turns=base_turns,
                context=[system_prompt] if system_prompt else None,
                **metadata
            )
            
            model_b_test_case = ConversationalTestCase(
                turns=finetuned_turns,
                context=[system_prompt] if system_prompt else None,
                **metadata
            )
            
            # Override chatbot_role with system prompt if default is being used
            if system_prompt:
                if not model_a_test_case.chatbot_role or model_a_test_case.chatbot_role == "helpful AI assistant":
                    model_a_test_case.chatbot_role = system_prompt
                if not model_b_test_case.chatbot_role or model_b_test_case.chatbot_role == "helpful AI assistant":
                    model_b_test_case.chatbot_role = system_prompt
            
            # Print chatbot role being used
            print(f"📋 Chatbot Role: {model_a_test_case.chatbot_role[:100]}..." if len(model_a_test_case.chatbot_role) > 100 else f"📋 Chatbot Role: {model_a_test_case.chatbot_role}")
            print()
            
            # Evaluate
            result = tester.evaluate_from_excel_test_cases(
                model_a_test_case,
                model_b_test_case,
                f"{filename} - Conversation {idx}"
            )
            all_results.append(result)
            
            # Store generated responses
            model_a_response = [t.content for t in base_turns if t.role == "assistant"][-1] if base_turns else ""
            model_b_response = [t.content for t in finetuned_turns if t.role == "assistant"][-1] if finetuned_turns else ""
            
            generated_data.append({
                "row_index": conv_data["row_index"],
                "user_query": user_query,
                "model_a_response": model_a_response,
                "model_b_response": model_b_response
            })
        
        # Save generated responses to Excel
        df = pd.read_excel(excel_path)
        for gen_data in generated_data:
            idx = gen_data["row_index"]
            df.at[idx, "Model A Response"] = gen_data["model_a_response"]
            df.at[idx, "Model B Response"] = gen_data["model_b_response"]
        
        excel_out_path = os.path.join(output_dir, filename.replace('.xlsx', '_with_responses.xlsx'))
        df.to_excel(excel_out_path, index=False)
        print(f"\n✓ Saved Excel with responses: {excel_out_path}\n")
        
        # Save combined results
        combined_results = {
            "file": filename,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "system_prompt": system_prompt[:200] if system_prompt else None,
            "total_conversations": len(conversations),
            "conversations": all_results
        }
    
    # Save JSON results
    json_path = os.path.join(output_dir, filename.replace('.xlsx', '_results.json'))
    # Convert DeepEval objects to clean dictionaries
    clean_results = deepeval_to_dict(combined_results)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved: {json_path}")
    
    # Create clean outputs
    try:
        from create_clean_output import process_result_file
        process_result_file(json_path)
    except Exception as e:
        print(f"⚠️  Could not create clean outputs: {e}")
    
    return combined_results


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
  
Each ROW in Excel = One separate conversation to evaluate
        '''
    )
    
    # Get default judge model from .env or use fallback
    default_judge = os.getenv('JUDGE_MODEL', 'gpt-4.1-nano')
    
    parser.add_argument('excel_files', nargs='*', help='Excel file(s) to evaluate')
    parser.add_argument('--mode', '-m', choices=['auto', 'generate', 'prerecorded'], default='auto',
                        help='Evaluation mode (default: auto)')
    parser.add_argument('--system-prompt', '-s', default='system_prompt.txt',
                        help='System prompt file (default: system_prompt.txt)')
    parser.add_argument('--judge', '-j', default=default_judge,
                        help=f'Judge model (default: {default_judge})')
    parser.add_argument('--metrics', choices=['all', 'builtin'], default='all',
                        help='Metrics to use (default: all)')
    parser.add_argument('--output', '-o', default='evaluation_result',
                        help='Output directory (default: evaluation_result)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose mode to see intermediate metric calculation steps')
    
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
    print(f"   Verbose: {'ON (shows intermediate steps)' if args.verbose else 'OFF'}")
    print(f"\n💡 Note: Each ROW in Excel = One conversation\n")
    
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
                args.output,
                verbose_mode=args.verbose
            )
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*80)
    print("✅ EVALUATION COMPLETE")
    print("="*80)
    print(f"\nResults in: {args.output}/\n")


if __name__ == "__main__":
    main()
