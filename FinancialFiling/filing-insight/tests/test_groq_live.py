"""
test_groq_live.py
-----------------
Helper script to test live Groq API connectivity and verify answer generation.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from groq import Groq
from backend.config import GROQ_MODEL, GROQ_API_KEY_ENV_VAR

load_dotenv()


def check_groq_connection(api_key: str = None) -> bool:
    key = api_key or os.environ.get(GROQ_API_KEY_ENV_VAR)
    if not key:
        print("STATUS: NO_KEY_FOUND")
        print(f"Please set {GROQ_API_KEY_ENV_VAR} in your environment or in a .env file, or enter it in the Streamlit UI.")
        return False

    print(f"Testing Groq API key: {key[:6]}...{key[-4:] if len(key) > 10 else ''}")
    try:
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful financial assistant."},
                {"role": "user", "content": "Respond with 'GROQ_API_ACTIVE' if you receive this message."},
            ],
            max_tokens=20,
            temperature=0.0,
        )
        content = response.choices[0].message.content.strip()
        print(f"Groq API Response: {content}")
        print("STATUS: LIVE_AND_OPERATIONAL")
        return True
    except Exception as e:
        print(f"Groq API Connection Error: {e}")
        print("STATUS: ERROR")
        return False


if __name__ == "__main__":
    provided_key = sys.argv[1] if len(sys.argv) > 1 else None
    check_groq_connection(provided_key)
