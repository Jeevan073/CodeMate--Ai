
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OpenRouter API key missing")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

try:
    response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        messages=[
            {
                "role": "user",
                "content": "Write a Python program to add two numbers."
            }
        ],
        temperature=0.2
    )

    print("OPENROUTER SUCCESS!")
    print(response.choices[0].message.content)

except Exception as e:
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR DETAILS:", str(e))
