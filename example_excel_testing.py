"""
Example: Testing with Excel Files
Load conversations from Excel and evaluate Model A vs Model B
"""
from excel_loader import ExcelConversationLoader, load_excel_test_cases
from multi_turn_testing import MultiTurnTester
from config import BASE_MODEL, FINETUNED_MODEL
import pandas as pd
import os


def create_example_excel_template(filename: str = "example_conversation_template.xlsx"):
    """
    Create an example Excel template for testing
    
    Args:
        filename: Name of Excel file to create
    """
    # Example conversation data
    data = {
        "Turn": [1, 2, 3, 4],
        "Initial Conversation": [
            "You are a helpful customer support agent for TechCorp",
            "",
            "",
            ""
        ],
        "User Query": [
            "I can't log into my account",
            "Yes, I tried resetting my password but didn't get the email",
            "I checked spam folder, nothing there",
            "My email is john@example.com"
        ],
        "Model A Response": [
            "I'm sorry to hear you're having trouble logging in. Have you tried resetting your password?",
            "I see. Let me help you with that. Can you confirm you've checked your spam folder?",
            "Okay, let me look into this. What email address is associated with your account?",
            "Thank you. I'll manually send you a password reset link to john@example.com. You should receive it within 5 minutes."
        ],
        "Model B Response": [
            "I understand you're unable to access your account. This must be frustrating. Let's get this resolved. Have you tried using the 'Forgot Password' feature?",
            "I see you've already tried that. Let me check a few things. First, can you confirm you've checked your spam/junk folder for the reset email?",
            "Got it. Since you've confirmed it's not in spam, let me verify your account details. Could you please provide the email address registered with your account?",
            "Perfect! I've just manually triggered a password reset for john@example.com. You should receive it within 2-3 minutes. If you don't see it, please check your spam folder again, and feel free to reach back out to me. Is there anything else I can help you with?"
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, sheet_name="Test Case 1")
    
    print(f"✓ Created example Excel template: {filename}")
    print("\nTemplate Structure:")
    print(f"  - Column A: Turn number (1, 2, 3, ...)")
    print(f"  - Column B: Initial Conversation context (optional, first row only)")
    print(f"  - Column C: User Query (required)")
    print(f"  - Column D: Model A Response (Base Model)")
    print(f"  - Column E: Model B Response (Finetuned Model)")
    print(f"\nYou can now edit this file with your own conversations!")


def test_from_excel_existing_responses(excel_path: str):
    """
    Test using pre-existing responses from Excel
    
    Args:
        excel_path: Path to Excel file with conversations
    """
    print("\n" + "="*80)
    print("TESTING FROM EXCEL - USING EXISTING RESPONSES")
    print("="*80 + "\n")
    
    # Load conversations from Excel as ConversationalTestCase
    print(f"📂 Loading test cases from: {excel_path}")
    loader = ExcelConversationLoader(excel_path)
    model_a_test_case, model_b_test_case = loader.parse_conversation_from_excel()
    
    print(f"✓ Loaded test case with {len(model_a_test_case.turns)} turns")
    print(f"\nPreview - Model A (Base):")
    for i, turn in enumerate(model_a_test_case.turns[:4], 1):
        print(f"  Turn {i} ({turn.role}): {turn.content[:80]}...")
    
    print(f"\nPreview - Model B (Finetuned):")
    for i, turn in enumerate(model_b_test_case.turns[:4], 1):
        print(f"  Turn {i} ({turn.role}): {turn.content[:80]}...")
    
    # Initialize tester with all 7 metrics
    print("\n🔧 Initializing evaluator with all 7 metrics...")
    tester = MultiTurnTester(
        BASE_MODEL,
        FINETUNED_MODEL,
        judge_model="gpt-4",
        use_all_metrics=True
    )
    
    # Evaluate the test cases
    print("\n📊 Evaluating test cases...")
    result = tester.evaluate_from_excel_test_cases(
        model_a_test_case,
        model_b_test_case,
        f"Excel Test: {os.path.basename(excel_path)}"
    )
    
    # Save and print results
    tester.save_results("excel_evaluation_results.json")
    tester.print_summary()
    
    print("\n✅ Evaluation complete!")


def test_from_excel_generate_new_responses(excel_path: str):
    """
    Extract user queries from Excel and generate fresh responses
    
    Args:
        excel_path: Path to Excel file with user queries
    """
    print("\n" + "="*80)
    print("TESTING FROM EXCEL - GENERATING NEW RESPONSES")
    print("="*80 + "\n")
    
    # Extract only user queries
    print(f"📂 Loading user queries from: {excel_path}")
    loader = ExcelConversationLoader(excel_path)
    user_turns = loader.extract_user_turns_only()
    
    print(f"✓ Extracted {len(user_turns)} user queries")
    for i, turn in enumerate(user_turns, 1):
        print(f"  {i}. {turn['content']}")
    
    # Initialize tester to generate new responses
    print("\n🤖 Initializing models to generate fresh responses...")
    tester = MultiTurnTester(
        BASE_MODEL,
        FINETUNED_MODEL,
        judge_model="gpt-4",
        use_all_metrics=True
    )
    
    # Generate and evaluate
    print("\n📊 Generating responses and evaluating...")
    base_conv, finetuned_conv = tester.generate_conversations(user_turns)
    
    result = tester.evaluate_from_excel_responses(
        base_conv,
        finetuned_conv,
        f"Generated from Excel: {os.path.basename(excel_path)}"
    )
    
    # Save results
    tester.save_results("excel_generated_evaluation_results.json")
    tester.print_summary()
    
    print("\n✅ Evaluation complete!")


def print_metric_definitions():
    """Print all available DeepEval multi-turn metrics"""
    print("\n" + "="*80)
    print("AVAILABLE METRICS FOR MULTI-TURN CONVERSATION EVALUATION")
    print("="*80 + "\n")
    
    metrics = {
        "1. Coherence": (
            "The collective quality of all sentences in the conversation. "
            "Evaluates logical flow, smooth transitions, and overall clarity."
        ),
        "2. Contextual Understanding": (
            "The assistant's ability to understand and maintain context throughout "
            "the conversation. Checks for appropriate context awareness and usage."
        ),
        "3. Helpfulness": (
            "How helpful and actionable the assistant's responses are. "
            "Evaluates practical value and usefulness of information provided."
        ),
        "4. Knowledge Retention": (
            "The assistant's ability to remember and reference information from "
            "earlier in the conversation. Checks for consistency and memory.\n"
            "📚 Built-in DeepEval metric: https://deepeval.com/docs/metrics-knowledge-retention"
        ),
        "5. Turn Relevancy": (
            "Whether each assistant response is relevant and appropriate to the user's "
            "query and conversation context. Checks for off-topic responses.\n"
            "📚 Built-in DeepEval metric: https://deepeval.com/docs/metrics-turn-relevancy"
        ),
        "6. Role Adherence": (
            "How consistently the assistant maintains its assigned role, personality, "
            "tone, and guidelines throughout the conversation.\n"
            "📚 Built-in DeepEval metric: https://deepeval.com/docs/metrics-role-adherence"
        ),
        "7. Conversation Completeness": (
            "Whether the conversation adequately addresses all user queries and reaches "
            "a satisfactory conclusion. Checks for unresolved questions.\n"
            "📚 Built-in DeepEval metric: https://deepeval.com/docs/metrics-conversation-completeness"
        ),
    }
    
    for metric_name, definition in metrics.items():
        print(f"{metric_name}")
        print(f"   {definition}\n")
    
    print("="*80)
    print(f"Total: {len(metrics)} metrics available (all using LLM-as-a-judge)")
    print("="*80 + "\n")


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("EXCEL-BASED MULTI-TURN CONVERSATION TESTING")
    print("="*80)
    
    # Show available metrics
    print_metric_definitions()
    
    # Create example template
    template_file = "example_conversation_template.xlsx"
    if not os.path.exists(template_file):
        print("\n📝 Creating example Excel template...")
        create_example_excel_template(template_file)
    else:
        print(f"\n✓ Example template already exists: {template_file}")
    
    # Instructions
    print("\n" + "="*80)
    print("HOW TO USE EXCEL TESTING")
    print("="*80)
    print("\n1. OPTION A - Use Pre-recorded Responses:")
    print("   - Open the Excel template")
    print("   - Fill in User Queries, Model A Responses, Model B Responses")
    print("   - Run: test_from_excel_existing_responses('your_file.xlsx')")
    print("   - This will evaluate the existing responses")
    
    print("\n2. OPTION B - Generate Fresh Responses:")
    print("   - Create Excel with just User Queries")
    print("   - Run: test_from_excel_generate_new_responses('your_file.xlsx')")
    print("   - Models will generate new responses and evaluate them")
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print(f"\n1. Edit the template: {template_file}")
    print("2. Add your actual Model A and Model B responses")
    print("3. Run the evaluation:")
    print(f"   python -c \"from example_excel_testing import test_from_excel_existing_responses; test_from_excel_existing_responses('{template_file}')\"")
    
    # If template exists, offer to test it
    if os.path.exists(template_file):
        print(f"\n\n🚀 Would you like to test the example template now?")
        print(f"   Uncomment the line below in main() to run:")
        print(f"   # test_from_excel_existing_responses('{template_file}')")


if __name__ == "__main__":
    main()
    
    # Uncomment to test with the example template:
    # test_from_excel_existing_responses("example_conversation_template.xlsx")

