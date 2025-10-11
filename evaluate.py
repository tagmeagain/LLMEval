#!/usr/bin/env python3
"""
Unified Evaluation CLI - All possible ways to run
Modularized command-line interface for LLM evaluation

Usage Examples:
    # Auto-detect mode (recommended)
    python3 evaluate.py input/test.xlsx
    
    # Force generate mode (even if responses exist)
    python3 evaluate.py input/test.xlsx --mode generate
    
    # Force pre-recorded mode (error if no responses)
    python3 evaluate.py input/test.xlsx --mode prerecorded
    
    # Multiple files with auto-detection
    python3 evaluate.py input/test1.xlsx input/test2.xlsx
    
    # Custom system prompt
    python3 evaluate.py input/test.xlsx --system-prompt prompts/custom.txt
    
    # Custom judge model
    python3 evaluate.py input/test.xlsx --judge gpt-4
    
    # Use only 4 built-in metrics
    python3 evaluate.py input/test.xlsx --metrics builtin
    
    # Combine options
    python3 evaluate.py input/test.xlsx --mode generate --judge gpt-3.5-turbo --metrics builtin
"""

import argparse
import sys
import os
from run_evaluation import evaluate_single_file, detect_excel_mode, ensure_directories
import pandas as pd


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="DeepEval Multi-Turn Conversation Evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect mode (recommended)
  %(prog)s input/test.xlsx
  
  # Force generate responses on-the-fly
  %(prog)s input/test.xlsx --mode generate
  
  # Use pre-recorded responses only
  %(prog)s input/test.xlsx --mode prerecorded
  
  # Multiple files
  %(prog)s input/test1.xlsx input/test2.xlsx
  
  # Custom configuration
  %(prog)s input/test.xlsx --judge gpt-4 --metrics all
  
  # All options
  %(prog)s input/test.xlsx --mode generate --system-prompt custom.txt --judge gpt-4 --metrics builtin
        """
    )
    
    # Positional arguments
    parser.add_argument(
        'excel_files',
        nargs='*',
        help='Excel file(s) to evaluate. If not provided, processes all files in input/ folder'
    )
    
    # Mode control
    parser.add_argument(
        '--mode', '-m',
        choices=['auto', 'generate', 'prerecorded'],
        default='auto',
        help='''Evaluation mode:
  auto: Auto-detect based on Excel columns (default)
  generate: Force on-the-fly generation (requires model config)
  prerecorded: Force use of pre-recorded responses (error if missing)'''
    )
    
    # System prompt
    parser.add_argument(
        '--system-prompt', '-s',
        default='system_prompt.txt',
        help='Path to system prompt file (default: system_prompt.txt)'
    )
    
    # Judge model
    parser.add_argument(
        '--judge', '-j',
        default='gpt-4.1-nano',
        help='Judge model for evaluation (default: gpt-4.1-nano)'
    )
    
    # Metrics selection
    parser.add_argument(
        '--metrics',
        choices=['all', 'builtin'],
        default='all',
        help='''Metrics to use:
  all: All 7 metrics (3 custom + 4 built-in) [default]
  builtin: Only 4 built-in DeepEval metrics'''
    )
    
    # Output directory
    parser.add_argument(
        '--output', '-o',
        default='evaluation_result',
        help='Output directory for results (default: evaluation_result)'
    )
    
    # Verbose mode
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def validate_mode(excel_path, mode):
    """
    Validate and determine final mode
    
    Args:
        excel_path: Path to Excel file
        mode: Requested mode ('auto', 'generate', 'prerecorded')
    
    Returns:
        Final mode to use ('generate' or 'prerecorded')
    """
    df = pd.read_excel(excel_path)
    detected_mode = detect_excel_mode(df)
    
    if mode == 'auto':
        # Auto-detection
        return detected_mode
    elif mode == 'generate':
        # Force generate mode
        if detected_mode == 'prerecorded':
            print(f"⚠️  Warning: Excel has Model A/B Response columns but forcing GENERATE mode")
            print(f"   Existing responses will be ignored, new ones will be generated\n")
        return 'generate'
    elif mode == 'prerecorded':
        # Force pre-recorded mode
        if detected_mode == 'generate':
            raise ValueError(
                f"Error: Excel file '{excel_path}' is missing Model A Response and/or Model B Response columns.\n"
                f"Cannot use --mode prerecorded without these columns.\n"
                f"Either add the columns or use --mode generate"
            )
        return 'prerecorded'
    
    return detected_mode


def main():
    """Main CLI entry point"""
    args = parse_arguments()
    
    print("\n" + "="*80)
    print("DEEPEVAL MULTI-TURN EVALUATION CLI")
    print("="*80 + "\n")
    
    # Ensure directories
    ensure_directories()
    
    # Load system prompt
    system_prompt = None
    if os.path.exists(args.system_prompt):
        if args.verbose:
            print(f"📄 Loading system prompt: {args.system_prompt}")
        with open(args.system_prompt, "r") as f:
            system_prompt = f.read().strip()
        print(f"✓ System prompt loaded ({len(system_prompt)} characters)")
    else:
        print(f"⚠️  System prompt not found: {args.system_prompt}")
        print("   Continuing without system prompt...")
    print()
    
    # Determine files to process
    excel_files = []
    
    if args.excel_files:
        # Use specified files
        for file_arg in args.excel_files:
            # Try different path combinations
            possible_paths = [
                file_arg,
                os.path.join('input', file_arg),
                os.path.join('input', os.path.basename(file_arg))
            ]
            
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    excel_files.append(path)
                    found = True
                    break
            
            if not found:
                print(f"❌ File not found: {file_arg}")
                print(f"   Tried: {', '.join(possible_paths)}\n")
    else:
        # Use all files in input/
        import glob
        excel_files = glob.glob("input/*.xlsx") + glob.glob("input/*.xls")
        
        if not excel_files:
            print("❌ No Excel files found\n")
            print("Usage:")
            print("  python3 evaluate.py <file.xlsx>")
            print("  python3 evaluate.py input/test1.xlsx input/test2.xlsx")
            print("  python3 evaluate.py  (processes all files in input/)\n")
            return
    
    if not excel_files:
        print("❌ No valid Excel files to process\n")
        return
    
    print(f"📂 Files to process: {len(excel_files)}")
    for f in excel_files:
        print(f"   - {f}")
    print()
    
    # Configuration summary
    print("⚙️  Configuration:")
    print(f"   - Mode: {args.mode.upper()}")
    print(f"   - Judge Model: {args.judge}")
    print(f"   - Metrics: {'All 7 metrics' if args.metrics == 'all' else 'Only 4 built-in metrics'}")
    print(f"   - Output Directory: {args.output}/")
    print()
    
    # Process each file
    all_results = []
    use_all_metrics = (args.metrics == 'all')
    
    for idx, excel_file in enumerate(excel_files, 1):
        print(f"\n{'='*80}")
        print(f"FILE {idx}/{len(excel_files)}: {os.path.basename(excel_file)}")
        print(f"{'='*80}\n")
        
        try:
            # Validate and determine mode
            final_mode = validate_mode(excel_file, args.mode)
            
            print(f"📊 Mode: {final_mode.upper()}")
            
            if final_mode == 'generate':
                print("   → Will generate responses on-the-fly from both models")
            else:
                print("   → Will use pre-recorded responses from Excel")
            print()
            
            # Evaluate
            result = evaluate_single_file(
                excel_path=excel_file,
                system_prompt=system_prompt,
                output_dir=args.output,
                use_all_metrics=use_all_metrics,
                judge_model=args.judge
            )
            
            all_results.append(result)
            
        except Exception as e:
            print(f"\n❌ Error processing {excel_file}:")
            print(f"   {str(e)}\n")
            if args.verbose:
                import traceback
                traceback.print_exc()
            continue
    
    # Summary
    if all_results:
        print("\n" + "="*80)
        print("EVALUATION SUMMARY")
        print("="*80 + "\n")
        
        print(f"Total files processed: {len(all_results)}/{len(excel_files)}")
        print(f"Pre-recorded: {sum(1 for r in all_results if r.get('mode') == 'pre_recorded')}")
        print(f"Generated: {sum(1 for r in all_results if r.get('mode') == 'generated')}")
        print()
        
        print(f"Results saved to: {args.output}/")
        print()
        
        print("="*80)
        print("✅ EVALUATION COMPLETE")
        print("="*80)
    else:
        print("\n❌ No files were successfully processed\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        sys.exit(1)

