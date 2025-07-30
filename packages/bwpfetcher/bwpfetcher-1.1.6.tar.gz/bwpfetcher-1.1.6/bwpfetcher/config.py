import os
from dotenv import load_dotenv; load_dotenv()


def get_api_key() -> str:
    """
    Make sure you import the following before running any api functions: 

    >>> from dotenv import load_dotenv; load_dotenv()

    This will make sure the API_KEY is loaded from your own .env file.
    """
    api_key = os.getenv("API_KEY")

    if not api_key:
        raise ValueError("Missing API_KEY. Set it via environment variable or constructor.")
    
    return api_key