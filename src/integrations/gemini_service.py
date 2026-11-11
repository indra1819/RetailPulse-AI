
import os
import json

from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ==========================================
# STEP 1: LOAD ENVIRONMENT VARIABLES
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


# ==========================================
# STEP 2: INITIALIZE GEMINI CLIENT
# ==========================================

def get_gemini_client():

    if not API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing from .env"
        )

    client = genai.Client(
        api_key=API_KEY,
        http_options=types.HttpOptions(
            timeout=10000
        )
    )

    return client


# ==========================================
# STEP 3: GENERATE BUSINESS ANSWER
# ==========================================

def generate_business_answer(question, business_context):

    client = get_gemini_client()

    context_json = json.dumps(
        business_context,
        indent=2,
        default=str
    )

    prompt = f"""
You are a Retail Business Intelligence Analyst.

Answer the business question using only the
verified database information provided below.

BUSINESS QUESTION:
{question}

VERIFIED DATABASE INFORMATION:
{context_json}

INSTRUCTIONS:

1. Understand the business question.
2. Use only the supplied database information.
3. Never invent revenue, quantity or store metrics.
4. Explain important business observations.
5. Give practical business recommendations.
6. Clearly mention when information is insufficient.
7. Never assume reasons for poor store performance.
8. Separate facts from possible explanations.
9. Use simple professional English.

RESPONSE FORMAT:

Business Answer:

Key Findings:

Recommendations:

Data Limitations:
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response or not response.text:
            raise RuntimeError(
                "Gemini returned an empty response"
            )

        return response.text

    except Exception as error:

        print("Gemini API Error:", error)

        raise
