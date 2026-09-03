from datetime import datetime


def build_forecast_response(data: dict):

    response = f"""
5-Day Weather Forecast
────────────────────────

Location : {data['city']}, {data['country']}

Generated : {datetime.now().strftime("%d %B %Y, %I:%M %p")}

"""

    forecast = data["forecast"]

    rainy_days = 0

    for day in forecast:

        date = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%d %b %Y")

        response += f"""
{date}
• Condition : {day['condition']}
• Max Temp  : {day['max_temp']} °C
• Min Temp  : {day['min_temp']} °C

"""

        if "Rain" in day["condition"] or "Thunderstorm" in day["condition"]:
            rainy_days += 1

    response += "Summary\n"

    if rainy_days >= 3:
        response += (
            "• Rain or thunderstorms are expected on most days.\n"
            "• Carry an umbrella if travelling.\n"
        )
    elif rainy_days > 0:
        response += (
            "• Some rainfall is expected during the forecast period.\n"
        )
    else:
        response += (
            "• No significant rainfall is expected.\n"
        )

    response += """
Source
• Provider : Open-Meteo
• Status   : 5-Day Forecast
"""

    return response