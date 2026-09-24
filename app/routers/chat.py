from datetime import datetime, timedelta

from fastapi import APIRouter
from pydantic import BaseModel
from functools import wraps

from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.auth_dependency import get_optional_current_user


from app.services.nlu import (
    extract_city,
    detect_intent,
    fallback_understand_weather_query
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
    conversation_id: int | None = None


# ==================================================
# LOCAL NLU CONFIDENCE
# ==================================================

def local_nlu_is_confident(result: dict) -> bool:

    city = result.get("city")
    intent = result.get("intent")

    if not city:
        return False

    if not intent:
        return False

    if intent == "unknown":
        return False

    return True


# ==================================================
# DECIDE WHETHER GEMINI LLM IS NEEDED
# ==================================================

def should_use_llm(
    intent: str,
    language: str
) -> bool:

    # --------------------------------------------------
    # Weather advice benefits from LLM reasoning.
    # --------------------------------------------------

    if intent == "weather_advice":
        return True


    # --------------------------------------------------
    # Simple English weather requests can use the
    # deterministic response builders directly.
    # --------------------------------------------------

    fast_intents = {
        "current_weather",
        "temperature",
        "humidity",
        "wind",
        "rain",
        "alerts",
        "landslide_risk",
        "forecast"
    }

    if intent in fast_intents:
        return False


    # Anything unknown/complex can use Gemini.
    return True


# ==================================================
# FINAL RESPONSE BUILDER
# ==================================================

def build_final_response(
    user_message: str,
    verified_text: str,
    intent: str,
    language: str
) -> str:

    if not should_use_llm(
        intent,
        language
    ):

        print(
            "FAST RESPONSE - "
            "GEMINI LLM SKIPPED"
        )

        return verified_text


    print(
        "USING GEMINI LLM FOR RESPONSE"
    )

    return build_ai_weather_response(
        user_message,
        verified_text,
        language
    )
def get_previous_city(
    conversation_id: int | None,
    db: Session
) -> str | None:

    if conversation_id is None:
        return None

    previous_messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
            Message.role == "user"
        )
        .order_by(Message.created_at.desc())
        .all()
    )

    for message in previous_messages:
        city = extract_city(message.content)

        if city:
            return city

    return None

# ==================================================
# RAIN RESPONSE
# ==================================================

def build_rain_response(
    weather: dict
) -> str:

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


# ==================================================
# CHAT
# ==================================================
def save_chat_history(
    user: User | None,
    db: Session,
    conversation_id: int | None,
    user_message: str,
    assistant_reply: str
):
    if user is None:
        return None

    conversation = None

    # Existing conversation
    if conversation_id is not None:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )
            .first()
        )

        if conversation is None:
            return None

    # Create a new conversation
    if conversation is None:
        title = user_message.strip()

        if len(title) > 60:
            title = title[:57] + "..."

        conversation = Conversation(
            user_id=user.id,
            title=title or "New Conversation"
        )

        db.add(conversation)
        db.flush()

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=user_message
    )

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=assistant_reply
    )

    db.add(user_msg)
    db.add(assistant_msg)

    # Make this conversation appear at the top
    conversation.updated_at = datetime.now()

    db.commit()

    return conversation.id
