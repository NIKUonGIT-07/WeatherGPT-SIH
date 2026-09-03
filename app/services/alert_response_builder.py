def generate_weather_alerts(weather: dict):

    alerts = []

    temperature = weather.get("temperature", 0)
    humidity = weather.get("humidity", 0)
    wind_speed = weather.get("wind_speed", 0)
    condition = weather.get("condition", "")

    # Thunderstorm
    if "Thunderstorm" in condition:
        alerts.append({
            "level": "HIGH",
            "type": "Thunderstorm",
            "message": "Thunderstorm activity detected.",
            "advice": [
                "Avoid outdoor activities.",
                "Stay away from tall trees and electric poles.",
                "Follow official weather advisories."
            ]
        })

    # Heavy Rain
    if "Rain" in condition:
        alerts.append({
            "level": "MEDIUM",
            "type": "Heavy Rain",
            "message": "Rainfall may affect travel conditions.",
            "advice": [
                "Carry an umbrella.",
                "Drive carefully on wet roads."
            ]
        })

    # Heatwave
    if temperature >= 40:
        alerts.append({
            "level": "HIGH",
            "type": "Heatwave",
            "message": "Extremely high temperature detected.",
            "advice": [
                "Stay hydrated.",
                "Avoid going outside during afternoon hours."
            ]
        })

    # Cold Wave
    if temperature <= 5:
        alerts.append({
            "level": "MEDIUM",
            "type": "Cold Wave",
            "message": "Very low temperature detected.",
            "advice": [
                "Wear warm clothing.",
                "Limit outdoor exposure."
            ]
        })

    # Strong Wind
    if wind_speed >= 40:
        alerts.append({
            "level": "MEDIUM",
            "type": "Strong Wind",
            "message": "Strong winds expected.",
            "advice": [
                "Secure loose outdoor objects.",
                "Avoid parking under trees."
            ]
        })

    # High Humidity
    if humidity >= 90:
        alerts.append({
            "level": "LOW",
            "type": "High Humidity",
            "message": "Humidity levels are very high.",
            "advice": [
                "Drink enough water.",
                "Wear light clothing."
            ]
        })

    return alerts