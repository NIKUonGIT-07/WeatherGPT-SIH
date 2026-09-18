from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models.user import User

from app.routers import auth, chat, alerts, weather, forecast
from app.services.gemini_nlu import understand_weather_query

app = FastAPI(
    title="Raikyn AI API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # We'll lock this down later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(alerts.router)
app.include_router(weather.router)
app.include_router(forecast.router)

@app.get("/")
def root():
    return {
        "project": "Raikyn AI",
        "status": "Running 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/nlu-test")
def nlu_test():

    result = understand_weather_query(
        "What's the weather like in Guwahati?"
)

    return result