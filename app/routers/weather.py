from fastapi import APIRouter
from app.services.weather_service import get_current_weather

router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/current/{city}")
def current_weather(city: str):
    return get_current_weather(city)