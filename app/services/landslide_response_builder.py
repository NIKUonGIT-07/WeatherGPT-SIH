def build_landslide_risk_response(
    city: str,
    country: str,
    risk: dict
) -> str:

    location = f"{city}, {country}" if country else city

    response = f"""
Landslide Risk Assessment
────────────────────────

Location : {location}

Risk Level : {risk['level']}

Indicators
"""

    indicators = risk.get("indicators", [])

    if indicators:
        for indicator in indicators:
            response += f"• {indicator}\n"
    else:
        response += (
            "• No significant weather-based landslide "
            "risk indicators detected.\n"
        )

    response += "\nAdvice\n"

    if risk["level"] == "HIGH":

        response += (
            "• Avoid unnecessary travel through vulnerable "
            "slopes and hilly roads.\n"
            "• Stay alert for changes in local conditions.\n"
            "• Monitor official disaster-management advisories.\n"
        )

    elif risk["level"] == "MEDIUM":

        response += (
            "• Exercise caution near slopes and vulnerable roads.\n"
            "• Avoid unnecessary travel during heavy rainfall.\n"
            "• Monitor official weather and disaster advisories.\n"
        )

    else:

        response += (
            "• No significant weather-based landslide risk "
            "is currently indicated.\n"
            "• Continue monitoring weather conditions.\n"
        )

    response += f"""
Risk Score : {risk['score']}

Important
• {risk['note']}

Source
• Provider : Open-Meteo
• Analysis : Weather-based prototype risk indicator
"""

    return response