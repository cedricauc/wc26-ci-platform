"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "HeatAware Hub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/heataware"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    
    # OpenWeather API
    OPENWEATHER_API_KEY: str
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    OPENWEATHER_RATE_LIMIT: int = 60  # calls per minute
    
    # Weather refresh intervals (seconds)
    WEATHER_REFRESH_INTERVAL: int = 600  # 10 minutes
    WEATHER_FORECAST_REFRESH: int = 3600  # 1 hour
    
    # Risk thresholds
    HEAT_INDEX_LOW: float = 27.0  # °C
    HEAT_INDEX_MODERATE: float = 32.0  # °C
    HEAT_INDEX_HIGH: float = 39.0  # °C
    HEAT_INDEX_CRITICAL: float = 51.0  # °C
    
    HUMIDITY_THRESHOLD: float = 60.0  # %
    UV_INDEX_HIGH: float = 6.0
    UV_INDEX_VERY_HIGH: float = 8.0
    UV_INDEX_EXTREME: float = 11.0
    
    # Player performance thresholds
    PLAYER_FATIGUE_MODERATE: float = 40.0
    PLAYER_FATIGUE_HIGH: float = 65.0
    PLAYER_FATIGUE_CRITICAL: float = 85.0
    
    # Fan safety thresholds
    FAN_RISK_MODERATE: float = 35.0
    FAN_RISK_HIGH: float = 60.0
    FAN_RISK_CRITICAL: float = 80.0
    
    # Match settings
    MATCH_DURATION_MINUTES: int = 90
    HALFTIME_DURATION_MINUTES: int = 15
    COOLING_BREAK_THRESHOLD_TEMP: float = 32.0  # °C
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:8000"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
