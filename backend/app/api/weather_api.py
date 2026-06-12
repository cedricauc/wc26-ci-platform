"""
Weather api for fetching and processing weather data from OpenWeather API
"""
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class WeatherApi:
    """Service for interacting with OpenWeather API"""
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _calculate_heat_index(self, temp_c: float, humidity: float) -> float:
        """
        Calculate heat index (feels like temperature) using Steadman's formula
        
        Args:
            temp_c: Temperature in Celsius
            humidity: Relative humidity (0-100)
        
        Returns:
            Heat index in Celsius
        """
        # Convert to Fahrenheit for calculation
        temp_f = (temp_c * 9/5) + 32
        
        # Steadman's formula
        if temp_f < 80:
            return temp_c
        
        hi = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
        hi -= 0.22475541 * temp_f * humidity
        hi -= 0.00683783 * temp_f * temp_f
        hi -= 0.05481717 * humidity * humidity
        hi += 0.00122874 * temp_f * temp_f * humidity
        hi += 0.00085282 * temp_f * humidity * humidity
        hi -= 0.00000199 * temp_f * temp_f * humidity * humidity
        
        # Convert back to Celsius
        heat_index_c = (hi - 32) * 5/9
        
        return round(heat_index_c, 2)
    
    async def get_current_weather(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """
        Get current weather for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
        
        Returns:
            Weather data dictionary or None if error
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant data
            weather_data = {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"].get("deg"),
                "cloud_cover": data["clouds"]["all"],
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "timestamp": datetime.fromtimestamp(data["dt"]),
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"])
            }
            
            # Calculate heat index
            weather_data["heat_index"] = self._calculate_heat_index(
                weather_data["temperature"],
                weather_data["humidity"]
            )
            
            return weather_data
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching current weather: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return None
    
    async def get_forecast(
        self, 
        latitude: float, 
        longitude: float,
        target_time: Optional[datetime] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get weather forecast for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            target_time: Specific time to get forecast for (optional)
        
        Returns:
            List of forecast data or None if error
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            forecasts = []
            for item in data["list"]:
                forecast = {
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "pressure": item["main"]["pressure"],
                    "wind_speed": item["wind"]["speed"],
                    "wind_direction": item["wind"].get("deg"),
                    "cloud_cover": item["clouds"]["all"],
                    "precipitation": item.get("rain", {}).get("3h", 0),
                    "condition": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "forecast_time": datetime.fromtimestamp(item["dt"]),
                    "pop": item.get("pop", 0) * 100  # Probability of precipitation
                }
                
                # Calculate heat index
                forecast["heat_index"] = self._calculate_heat_index(
                    forecast["temperature"],
                    forecast["humidity"]
                )
                
                forecasts.append(forecast)
            
            # If target time specified, find closest forecast
            if target_time:
                closest = min(
                    forecasts,
                    key=lambda x: abs((x["forecast_time"] - target_time).total_seconds())
                )
                return [closest]
            
            return forecasts
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching forecast: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return None
    
    async def get_uv_index(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[float]:
        """
        Get UV index for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
        
        Returns:
            UV index value or None if error
        """
        try:
            url = f"{self.base_url}/uvi"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get("value")
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching UV index: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching UV index: {e}")
            return None
    
    async def get_match_weather(
        self,
        latitude: float,
        longitude: float,
        match_time: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Get weather data for a specific match time
        
        Args:
            latitude: Stadium latitude
            longitude: Stadium longitude
            match_time: Match kickoff time
        
        Returns:
            Weather data for the match or None if error
        """
        time_until_match = (match_time - datetime.utcnow()).total_seconds()
        
        # If match is more than 5 days away, use historical climate data
        if time_until_match > 5 * 24 * 3600:
            logger.info(f"Match too far in future, using climate prediction")
            return await self._get_climate_prediction(latitude, longitude, match_time)
        
        # If match is within forecast range, get forecast
        forecasts = await self.get_forecast(latitude, longitude, match_time)
        if forecasts and len(forecasts) > 0:
            forecast = forecasts[0]
            
            # Get UV index
            uv_index = await self.get_uv_index(latitude, longitude)
            if uv_index:
                forecast["uv_index"] = uv_index
            
            return forecast
        
        return None
    
    async def _get_climate_prediction(
        self,
        latitude: float,
        longitude: float,
        match_time: datetime
    ) -> Dict[str, Any]:
        """
        Predict weather based on historical climate data
        This is a simplified version - in production, use historical weather API
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            match_time: Target time
        
        Returns:
            Predicted weather data
        """
        # Simplified climate model based on latitude and month
        month = match_time.month
        
        # Base temperature estimation (very simplified)
        if abs(latitude) < 23.5:  # Tropics
            base_temp = 28 + (month - 6) * 2
        elif abs(latitude) < 45:  # Temperate
            base_temp = 20 + (month - 6) * 3
        else:  # Polar
            base_temp = 10 + (month - 6) * 4
        
        return {
            "temperature": base_temp,
            "feels_like": base_temp + 2,
            "humidity": 60,
            "heat_index": self._calculate_heat_index(base_temp, 60),
            "wind_speed": 3.0,
            "wind_direction": 180,
            "cloud_cover": 40,
            "precipitation": 0,
            "condition": "Clear",
            "description": "Predicted based on climate patterns",
            "forecast_time": match_time,
            "uv_index": 6.0,
            "is_prediction": True
        }


# Global weather api instance
weather_api = WeatherApi()

