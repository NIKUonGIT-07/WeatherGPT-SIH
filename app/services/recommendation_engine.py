def generate_weather_advice(weather: dict):

    assessment = []
    recommendations = []

    temperature = weather["temperature"]
    humidity = weather["humidity"]
    wind_speed = weather["wind_speed"]
    condition = weather["condition"]

    # -----------------------------
    # Weather Condition
    # -----------------------------
    if "Thunderstorm" in condition:
        assessment.append("Thunderstorm activity detected.")
        recommendations.append("Avoid outdoor activities.")
        recommendations.append("Stay away from tall trees and electric poles.")
        recommendations.append("Follow official weather advisories.")

    elif "Rain" in condition:
        assessment.append("Rainfall is expected or currently occurring.")
        recommendations.append("Carry an umbrella or raincoat.")
        recommendations.append("Drive carefully on wet roads.")

    elif "Fog" in condition:
        assessment.append("Fog may reduce visibility.")
        recommendations.append("Drive with caution.")
        recommendations.append("Use headlights if travelling.")

    elif "Snow" in condition:
        assessment.append("Snowfall conditions detected.")
        recommendations.append("Wear warm clothing.")
        recommendations.append("Travel only if necessary.")

    elif "Clear" in condition:
        assessment.append("Clear weather conditions.")
        recommendations.append("Good conditions for outdoor activities.")

    elif "Cloud" in condition or "Overcast" in condition:
        assessment.append("Cloudy weather conditions.")
        recommendations.append("No significant weather risks detected.")

    else:
        assessment.append("Weather conditions are stable.")
        recommendations.append("No immediate precautions required.")

    # -----------------------------
    # Temperature
    # -----------------------------
    if temperature >= 40:
        recommendations.append("Stay hydrated.")
        recommendations.append("Avoid direct sunlight during peak hours.")

    elif temperature >= 35:
        recommendations.append("Limit prolonged outdoor exposure.")

    elif temperature <= 10:
        recommendations.append("Wear warm clothing.")

    # -----------------------------
    # Humidity
    # -----------------------------
    if humidity >= 85:
        recommendations.append("High humidity may cause discomfort.")

    # -----------------------------
    # Wind
    # -----------------------------
    if wind_speed >= 40:
        recommendations.append("Secure loose outdoor objects.")

    return {
        "assessment": assessment,
        "recommendations": recommendations
    }