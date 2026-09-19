def extract_city(message: str):
    message = message.strip()

    stop_words = [
        "weather",
        "forecast",
        "today",
        "tomorrow",
        "tonight",
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
        "current",
        "alert",
        "alerts",
        "warning",
        "warnings",
        "advisory",
        "advisories",
        "severe",
        "dangerous",
        "weather",
        "landslide",
        "landslides",
        "risk",
        "danger",
        "safe",
        "outside",
        "could",
        "be",
        "any",
        "for",
    ]

    hindi_stop_words = [
        "में",
        "का",
        "की",
        "के",
        "को",
        "है",
        "क्या",
        "कोई",
        "मौसम",
        "चेतावनी",
        "खतरा",
        "भूस्खलन",
        "जोखिम",
        "बारिश",
        "वर्षा",
        "आज",
        "कल",
    ]

    assamese_stop_words = [
        "ত",
        "তেওঁ",
        "আছে",
        "নেকি",
        "বতৰ",
        "সতৰ্কবাণী",
        "ভূমিস্খলন",
        "আশংকা",
        "বৰষুণ",
        "আজি",
        "কাইলৈ",
    ]

    bengali_stop_words = [
        "তে",
        "এ",
        "আছে",
        "কি",
        "নাকি",
        "আবহাওয়া",
        "সতর্কতা",
        "ভূমিধস",
        "ঝুঁকি",
        "বৃষ্টি",
        "আজ",
        "আগামীকাল",
    ]

    words = (
        message
        .replace("?", "")
        .replace(".", "")
        .replace(",", "")
        .replace("।", "")
        .split()
    )

    lower_words = [word.lower() for word in words]

    all_stop_words = (
        stop_words
        + hindi_stop_words
        + assamese_stop_words
        + bengali_stop_words
    )

    # First try locations after common location words.
    location_words = [
        "in",
        "at",
        "for",
        "में",
        "में",
        "ত",
        "তে",
        "এ"
    ]

    for keyword in location_words:
        if keyword.lower() in lower_words:
            index = lower_words.index(keyword.lower())
            city_words = words[index + 1:]

            filtered_city = [
                word for word in city_words
                if word.lower() not in all_stop_words
            ]

            if filtered_city:
                return " ".join(filtered_city).strip()

    # Fallback: remove known weather words.
    city_words = [
        word
        for word in words
        if word.lower() not in all_stop_words
    ]

    if city_words:
        return " ".join(city_words).strip()

    return None


def detect_language(message: str):
    """
    Basic multilingual fallback language detection.

    Gemini remains the primary NLU.
    This function is only used when Gemini NLU fails.
    """

    # Hindi Unicode range
    if any("\u0900" <= char <= "\u097F" for char in message):
        return "hindi"

    # Bengali / Assamese Unicode range
    if any("\u0980" <= char <= "\u09FF" for char in message):
        # Common Assamese characters
        assamese_markers = [
            "ৰ",
            "ৱ",
            "ক্ষ",
            "কাইলৈ",
            "বতৰ",
            "সতৰ্কবাণী",
            "ভূমিস্খলন",
        ]

        if any(marker in message for marker in assamese_markers):
            return "assamese"

        return "bengali"

    return "english"


def detect_time(message: str):
    message_lower = message.lower()

    tomorrow_keywords = [
        "tomorrow",
        "कल",
        "কাইলৈ",
        "আগামীকাল",
    ]

    today_keywords = [
        "today",
        "आज",
        "আজি",
        "আজ",
    ]

    tonight_keywords = [
        "tonight",
        "आज रात",
        "আজি ৰাতি",
        "আজ রাতে",
    ]

    next_week_keywords = [
        "next week",
        "अगले सप्ताह",
        "अगले हफ्ते",
        "পৰৱৰ্তী সপ্তাহ",
        "আগামী সপ্তাহ",
    ]

    this_week_keywords = [
        "this week",
        "इस सप्ताह",
        "इस हफ्ते",
        "এই সপ্তাহ",
        "এই সপ্তাহত",
    ]

    if any(keyword in message_lower for keyword in tomorrow_keywords):
        return "tomorrow"

    if any(keyword in message_lower for keyword in tonight_keywords):
        return "tonight"

    if any(keyword in message_lower for keyword in next_week_keywords):
        return "next_week"

    if any(keyword in message_lower for keyword in this_week_keywords):
        return "this_week"

    if any(keyword in message_lower for keyword in today_keywords):
        return "today"

    return "unspecified"


