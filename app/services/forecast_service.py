import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

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


def get_forecast(city: str):

    # -----------------------------------
    # Get Latitude & Longitude
    # -----------------------------------

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

    # -----------------------------------
    # Get 5-Day Forecast
    # -----------------------------------

    weather_response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "forecast_days": 5
        }
    )

    weather_data = weather_response.json()["daily"]

    forecast = []

    for i in range(len(weather_data["time"])):

        weather_code = weather_data["weather_code"][i]

        forecast.append({

            "date": weather_data["time"][i],

            "condition": WEATHER_CODES.get(
                weather_code,
                "Unknown"
            ),

            "max_temp": weather_data["temperature_2m_max"][i],

            "min_temp": weather_data["temperature_2m_min"][i]

        })

    return {
        "city": location["name"],
        "country": location.get("country", ""),
        "forecast": forecast
    }