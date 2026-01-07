import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, PostgresDsn

load_dotenv(os.getenv("ENV_FILE", ".env"))


class Config:
    # Basic project configs
    BASE_DIR = str(Path(os.path.dirname(__file__)).parent)
    PROJECT_NAME: str = "Markme - Online Attendance Systems"
    CONTACT_EMAIL: str = os.environ["CONTACT_EMAIL"]
    PROJECT_DESCRIPTION: str = f"""
        {PROJECT_NAME} API document.
        Contact us at {CONTACT_EMAIL}
    """

    # Server configs
    LOG_LEVEL: str = os.environ["LOG_LEVEL"]
    DEPLOYMENT_ENV: str = os.environ["DEPLOYMENT_ENV"]
    SERVER_PORT: Optional[int] = os.environ["SERVER_PORT"]
    SERVER_HOST: Optional[str or AnyHttpUrl] = os.environ["SERVER_HOST"]
    TERMS_OF_SERVICE: str = os.environ["TERMS_OF_SERVICE"]

    if DEPLOYMENT_ENV == "DEV":
        BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
            "http://localhost.tiangolo.com",
            "https://localhost.tiangolo.com",
            "http://localhost:3000",
            "http://localhost:8080",
            "http://localhost:5173",
            "https://mark-me-backend.onrender.com",
            "https://mark-me-frontend-ibefewd5g-monils-projects-d77ced3c.vercel.app",
            "https://mark-me-frontend.vercel.app"
        ]
    else:
        BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @staticmethod
    def assemble_db_connection():
        return PostgresDsn.build(
            scheme="postgresql",
            username=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            port=int(os.environ["POSTGRES_PORT"]),
            host=os.environ["POSTGRES_SERVER"],
            path=os.environ["POSTGRES_DB"] or "",
        ).unicode_string()

    # =============================== User Domain Config =========================================
    JWT_ALGORITHM: str = os.environ["JWT_ALGORITHM"]
    JWT_SECRET_KEY: str = os.environ["JWT_SECRET_KEY"]
    JWT_EXPIRATION_TIME: int = os.environ["JWT_EXPIRATION_TIME"]

    # Brevo SMTP
    BREVO_URL: str = os.environ["BREVO_URL"]
    BREVO_API_KEY: str = os.environ["BREVO_API_KEY"]
    BREVO_SENDER_EMAIL: str = os.environ["BREVO_SENDER_EMAIL"]
