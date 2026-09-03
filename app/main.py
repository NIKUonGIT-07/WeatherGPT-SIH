from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, chat, weather, forecast

app = FastAPI(
    title="Raikyn AI API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # We'll lock this down later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
# app.include_router(alerts.router)
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