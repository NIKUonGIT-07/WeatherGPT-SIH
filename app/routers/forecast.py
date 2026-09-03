from fastapi import APIRouter
from app.services.forecast_service import get_forecast

router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"]
)


@router.get("/{city}")
def forecast(city: str):
    return get_forecast(city)