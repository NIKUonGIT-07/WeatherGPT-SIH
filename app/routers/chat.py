from fastapi import APIRouter
from pydantic import BaseModel

from app.services.nlu import extract_city, detect_intent

from app.services.weather_service import get_current_weather
from app.services.forecast_service import get_forecast

from app.services.response_builder import build_weather_response
from app.services.forecast_response_builder import build_forecast_response

from app.services.decision_engine import generate_decision
from app.services.decision_response_builder import build_decision_response


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(request: ChatRequest):

    intent = detect_intent(request.message)

    city = extract_city(request.message)

    if intent in [
        "current_weather",
        "forecast",
        "umbrella",
        "travel",
        "outdoor",
        "health"
    ] and not city:

        return {
            "reply": "Sorry, I couldn't identify the city in your message."
        }

    # -----------------------------
    # Forecast
    # -----------------------------

    if intent == "forecast":

        forecast = get_forecast(city)

        if "error" in forecast:
            return {"reply": forecast["error"]}

        return {
            "reply": build_forecast_response(forecast)
        }

    # -----------------------------
    # Weather + Decision Support
    # -----------------------------

    weather = get_current_weather(city)

    if "error" in weather:
        return {"reply": weather["error"]}

    decisions = generate_decision(weather)

    if intent == "umbrella":

        return {
            "reply": build_decision_response(
                decisions,
                "Umbrella"
            )
        }

    if intent == "travel":

        return {
            "reply": build_decision_response(
                decisions,
                "Travel"
            )
        }

    if intent == "outdoor":

        return {
            "reply": build_decision_response(
                decisions,
                "Outdoor"
            )
        }

    if intent == "health":

        return {
            "reply": build_decision_response(
                decisions,
                "Health"
            )
        }

    weather_report = build_weather_response(weather)

    decision_report = build_decision_response(decisions)

    return {
        "reply": weather_report + "\n" + decision_report
    }