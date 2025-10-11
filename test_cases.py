"""
Define multi-turn conversation test cases
"""
from deepeval.test_case import ConversationalTestCase, LLMTestCase
from typing import List, Dict


def create_customer_support_test_cases() -> List[List[Dict[str, str]]]:
    """
    Create test cases for customer support scenarios
    Returns a list of conversations (each conversation is a list of user turns)
    """
    return [
        # Test Case 1: Technical Support
        [
            {"role": "user", "content": "My application keeps crashing when I try to upload files."},
            {"role": "user", "content": "I'm using Chrome on Windows 10."},
            {"role": "user", "content": "The files are PDFs, around 5MB each."},
            {"role": "user", "content": "Thank you! Should I clear my browser cache?"}
        ],
        # Test Case 2: Product Inquiry
        [
            {"role": "user", "content": "What are the differences between your Basic and Pro plans?"},
            {"role": "user", "content": "How many users can I have on the Pro plan?"},
            {"role": "user", "content": "Can I upgrade from Basic to Pro later?"},
            {"role": "user", "content": "Is there a discount for annual subscriptions?"}
        ],
        # Test Case 3: Account Management
        [
            {"role": "user", "content": "I can't log into my account."},
            {"role": "user", "content": "Yes, I tried resetting my password but didn't receive the email."},
            {"role": "user", "content": "I checked spam, it's not there either."},
            {"role": "user", "content": "My email is user@example.com"}
        ],
        # Test Case 4: Feature Request
        [
            {"role": "user", "content": "Does your platform support API integrations?"},
            {"role": "user", "content": "Specifically, I need to integrate with Salesforce."},
            {"role": "user", "content": "What authentication methods do you support?"},
            {"role": "user", "content": "Great! Where can I find the API documentation?"}
        ],
    ]


def create_conversational_test_cases() -> List[List[Dict[str, str]]]:
    """
    Create general conversational test cases
    """
    return [
        # Test Case 1: Contextual Understanding
        [
            {"role": "user", "content": "I'm planning a trip to Japan."},
            {"role": "user", "content": "What's the best time to visit?"},
            {"role": "user", "content": "I want to see cherry blossoms."},
            {"role": "user", "content": "What cities should I visit for that?"}
        ],
        # Test Case 2: Knowledge Retention
        [
            {"role": "user", "content": "My name is Alex and I work as a software engineer."},
            {"role": "user", "content": "I'm interested in learning about machine learning."},
            {"role": "user", "content": "What resources would you recommend for someone with my background?"},
            {"role": "user", "content": "Remember, I mentioned my profession earlier - what's relevant to that?"}
        ],
    ]


def create_deepeval_conversational_test_case(
    conversation: List[Dict[str, str]], 
    additional_metadata: dict = None
) -> ConversationalTestCase:
    """
    Convert a conversation to DeepEval's ConversationalTestCase format
    
    Args:
        conversation: List of turns with 'role' and 'content'
        additional_metadata: Optional metadata to attach to test case
        
    Returns:
        ConversationalTestCase object
    """
    from deepeval.test_case import Turn
    
    turns = [Turn(role=turn["role"], content=turn["content"]) for turn in conversation]
    
    return ConversationalTestCase(
        turns=turns,
        additional_metadata=additional_metadata or {}
    )


def create_arena_test_case_from_conversations(
    base_conversation: List[Dict[str, str]],
    finetuned_conversation: List[Dict[str, str]],
    original_input: str
) -> dict:
    """
    Create an arena test case for comparing base vs finetuned model
    
    Args:
        base_conversation: Complete conversation from base model
        finetuned_conversation: Complete conversation from finetuned model
        original_input: The original user query
        
    Returns:
        Dictionary with test case data for arena comparison
    """
    # Extract only assistant responses for comparison
    base_responses = [turn["content"] for turn in base_conversation if turn["role"] == "assistant"]
    finetuned_responses = [turn["content"] for turn in finetuned_conversation if turn["role"] == "assistant"]
    
    return {
        "input": original_input,
        "base_output": "\n\n".join(base_responses),
        "finetuned_output": "\n\n".join(finetuned_responses),
        "base_conversation": base_conversation,
        "finetuned_conversation": finetuned_conversation
    }


