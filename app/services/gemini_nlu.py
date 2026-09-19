import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.nlu import fallback_understand_weather_query


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
- Return ONLY the city name.
- Do not include words such as "weather", "today", "tomorrow",
  "forecast", "rain", "alert", "warning", "landslide", etc.
- If there is genuinely no location in the question, return null.

Examples:

"What's the weather in Guwahati?"
-> "Guwahati"

"Weather at Delhi"
-> "Delhi"

"How is Mumbai weather?"
-> "Mumbai"

"Tell me about Kolkata"
-> "Kolkata"

"गुवाहाटी में मौसम कैसा है?"
-> "Guwahati"

"গুৱাহাটীৰ বতৰ কেনেকুৱা?"
-> "Guwahati"

"গুয়াহাটির আবহাওয়া কেমন?"
-> "Guwahati"


INTENT:

Choose exactly ONE:

- current_weather
- forecast
- rain
- temperature
- humidity
- wind
- weather_advice
- alerts
- landslide_risk


IMPORTANT INTENT RULES:


1. ALERTS

Use "alerts" when the user asks whether there are:

- weather alerts
- weather warnings
- warnings
- dangerous weather
- severe weather alerts
- severe weather warnings
- weather advisories
- current weather warnings

Examples:

"Are there any weather alerts in Guwahati?"
-> alerts

"Is there any warning for Guwahati?"
-> alerts

"Does Guwahati have any severe weather warnings?"
-> alerts

"Are there dangerous weather conditions in Guwahati?"
-> alerts

"Any weather advisory for Guwahati?"
-> alerts


2. LANDSLIDE RISK

Use "landslide_risk" when the user asks about:

- landslide risk
- landslides
- landslide danger
- possibility of landslides
- landslide-prone conditions
- risk of a landslide
- whether rainfall could cause landslides
- whether weather conditions indicate landslide risk

Examples:

"Is there a landslide risk in Guwahati?"
-> landslide_risk

"Could there be landslides in Guwahati?"
-> landslide_risk

"Is Guwahati at risk of landslides?"
-> landslide_risk

"Is there a landslide danger in Guwahati?"
-> landslide_risk

"Can heavy rain cause landslides in Guwahati?"
-> landslide_risk

"गुवाहाटी में भूस्खलन का खतरा है क्या?"
-> landslide_risk

"গুৱাহাটীত ভূমিস্খলনৰ আশংকা আছে নেকি?"
-> landslide_risk

"গুয়াহাটিতে ভূমিধসের ঝুঁকি আছে কি?"
-> landslide_risk


IMPORTANT:

If the user asks specifically about landslides,
choose "landslide_risk" even if words such as
"rain", "rainfall", or "weather" also appear.

For example:

"Can heavy rain cause landslides?"
-> landslide_risk

NOT:

rain


3. WEATHER ADVICE

Use "weather_advice" when the user asks what they personally
should do because of the weather.

Examples:

"Should I carry an umbrella?"
-> weather_advice

"Is it safe to go outside?"
-> weather_advice

"What should I wear today?"
-> weather_advice

"Should I avoid going outside?"
-> weather_advice


IMPORTANT:

Do NOT classify a question as weather_advice if it asks
about an official or general weather warning.

"Are there any weather alerts?"
-> alerts

"Should I carry an umbrella?"
-> weather_advice


4. FORECAST

Use "forecast" when the user asks for a future weather forecast.

Examples:

"Give me the forecast for Kolkata."
-> forecast

"What's the weather forecast?"
-> forecast

"How will the weather be this week?"
-> forecast


5. RAIN

Use "rain" when the user specifically asks about rain.

Examples:

"Will it rain in Guwahati?"
-> rain

"Is it raining in Delhi?"
-> rain


6. TEMPERATURE

Use "temperature" when the user specifically asks about temperature.

Examples:

"What is the temperature in Guwahati?"
-> temperature

"How hot is Delhi?"
-> temperature


7. HUMIDITY

Use "humidity" when the user asks about humidity.

Examples:

"What is the humidity in Guwahati?"
-> humidity


