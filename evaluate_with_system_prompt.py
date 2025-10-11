"""
Evaluation script that loads system prompt from file and initial conversation from Excel
"""
from excel_loader import ExcelConversationLoader
from multi_turn_testing import MultiTurnTester
from config import BASE_MODEL, FINETUNED_MODEL
import os


def load_and_evaluate(
    excel_path: str,
    system_prompt_path: str = "system_prompt.txt",
    test_name: str = None,
    use_all_metrics: bool = True,
    judge_model: str = "gpt-4"
):
    """
    Load conversations from Excel and evaluate with system prompt
    
    Args:
        excel_path: Path to Excel file with conversations
        system_prompt_path: Path to system prompt text file
        test_name: Name for this test (default: Excel filename)
        use_all_metrics: Use all 7 metrics or just 4 built-in (default: True)
        judge_model: LLM to use as judge (default: gpt-4)
    
    Excel Format:
        - Initial Conversation: JSON array of prior turns OR leave empty
          Example JSON: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}]
        - User Query: User's question
        - Model A Response: Base model's response
        - Model B Response: Finetuned model's response
        - Scenario (optional): Test scenario description
        - Expected Outcome (optional): What should happen
        - Chatbot Role (optional): Role the chatbot should play
    """
    print("\n" + "="*80)
    print("DEEPEVAL MULTI-TURN CONVERSATION EVALUATION")
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
    
    # 2. Load conversations from Excel
    print(f"📊 Loading conversations from Excel: {excel_path}")
    loader = ExcelConversationLoader(excel_path)
    model_a_test_case, model_b_test_case = loader.parse_conversation_from_excel()
    
    print(f"✓ Loaded test case with {len(model_a_test_case.turns)} turns")
    
    # Show initial conversation if present (first few turns before user queries)
    if model_a_test_case.turns and hasattr(model_a_test_case, '_initial_turns_count'):
        print(f"  - Initial conversation: {model_a_test_case._initial_turns_count} prior turns")
    
    print(f"  - Scenario: {model_a_test_case.scenario or 'Not specified'}")
    print(f"  - Expected Outcome: {model_a_test_case.expected_outcome or 'Not specified'}")
    print(f"  - Chatbot Role: {model_a_test_case.chatbot_role or 'Not specified'}")
    
    # 3. Add system prompt to test cases (as context)
    if system_prompt:
        # Preserve any existing context and add system prompt
        existing_context = model_a_test_case.context or []
        model_a_test_case.context = [system_prompt] + existing_context
        model_b_test_case.context = [system_prompt] + existing_context
        print(f"✓ System prompt added to test cases as context\n")
    
    # 4. Preview conversations
    print("\n" + "-"*80)
    print("PREVIEW - Model A (Base Model)")
    print("-"*80)
    for i, turn in enumerate(model_a_test_case.turns[:6], 1):  # Show first 6 turns
        content_preview = turn.content[:100] + "..." if len(turn.content) > 100 else turn.content
        print(f"  Turn {i} [{turn.role}]: {content_preview}")
    if len(model_a_test_case.turns) > 6:
        print(f"  ... and {len(model_a_test_case.turns) - 6} more turns")
    
    print("\n" + "-"*80)
    print("PREVIEW - Model B (Finetuned Model)")
    print("-"*80)
    for i, turn in enumerate(model_b_test_case.turns[:6], 1):
        content_preview = turn.content[:100] + "..." if len(turn.content) > 100 else turn.content
        print(f"  Turn {i} [{turn.role}]: {content_preview}")
    if len(model_b_test_case.turns) > 6:
        print(f"  ... and {len(model_b_test_case.turns) - 6} more turns")
    
    # 5. Initialize tester
    print("\n" + "="*80)
    print(f"INITIALIZING EVALUATOR")
    print("="*80)
    print(f"  Judge Model: {judge_model}")
    print(f"  Metrics: {'All 7 metrics (3 custom + 4 built-in)' if use_all_metrics else 'Only 4 built-in metrics'}")
    print()
    
    tester = MultiTurnTester(
        BASE_MODEL,
        FINETUNED_MODEL,
        judge_model=judge_model,
        use_all_metrics=use_all_metrics
    )
    
    # 6. Run evaluation
    test_case_name = test_name or f"Excel Test: {os.path.basename(excel_path)}"
    print("="*80)
    print(f"RUNNING EVALUATION: {test_case_name}")
    print("="*80 + "\n")
    
    result = tester.evaluate_from_excel_test_cases(
        model_a_test_case,
        model_b_test_case,
        test_case_name
    )
    
    # 7. Save results
    output_filename = f"results_{os.path.basename(excel_path).replace('.xlsx', '')}.json"
    tester.save_results(output_filename)
    
    # 8. Print summary
    tester.print_summary()
    
    print("\n" + "="*80)
    print("✅ EVALUATION COMPLETE")
    print("="*80)
    print(f"Results saved to: {output_filename}")
    print()
    
    return result


