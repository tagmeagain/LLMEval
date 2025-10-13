"""
Excel Conversation Loader
Loads conversation data from Excel and converts to DeepEval test cases

Each ROW in Excel represents a SEPARATE conversation:
- Initial Conversation: Prior conversation turns (JSON format)
- User Query: The last user message
- Model A Response: Base model's response (optional)
- Model B Response: Finetuned model's response (optional)
"""

import pandas as pd
import json
from typing import List, Tuple
from deepeval.test_case import ConversationalTestCase, Turn


class ExcelConversationLoader:
    def __init__(self, excel_path: str):
        """Load Excel file"""
        self.excel_path = excel_path
        self.df = pd.read_excel(excel_path)
    
    def get_conversations_for_generation(self) -> List[dict]:
        """
        Extract conversations for on-the-fly generation
        
        Returns:
            List of conversation dicts, each with:
            - initial_turns: List of Turn objects from Initial Conversation
            - user_query: The last user message
            - metadata: chatbot_role, scenario, etc.
        """
        conversations = []
        
        for idx, row in self.df.iterrows():
            # Get user query
            if "User Query" not in self.df.columns or pd.isna(row["User Query"]):
                continue
            
            user_query = str(row["User Query"]).strip()
            if not user_query:
                continue
            
            # Parse initial conversation (JSON)
            initial_turns = []
            if "Initial Conversation" in self.df.columns and pd.notna(row["Initial Conversation"]):
                initial_conv_str = str(row["Initial Conversation"]).strip()
                try:
                    initial_conv_json = json.loads(initial_conv_str)
                    for turn_data in initial_conv_json:
                        role = turn_data.get("role", "user")
                        content = turn_data.get("content", "")
                        if role in ["user", "assistant"]:
                            initial_turns.append({"role": role, "content": content})
                except (json.JSONDecodeError, ValueError):
                    pass  # No initial conversation or invalid JSON
            
            # Get metadata
            metadata = {
                "chatbot_role": None,
                "scenario": None,
                "expected_outcome": None
            }
            
            if "Chatbot Role" in self.df.columns and pd.notna(row["Chatbot Role"]):
                metadata["chatbot_role"] = str(row["Chatbot Role"]).strip()
            if "Scenario" in self.df.columns and pd.notna(row["Scenario"]):
                metadata["scenario"] = str(row["Scenario"]).strip()
            if "Expected Outcome" in self.df.columns and pd.notna(row["Expected Outcome"]):
                metadata["expected_outcome"] = str(row["Expected Outcome"]).strip()
            
            conversations.append({
                "initial_turns": initial_turns,
                "user_query": user_query,
                "metadata": metadata,
                "row_index": idx
            })
        
        return conversations
    
    def get_conversations_prerecorded(self) -> List[Tuple[ConversationalTestCase, ConversationalTestCase]]:
        """
        Extract conversations with pre-recorded responses
        
        Returns:
            List of (model_a_test_case, model_b_test_case) tuples
        """
        test_cases = []
        
        for idx, row in self.df.iterrows():
            # Get user query
            if "User Query" not in self.df.columns or pd.isna(row["User Query"]):
                continue
            
            user_query = str(row["User Query"]).strip()
            if not user_query:
                continue
            
            # Get model responses
            if "Model A Response" not in self.df.columns or pd.isna(row["Model A Response"]):
                continue
            if "Model B Response" not in self.df.columns or pd.isna(row["Model B Response"]):
                continue
            
            model_a_response = str(row["Model A Response"]).strip()
            model_b_response = str(row["Model B Response"]).strip()
            
            if not model_a_response or not model_b_response:
                continue
            
            # Parse initial conversation
            initial_turns = []
            if "Initial Conversation" in self.df.columns and pd.notna(row["Initial Conversation"]):
                initial_conv_str = str(row["Initial Conversation"]).strip()
                try:
                    initial_conv_json = json.loads(initial_conv_str)
                    for turn_data in initial_conv_json:
                        role = turn_data.get("role", "user")
                        content = turn_data.get("content", "")
                        if role in ["user", "assistant"]:
                            initial_turns.append(Turn(role=role, content=content))
                except (json.JSONDecodeError, ValueError):
                    pass
            
            # Build conversation turns for Model A
            model_a_turns = initial_turns.copy()
            model_a_turns.append(Turn(role="user", content=user_query))
            model_a_turns.append(Turn(role="assistant", content=model_a_response))
            
            # Build conversation turns for Model B
            model_b_turns = initial_turns.copy()
            model_b_turns.append(Turn(role="user", content=user_query))
            model_b_turns.append(Turn(role="assistant", content=model_b_response))
            
            # Get metadata
            metadata = {}
            if "Chatbot Role" in self.df.columns and pd.notna(row["Chatbot Role"]):
                metadata["chatbot_role"] = str(row["Chatbot Role"]).strip()
            if "Scenario" in self.df.columns and pd.notna(row["Scenario"]):
                metadata["scenario"] = str(row["Scenario"]).strip()
            if "Expected Outcome" in self.df.columns and pd.notna(row["Expected Outcome"]):
                metadata["expected_outcome"] = str(row["Expected Outcome"]).strip()
            
            # Create test cases
            model_a_test_case = ConversationalTestCase(
                turns=model_a_turns,
                **metadata
            )
            
            model_b_test_case = ConversationalTestCase(
                turns=model_b_turns,
                **metadata
            )
            
            test_cases.append((model_a_test_case, model_b_test_case))
        
        return test_cases
    
    def parse_conversation_from_excel(self) -> Tuple[ConversationalTestCase, ConversationalTestCase]:
        """
        Legacy method for backward compatibility
        Returns the first conversation pair
        """
        test_cases = self.get_conversations_prerecorded()
        if test_cases:
            return test_cases[0]
        else:
            raise ValueError("No valid conversations found in Excel")
