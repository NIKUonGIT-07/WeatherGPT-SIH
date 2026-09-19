def build_alert_response(city: str, country: str, alerts: list, forecast: bool = False) -> str:
    location = f"{city}, {country}" if country else city
    title = "Forecast Alerts" if forecast else "Weather Alerts"

    if not alerts:
        return f"""
{title}
────────────────────────

Location : {location}

• No significant WeatherGPT risk indications are currently detected.
• These automated indications are not official government warnings.

Source
• Provider : Open-Meteo
• Status   : Live Weather Data
"""

    response = f"""
{title}
────────────────────────

Location : {location}

"""

    for alert in alerts:
        response += f"""
{alert['type']}
• Level   : {alert['level']}
• Message : {alert['message']}
"""
        if alert.get("advice"):
            response += "• Advice  :\n"
            for advice in alert["advice"]:
                response += f"  • {advice}\n"
        response += "\n"

    response += """Note
• These are automated WeatherGPT risk indications based on forecast data.
• They are not official government warnings.

Source
• Provider : Open-Meteo
• Status   : Weather Data / Forecast
"""
    return response
