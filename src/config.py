import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    DOCKER_CONTAINER = os.environ.get("DOCKER_CONTAINER")
    if DOCKER_CONTAINER:
        SQLALCHEMY_DATABASE_URI = (
            os.environ.get("SQLALCHEMY_DATABASE_URI") or "sqlite:////data/chat.db"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///../../data/chat.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL") or "http://localhost:11434"

    APP_DEBUG = os.environ.get("APP_DEBUG", "false").lower() in ("true", "1", "t")
