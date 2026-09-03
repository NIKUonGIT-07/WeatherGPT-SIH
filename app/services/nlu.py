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

    for keyword in forecast_keywords:
        if keyword in message:
            return "forecast"

    return "current_weather"