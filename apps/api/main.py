from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from .routers.homequest import router as homequest_router

app = FastAPI(title="RainCheck API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(homequest_router)

class Health(BaseModel):
    status: str
    api_port: int
    env: str

@app.get("/health", response_model=Health)
def health():
    return Health(
        status="ok",
        api_port=int(os.getenv("API_PORT", "8000")),
        env=os.getenv("ENV", "dev"),
    )
