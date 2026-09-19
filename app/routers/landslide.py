from fastapi import APIRouter

from app.services.weather_service import get_current_weather
from app.services.forecast_service import get_forecast

from app.services.landslide_risk_service import (
    calculate_landslide_risk
)

from app.services.landslide_response_builder import (
    build_landslide_risk_response
)


router = APIRouter(
    prefix="/landslide-risk",
    tags=["Landslide Risk"]
)


@router.get("/{city}")
def get_landslide_risk(city: str):

    current_weather = get_current_weather(city)

    if "error" in current_weather:
        return {
            "error": current_weather["error"]
        }

    forecast = get_forecast(city)

    if "error" in forecast:
        return {
            "error": forecast["error"]
        }

    risk = calculate_landslide_risk(
        forecast=forecast,
        current_weather=current_weather
    )

    response = build_landslide_risk_response(
        city=current_weather.get("city", city),
        country=current_weather.get("country", ""),
        risk=risk
    )

    return {
        "city": current_weather.get("city", city),
        "risk": risk,
        "reply": response
    }