from datetime import datetime, timedelta

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.nlu import extract_city, detect_intent
from app.services.gemini_nlu import understand_weather_query

from app.services.weather_service import get_current_weather
from app.services.forecast_service import (
    get_forecast,
    get_forecast_day
)

from app.services.response_builder import build_weather_response
from app.services.forecast_response_builder import (
    build_forecast_response,
    build_single_day_response
)

from app.services.ai_response_builder import build_ai_weather_response


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str


def build_rain_response(weather: dict) -> str:

    city = weather.get("city", "your location")
    country = weather.get("country", "")
    condition = weather.get("condition", "Unknown")
    temperature = weather.get("temperature", "N/A")
    humidity = weather.get("humidity", "N/A")
    wind_speed = weather.get("wind_speed", "N/A")

    location = (
        f"{city}, {country}"
        if country
        else city
    )

    condition_text = str(condition).lower()

    rain_likely = (
        "rain" in condition_text
        or "drizzle" in condition_text
        or "shower" in condition_text
        or "thunderstorm" in condition_text
    )

    if rain_likely:

        answer = (
            "Yes, rain or thunderstorm activity "
            "is possible today."
        )

        advice = (
            "Carry an umbrella or raincoat "
            "if you are going outside."
        )

    else:

        answer = "Rain is not very likely right now."

        advice = (
            "You probably do not need an umbrella, "
            "but check again before travelling."
        )

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

    user_message = request.message.strip()

    if not user_message:

        return {
            "reply": "Please enter a weather question."
        }

    # -----------------------------------
    # Gemini NLU
    # -----------------------------------

    try:

        nlu_result = understand_weather_query(
            user_message
        )

        print("GEMINI NLU RESULT:", nlu_result)

        city = nlu_result.get("city")
        intent = nlu_result.get("intent")
        time = nlu_result.get("time")

    except Exception:

        # Fallback to rule-based NLU

        city = extract_city(user_message)
        intent = detect_intent(user_message)
        time = "unspecified"

    # -----------------------------------
    # City fallback
    # -----------------------------------

    if not city:

        city = extract_city(user_message)

    if not city:

        return {
            "reply": (
                "Sorry, I couldn't identify the city "
                "in your message. Try asking: "
                "What's the weather in Guwahati?"
            )
        }

    # ===================================
    # TOMORROW
    # ===================================

    if time == "tomorrow":

        forecast = get_forecast(city)

        if "error" in forecast:

            return {
                "reply": forecast["error"]
            }

        tomorrow_date = (
            datetime.now() + timedelta(days=1)
        ).strftime("%Y-%m-%d")

        tomorrow = get_forecast_day(
            forecast,
            tomorrow_date
        )

        if not tomorrow:

            return {
                "reply": (
                    "Sorry, tomorrow's forecast "
                    "is not available."
                )
            }

        forecast_text = build_single_day_response(
            forecast,
            tomorrow,
            "Tomorrow"
        )

        ai_reply = build_ai_weather_response(
            user_message,
            forecast_text
        )

        return {
            "reply": ai_reply
        }

    # ===================================
    # TONIGHT
    # ===================================

    if time == "tonight":

        weather = get_current_weather(city)

        if "error" in weather:

            return {
                "reply": weather["error"]
            }

        normal_reply = build_weather_response(
            weather
        )

        ai_reply = build_ai_weather_response(
            user_message,
            normal_reply
        )

        return {
            "reply": ai_reply
        }

    # ===================================
    # THIS WEEK
    # ===================================

    if time == "this_week":

        forecast = get_forecast(city)

        if "error" in forecast:

            return {
                "reply": forecast["error"]
            }

        forecast_text = build_forecast_response(
            forecast
        )

        ai_reply = build_ai_weather_response(
            user_message,
            forecast_text
        )

        return {
            "reply": ai_reply
        }

    # ===================================
    # NEXT WEEK
    # ===================================

    if time == "next_week":

        return {
            "reply": (
                "Sorry, next week's forecast is "
                "not available yet. I currently "
                "provide a 5-day forecast."
            )
        }

    # ===================================
    # FULL FORECAST
    # ===================================

    if intent == "forecast":

        forecast = get_forecast(city)

        if "error" in forecast:

            return {
                "reply": forecast["error"]
            }

        forecast_text = build_forecast_response(
            forecast
        )

        ai_reply = build_ai_weather_response(
            user_message,
            forecast_text
        )

        return {
            "reply": ai_reply
        }

    # ===================================
    # CURRENT WEATHER
    # ===================================

    if intent in [
        "current_weather",
        "rain",
        "temperature",
        "humidity",
        "wind",
        "weather_advice"
    ]:

        weather = get_current_weather(city)

        if "error" in weather:

            return {
                "reply": weather["error"]
            }

        if intent == "rain":

            normal_reply = build_rain_response(
                weather
            )

        else:

            normal_reply = build_weather_response(
                weather
            )

        ai_reply = build_ai_weather_response(
            user_message,
            normal_reply
        )

        return {
            "reply": ai_reply
        }

    # ===================================
    # UNKNOWN
    # ===================================

    return {
        "reply": (
            "Sorry, I couldn't understand your request. "
            "Try asking about the weather, temperature, "
            "rain, humidity, wind, or forecast."
        )
    }