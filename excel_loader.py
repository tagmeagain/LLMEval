"""
Excel Loader for Multi-Turn Conversation Testing
Loads test data from Excel files with Model A and Model B responses
Converts to DeepEval's ConversationalTestCase format
"""
import pandas as pd
from typing import List, Dict, Tuple
import json
from deepeval.test_case import ConversationalTestCase, Turn


class ExcelConversationLoader:
    """
    Load multi-turn conversations from Excel files
    
    Expected Excel Format:
    - Column A: Turn Number (1, 2, 3, etc.)
    - Column B: Initial Conversation Context (optional, only in first row)
    - Column C: User Query
    - Column D: Model A Response (Base Model)
    - Column E: Model B Response (Finetuned Model)
    """
    
    def __init__(self, excel_path: str):
        """
        Initialize loader with Excel file path
        
        Args:
            excel_path: Path to Excel file (.xlsx or .xls)
        """
        self.excel_path = excel_path
        self.df = None
        
    def load_data(self, sheet_name: str = 0) -> pd.DataFrame:
        """
        Load data from Excel file
        
        Args:
            sheet_name: Sheet name or index (default: 0 for first sheet)
            
        Returns:
            DataFrame with conversation data
        """
        self.df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
        return self.df
    
    def parse_conversation_from_excel(
        self, 
        turn_col: str = "Turn",
        context_col: str = "Initial Conversation",
        user_query_col: str = "User Query",
        model_a_col: str = "Model A Response",
        model_b_col: str = "Model B Response",
        scenario_col: str = "Scenario",
        expected_outcome_col: str = "Expected Outcome",
        chatbot_role_col: str = "Chatbot Role"
    ) -> Tuple[ConversationalTestCase, ConversationalTestCase]:
        """
        Parse Excel data into DeepEval ConversationalTestCase format for both models
        
        Args:
            turn_col: Column name for turn number
            context_col: Column name for initial context
            user_query_col: Column name for user queries
            model_a_col: Column name for Model A (base) responses
            model_b_col: Column name for Model B (finetuned) responses
            scenario_col: Column name for scenario description (optional)
            expected_outcome_col: Column name for expected outcome (optional)
            chatbot_role_col: Column name for chatbot role (optional)
            
        Returns:
            Tuple of (model_a_test_case, model_b_test_case)
            Each is a ConversationalTestCase with Turn objects
        """
        if self.df is None:
            self.load_data()
        
        model_a_turns = []
        model_b_turns = []
        
        # Extract optional metadata from first row
        context = None
        scenario = None
        expected_outcome = None
        chatbot_role = None
        initial_conversation_json = None
        
        if context_col in self.df.columns and pd.notna(self.df.iloc[0][context_col]):
            context_val = str(self.df.iloc[0][context_col]).strip()
            if context_val:
                # Check if it's JSON (initial conversation) or plain text (system prompt)
                try:
                    import json as json_lib
                    initial_conversation_json = json_lib.loads(context_val)
                except (json_lib.JSONDecodeError, ValueError):
                    # Not JSON, treat as plain text context
                    context = [context_val]
        
        if scenario_col in self.df.columns and pd.notna(self.df.iloc[0][scenario_col]):
            scenario = str(self.df.iloc[0][scenario_col]).strip()
        
        if expected_outcome_col in self.df.columns and pd.notna(self.df.iloc[0][expected_outcome_col]):
            expected_outcome = str(self.df.iloc[0][expected_outcome_col]).strip()
            
        if chatbot_role_col in self.df.columns and pd.notna(self.df.iloc[0][chatbot_role_col]):
            chatbot_role = str(self.df.iloc[0][chatbot_role_col]).strip()
        
        # Add initial conversation turns if provided as JSON
        if initial_conversation_json:
            for turn_data in initial_conversation_json:
                turn = Turn(
                    role=turn_data.get("role", "user"),
                    content=turn_data.get("content", "")
                )
                model_a_turns.append(turn)
                model_b_turns.append(turn)
        
        # Parse each turn
        for idx, row in self.df.iterrows():
            # Skip empty rows
            if pd.isna(row[user_query_col]):
                continue
                
            user_query = str(row[user_query_col]).strip()
            model_a_response = str(row[model_a_col]).strip() if pd.notna(row[model_a_col]) else ""
            model_b_response = str(row[model_b_col]).strip() if pd.notna(row[model_b_col]) else ""
            
            # Add user turn and assistant turn for Model A
            if user_query:
                model_a_turns.append(Turn(role="user", content=user_query))
                if model_a_response:
                    model_a_turns.append(Turn(role="assistant", content=model_a_response))
            
            # Add user turn and assistant turn for Model B
            if user_query:
                model_b_turns.append(Turn(role="user", content=user_query))
                if model_b_response:
                    model_b_turns.append(Turn(role="assistant", content=model_b_response))
        
        # Create ConversationalTestCase for both models
        model_a_test_case = ConversationalTestCase(
            turns=model_a_turns,
            context=context,
            scenario=scenario,
            expected_outcome=expected_outcome,
            chatbot_role=chatbot_role
        )
        
        model_b_test_case = ConversationalTestCase(
            turns=model_b_turns,
            context=context,
            scenario=scenario,
            expected_outcome=expected_outcome,
            chatbot_role=chatbot_role
        )
        
        return model_a_test_case, model_b_test_case
    
    def load_multiple_conversations(
        self,
        sheet_names: List[str] = None,
        **column_mappings
    ) -> List[Tuple[List[Dict[str, str]], List[Dict[str, str]]]]:
        """
        Load multiple conversations from multiple sheets
        
        Args:
            sheet_names: List of sheet names to load (None = all sheets)
            **column_mappings: Column name mappings (same as parse_conversation_from_excel)
            
        Returns:
            List of conversation tuples (model_a_conversation, model_b_conversation)
        """
        excel_file = pd.ExcelFile(self.excel_path)
        
        if sheet_names is None:
            sheet_names = excel_file.sheet_names
        
        all_conversations = []
        
        for sheet in sheet_names:
            self.load_data(sheet_name=sheet)
            conversations = self.parse_conversation_from_excel(**column_mappings)
            all_conversations.append(conversations)
        
        return all_conversations
    
    def extract_user_turns_only(
        self,
        user_query_col: str = "User Query"
    ) -> List[Dict[str, str]]:
        """
        Extract only user turns for generating new model responses
        (Use when you want to generate fresh responses instead of using pre-recorded ones)
        
        Args:
            user_query_col: Column name for user queries
            
        Returns:
            List of user turns in format [{"role": "user", "content": "..."}]
        """
        if self.df is None:
            self.load_data()
        
        user_turns = []
        
        for idx, row in self.df.iterrows():
            if pd.notna(row[user_query_col]):
                user_query = str(row[user_query_col]).strip()
                if user_query:
                    user_turns.append({
                        "role": "user",
                        "content": user_query
                    })
        
        return user_turns
    
    def save_test_cases_to_json(
        self,
        output_path: str,
        model_a_test_case: ConversationalTestCase,
        model_b_test_case: ConversationalTestCase
    ):
        """
        Save parsed test cases to JSON for inspection
        
        Args:
            output_path: Path to save JSON file
            model_a_test_case: Model A ConversationalTestCase
            model_b_test_case: Model B ConversationalTestCase
        """
        data = {
            "model_a_test_case": {
                "turns": [{"role": t.role, "content": t.content} for t in model_a_test_case.turns],
                "context": model_a_test_case.context,
                "scenario": model_a_test_case.scenario,
                "expected_outcome": model_a_test_case.expected_outcome,
                "chatbot_role": model_a_test_case.chatbot_role
            },
            "model_b_test_case": {
                "turns": [{"role": t.role, "content": t.content} for t in model_b_test_case.turns],
                "context": model_b_test_case.context,
                "scenario": model_b_test_case.scenario,
                "expected_outcome": model_b_test_case.expected_outcome,
                "chatbot_role": model_b_test_case.chatbot_role
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Test cases saved to {output_path}")


def load_excel_test_cases(
    excel_path: str,
    mode: str = "use_existing_responses"
) -> dict:
    """
    Convenience function to load test cases from Excel
    
    Args:
        excel_path: Path to Excel file
        mode: "use_existing_responses" or "generate_new_responses"
            - use_existing_responses: Use Model A/B responses from Excel
            - generate_new_responses: Only extract user queries, generate new responses
            
    Returns:
        Dictionary with loaded data
    """
    loader = ExcelConversationLoader(excel_path)
    loader.load_data()
    
    if mode == "use_existing_responses":
        model_a_conv, model_b_conv = loader.parse_conversation_from_excel()
        return {
            "mode": "existing_responses",
            "model_a_conversation": model_a_conv,
            "model_b_conversation": model_b_conv
        }
    elif mode == "generate_new_responses":
        user_turns = loader.extract_user_turns_only()
        return {
            "mode": "generate_new",
            "user_turns": user_turns
        }
    else:
        raise ValueError(f"Invalid mode: {mode}. Use 'use_existing_responses' or 'generate_new_responses'")


# Example usage
if __name__ == "__main__":
    # Example: Load conversations from Excel
    loader = ExcelConversationLoader("test_conversations.xlsx")
    
    # Load as ConversationalTestCase objects
    model_a_test_case, model_b_test_case = loader.parse_conversation_from_excel()
    
    print("Model A Test Case:")
    print(f"  Scenario: {model_a_test_case.scenario}")
    print(f"  Turns: {len(model_a_test_case.turns)}")
    for turn in model_a_test_case.turns[:4]:
        print(f"    {turn.role}: {turn.content[:80]}...")
    
    print("\nModel B Test Case:")
    print(f"  Scenario: {model_b_test_case.scenario}")
    print(f"  Turns: {len(model_b_test_case.turns)}")
    for turn in model_b_test_case.turns[:4]:
        print(f"    {turn.role}: {turn.content[:80]}...")
    
    # Save to JSON for inspection
    loader.save_test_cases_to_json(
        "parsed_test_cases.json",
        model_a_test_case,
        model_b_test_case
    )

