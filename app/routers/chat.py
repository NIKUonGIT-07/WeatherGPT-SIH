from datetime import datetime, timedelta

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.nlu import (
    extract_city,
    detect_intent
)

from app.services.gemini_nlu import (
    understand_weather_query
)

from app.services.weather_service import (
    get_current_weather
)

from app.services.forecast_service import (
    get_forecast,
    get_forecast_day
)

from app.services.alert_service import (
    generate_weather_alerts
)

from app.services.alert_response_builder import (
    build_alert_response
)

from app.services.response_builder import (
    build_weather_response
)

from app.services.forecast_response_builder import (
    build_forecast_response,
    build_single_day_response
)

from app.services.ai_response_builder import (
    build_ai_weather_response
)

from app.services.landslide_risk_service import (
    calculate_landslide_risk
)

from app.services.landslide_response_builder import (
    build_landslide_risk_response
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str


def build_rain_response(weather: dict) -> str:

    city = weather.get(
        "city",
        "your location"
    )

    country = weather.get(
        "country",
        ""
    )

    condition = weather.get(
        "condition",
        "Unknown"
    )

    temperature = weather.get(
        "temperature",
        "N/A"
    )

    humidity = weather.get(
        "humidity",
        "N/A"
    )

    wind_speed = weather.get(
        "wind_speed",
        "N/A"
    )

    location = (
        f"{city}, {country}"
        if country
        else city
    )

    condition_text = str(
        condition
    ).lower()

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

        answer = (
            "Rain is not very likely right now."
        )

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
            "reply": (
                "Please enter a weather question."
            )
        }

    # --------------------------------------------------
    # NLU
    # --------------------------------------------------

    try:

        nlu_result = (
            understand_weather_query(
                user_message
            )
        )

        print(
            "NLU RESULT:",
            nlu_result
        )

        city = nlu_result.get(
            "city"
        )

        intent = nlu_result.get(
            "intent"
        )

        time = nlu_result.get(
            "time"
        )

        language = nlu_result.get(
            "language",
            "english"
        )

    except Exception as e:

        print(
            "NLU ROUTING ERROR:",
            repr(e)
        )

        city = extract_city(
            user_message
        )

        intent = detect_intent(
            user_message
        )

        time = "unspecified"

        language = "english"


    # --------------------------------------------------
    # CITY FALLBACK
    # --------------------------------------------------

    if not city:

        city = extract_city(
            user_message
        )


    if not city:

        return {
            "reply": (
                "Sorry, I couldn't identify the city "
                "in your message. Try asking: "
                "What's the weather in Guwahati?"
            )
        }


    # --------------------------------------------------
    # WEATHER ALERTS
    # --------------------------------------------------

    if intent == "alerts":

        weather = get_current_weather(
            city
        )

        if "error" in weather:

            return {
                "reply": weather["error"]
            }

        alerts = generate_weather_alerts(
            weather
        )

        alert_text = build_alert_response(
            city=weather.get(
                "city",
                city
            ),
            country=weather.get(
                "country",
                ""
            ),
            alerts=alerts
        )

        ai_reply = build_ai_weather_response(
            user_message,
            alert_text,
            language
        )

        return {
            "reply": ai_reply
        }


    # --------------------------------------------------
    # LANDSLIDE RISK
    # --------------------------------------------------

    if intent == "landslide_risk":

        current_weather = get_current_weather(
            city
        )

        if "error" in current_weather:

            return {
                "reply": current_weather["error"]
            }

        forecast = get_forecast(
            city
        )

        if "error" in forecast:

            return {
                "reply": forecast["error"]
            }

        risk = calculate_landslide_risk(
            forecast=forecast,
            current_weather=current_weather
        )

        risk_text = build_landslide_risk_response(
            city=current_weather.get(
                "city",
                city
            ),
            country=current_weather.get(
                "country",
                ""
            ),
            risk=risk
        )

        ai_reply = build_ai_weather_response(
            user_message,
            risk_text,
            language
        )

        return {
            "reply": ai_reply
        }


    # --------------------------------------------------
    # TOMORROW
    # --------------------------------------------------

    if time == "tomorrow":

        forecast = get_forecast(
            city
        )

        if "error" in forecast:

            return {
                "reply": forecast["error"]
            }

        tomorrow_date = (
            datetime.now()
            + timedelta(days=1)
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
            forecast_text,
            language
        )

        return {
            "reply": ai_reply
        }


    # --------------------------------------------------
    # TONIGHT
    # --------------------------------------------------

    if time == "tonight":

        weather = get_current_weather(
            city
        )

        if "error" in weather:

            return {
                "reply": weather["error"]
            }

        normal_reply = build_weather_response(
            weather
        )

        ai_reply = build_ai_weather_response(
            user_message,
            normal_reply,
            language
        )

        return {
            "reply": ai_reply
        }


    # --------------------------------------------------
    # THIS WEEK
    # --------------------------------------------------

    if time == "this_week":

        forecast = get_forecast(
            city
        )

        if "error" in forecast:

            return {
                "reply": forecast["error"]
            }

        forecast_text = build_forecast_response(
            forecast
        )

        ai_reply = build_ai_weather_response(
            user_message,
            forecast_text,
            language
        )

        return {
            "reply": ai_reply
        }


    # --------------------------------------------------
    # NEXT WEEK
    # --------------------------------------------------

    if time == "next_week":

        return {
            "reply": (
                "Sorry, next week's forecast is "
                "not available yet. I currently "
                "provide a 5-day forecast."
            )
        }


    # --------------------------------------------------
    # FORECAST
    # --------------------------------------------------

    if intent == "forecast":

        forecast = get_forecast(
            city
        )

        if "error" in forecast:

            return {
                "reply": forecast["error"]
            }

        forecast_text = build_forecast_response(
            forecast
        )

        ai_reply = build_ai_weather_response(
            user_message,
            forecast_text,
            language
        )

        return {
            "reply": ai_reply
        }


    # --------------------------------------------------
    # CURRENT WEATHER / OTHER WEATHER INTENTS
    # --------------------------------------------------

    if intent in [
        "current_weather",
        "rain",
        "temperature",
        "humidity",
        "wind",
        "weather_advice"
    ]:

        weather = get_current_weather(
            city
        )

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
            normal_reply,
            language
        )

        return {
            "reply": ai_reply
        }


    # --------------------------------------------------
    # UNKNOWN INTENT
    # --------------------------------------------------

    return {
        "reply": (
            "Sorry, I couldn't understand your request. "
            "Try asking about the weather, temperature, "
            "rain, humidity, wind, alerts, forecast, "
            "or landslide risk."
        )
    }