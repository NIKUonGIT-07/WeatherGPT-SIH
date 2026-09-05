def extract_city(message: str):
    message = message.strip()

    stop_words = [
        "weather",
        "forecast",
        "today",
        "tomorrow",
        "will",
        "it",
        "rain",
        "raining",
        "rainfall",
        "in",
        "at",
        "for",
        "of",
        "the",
        "is",
        "there",
        "what",
        "how",
        "tell",
        "me",
        "about",
        "please",
        "should",
        "i",
        "carry",
        "umbrella",
        "an",
        "a",
        "current"
    ]

    words = message.replace("?", "").replace(".", "").replace(",", "").split()

    # Best case: city after "in", "at", or "for"
    lower_words = [word.lower() for word in words]

    for keyword in ["in", "at", "for"]:
        if keyword in lower_words:
            index = lower_words.index(keyword)
            city_words = words[index + 1:]

            if city_words:
                return " ".join(city_words).strip()

    # Fallback: remove common question words
    city_words = [
        word for word in words
        if word.lower() not in stop_words
    ]

    if city_words:
        return " ".join(city_words).strip()

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

    rain_keywords = [
        "rain",
        "raining",
        "rainfall",
        "shower",
        "drizzle",
        "umbrella"
    ]

    if any(keyword in message for keyword in forecast_keywords):
        return "forecast"

    if any(keyword in message for keyword in rain_keywords):
        return "current_weather"

    return "current_weather"