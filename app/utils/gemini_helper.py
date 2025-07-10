# utils/gemini_helper.py

import time
import google.generativeai as genai


def safe_generate_content(model, prompt, retries=3, delay=2.5, fallback_text="⚠️ Gemini is currently unavailable."):
    """
    Calls Gemini's generate_content with retry + logging.

    Args:
        model: Gemini GenerativeModel instance
        prompt: string prompt to send
        retries: number of retry attempts
        delay: delay between retries (multiplied each retry)
        fallback_text: return this if all attempts fail

    Returns:
        string: Gemini response text or fallback/error
    """
    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            print(f"[Gemini] Attempt {attempt}...")
            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            last_exception = e
            err_msg = str(e).lower()

            if "429" in err_msg or "503" in err_msg or "timeout" in err_msg:
                print(f"[Gemini Retry] Error: {e}. Retrying in {delay * attempt:.1f}s...")
                time.sleep(delay * attempt)
                continue
            else:
                print(f"[Gemini] Unrecoverable error: {e}")
                return f"⚠️ Gemini API error: {e}"

    print(f"[Gemini] Final failure after {retries} retries. Last error: {last_exception}")
    return f"{fallback_text}\n\n(Last error: {last_exception})"