def detect_intent(message: str):
    message_lower = message.lower()

    # Landslide
    landslide_keywords = [
        "landslide",
        "landslides",
        "landslide risk",
        "landslide danger",
        "landslide-prone",
        "landslide prone",
        "risk of landslide",
        "risk of landslides",
        "भूस्खलन",
        "भूस्खलन का खतरा",
        "भूस्खलन का जोखिम",
        "भूमिस्खलन",
        "ভূমিস্খলন",
        "ভূমিধস",
        "ভূমিধসের ঝুঁকি",
        "ভূমিস্খলনৰ আশংকা",
    ]

    if any(keyword in message_lower for keyword in landslide_keywords):
        return "landslide_risk"

    # Weather alerts / warnings
    alert_keywords = [
        "weather alert",
        "weather alerts",
        "weather warning",
        "weather warnings",
        "warning",
        "warnings",
        "advisory",
        "advisories",
        "severe weather",
        "dangerous weather",
        "weather alert",
        "मौसम चेतावनी",
        "मौसम की चेतावनी",
        "चेतावनी",
        "मौसम अलर्ट",
        "সতৰ্কবাণী",
        "বতৰৰ সতৰ্কবাণী",
        "আবহাওয়া সতর্কতা",
        "আবহাওয়ার সতর্কতা",
    ]

    if any(keyword in message_lower for keyword in alert_keywords):
        return "alerts"

    # Forecast
    forecast_keywords = [
        "forecast",
        "tomorrow",
        "next",
        "week",
        "5 day",
        "five day",
        "upcoming",
        "पूर्वानुमान",
        "कल",
        "আগামীকাল",
        "পূৰ্বানুমান",
        "পূর্বাভাস",
    ]

    if any(keyword in message_lower for keyword in forecast_keywords):
        return "forecast"

    # Weather advice
    advice_keywords = [
        "should i",
        "should we",
        "is it safe",
        "what should i",
        "what should we",
        "carry an umbrella",
        "what should i wear",
        "avoid going outside",
        "safe to go outside",
        "क्या मुझे",
        "क्या हमें",
        "क्या मैं",
        "बाहर जाना सुरक्षित",
        "क्या पहनना",
        "छाता",
        "umbrella",
        "কি মই",
        "মই কি",
        "বাহিৰলৈ যোৱা",
    ]

    if any(keyword in message_lower for keyword in advice_keywords):
        return "weather_advice"

    # Rain
    rain_keywords = [
        "rain",
        "raining",
        "rainfall",
        "shower",
        "drizzle",
        "बरसात",
        "बारिश",
        "वर्षा",
        "बरसने",
        "বৰষুণ",
        "বৰষুণীয়া",
        "বৃষ্টি",
    ]

    if any(keyword in message_lower for keyword in rain_keywords):
        return "rain"

    # Temperature
    temperature_keywords = [
        "temperature",
        "hot",
        "cold",
        "गरमी",
        "गर्मी",
        "ठंड",
        "तापमान",
        "উষ্ণতা",
        "ঠাণ্ডা",
        "গৰম",
        "তাপমাত্ৰা",
    ]

    if any(keyword in message_lower for keyword in temperature_keywords):
        return "temperature"

    # Humidity
    humidity_keywords = [
        "humidity",
        "humid",
        "नमी",
        "आर्द्रता",
        "আৰ্দ্ৰতা",
        "আর্দ্রতা",
    ]

    if any(keyword in message_lower for keyword in humidity_keywords):
        return "humidity"

    # Wind
    wind_keywords = [
        "wind",
        "wind speed",
        "strong wind",
        "हवा",
        "हवा की गति",
        "तेज हवा",
        "বতাহ",
        "বতাহৰ গতি",
        "ঝড়ো হাওয়া",
    ]

    if any(keyword in message_lower for keyword in wind_keywords):
        return "wind"

    return "current_weather"


def fallback_understand_weather_query(message: str):
    return {
        "city": extract_city(message),
        "intent": detect_intent(message),
        "time": detect_time(message),
        "language": detect_language(message),
    }
def localize_text(text: str, language: str = "english") -> str:
    """
    Basic fallback localization.

    Gemini handles the main multilingual response generation.
    This function provides a safe fallback when Gemini is unavailable.
    """

    if not text:
        return text

    # English
    if language == "english":
        return text

    # Hindi
    if language == "hindi":
        translations = {
            "Weather Alerts": "मौसम चेतावनी",
            "Landslide Risk Assessment": "भूस्खलन जोखिम आकलन",
            "Risk Level": "जोखिम स्तर",
            "Indicators": "संकेतक",
            "Advice": "सलाह",
            "Important": "महत्वपूर्ण",
            "Source": "स्रोत",
            "Current Weather": "वर्तमान मौसम",
            "Forecast": "पूर्वानुमान",
            "LOW": "कम",
            "MEDIUM": "मध्यम",
            "HIGH": "उच्च",
        }

        for english, translated in translations.items():
            text = text.replace(
                english,
                translated
            )

        return text

    # Assamese
    if language == "assamese":
        translations = {
            "Weather Alerts": "বতৰৰ সতৰ্কবাণী",
            "Landslide Risk Assessment": "ভূমিস্খলন বিপদাশংকা মূল্যায়ন",
            "Risk Level": "বিপদাশংকাৰ স্তৰ",
            "Indicators": "সূচকসমূহ",
            "Advice": "পৰামৰ্শ",
            "Important": "গুৰুত্বপূৰ্ণ",
            "Source": "উৎস",
            "Current Weather": "বৰ্তমান বতৰ",
            "Forecast": "পূৰ্বানুমান",
            "LOW": "কম",
            "MEDIUM": "মধ্যম",
            "HIGH": "উচ্চ",
        }

        for english, translated in translations.items():
            text = text.replace(
                english,
                translated
            )

        return text

    # Bengali
    if language == "bengali":
        translations = {
            "Weather Alerts": "আবহাওয়া সতর্কতা",
            "Landslide Risk Assessment": "ভূমিধস ঝুঁকি মূল্যায়ন",
            "Risk Level": "ঝুঁকির স্তর",
            "Indicators": "নির্দেশক",
            "Advice": "পরামর্শ",
            "Important": "গুরুত্বপূর্ণ",
            "Source": "উৎস",
            "Current Weather": "বর্তমান আবহাওয়া",
            "Forecast": "পূর্বাভাস",
            "LOW": "কম",
            "MEDIUM": "মাঝারি",
            "HIGH": "উচ্চ",
        }

        for english, translated in translations.items():
            text = text.replace(
                english,
                translated
            )

        return text

    return text