import os
import tiktoken
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")

class TokenUtils:
    @staticmethod
    def truncate_to_10000_tokens(prompt: str) -> str:
        """Truncate a prompt to 10,000 tokens using tiktoken."""
        model_name = MODEL_NAME
        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(prompt)

        if len(tokens) > 10000:
            tokens = tokens[:10000]
        return encoding.decode(tokens)
    
    @staticmethod
    def token_count(prompt: str):
        """ Get token cound for prompt"""
        model_name = MODEL_NAME
        encoding = tiktoken.encoding_for_model(model_name) 
        count = len(encoding.encode(prompt))
        return count