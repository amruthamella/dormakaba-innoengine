import requests
import os

# Manually read the .env file (bypasses dotenv library issues)
def load_env():
    try:
        with open(os.path.join(os.path.dirname(__file__), "../.env")) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()
    except:
        pass

load_env()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

def generate_response(prompt: str) -> str:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a world-class innovation strategist. You ONLY respond with raw valid JSON. No explanation, no markdown, no code fences. Just the JSON object."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        },
        timeout=60
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]