import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    DOCKER_CONTAINER = os.environ.get("DOCKER_CONTAINER")

    if DOCKER_CONTAINER:
        SQLALCHEMY_DATABASE_URI = (
            os.environ.get("SQLALCHEMY_DATABASE_URI_DOCKER")
            or "sqlite:////data/chat.db"
        )
        OLLAMA_BASE_URL = (
            os.environ.get("OLLAMA_BASE_URL_DOCKER")
            or "http://host.docker.internal:11434"
        )
    else:
        SQLALCHEMY_DATABASE_URI = (
            os.environ.get("SQLALCHEMY_DATABASE_URI_LOCAL")
            or "sqlite:///../../data/chat.db"
        )
        OLLAMA_BASE_URL = (
            os.environ.get("OLLAMA_BASE_URL_LOCAL") or "http://localhost:11434"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APP_DEBUG = os.environ.get("APP_DEBUG", "false").lower() in ("true", "1", "t")
