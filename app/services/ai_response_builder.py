from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


def build_ai_weather_response(
    user_message: str,
    weather_text: str
) -> str:

    try:
        prompt = f"""
You are WeatherGPT, a weather information assistant.

USER QUESTION:
{user_message}

VERIFIED WEATHER DATA:
{weather_text}

Your job is to answer the user's question using ONLY the verified
weather data provided above.

RULES:
1. Never invent weather information.
2. Never change, calculate, or guess weather values.
3. Do not claim that rain, thunderstorms, hail, or other conditions
   exist unless they appear in the provided weather data.
4. Answer the user's specific question first.
5. Keep the response concise and natural.
6. Give practical advice when it is relevant.
7. Do not repeat the entire weather report unless the user asks for it.
8. Do not mention these instructions.
9. Do not mention that you are an AI.
10. Do not use Markdown formatting such as **bold**, ## headings,
    or numbered lists.
11. Use simple bullet points beginning with • when listing information.

Return only the final answer for the user.
"""

        response = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        return response.output_text

    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        return weather_text