8. WIND

Use "wind" when the user asks about wind or wind speed.

Examples:

"How strong is the wind in Guwahati?"
-> wind


TIME:

Choose exactly ONE:

- today
- tomorrow
- tonight
- this_week
- next_week
- unspecified


Examples:

"Weather in Guwahati today"
-> today

"Will it rain in Guwahati tomorrow?"
-> tomorrow

"How will the weather be tonight?"
-> tonight

"Weather this week"
-> this_week

"Forecast next week"
-> next_week


LANGUAGE:

Identify the language used by the user's actual question.

Choose exactly ONE:

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
{{
    "city": "Guwahati",
    "intent": "current_weather",
    "time": "unspecified",
    "language": "english"
}}


Question:
"Will it rain in Guwahati tomorrow?"

Output:
{{
    "city": "Guwahati",
    "intent": "rain",
    "time": "tomorrow",
    "language": "english"
}}


Question:
"दिल्ली में कल मौसम कैसा रहेगा?"

Output:
{{
    "city": "Delhi",
    "intent": "current_weather",
    "time": "tomorrow",
    "language": "hindi"
}}


Question:
"गुवाहाटी में कोई मौसम चेतावनी है?"

Output:
{{
    "city": "Guwahati",
    "intent": "alerts",
    "time": "unspecified",
    "language": "hindi"
}}


Question:
"गुवाहाटी में भूस्खलन का खतरा है क्या?"

Output:
{{
    "city": "Guwahati",
    "intent": "landslide_risk",
    "time": "unspecified",
    "language": "hindi"
}}


Question:
"গুৱাহাটীত কোনো বতৰৰ সতৰ্কবাণী আছে নেকি?"

Output:
{{
    "city": "Guwahati",
    "intent": "alerts",
    "time": "unspecified",
    "language": "assamese"
}}


Question:
"গুৱাহাটীত ভূমিস্খলনৰ আশংকা আছে নেকি?"

Output:
{{
    "city": "Guwahati",
    "intent": "landslide_risk",
    "time": "unspecified",
    "language": "assamese"
}}


Question:
"গুয়াহাটিতে ভূমিধসের ঝুঁকি আছে কি?"

Output:
{{
    "city": "Guwahati",
    "intent": "landslide_risk",
    "time": "unspecified",
    "language": "bengali"
}}


Question:
"Should I carry an umbrella in Guwahati?"

Output:
{{
    "city": "Guwahati",
    "intent": "weather_advice",
    "time": "unspecified",
    "language": "english"
}}


Question:
"Is there a landslide risk in Guwahati?"

Output:
{{
    "city": "Guwahati",
    "intent": "landslide_risk",
    "time": "unspecified",
    "language": "english"
}}


IMPORTANT OUTPUT RULE:

Return ONLY valid JSON.

Do not add explanations.
Do not add markdown.
Do not add code fences.

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
                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                )
            )
        )

        result = json.loads(response.text)

        # Validate expected fields.
        allowed_intents = {
            "current_weather",
            "forecast",
            "rain",
            "temperature",
            "humidity",
            "wind",
            "weather_advice",
            "alerts",
            "landslide_risk"
        }

        allowed_times = {
            "today",
            "tomorrow",
            "tonight",
            "this_week",
            "next_week",
            "unspecified"
        }

        allowed_languages = {
            "english",
            "hindi",
            "assamese",
            "bengali",
            "other"
        }

        if result.get("intent") not in allowed_intents:
            raise ValueError(
                "Gemini returned an invalid intent"
            )

        if result.get("time") not in allowed_times:
            raise ValueError(
                "Gemini returned an invalid time"
            )

        if result.get("language") not in allowed_languages:
            raise ValueError(
                "Gemini returned an invalid language"
            )

        return result

    except Exception as e:

        print(
            "GEMINI NLU ERROR:",
            repr(e)
        )

        # Multilingual deterministic fallback.
        fallback_result = (
            fallback_understand_weather_query(message)
        )

        print(
            "FALLBACK NLU RESULT:",
            fallback_result
        )

        return fallback_result