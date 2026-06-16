import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ParkSense AI"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://parksense:parksense123@localhost:5432/parksense_db"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8-hour shift

    # Mapbox
    MAPBOX_TOKEN: str = os.getenv("MAPBOX_TOKEN", "")

    # ML
    MODEL_PATH: str = os.getenv("MODEL_PATH", "../models")
    RETRAIN_INTERVAL_DAYS: int = 7

    # Spatial
    BENGALURU_BBOX: dict = {
        "lat_min": 12.80, "lat_max": 13.30,
        "lon_min": 77.44, "lon_max": 77.78,
    }
    H3_RESOLUTION: int = 7          # ~460m cells
    DBSCAN_EPS_DEGREES: float = 0.0015  # ~150m
    DBSCAN_MIN_SAMPLES: int = 25

    class Config:
        env_file = ".env"

settings = Settings()
