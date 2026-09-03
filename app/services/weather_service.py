import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Weather Code Mapping
WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    80: "Rain Showers",
    81: "Heavy Rain Showers",
    82: "Violent Rain Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Hail",
    99: "Severe Thunderstorm with Hail"
}


def get_current_weather(city: str):

    # -----------------------------
    # Step 1: Get Latitude & Longitude
    # -----------------------------
    geo_response = requests.get(
        GEOCODING_URL,
        params={
            "name": city,
            "count": 1
        }
    )

    geo_data = geo_response.json()

    if "results" not in geo_data:
        return {
            "error": "City not found"
        }

    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # -----------------------------
    # Step 2: Get Current Weather
    # -----------------------------
    weather_response = requests.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
        }
    )

    weather_data = weather_response.json()

    current = weather_data["current"]

    weather_code = current["weather_code"]

    # -----------------------------
    # Step 3: Return Structured Data
    # -----------------------------
    return {

        "city": location["name"],
        "country": location.get("country", ""),

        "latitude": latitude,
        "longitude": longitude,

        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],

        "weather_code": weather_code,
        "condition": WEATHER_CODES.get(
            weather_code,
            "Unknown"
        ),

        "time": current["time"]
    }