def persist_chat_response(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        result = func(*args, **kwargs)

        if not isinstance(result, dict):
            return result

        reply = result.get("reply")

        if not reply:
            return result

        request = kwargs.get("request")
        db = kwargs.get("db")
        current_user = kwargs.get("current_user")

        if (
            request is None
            or db is None
            or current_user is None
        ):
            return result

        conversation_id = request.conversation_id

        saved_conversation_id = save_chat_history(
            user=current_user,
            db=db,
            conversation_id=conversation_id,
            user_message=request.message,
            assistant_reply=reply
        )

        if saved_conversation_id is not None:
            result["conversation_id"] = saved_conversation_id

        return result

    return wrapper
@router.post("/")
@persist_chat_response
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(
        get_optional_current_user
    )
):

    user_message = request.message.strip()


    if not user_message:

        return {
            "reply": (
                "Please enter a weather question."
            )
        }


    # ==================================================
    # NLU
    # ==================================================

    local_nlu_result = (
        fallback_understand_weather_query(
            user_message
        )
    )


    print(
        "LOCAL NLU RESULT:",
        local_nlu_result
    )


    if local_nlu_is_confident(
        local_nlu_result
    ):

        nlu_result = local_nlu_result

        print(
            "USING LOCAL NLU"
        )


    else:

        print(
            "LOCAL NLU UNCERTAIN - "
            "TRYING GEMINI NLU"
        )


        try:

            nlu_result = (
                understand_weather_query(
                    user_message
                )
            )


            print(
                "GEMINI NLU RESULT:",
                nlu_result
            )


        except Exception as e:

            print(
                "GEMINI NLU ERROR:",
                repr(e)
            )


            nlu_result = {

                "city": extract_city(
                    user_message
                ),

                "intent": detect_intent(
                    user_message
                ),

                "time": "unspecified",

                "language": "english"
            }


            print(
                "FINAL FALLBACK NLU RESULT:",
                nlu_result
            )


    # ==================================================
    # NLU VALUES
    # ==================================================

    city = nlu_result.get(
        "city"
    )

    intent = nlu_result.get(
        "intent"
    )

    time = nlu_result.get(
        "time",
        "unspecified"
    )

    language = nlu_result.get(
        "language",
        "english"
    )


    print(
        "NLU RESULT:",
        nlu_result
    )


    # ==================================================
    # CITY FALLBACK + CONVERSATION CONTEXT
    # ==================================================
    
    print("CURRENT MESSAGE:", user_message)
    print("CONVERSATION ID:", request.conversation_id)
    print("CITY FROM NLU:", city)
    
    if not city:
        city = extract_city(user_message)
    
    # If the current message does not mention a city,
    # use the city from the previous message.
    if not city and request.conversation_id is not None:
        previous_city = get_previous_city(
            request.conversation_id,
            db
        )
    
        if previous_city:
            city = previous_city
            print("USING CONVERSATION CITY:", city)
    
    if not city:
        return {
            "reply": (
                    "Location not specified. Please provide a city "
                    "or region to continue.\n"
                    "Example: \"What's the weather in Guwahati?\""
                )
        }


    # ==================================================
    # WEATHER ALERTS
    # ==================================================

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


        final_reply = build_final_response(
            user_message,
            alert_text,
            intent,
            language
        )


        return {
                "reply": final_reply
            }

    # ==================================================
    # LANDSLIDE RISK
    # ==================================================

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


        final_reply = build_final_response(
            user_message,
            risk_text,
            intent,
            language
        )


        return {
            "reply": final_reply
        }


    # ==================================================
    # TOMORROW
    # ==================================================

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
        ).strftime(
            "%Y-%m-%d"
        )


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
        
        final_reply = build_final_response(
            user_message,
            forecast_text,
            intent,
            language
        )


    # ==================================================
    # TONIGHT
    # ==================================================

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


        final_reply = build_final_response(
            user_message,
            normal_reply,
            intent,
            language
        )


        return {
            "reply": final_reply
        }


    # ==================================================
    # THIS WEEK
    # ==================================================

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


        final_reply = build_final_response(
            user_message,
            forecast_text,
            intent,
            language
        )


        return {
            "reply": final_reply
        }


    # ==================================================
    # NEXT WEEK
    # ==================================================

    if time == "next_week":

        return {
            "reply": (
                "Sorry, next week's forecast is "
                "not available yet. I currently "
                "provide a 5-day forecast."
            )
        }


    # ==================================================
    # FORECAST
    # ==================================================

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


        final_reply = build_final_response(
            user_message,
            forecast_text,
            intent,
            language
        )


        return {
            "reply": final_reply
        }


    # ==================================================
    # CURRENT WEATHER / OTHER WEATHER INTENTS
    # ==================================================

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


        final_reply = build_final_response(
            user_message,
            normal_reply,
            intent,
            language
        )


        return {
            "reply": final_reply,
            "weather": {
                "city": weather.get("city"),
                "country": weather.get("country"),
                "temperature": weather.get("temperature"),
                "humidity": weather.get("humidity"),
                "wind_speed": weather.get("wind_speed"),
                "condition": weather.get("condition"),
                "uv_index": weather.get("uv_index"),
                "sunrise": weather.get("sunrise"),
                "sunset": weather.get("sunset")
            }
        }


    # ==================================================
    # UNKNOWN INTENT
    # ==================================================

    return {
        "reply": (
            "Sorry, I couldn't understand your request. "
            "Try asking about the weather, temperature, "
            "rain, humidity, wind, alerts, forecast, "
            "or landslide risk."
        )
    }