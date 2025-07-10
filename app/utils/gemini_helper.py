# utils/gemini_helper.py

import time
import google.generativeai as genai

def safe_generate_content(model, prompt, retries=3, delay=2.5):
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            if "429" in str(e) or "503" in str(e) or "timeout" in str(e).lower():
                time.sleep(delay * (attempt + 1))  # exponential backoff
                continue
            return f"⚠️ Gemini API error: {e}"
    return "⚠️ Gemini failed after retries."
