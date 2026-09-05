from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError, AuthenticationError, APIError

load_dotenv()

client = OpenAI()


def build_ai_weather_response(user_message: str, weather_text: str) -> str:
    try:
        response = client.responses.create(
            model="gpt-5-mini",
            input=f"""
You are WeatherGPT, a simple weather assistant.

User asked:
{user_message}

Weather data:
{weather_text}

Reply in simple language.
Keep it short.
Give practical advice.
Do not invent weather data.
"""
        )

        return response.output_text

    except RateLimitError:
        return weather_text

    except AuthenticationError:
        return weather_text

    except APIError:
        return weather_text

    except Exception:
        return weather_text