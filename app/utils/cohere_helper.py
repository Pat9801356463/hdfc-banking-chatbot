import os
import time
import cohere
from dotenv import load_dotenv

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

def safe_generate_cohere(prompt, retries=3, delay=2.5, model="command-r-plus"):
    """
    Calls Cohere Command-R+ API with retry logic.
    """
    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            print(f"[Cohere] Attempt {attempt}")
            response = co.generate(
                model=model,
                prompt=prompt,
                max_tokens=800,
                temperature=0.5,
                stop_sequences=["\n\n"],
            )
            return response.generations[0].text.strip()
        except Exception as e:
            last_exception = e
            time.sleep(delay * attempt)

    return f"⚠️ Cohere failed after retries. Last error: {last_exception}"
