import os
from dotenv import load_dotenv
from google import genai

# Force load_dotenv to override existing environment variables
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Print the last 4 characters to confirm which key Python is actually loading
print(f"Loaded Key Ending In: ...{api_key[-4:] if api_key else 'NONE'}")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing in the .env file.")

client = genai.Client(api_key=api_key)

try:
    print("Connecting to Gemini...")
    response = client.models.generate_content(
        model=model_name,
        contents="Explain python variables in one simple sentence."
    )
    print("\nGemini API connection successful!")
    print("Model:", model_name)
    print("Response:", response.text)
except Exception as error:
    print("\nGemini API request failed")
    print("Error type:", type(error).__name__)
    print("Details:", str(error))