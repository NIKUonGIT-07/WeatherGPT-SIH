import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def understand_weather_query(message: str) -> dict:

    prompt = f"""
You are the Natural Language Understanding system for WeatherGPT.

Your task is to analyze a user's weather-related question and extract
four pieces of information:

- city
- intent
- time
- language

USER QUESTION:
"{message}"

CITY EXTRACTION:
- Find the location/place/city mentioned by the user.
- The city can appear anywhere in the sentence.
- Examples:
  "What's the weather in Guwahati?" -> "Guwahati"
  "Weather at Delhi" -> "Delhi"
  "How is Mumbai weather?" -> "Mumbai"
  "Tell me about Kolkata" -> "Kolkata"
- Return ONLY the city name.
- Do not include words such as "weather", "today", "tomorrow",
  "forecast", "rain", etc.
- If there is genuinely no location in the question, return null.

INTENT:
Choose exactly one:

- current_weather
- forecast
- rain
- temperature
- humidity
- wind
- weather_advice

TIME:
Choose exactly one:

- today
- tomorrow
- tonight
- this_week
- next_week
- unspecified

LANGUAGE:
Identify the language used by the user.

Choose exactly one:

- english
- hindi
- assamese
- bengali
- other

IMPORTANT:
- Detect the language of the user's actual question.
- Do not determine language from the city name.
- If the question mixes English with another language,
  choose the main language of the sentence.
- If the language is not English, Hindi, Assamese, or Bengali,
  return "other".

Examples:

Question:
"What's the weather like in Guwahati?"

Output:
{{"city": "Guwahati", "intent": "current_weather", "time": "unspecified", "language": "english"}}

Question:
"Will it rain in Guwahati tomorrow?"

Output:
{{"city": "Guwahati", "intent": "rain", "time": "tomorrow", "language": "english"}}

Question:
"दिल्ली में कल मौसम कैसा रहेगा?"

Output:
{{"city": "Delhi", "intent": "current_weather", "time": "tomorrow", "language": "hindi"}}

Question:
"গুৱাহাটীত কাইলৈ বৰষুণ হ'ব নেকি?"

Output:
{{"city": "Guwahati", "intent": "rain", "time": "tomorrow", "language": "assamese"}}

Question:
"গুৱাহাটীর আবহাওয়া কেমন?"

Output:
{{"city": "Guwahati", "intent": "current_weather", "time": "unspecified", "language": "bengali"}}

Question:
"Give me the forecast for Kolkata next week."

Output:
{{"city": "Kolkata", "intent": "forecast", "time": "next_week", "language": "english"}}

Return ONLY valid JSON.
Do not add explanations or markdown.

JSON format:
{{
    "city": "city name or null",
    "intent": "one allowed intent",
    "time": "one allowed time value",
    "language": "one allowed language"
}}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )
        )

        result = json.loads(response.text)

        return result

    except Exception as e:

        print("GEMINI NLU ERROR:", repr(e))

        return {
            "city": None,
            "intent": "current_weather",
            "time": "unspecified",
            "language": "english"
        }