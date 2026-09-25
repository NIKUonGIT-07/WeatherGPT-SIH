from datetime import datetime


def build_forecast_response(data: dict):

    forecast = data["forecast"]
    rainy_days = 0

    response = f"""
5-Day Weather Forecast
────────────────────────

Location : {data['city']}, {data['country']}

Generated : {datetime.now().strftime("%d %B %Y, %I:%M %p")}

"""

    for day in forecast:

        date = datetime.strptime(
            day["date"], "%Y-%m-%d"
        ).strftime("%d %b %Y")

        response += f"""
{date}
• Condition : {day['condition']}
• Max Temp  : {day['max_temp']} °C
• Min Temp  : {day['min_temp']} °C
• Rainfall  : {day.get('rainfall', 0)} mm
• Rain Chance: {day.get('rain_probability', 0)} %

"""

        if (
            "Rain" in day["condition"]
            or "Thunderstorm" in day["condition"]
        ):
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

    return {
        "reply": response,
        "type": "forecast",
        "data": {
            "city": data["city"],
            "country": data["country"],
            "forecast": forecast
        }
    }
def build_single_day_response(
    data: dict,
    day: dict,
    label: str
):

    date = datetime.strptime(
        day["date"],
        "%Y-%m-%d"
    ).strftime("%d %B %Y")

    return f"""
Weather Forecast
────────────────────────

Location : {data['city']}, {data['country']}

{label} : {date}

• Condition : {day['condition']}
• Max Temp  : {day['max_temp']} °C
• Min Temp  : {day['min_temp']} °C
• Max Wind  : {day.get('max_wind_speed', 'N/A')} km/h
• Rainfall  : {day.get('rainfall', 'N/A')} mm
• Rain Chance: {day.get('rain_probability', 'N/A')} %

Source
• Provider : Open-Meteo
• Status   : Forecast Data
"""