from fastapi import APIRouter

from app.services.alert_response_builder import build_alert_response
from app.services.alert_service import generate_forecast_alerts, generate_weather_alerts
from app.services.forecast_service import get_forecast
from app.services.weather_service import get_current_weather

router = APIRouter(
    prefix="/alerts",
    tags=["Weather Alerts"]
)


@router.get("/{city}")
def get_weather_alerts(city: str):
    weather = get_current_weather(city)
    if "error" in weather:
        return {"error": weather["error"]}

    alerts = generate_weather_alerts(weather)
    response = build_alert_response(
        city=weather.get("city", city),
        country=weather.get("country", ""),
        alerts=alerts,
        forecast=False
    )

    return {
        "city": weather.get("city", city),
        "alerts": alerts,
        "reply": response
    }


@router.get("/{city}/forecast")
def get_forecast_alerts(city: str):
    forecast = get_forecast(city)
    if "error" in forecast:
        return {"error": forecast["error"]}

    alerts = generate_forecast_alerts(forecast)
    response = build_alert_response(
        city=forecast.get("city", city),
        country=forecast.get("country", ""),
        alerts=alerts,
        forecast=True
    )

    return {
        "city": forecast.get("city", city),
        "alerts": alerts,
        "reply": response
    }
