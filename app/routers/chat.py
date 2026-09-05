from fastapi import APIRouter
from pydantic import BaseModel

from app.services.nlu import extract_city, detect_intent
from app.services.weather_service import get_current_weather
from app.services.forecast_service import get_forecast
from app.services.response_builder import build_weather_response
from app.services.forecast_response_builder import build_forecast_response
from app.services.ai_response_builder import build_ai_weather_response


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str


def is_rain_question(message: str) -> bool:
    message = message.lower()

    rain_keywords = [
        "rain",
        "raining",
        "rainfall",
        "shower",
        "drizzle",
        "umbrella"
    ]

    return any(keyword in message for keyword in rain_keywords)


def build_rain_response(weather: dict) -> str:
    city = weather.get("city", "your location")
    country = weather.get("country", "")
    condition = weather.get("condition", "Unknown")
    temperature = weather.get("temperature", "N/A")
    humidity = weather.get("humidity", "N/A")
    wind_speed = weather.get("wind_speed", "N/A")

    location = f"{city}, {country}" if country else city
    condition_text = str(condition).lower()

    rain_likely = (
        "rain" in condition_text
        or "drizzle" in condition_text
        or "shower" in condition_text
        or "thunderstorm" in condition_text
    )

    if rain_likely:
        answer = "Yes, rain or thunderstorm activity is possible today."
        advice = "Carry an umbrella or raincoat if you are going outside."
    else:
        answer = "Rain is not very likely right now."
        advice = "You probably do not need an umbrella, but check again before travelling."

    return f"""
Rain Check
────────────────────────

Location : {location}

Answer
• {answer}

Current Weather
• Condition   : {condition}
• Temperature : {temperature} °C
• Humidity    : {humidity} %
• Wind Speed  : {wind_speed} km/h

Simple Advice
• {advice}

Source
• Provider : Open-Meteo
• Status   : Live Weather Data
"""


@router.post("/")
def chat(request: ChatRequest):
    user_message = request.message

    city = extract_city(user_message)

    if not city:
        return {
            "reply": "Sorry, I couldn't identify the city in your message. Try asking: Will it rain today in Guwahati?"
        }

    if is_rain_question(user_message):
        weather = get_current_weather(city)

        if "error" in weather:
            return {
                "reply": weather["error"]
            }

        normal_reply = build_rain_response(weather)

        ai_reply = build_ai_weather_response(user_message, normal_reply)

        return {
            "reply": ai_reply
        }

    intent = detect_intent(user_message)

    if intent == "current_weather":
        weather = get_current_weather(city)

        if "error" in weather:
            return {
                "reply": weather["error"]
            }

        return {
            "reply": build_weather_response(weather)
        }

    elif intent == "forecast":
        forecast = get_forecast(city)

        if "error" in forecast:
            return {
                "reply": forecast["error"]
            }

        return {
            "reply": build_forecast_response(forecast)
        }

    return {
        "reply": "Sorry, I couldn't understand your request. Try: Weather in Guwahati, Forecast in Guwahati, or Will it rain today in Guwahati?"
    }