def extract_city(text: str) -> str | None:

    if not text:
        return None

    text = text.strip()

    # --------------------------------------------------
    # Known city names
    # --------------------------------------------------

    city_map = {
        # English
        "guwahati": "Guwahati",
        "delhi": "Delhi",
        "mumbai": "Mumbai",
        "kolkata": "Kolkata",
        "chennai": "Chennai",
        "bengaluru": "Bengaluru",
        "bangalore": "Bengaluru",
        "hyderabad": "Hyderabad",

        # Hindi
        "गुवाहाटी": "Guwahati",
        "दिल्ली": "Delhi",
        "मुंबई": "Mumbai",
        "कोलकाता": "Kolkata",
        "चेन्नई": "Chennai",
        "बेंगलुरु": "Bengaluru",
        "हैदराबाद": "Hyderabad",

        # Assamese
        "গুৱাহাটী": "Guwahati",
        "দিল্লী": "Delhi",
        "মুম্বাই": "Mumbai",
        "কলকাতা": "Kolkata",

        # Bengali
        "গুয়াহাটি": "Guwahati",
        "গুৱাহাটী": "Guwahati",
        "দিল্লি": "Delhi",
        "মুম্বাই": "Mumbai",
        "কলকাতা": "Kolkata",
    }

    # --------------------------------------------------
    # Direct city detection
    # --------------------------------------------------

    text_lower = text.lower()

    for name, canonical_name in city_map.items():

        if name.lower() in text_lower:
            return canonical_name

    # --------------------------------------------------
    # Bengali / Assamese attached suffixes
    # --------------------------------------------------

    regional_variants = {
        "গুয়াহাটিতে": "Guwahati",
        "গুৱাহাটীতে": "Guwahati",
        "গুৱাহাটীত": "Guwahati",
        "গুৱাহাটিত": "Guwahati",
    }

    for variant, canonical_name in regional_variants.items():

        if variant in text:
            return canonical_name

    # --------------------------------------------------
    # Hindi attached forms
    # --------------------------------------------------

    hindi_variants = {
        "गुवाहाटीमें": "Guwahati",
        "दिल्लीमें": "Delhi",
        "मुंबईमें": "Mumbai",
        "कोलकातामें": "Kolkata",
    }

    for variant, canonical_name in hindi_variants.items():

        if variant in text:
            return canonical_name

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

    # ==================================================
    # Landslide Risk
    # ==================================================

    landslide_keywords = [
        "landslide",
        "landslides",
        "landslide risk",
        "landslide danger",
        "landslide-prone",
        "landslide prone",
        "risk of landslide",
        "risk of landslides",

        # Hindi
        "भूस्खलन",
        "भूस्खलन का खतरा",
        "भूस्खलन का जोखिम",

        # Assamese
        "ভূমিস্খলন",
        "ভূমিধস",
        "ভূমিস্খলনৰ আশংকা",

        # Bengali
        "ভূমিধসের ঝুঁকি",
    ]

    if any(keyword in message_lower for keyword in landslide_keywords):
        return "landslide_risk"


    # ==================================================
    # Weather Alerts
    # ==================================================

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

        # Hindi
        "मौसम चेतावनी",
        "मौसम की चेतावनी",
        "चेतावनी",
        "मौसम अलर्ट",

        # Assamese
        "সতৰ্কবাণী",
        "বতৰৰ সতৰ্কবাণী",

        # Bengali
        "আবহাওয়া সতর্কতা",
        "আবহাওয়ার সতর্কতা",
    ]

    if any(keyword in message_lower for keyword in alert_keywords):
        return "alerts"


    # ==================================================
    # Weather Advice
    # ==================================================

    advice_keywords = [
        "should i",
        "should i wear",
        "should i carry",
        "should i go",
        "is it safe",
        "what should i",
        "carry an umbrella",
        "what should i wear",
        "avoid going outside",
        "safe to go outside",

        # Hindi
        "क्या मुझे",
        "क्या हमें",
        "क्या मैं",
        "बाहर जाना सुरक्षित",
        "क्या पहनना",

        # Assamese
        "ছাতি",
        "মই কি",
        "বাহিৰলৈ যোৱা",
        "বাহিৰলৈ যোৱা সুৰক্ষিত",

        # Bengali
        "কি আমি",
        "ছাতা",
    ]

    if any(keyword in message_lower for keyword in advice_keywords):
        return "weather_advice"


    # ==================================================
    # Rain
    # ==================================================

    rain_keywords = [
        "rain",
        "raining",
        "rainfall",
        "rainy",
        "shower",
        "showers",
        "drizzle",
        "precipitation",

        # Hindi
        "बारिश",
        "बारिश होगी",
        "वर्षा",
        "बरसात",
        "बरसने",

        # Assamese
        "বৰষুণ",
        "বৰষুণীয়া",
        "বৃষ্টি",

        # Bengali
        "বৃষ্টি",
    ]

    if any(keyword in message_lower for keyword in rain_keywords):
        return "rain"


    # ==================================================
    # Temperature
    # ==================================================

    temperature_keywords = [
        "temperature",
        "how hot",
        "how cold",
        "hot",
        "cold",

        # Hindi
        "गर्मी",
        "ठंडी",
        "तापमान",

        # Assamese
        "উষ্ণতা",
        "ঠাণ্ডা",
        "গৰম",
        "তাপমাত্ৰা",

        # Bengali
        "তাপমাত্রা",
    ]

    if any(keyword in message_lower for keyword in temperature_keywords):
        return "temperature"


    # ==================================================
    # Humidity
    # ==================================================

    humidity_keywords = [
        "humidity",
        "humid",

        # Hindi
        "नमी",
        "आर्द्रता",

        # Assamese
        "আৰ্দ্ৰতা",

        # Bengali
        "আর্দ্রতা",
    ]

    if any(keyword in message_lower for keyword in humidity_keywords):
        return "humidity"


    # ==================================================
    # Wind
    # ==================================================

    wind_keywords = [
        "wind",
        "wind speed",
        "strong wind",
        "windy",

        # Hindi
        "हवा",
        "हवा की गति",
        "तेज हवा",

        # Assamese
        "বতাহ",
        "বতাহৰ গতি",

        # Bengali
        "ঝড়ো হাওয়া",
    ]

    if any(keyword in message_lower for keyword in wind_keywords):
        return "wind"


    # ==================================================
    # Forecast
    # ==================================================

    forecast_keywords = [
        "forecast",
        "5 day",
        "five day",
        "upcoming",
        "weather forecast",

        # Hindi
        "पूर्वानुमान",

        # Assamese
        "পূৰ্বানুমান",
        "পূৰ্বাভাস",

        # Bengali
        "পূর্বাভাস",
    ]

    if any(keyword in message_lower for keyword in forecast_keywords):
        return "forecast"


    # ==================================================
    # Default
    # ==================================================

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