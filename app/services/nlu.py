import re


def extract_city(message: str):

    match = re.search(r"in\s+([A-Za-z ]+)", message, re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return None


def detect_intent(message: str):

    message = message.lower()

    forecast_keywords = [
        "forecast",
        "tomorrow",
        "next",
        "week",
        "5 day",
        "five day",
        "upcoming"
    ]

    umbrella_keywords = [
        "umbrella",
        "raincoat",
        "rain"
    ]

    travel_keywords = [
        "travel",
        "drive",
        "trip",
        "journey",
        "flight"
    ]

    outdoor_keywords = [
        "walk",
        "jog",
        "cricket",
        "football",
        "play",
        "outside",
        "outdoor"
    ]

    health_keywords = [
        "humidity",
        "health",
        "heat",
        "hot",
        "temperature"
    ]

    for word in forecast_keywords:
        if word in message:
            return "forecast"

    for word in umbrella_keywords:
        if word in message:
            return "umbrella"

    for word in travel_keywords:
        if word in message:
            return "travel"

    for word in outdoor_keywords:
        if word in message:
            return "outdoor"

    for word in health_keywords:
        if word in message:
            return "health"

    return "current_weather"