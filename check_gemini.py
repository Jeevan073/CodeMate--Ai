
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: Gemini API key not found")
    raise SystemExit(1)

try:
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Write a Python program to add two numbers."
    )

    print("SUCCESS: Gemini API is working!")
    print(response.text)

except Exception as e:
    print("GEMINI ERROR TYPE:", type(e).__name__)
    print("GEMINI ERROR DETAILS:", str(e))
