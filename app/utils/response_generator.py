# utils/response_generator.py

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API with secure API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Choose your model: "gemini-1.5-pro" for depth, "gemini-1.5-flash" for speed
MODEL_NAME = "gemini-1.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

def generate_final_answer(query, context, user_name=None):
    prompt = f"""
You are a highly informative and polite banking assistant for HDFC Bank.

Always provide structured, clear responses of **at least 4–6 sentences**, using the provided document context.
Be professional, friendly, and helpful in tone.

User: {user_name if user_name else 'a customer'}
Query: "{query}"

📄 Document Context:
{context}

Please now generate a detailed, helpful response addressing the query.
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Gemini API error: {e}"
