def generate_decision(weather: dict):

    condition = weather.get("condition", "")
    temperature = weather.get("temperature", 0)
    humidity = weather.get("humidity", 0)
    wind_speed = weather.get("wind_speed", 0)

    decisions = []

    # -----------------------------
    # Umbrella Advice
    # -----------------------------
    if "Rain" in condition or "Thunderstorm" in condition:
        decisions.append({
            "title": "Umbrella Advice",
            "status": "Recommended",
            "reason": "Rain or thunderstorms are expected.",
            "advice": "Carry an umbrella or raincoat."
        })
    else:
        decisions.append({
            "title": "Umbrella Advice",
            "status": "Not Required",
            "reason": "No rainfall is expected.",
            "advice": "An umbrella is optional."
        })

    # -----------------------------
    # Travel Advisory
    # -----------------------------
    if "Thunderstorm" in condition or wind_speed >= 40:
        decisions.append({
            "title": "Travel Advisory",
            "status": "Travel with Caution",
            "reason": "Severe weather conditions may affect travel.",
            "advice": "Check road and weather conditions before leaving."
        })
    else:
        decisions.append({
            "title": "Travel Advisory",
            "status": "Safe",
            "reason": "No significant travel disruptions expected.",
            "advice": "Normal travel conditions."
        })

    # -----------------------------
    # Outdoor Activities
    # -----------------------------
    if "Thunderstorm" in condition:
        decisions.append({
            "title": "Outdoor Activities",
            "status": "Not Recommended",
            "reason": "Thunderstorm activity detected.",
            "advice": "Avoid outdoor sports and gatherings."
        })
    elif temperature >= 38:
        decisions.append({
            "title": "Outdoor Activities",
            "status": "Limited",
            "reason": "High temperature.",
            "advice": "Avoid outdoor activities during the afternoon."
        })
    else:
        decisions.append({
            "title": "Outdoor Activities",
            "status": "Suitable",
            "reason": "Weather conditions are generally favorable.",
            "advice": "Outdoor activities can be planned."
        })

    # -----------------------------
    # Health Advisory
    # -----------------------------
    if humidity >= 90:
        decisions.append({
            "title": "Health Advisory",
            "status": "High Humidity",
            "reason": "Humidity is very high.",
            "advice": "Stay hydrated and wear light clothing."
        })
    elif temperature >= 40:
        decisions.append({
            "title": "Health Advisory",
            "status": "Heat Stress",
            "reason": "Very high temperature.",
            "advice": "Avoid prolonged sun exposure and drink plenty of water."
        })
    else:
        decisions.append({
            "title": "Health Advisory",
            "status": "Normal",
            "reason": "No major weather-related health risks.",
            "advice": "Maintain normal precautions."
        })

    return decisions