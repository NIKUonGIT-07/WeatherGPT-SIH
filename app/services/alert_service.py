RAIN_CONDITIONS = {"light rain", "moderate rain", "heavy rain", "rain showers", "heavy rain showers", "violent rain showers"}


def _condition(weather: dict) -> str:
    return str(weather.get("condition", "")).strip().lower()


def generate_weather_alerts(weather: dict):
    """Generate application-level risk indications from current weather.

    These are not official government warnings. Thresholds are deliberately
    simple and should be calibrated with authoritative regional criteria later.
    """
    alerts = []
    temperature = float(weather.get("temperature") or 0)
    humidity = float(weather.get("humidity") or 0)
    wind_speed = float(weather.get("wind_speed") or 0)
    condition = _condition(weather)

    if "thunderstorm" in condition:
        level = "HIGH"
        alert_type = "Thunderstorm with Hail" if "hail" in condition else "Thunderstorm"
        alerts.append({
            "level": level,
            "type": alert_type,
            "message": "Thunderstorm activity detected.",
            "advice": [
                "Avoid outdoor activities.",
                "Stay away from tall trees and electric poles.",
                "Stay indoors during severe activity.",
                "Follow official weather advisories."
            ]
        })

    if condition in {"heavy rain", "heavy rain showers", "violent rain showers"}:
        alerts.append({
            "level": "HIGH",
            "type": "Heavy Rain",
            "message": "Heavy rainfall may affect travel conditions.",
            "advice": [
                "Carry an umbrella or raincoat.",
                "Drive carefully on wet roads.",
                "Avoid flooded or waterlogged areas."
            ]
        })
    elif condition in {"moderate rain", "rain showers", "light rain", "moderate drizzle", "dense drizzle"}:
        alerts.append({
            "level": "MEDIUM",
            "type": "Rain",
            "message": "Rainfall may affect outdoor activities and travel.",
            "advice": [
                "Carry an umbrella or raincoat.",
                "Use caution on wet roads."
            ]
        })

    if temperature >= 40:
        alerts.append({
            "level": "HIGH",
            "type": "Heatwave Risk",
            "message": "Very high temperature detected.",
            "advice": [
                "Stay hydrated.",
                "Avoid prolonged direct sunlight.",
                "Avoid strenuous outdoor activity during peak heat."
            ]
        })
    elif temperature >= 38:
        alerts.append({
            "level": "MEDIUM",
            "type": "High Heat",
            "message": "High temperature may cause heat discomfort.",
            "advice": [
                "Drink enough water.",
                "Limit prolonged exposure to direct sunlight."
            ]
        })

    if temperature <= 5:
        alerts.append({
            "level": "MEDIUM",
            "type": "Cold Wave Risk",
            "message": "Very low temperature detected.",
            "advice": [
                "Wear warm clothing.",
                "Limit prolonged outdoor exposure."
            ]
        })

    if wind_speed >= 60:
        alerts.append({
            "level": "HIGH",
            "type": "Strong Wind",
            "message": "Very strong winds detected.",
            "advice": [
                "Secure loose outdoor objects.",
                "Avoid parking under trees or near unstable structures.",
                "Use caution while travelling."
            ]
        })
    elif wind_speed >= 40:
        alerts.append({
            "level": "MEDIUM",
            "type": "Strong Wind",
            "message": "Strong winds detected.",
            "advice": [
                "Secure loose outdoor objects.",
                "Use caution while travelling."
            ]
        })

    if humidity >= 90:
        alerts.append({
            "level": "LOW",
            "type": "High Humidity",
            "message": "Humidity levels are very high.",
            "advice": [
                "Drink enough water.",
                "Wear light and breathable clothing."
            ]
        })

    return alerts


def generate_forecast_alerts(forecast_data: dict):
    """Generate alerts from the available daily forecast."""
    alerts = []

    for day in forecast_data.get("forecast", []):
        condition = str(day.get("condition", "")).lower()
        max_temp = float(day.get("max_temp") or 0)
        min_temp = float(day.get("min_temp") or 0)
        wind_speed = float(day.get("max_wind_speed") or 0)
        date = day.get("date")

        prefix = f"{date}: " if date else ""

        if "thunderstorm" in condition:
            alerts.append({
                "level": "HIGH",
                "type": "Forecast Thunderstorm",
                "date": date,
                "message": prefix + "Thunderstorm activity is forecast.",
                "advice": [
                    "Avoid outdoor activities if conditions worsen.",
                    "Monitor official weather advisories."
                ]
            })

        if "heavy rain" in condition or "violent rain" in condition:
            alerts.append({
                "level": "HIGH",
                "type": "Forecast Heavy Rain",
                "date": date,
                "message": prefix + "Heavy rainfall is forecast.",
                "advice": [
                    "Plan for wet-road conditions.",
                    "Carry rain protection."
                ]
            })
        elif "rain" in condition or "drizzle" in condition or "shower" in condition:
            alerts.append({
                "level": "MEDIUM",
                "type": "Forecast Rain",
                "date": date,
                "message": prefix + "Rainfall is forecast.",
                "advice": [
                    "Carry an umbrella or raincoat.",
                    "Allow extra travel time on wet roads."
                ]
            })

        if max_temp >= 40:
            alerts.append({
                "level": "HIGH",
                "type": "Forecast Heatwave Risk",
                "date": date,
                "message": prefix + "Very high temperature is forecast.",
                "advice": [
                    "Stay hydrated.",
                    "Avoid prolonged direct sunlight."
                ]
            })
        elif max_temp >= 38:
            alerts.append({
                "level": "MEDIUM",
                "type": "Forecast High Heat",
                "date": date,
                "message": prefix + "High temperature is forecast.",
                "advice": ["Stay hydrated and limit prolonged heat exposure."]
            })

        if min_temp <= 5:
            alerts.append({
                "level": "MEDIUM",
                "type": "Forecast Cold Wave Risk",
                "date": date,
                "message": prefix + "Very low temperature is forecast.",
                "advice": ["Wear warm clothing and limit prolonged exposure."]
            })

        if wind_speed >= 60:
            alerts.append({
                "level": "HIGH",
                "type": "Forecast Strong Wind",
                "date": date,
                "message": prefix + "Very strong winds are forecast.",
                "advice": ["Secure loose objects and use caution while travelling."]
            })
        elif wind_speed >= 40:
            alerts.append({
                "level": "MEDIUM",
                "type": "Forecast Strong Wind",
                "date": date,
                "message": prefix + "Strong winds are forecast.",
                "advice": ["Secure loose outdoor objects and use caution while travelling."]
            })

    return alerts
