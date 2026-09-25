import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing Rime Fog", 51: "Light Drizzle",
    53: "Moderate Drizzle", 55: "Dense Drizzle", 61: "Light Rain",
    63: "Moderate Rain", 65: "Heavy Rain", 71: "Light Snow",
    73: "Moderate Snow", 75: "Heavy Snow", 80: "Rain Showers",
    81: "Heavy Rain Showers", 82: "Violent Rain Showers", 95: "Thunderstorm",
    96: "Thunderstorm with Hail", 99: "Severe Thunderstorm with Hail"
}


def get_forecast(city: str):
    try:
        geo_response = requests.get(
            GEOCODING_URL,
            params={"name": city, "count": 1},
            timeout=10
        )
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return {"error": "City not found"}

        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]

        weather_response = requests.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": (
                    "weather_code,"
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "wind_speed_10m_max,"
                    "precipitation_sum,"
                    "precipitation_probability_max"
                ),
                "forecast_days": 5
            },
            timeout=10
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json().get("daily", {})

        forecast = []
        for i, date in enumerate(weather_data.get("time", [])):
            weather_code = weather_data["weather_code"][i]
            forecast.append({
                "date": date,
                "condition": WEATHER_CODES.get(weather_code, "Unknown"),
                "max_temp": weather_data["temperature_2m_max"][i],
                "min_temp": weather_data["temperature_2m_min"][i],
                "max_wind_speed": weather_data.get("wind_speed_10m_max", [None] * len(weather_data["time"]))[i],
                "rainfall": weather_data["precipitation_sum"][i],
                "rain_probability": weather_data["precipitation_probability_max"][i]
            })

        return {
            "city": location["name"],
            "country": location.get("country", ""),
            "latitude": latitude,
            "longitude": longitude,
            "forecast": forecast
        }

    except requests.RequestException as e:
        print("FORECAST API ERROR:", repr(e))
        return {"error": "Weather forecast service is temporarily unavailable."}
    except (KeyError, ValueError, TypeError) as e:
        print("FORECAST DATA ERROR:", repr(e))
        return {"error": "Weather forecast data could not be read."}


def get_forecast_day(forecast_data: dict, target_date: str):
    for day in forecast_data.get("forecast", []):
        if day["date"] == target_date:
            return day
    return None
