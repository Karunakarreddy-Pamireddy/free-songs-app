import os
from dotenv import load_dotenv

# Find the path to the backend/.env file dynamically
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, ".env"))

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "DEV_FALLBACK_KEY_DO_NOT_USE_IN_PROD")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
    SONGS_DIR: str = os.getenv("SONGS_DIR", "../storage/uploaded_songs")
    ANALYTICS_FILE: str = os.getenv("ANALYTICS_FILE", "../storage/data/analytics.csv")

settings = Settings()