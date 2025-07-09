import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load model
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_final_answer(query, context, user_name=None):
    prompt = f"""
You are a helpful banking assistant for HDFC Bank.

User: {user_name if user_name else 'a customer'}
Query: "{query}"

Based on the following context extracted from documents:
{context}

Respond clearly, politely, and concisely to the user.
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Gemini API error: {e}"
