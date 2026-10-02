"""
Sight Companion API
AI backend for visually impaired users — scene description, text reading, tutor.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import vision, education

# Configure basic structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sight_companion")

app = FastAPI(
    title="Sight Companion API",
    description=(
        "AI backend for people who are blind or have low vision. "
        "Provides scene description, text reading, visual Q&A, and study tutor."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vision.router)
app.include_router(education.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "Sight Companion API", "version": "0.1.0"}


@app.get("/")
def root():
    return {
        "message": "Sight Companion API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "vision": [
                "POST /vision/describe-scene",
                "POST /vision/read-text",
                "POST /vision/ask-about-image",
            ],
            "education": [
                "POST /education/tutor",
                "POST /education/generate-quiz",
            ],
        },
    }
