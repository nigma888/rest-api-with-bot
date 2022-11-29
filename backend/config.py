import os


class Config:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME = os.getenv("DB_NAME", "landing")
    DB_HOST = os.getenv("DB_HOST", "db")
    # DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_CONFIG = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

    # API_HOST = os.getenv("API_HOST", "localhost")
    # API_PORT = os.getenv("API_PORT", "8000")

    ADMIN_URL = os.getenv(
        "ADMIN_URL", "example"
    )  # Формирование ссылки в боте {ADMIN_URL}+token

    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    BOT_WS_URL = os.getenv("BOT_WS_URL", "ws://localhost:8000/ws/article")
    SECRET_TOKEN_WS = os.getenv("SECRET_TOKEN_WS", "")
