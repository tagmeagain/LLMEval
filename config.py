"""
Configuration file for base and finetuned models
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Base Model Configuration
BASE_MODEL = {
    "name": "gpt-4.1-nano",  # Base model
    "api_key": OPENAI_API_KEY,
    "temperature": 0.7,
    "max_tokens": 500
}

# Finetuned Model Configuration
FINETUNED_MODEL = {
    "name": "gpt-4.1-nano",  # Finetuned model (using same model for testing)
    "api_key": OPENAI_API_KEY,
    "temperature": 0.7,
    "max_tokens": 500
}

# You can also use custom models from other providers
# CUSTOM_BASE_MODEL = {
#     "name": "custom-base",
#     "api_base": "http://localhost:8000/v1",
#     "api_key": "your-key"
# }


