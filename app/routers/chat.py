from fastapi import APIRouter
from pydantic import BaseModel

from app.services.nlu import extract_city
from app.services.weather_service import get_current_weather
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

    if city:

        weather = get_current_weather(city)
        reply = build_weather_response(weather)

        return {
            "reply": reply
   }