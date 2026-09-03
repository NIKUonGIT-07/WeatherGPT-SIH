from fastapi import APIRouter
from pydantic import BaseModel

from app.services.nlu import extract_city, detect_intent
from app.services.weather_service import get_current_weather
from app.services.forecast_service import get_forecast
from app.services.response_builder import build_weather_response

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(request: ChatRequest):

    city = extract_city(request.message)

    if not city:
        return {
            "reply": "Sorry, I couldn't identify the city in your message."
        }

    intent = detect_intent(request.message)

    # -------------------------
    # Current Weather
    # -------------------------
    if intent == "current_weather":

        weather = get_current_weather(city)

        if "error" in weather:
            return {
                "reply": weather["error"]
            }

        return {
            "reply": build_weather_response(weather)
        }

    # -------------------------
    # Forecast
    # -------------------------
    elif intent == "forecast":

        forecast = get_forecast(city)

        if "error" in forecast:
            return {
                "reply": forecast["error"]
            }

        return forecast

    # -------------------------
    # Unknown Request
    # -------------------------
    return {
        "reply": "Sorry, I couldn't understand your request."
    }