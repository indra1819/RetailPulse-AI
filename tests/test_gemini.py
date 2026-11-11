import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

print("API Key Loaded:", bool(API_KEY))
print("Model:", MODEL)

if not API_KEY:
    raise ValueError("API key missing")

if not MODEL:
    raise ValueError("Model missing")

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model=MODEL,
    contents="Explain retail sales analysis in simple words."
)

print("\nGemini Response:")
print(response.text)