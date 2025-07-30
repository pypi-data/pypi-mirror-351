import os
from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str:
    api_key = os.getenv("API_KEY")

    if not api_key:
        raise ValueError("Missing API_KEY. Set it via environment variable or constructor.")
    
    return api_key