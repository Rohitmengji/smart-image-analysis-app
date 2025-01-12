# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration settings
class Config:
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
    MAX_IMAGE_SIZE = 10 * 1024 * 2064  # 10MB
    MODEL_NAME = "claude-3-sonnet-20240229"
    MAX_TOKENS = 1000  # Increased token limit for detailed analysis

    @classmethod
    def print_debug_info(cls):
        # Print first and last 4 characters of API key for verification
        api_key = cls.ANTHROPIC_API_KEY
        if api_key:
            print(f"API Key loaded (showing first 4 and last 4 chars): {api_key[:4]}...{api_key[-4:]}")
        else:
            print("No API key loaded!")