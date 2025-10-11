"""
Model wrapper to handle both base and finetuned models
"""
from typing import List, Dict
import openai


class ModelWrapper:
    """Wrapper class to handle model inference"""
    
    def __init__(self, model_config: dict):
        self.model_name = model_config["name"]
        self.api_key = model_config["api_key"]
        self.temperature = model_config.get("temperature", 0.7)
        self.max_tokens = model_config.get("max_tokens", 500)
        self.api_base = model_config.get("api_base", None)
        
        # Set up OpenAI client
        if self.api_base:
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.api_base)
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response given a list of messages
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            
        Returns:
            The model's response as a string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response with {self.model_name}: {e}")
            return f"Error: {str(e)}"
    
    def generate_multi_turn_conversation(self, turns: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Generate responses for a multi-turn conversation
        
        Args:
            turns: List of conversation turns. Each turn should have 'role' and 'content'.
                  Only provide 'user' turns, the assistant turns will be generated.
        
        Returns:
            Complete conversation including generated assistant responses
        """
        conversation = []
        messages = []
        
        for turn in turns:
            if turn["role"] == "user":
                # Add user message
                messages.append({"role": "user", "content": turn["content"]})
                conversation.append(turn)
                
                # Generate assistant response
                assistant_response = self.generate_response(messages)
                assistant_turn = {"role": "assistant", "content": assistant_response}
                messages.append(assistant_turn)
                conversation.append(assistant_turn)
            else:
                # If assistant turn is provided in input, use it instead
                messages.append(turn)
                conversation.append(turn)
        
        return conversation


