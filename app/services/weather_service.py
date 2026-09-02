import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_current_weather(city: str):
    # Get latitude and longitude
    geo = requests.get(
        GEOCODING_URL,
        params={"name": city, "count": 1}
    )

    geo_data = geo.json()

    if "results" not in geo_data:
        return {"error": "City not found"}

    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # Get weather
    weather = requests.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m"
        }
    )

    weather_data = weather.json()

    return {
        "city": city,
        "temperature": weather_data["current"]["temperature_2m"],
        "wind_speed": weather_data["current"]["wind_speed_10m"]
    }