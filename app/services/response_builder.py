from datetime import datetime


def build_weather_response(weather: dict):

    current_time = datetime.now().strftime("%d %B %Y, %I:%M %p")

    response = f"""
Weather Report
────────────────────────

Location        : {weather['city']}

Date & Time     : {current_time}

Current Conditions
• Temperature   : {weather['temperature']} °C
• Wind Speed    : {weather['wind_speed']} km/h
"""

    # Optional fields
    if "humidity" in weather:
        response += f"• Humidity      : {weather['humidity']} %\n"

    if "condition" in weather:
        response += f"• Condition     : {weather['condition']}\n"

    response += """

Assessment
"""

    temp = weather["temperature"]

    if temp >= 40:
        response += "• Very hot weather is expected.\n"
    elif temp >= 30:
        response += "• Warm weather conditions.\n"
    elif temp <= 10:
        response += "• Cold weather conditions.\n"
    else:
        response += "• Pleasant weather conditions.\n"

    response += """
Recommendations
"""

    if temp >= 40:
        response += "• Stay hydrated.\n"
        response += "• Avoid direct sunlight during peak hours.\n"

    elif temp >= 30:
        response += "• Carry drinking water if travelling.\n"

    elif temp <= 10:
        response += "• Wear warm clothing.\n"

    else:
        response += "• Suitable for normal outdoor activities.\n"

    response += """
Source
• Provider : Open-Meteo
• Status   : Live Weather Data
"""

    return response