def calculate_landslide_risk(
    forecast: dict,
    current_weather: dict | None = None
):
    risk_score = 0
    indicators = []

    forecast_days = forecast.get("forecast", [])

    rainy_days = 0
    heavy_rain_days = 0
    thunderstorm_days = 0

    for day in forecast_days:

        condition = str(
            day.get("condition", "")
        ).lower()

        if (
            "rain" in condition
            or "drizzle" in condition
            or "shower" in condition
        ):
            rainy_days += 1

        if (
            "heavy rain" in condition
            or "violent rain" in condition
        ):
            heavy_rain_days += 1

        if "thunderstorm" in condition:
            thunderstorm_days += 1

    # Persistent rainfall
    if rainy_days >= 3:

        risk_score += 2

        indicators.append(
            "Persistent rainfall is forecast."
        )

    elif rainy_days >= 1:

        risk_score += 1

        indicators.append(
            "Rainfall is forecast during the period."
        )

    # Heavy rainfall
    if heavy_rain_days >= 2:

        risk_score += 3

        indicators.append(
            "Multiple days of heavy rainfall are forecast."
        )

    elif heavy_rain_days == 1:

        risk_score += 2

        indicators.append(
            "Heavy rainfall is forecast."
        )

    # Thunderstorms
    if thunderstorm_days >= 2:

        risk_score += 1

        indicators.append(
            "Thunderstorm activity is forecast on multiple days."
        )

    # Current humidity
    if current_weather:

        humidity = current_weather.get(
            "humidity",
            0
        )

        if humidity >= 90:

            risk_score += 1

            indicators.append(
                "Current humidity is very high."
            )

    # Convert score to risk level
    if risk_score >= 5:

        level = "HIGH"

    elif risk_score >= 2:

        level = "MEDIUM"

    else:

        level = "LOW"

    return {
        "level": level,
        "score": risk_score,
        "indicators": indicators,
        "note": (
            "This is an automated weather-based "
            "landslide risk indicator, not an official "
            "government warning."
        )
    }