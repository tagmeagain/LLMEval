"""
Main testing framework for comparing base vs finetuned models
using multi-turn conversations with DeepEval
"""
from typing import List, Dict
import json
from deepeval import evaluate
from deepeval.test_case import LLMTestCase, ConversationalTestCase, TurnParams
from deepeval.metrics import (
    ConversationalGEval,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
    # Built-in Multi-Turn Conversation Metrics
    TurnRelevancyMetric,
    RoleAdherenceMetric,
    KnowledgeRetentionMetric,
    ConversationCompletenessMetric,
)

from model_wrapper import ModelWrapper
from config import BASE_MODEL, FINETUNED_MODEL
# Test cases removed - use Excel files instead


class MultiTurnTester:
    """Framework for testing multi-turn conversations"""
    
    def __init__(self, base_model_config: dict, finetuned_model_config: dict, judge_model: str = "gpt-4", use_all_metrics: bool = True, verbose_mode: bool = False):
        self.base_model = ModelWrapper(base_model_config)
        self.finetuned_model = ModelWrapper(finetuned_model_config)
        self.judge_model = judge_model  # Store judge model for all evaluations
        self.use_all_metrics = use_all_metrics  # Whether to use all 7 metrics or just original 4
        self.verbose_mode = verbose_mode  # Whether to print intermediate metric calculation steps
        self.results = []
    
    def generate_conversations(self, user_turns: List[Dict[str, str]]) -> tuple:
        """
        Generate complete conversations for both models
        
        Args:
            user_turns: List of user messages
            
        Returns:
            Tuple of (base_conversation, finetuned_conversation)
        """
        base_conversation = self.base_model.generate_multi_turn_conversation(user_turns)
        finetuned_conversation = self.finetuned_model.generate_multi_turn_conversation(user_turns)
        
        return base_conversation, finetuned_conversation
    
    def create_conversational_metrics(self, judge_model: str = "gpt-4", use_all_metrics: bool = True):
        """
        Create metrics for evaluating multi-turn conversations
        Uses LLM-as-a-judge for evaluation with DeepEval's built-in metrics
        
        Args:
            judge_model: Model to use as judge (default: "gpt-4")
                        Options: "gpt-4", "gpt-4o", "gpt-3.5-turbo", etc.
            use_all_metrics: If True, use all 7 metrics. If False, use basic 4 metrics (default: True)
        """
        if use_all_metrics:
            # Use all 7 conversational metrics (3 custom + 4 built-in)
            return [
                # Custom Conversational GEval metrics (following official docs)
                ConversationalGEval(
                    name="Coherence",
                    evaluation_steps=[
                        "Evaluate whether the conversation flows logically from one turn to the next",
                        "Check if responses are well-structured and easy to follow",
                        "Assess if there are smooth transitions between topics",
                        "Identify any abrupt changes or confusing sequences that disrupt coherence"
                    ],
                    evaluation_params=[TurnParams.CONTENT],  # Evaluates turn content
                    model=judge_model,
                ),
                ConversationalGEval(
                    name="Contextual Understanding",
                    evaluation_steps=[
                        "Check if the assistant understands the full context of the conversation",
                        "Verify that responses build appropriately on previous turns",
                        "Identify any instances where context is misunderstood or ignored",
                        "Assess whether the assistant maintains awareness of the overall conversation thread"
                    ],
                    evaluation_params=[TurnParams.CONTENT],  # Evaluates turn content
                    model=judge_model,
                ),
                ConversationalGEval(
                    name="Helpfulness",
                    evaluation_steps=[
                        "Determine if the responses provide practical, actionable information",
                        "Assess whether the assistant addresses the user's needs effectively",
                        "Check if explanations are clear and useful for the user",
                        "Evaluate if the assistant goes beyond surface-level responses to truly help"
                    ],
                    evaluation_params=[TurnParams.CONTENT],  # Evaluates turn content
                    model=judge_model,
                ),
                # DeepEval's built-in multi-turn conversation metrics
                # Using ALL available parameters from official docs
                KnowledgeRetentionMetric(
                    threshold=0.5,
                    model=judge_model,
                    include_reason=True,      # Include reasoning for scores
                    strict_mode=False,         # Allow scores between 0-1
                    async_mode=True,           # Enable concurrent execution
                    verbose_mode=self.verbose_mode  # Shows intermediate steps if enabled
                ),
                TurnRelevancyMetric(
                    threshold=0.5,
                    model=judge_model,
                    include_reason=True,       # Include reasoning for scores
                    strict_mode=False,         # Allow scores between 0-1
                    async_mode=True,           # Enable concurrent execution
                    verbose_mode=self.verbose_mode,  # Shows intermediate steps if enabled
                    window_size=10             # Sliding window size for context
                ),
                RoleAdherenceMetric(
                    threshold=0.5,
                    model=judge_model,
                    include_reason=True,       # Include reasoning for scores
                    strict_mode=False,         # Allow scores between 0-1
                    async_mode=True,           # Enable concurrent execution
                    verbose_mode=self.verbose_mode  # Shows intermediate steps if enabled
                ),
                ConversationCompletenessMetric(
                    threshold=0.5,
                    model=judge_model,
                    include_reason=True,       # Include reasoning for scores
                    strict_mode=False,         # Allow scores between 0-1
                    async_mode=True,           # Enable concurrent execution
                    verbose_mode=self.verbose_mode  # Shows intermediate steps if enabled
                ),
            ]
        else:
            # Only 4 built-in metrics (for cost savings - no custom GEval)
            # Using ALL available parameters
            return [
                KnowledgeRetentionMetric(
                    threshold=0.5,
                    model=judge_model,
                    include_reason=True,
                    strict_mode=False,
                    async_mode=True,
                    verbose_mode=self.verbose_mode
                ),
                TurnRelevancyMetric(
                    threshold=0.5,
                    model=judge_model,
                    include_reason=True,
                    strict_mode=False,
                    async_mode=True,
                    verbose_mode=self.verbose_mode,
                    window_size=10
                ),
                RoleAdherenceMetric(
                    threshold=0.5,
                    model=judge_model,
                    include_reason=True,
                    strict_mode=False,
                    async_mode=True,
                    verbose_mode=self.verbose_mode
                ),
                ConversationCompletenessMetric(
                    threshold=0.5,
                    model=judge_model,
                    include_reason=True,
                    strict_mode=False,
                    async_mode=True,
                    verbose_mode=self.verbose_mode
                ),
            ]
    
    def evaluate_conversation(self, test_case: ConversationalTestCase, model_name: str) -> dict:
        """
        Evaluate a ConversationalTestCase using DeepEval metrics
        
        Args:
            test_case: ConversationalTestCase with Turn objects
            model_name: Name of the model for tracking
            
        Returns:
            Evaluation results
        """
        # Get metrics with configured judge model
        metrics = self.create_conversational_metrics(judge_model=self.judge_model, use_all_metrics=self.use_all_metrics)
        
        # Evaluate using DeepEval's evaluate function
        results = evaluate(
            test_cases=[test_case],
            metrics=metrics
        )
        
        return {
            "model": model_name,
            "test_case": test_case,
            "metrics": results
        }
    
    def evaluate_from_excel_test_cases(self, model_a_test_case: ConversationalTestCase, model_b_test_case: ConversationalTestCase, test_name: str) -> dict:
        """
        Evaluate both models from pre-constructed test cases
        
        Args:
            model_a_test_case: Test case for Model A (base)
            model_b_test_case: Test case for Model B (finetuned)
            test_name: Name of the test
        
        Returns:
            Dictionary with both evaluations
        """
        print("Evaluating Model A (Base)...")
        model_a_results = self.evaluate_conversation(model_a_test_case, "Model A (Base)")
        
        print("\nEvaluating Model B (Finetuned)...")
        model_b_results = self.evaluate_conversation(model_b_test_case, "Model B (Finetuned)")
        
        return {
            "test_name": test_name,
            "model_a_evaluation": model_a_results,
            "model_b_evaluation": model_b_results
        }
    
    def compare_models_arena(
        self, 
        base_conversation: List[Dict[str, str]], 
        finetuned_conversation: List[Dict[str, str]],
        criteria: str = "Which conversation is more helpful, coherent, and demonstrates better understanding of context?"
    ) -> dict:
        """
        Compare two model outputs using Arena G-Eval (LLM-as-a-judge)
        
        Args:
            base_conversation: Conversation from base model
            finetuned_conversation: Conversation from finetuned model
            criteria: Criteria for comparison
            
        Returns:
            Comparison results
        """
        from deepeval.test_case import ArenaTestCase
        from deepeval.metrics import ArenaGEval
        from deepeval import compare
        
        # Convert conversations to strings
        base_text = "\n".join([
            f"{turn['role'].upper()}: {turn['content']}" 
            for turn in base_conversation
        ])
        finetuned_text = "\n".join([
            f"{turn['role'].upper()}: {turn['content']}" 
            for turn in finetuned_conversation
        ])
        
        # Create test cases for each model
        base_test_case = LLMTestCase(
            input=base_conversation[0]["content"],
            actual_output=base_text
        )
        
        finetuned_test_case = LLMTestCase(
            input=finetuned_conversation[0]["content"],
            actual_output=finetuned_text
        )
        
        # Create arena test case
        arena_test_case = ArenaTestCase(
            contestants={
                "Base Model": base_test_case,
                "Finetuned Model": finetuned_test_case
            }
        )
        
        # Create arena metric (LLM-as-a-judge) with configured judge model
        arena_metric = ArenaGEval(criteria=criteria, model=self.judge_model)
        
        # Compare
        comparison_results = compare(
            test_cases=[arena_test_case],
            metric=arena_metric,
            print_results=True
        )
        
        return {
            "better_performer": arena_metric.name,
            "criteria": criteria,
            "base_conversation": base_conversation,
            "finetuned_conversation": finetuned_conversation,
            "results": comparison_results
        }
    
    def run_test_suite(self, test_cases: List[List[Dict[str, str]]], suite_name: str = "Test Suite"):
        """
        Run complete test suite comparing both models
        
        Args:
            test_cases: List of user turn sequences
            suite_name: Name of the test suite
        """
        print(f"\n{'='*80}")
        print(f"Running Test Suite: {suite_name}")
        print(f"{'='*80}\n")
        
        all_results = []
        
        for idx, user_turns in enumerate(test_cases, 1):
            print(f"\n--- Test Case {idx} ---")
            print(f"Initial Query: {user_turns[0]['content']}")
            
            # Generate conversations from both models
            base_conv, finetuned_conv = self.generate_conversations(user_turns)
            
            print("\n[Base Model Response Preview]")
            print(f"{base_conv[1]['content'][:200]}...")
            
            print("\n[Finetuned Model Response Preview]")
            print(f"{finetuned_conv[1]['content'][:200]}...")
            
            # Evaluate both conversations individually
            print("\nEvaluating Base Model...")
            base_eval = self.evaluate_conversation(base_conv, "Base Model")
            
            print("Evaluating Finetuned Model...")
            finetuned_eval = self.evaluate_conversation(finetuned_conv, "Finetuned Model")
            
            # Arena comparison (LLM-as-a-judge)
            print("\nRunning Arena Comparison (LLM-as-a-judge)...")
            arena_result = self.compare_models_arena(base_conv, finetuned_conv)
            
            all_results.append({
                "test_case_id": idx,
                "user_turns": user_turns,
                "base_evaluation": base_eval,
                "finetuned_evaluation": finetuned_eval,
                "arena_comparison": arena_result
            })
            
            print(f"\n{'='*80}\n")
        
        # Save results
        self.results = all_results
        self.save_results(f"{suite_name.replace(' ', '_').lower()}_results.json")
        
        return all_results
    
    def save_results(self, filename: str):
        """Save test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nResults saved to {filename}")
    
    def print_summary(self):
        """Print summary of test results"""
        if not self.results:
            print("No results to summarize")
            return
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        base_higher = sum(1 for r in self.results 
                       if "Base Model" in str(r.get("arena_comparison", {}).get("better_performer", "")))
        finetuned_higher = len(self.results) - base_higher
        
        print(f"\nTotal Test Cases: {len(self.results)}")
        print(f"Base Model Scores Higher: {base_higher}")
        print(f"Finetuned Model Scores Higher: {finetuned_higher}")
        print(f"Performance Rate (Finetuned): {finetuned_higher/len(self.results)*100:.1f}%")
        print(f"\nMetrics Used: {'All 7 metrics' if self.use_all_metrics else 'Original 4 metrics'}")
        print("\n" + "="*80)
    
    def evaluate_from_excel_test_cases(
        self,
        model_a_test_case: ConversationalTestCase,
        model_b_test_case: ConversationalTestCase,
        test_case_name: str = "Excel Test Case"
    ) -> dict:
        """
        Evaluate pre-existing ConversationalTestCases loaded from Excel
        
        Args:
            model_a_test_case: ConversationalTestCase from Model A (Base)
            model_b_test_case: ConversationalTestCase from Model B (Finetuned)
            test_case_name: Name for this test case
            
        Returns:
            Evaluation results including individual metrics and arena comparison
        """
        print(f"\n{'='*80}")
        print(f"Evaluating: {test_case_name}")
        print(f"{'='*80}\n")
        
        # Evaluate Model A (Base)
        print("Evaluating Model A (Base)...")
        base_eval = self.evaluate_conversation(model_a_test_case, "Model A (Base)")
        
        # Evaluate Model B (Finetuned)
        print("Evaluating Model B (Finetuned)...")
        finetuned_eval = self.evaluate_conversation(model_b_test_case, "Model B (Finetuned)")
        
        result = {
            "test_case_name": test_case_name,
            "model_a_evaluation": base_eval,
            "model_b_evaluation": finetuned_eval
        }
        
        self.results.append(result)
        
        print(f"\n{'='*80}\n")
        return result


def main():
    """Main execution function"""
    print("Initializing Multi-Turn Conversation Testing Framework")
    print("This framework uses DeepEval with LLM-as-a-judge metrics\n")
    
    # Initialize tester with judge model
    # Options: "gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo", etc.
    tester = MultiTurnTester(BASE_MODEL, FINETUNED_MODEL, judge_model="gpt-4")
    
    # Run customer support test cases
    customer_support_cases = create_customer_support_test_cases()
    tester.run_test_suite(customer_support_cases, "Customer Support Scenarios")
    
    # Run conversational test cases
    conversational_cases = create_conversational_test_cases()
    tester.run_test_suite(conversational_cases, "General Conversation Scenarios")
    
    # Print summary
    tester.print_summary()


if __name__ == "__main__":
    main()

