from datetime import datetime
from app.services.recommendation_engine import generate_weather_advice


def build_weather_response(weather: dict):

    current_time = datetime.now().strftime("%d %B %Y, %I:%M %p")

    advice = generate_weather_advice(weather)

    response = f"""
Weather Report
────────────────────────

Location        : {weather['city']}, {weather['country']}

Date & Time     : {current_time}

Current Conditions
• Condition     : {weather['condition']}
• Temperature   : {weather['temperature']} °C
• Humidity      : {weather['humidity']} %
• Wind Speed    : {weather['wind_speed']} km/h

Assessment
"""

    for item in advice["assessment"]:
        response += f"• {item}\n"

    response += "\nRecommendations\n"

    for item in advice["recommendations"]:
        response += f"• {item}\n"

    response += """
Source
• Provider : Open-Meteo
• Status   : Live Weather Data
"""

    return response