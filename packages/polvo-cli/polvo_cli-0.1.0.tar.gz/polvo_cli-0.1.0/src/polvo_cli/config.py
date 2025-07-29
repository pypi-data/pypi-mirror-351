import os
from dotenv import load_dotenv

load_dotenv()


def get_api_url() -> str:
    """Get API URL from environment or default."""
    return os.getenv("POLVO_API_URL", "http://localhost:8000") 