def batch_evaluate(
    excel_files: list,
    system_prompt_path: str = "system_prompt.txt",
    use_all_metrics: bool = True,
    judge_model: str = "gpt-4"
):
    """
    Evaluate multiple Excel files with the same system prompt
    
    Args:
        excel_files: List of Excel file paths
        system_prompt_path: Path to system prompt
        use_all_metrics: Use all 7 metrics (default: True)
        judge_model: Judge model (default: gpt-4)
    """
    print("\n" + "="*80)
    print(f"BATCH EVALUATION - {len(excel_files)} TEST FILES")
    print("="*80 + "\n")
    
    results = []
    
    for i, excel_path in enumerate(excel_files, 1):
        print(f"\n{'='*80}")
        print(f"TEST FILE {i}/{len(excel_files)}: {excel_path}")
        print(f"{'='*80}\n")
        
        result = load_and_evaluate(
            excel_path=excel_path,
            system_prompt_path=system_prompt_path,
            test_name=f"Batch Test {i}: {os.path.basename(excel_path)}",
            use_all_metrics=use_all_metrics,
            judge_model=judge_model
        )
        results.append(result)
    
    print("\n" + "="*80)
    print(f"✅ BATCH EVALUATION COMPLETE - {len(excel_files)} FILES PROCESSED")
    print("="*80 + "\n")
    
    return results


# Example usage
if __name__ == "__main__":
    import sys
    
    # Check if Excel file provided as argument
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
        system_prompt_file = sys.argv[2] if len(sys.argv) > 2 else "system_prompt.txt"
        
        load_and_evaluate(
            excel_path=excel_file,
            system_prompt_path=system_prompt_file,
            use_all_metrics=True,
            judge_model="gpt-4"
        )
    else:
        print("\n" + "="*80)
        print("USAGE EXAMPLES")
        print("="*80 + "\n")
        
        print("1. Single file evaluation:")
        print("   python3 evaluate_with_system_prompt.py conversations.xlsx")
        print()
        
        print("2. With custom system prompt location:")
        print("   python3 evaluate_with_system_prompt.py conversations.xlsx prompts/system.txt")
        print()
        
        print("3. Programmatic usage:")
        print('''
from evaluate_with_system_prompt import load_and_evaluate

# Evaluate single file
load_and_evaluate(
    excel_path="conversations.xlsx",
    system_prompt_path="system_prompt.txt",
    test_name="Customer Support Test 1",
    use_all_metrics=True,
    judge_model="gpt-4"
)

# Batch evaluate multiple files
from evaluate_with_system_prompt import batch_evaluate

batch_evaluate(
    excel_files=[
        "test1.xlsx",
        "test2.xlsx",
        "test3.xlsx"
    ],
    system_prompt_path="system_prompt.txt"
)
        ''')
        print()
        
        print("="*80)
        print("EXCEL FORMAT")
        print("="*80 + "\n")
        
        print("Required columns:")
        print("  - Turn: Turn number (1, 2, 3, ...)")
        print("  - User Query: User's question")
        print("  - Model A Response: Base model's answer")
        print("  - Model B Response: Finetuned model's answer")
        print()
        
        print("Optional columns:")
        print("  - Initial Conversation: JSON array of prior conversation")
        print('    Example: [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello!"}]')
        print("  - Scenario: Test scenario description")
        print("  - Expected Outcome: Expected result")
        print("  - Chatbot Role: Role the chatbot should play")
        print()
        
        print("System Prompt:")
        print("  - Create system_prompt.txt with your system prompt")
        print("  - Will be automatically loaded and added as context")
        print()


