"""
Risk analysis engine for calculating player fatigue and fan safety risks
"""
import math
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class RiskEngine:
    """Engine for calculating heat-related risks for players and fans"""
    
    def __init__(self):
        self.config = settings
    
    def calculate_player_risk(
        self,
        weather_data: Dict[str, Any],
        match_duration: int = 90,
        pitch_zones: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate player fatigue and stress risk
        
        Args:
            weather_data: Weather conditions
            match_duration: Match duration in minutes
            pitch_zones: Pitch zone definitions
        
        Returns:
            Risk analysis with score and level
        """
        temp = weather_data.get("temperature", 25)
        humidity = weather_data.get("humidity", 50)
        heat_index = weather_data.get("heat_index", temp)
        wind_speed = weather_data.get("wind_speed", 0)
        uv_index = weather_data.get("uv_index", 5)
        
        # Base risk from heat index
        heat_risk = self._calculate_heat_risk(heat_index)
        
        # Humidity impact (higher humidity = worse heat dissipation)
        humidity_factor = self._calculate_humidity_factor(humidity)
        
        # Physical exertion multiplier for players
        exertion_multiplier = 1.5
        
        # Wind cooling effect (negative factor)
        wind_factor = max(0, 1 - (wind_speed * 0.05))
        
        # UV exposure (additional stress)
        uv_factor = self._calculate_uv_factor(uv_index)
        
        # Match duration impact
        duration_factor = match_duration / 90.0
        
        # Calculate overall player risk score (0-100)
        risk_score = (
            heat_risk * 0.4 +
            humidity_factor * 0.25 +
            uv_factor * 0.15 +
            (exertion_multiplier * 10) * 0.2
        ) * wind_factor * duration_factor
        
        risk_score = min(100, max(0, risk_score))
        
        # Determine risk level
        risk_level = self._get_risk_level(
            risk_score,
            self.config.PLAYER_FATIGUE_MODERATE,
            self.config.PLAYER_FATIGUE_HIGH,
            self.config.PLAYER_FATIGUE_CRITICAL
        )
        
        # Calculate zone-specific risks if pitch zones provided
        zone_risks = {}
        if pitch_zones:
            zone_risks = self._calculate_pitch_zone_risks(
                pitch_zones,
                weather_data,
                risk_score
            )
        
        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "heat_stress_factor": round(heat_risk, 2),
            "humidity_factor": round(humidity_factor, 2),
            "uv_factor": round(uv_factor, 2),
            "wind_factor": round(wind_factor, 2),
            "zone_risks": zone_risks,
            "cooling_breaks_recommended": risk_score > self.config.PLAYER_FATIGUE_HIGH
        }
    
    def calculate_fan_risk(
        self,
        weather_data: Dict[str, Any],
        seating_blocks: Dict[str, Any] = None,
        sun_exposed_areas: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate fan heat exposure and safety risk
        
        Args:
            weather_data: Weather conditions
            seating_blocks: Seating block definitions
            sun_exposed_areas: Sun exposure data
        
        Returns:
            Risk analysis with score and level
        """
        temp = weather_data.get("temperature", 25)
        humidity = weather_data.get("humidity", 50)
        heat_index = weather_data.get("heat_index", temp)
        uv_index = weather_data.get("uv_index", 5)
        cloud_cover = weather_data.get("cloud_cover", 50)
        
        # Base risk from heat index
        heat_risk = self._calculate_heat_risk(heat_index)
        
        # Humidity impact
        humidity_factor = self._calculate_humidity_factor(humidity)
        
        # UV exposure (fans are stationary, more vulnerable)
        uv_factor = self._calculate_uv_factor(uv_index) * 1.2
        
        # Cloud cover provides some protection
        cloud_protection = cloud_cover / 100.0 * 0.2
        
        # Fans are less active but exposed longer
        exposure_multiplier = 1.2
        
        # Calculate overall fan risk score (0-100)
        risk_score = (
            heat_risk * 0.45 +
            humidity_factor * 0.25 +
            uv_factor * 0.3
        ) * exposure_multiplier * (1 - cloud_protection)
        
        risk_score = min(100, max(0, risk_score))
        
        # Determine risk level
        risk_level = self._get_risk_level(
            risk_score,
            self.config.FAN_RISK_MODERATE,
            self.config.FAN_RISK_HIGH,
            self.config.FAN_RISK_CRITICAL
        )
        
        # Calculate zone-specific risks if seating data provided
        zone_risks = {}
        if seating_blocks and sun_exposed_areas:
            zone_risks = self._calculate_seating_zone_risks(
                seating_blocks,
                sun_exposed_areas,
                weather_data,
                risk_score
            )
        
        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "heat_stress_factor": round(heat_risk, 2),
            "humidity_factor": round(humidity_factor, 2),
            "uv_factor": round(uv_factor, 2),
            "zone_risks": zone_risks,
            "high_risk_zones": [
                zone_id for zone_id, data in zone_risks.items()
                if data["risk_score"] > self.config.FAN_RISK_HIGH
            ]
        }
    
    def _calculate_heat_risk(self, heat_index: float) -> float:
        """
        Calculate risk from heat index
        
        Args:
            heat_index: Heat index in Celsius
        
        Returns:
            Risk score (0-100)
        """
        if heat_index < self.config.HEAT_INDEX_LOW:
            return 10
        elif heat_index < self.config.HEAT_INDEX_MODERATE:
            return 10 + (heat_index - self.config.HEAT_INDEX_LOW) * 3
        elif heat_index < self.config.HEAT_INDEX_HIGH:
            return 40 + (heat_index - self.config.HEAT_INDEX_MODERATE) * 4
        elif heat_index < self.config.HEAT_INDEX_CRITICAL:
            return 70 + (heat_index - self.config.HEAT_INDEX_HIGH) * 2.5
        else:
            return 100
    
    def _calculate_humidity_factor(self, humidity: float) -> float:
        """
        Calculate risk factor from humidity
        
        Args:
            humidity: Relative humidity (0-100)
        
        Returns:
            Risk factor (0-100)
        """
        if humidity < self.config.HUMIDITY_THRESHOLD:
            return humidity * 0.5
        else:
            return 30 + (humidity - self.config.HUMIDITY_THRESHOLD) * 1.5
    
    def _calculate_uv_factor(self, uv_index: float) -> float:
        """
        Calculate risk factor from UV index
        
        Args:
            uv_index: UV index value
        
        Returns:
            Risk factor (0-100)
        """
        if uv_index < self.config.UV_INDEX_HIGH:
            return uv_index * 3
        elif uv_index < self.config.UV_INDEX_VERY_HIGH:
            return 18 + (uv_index - self.config.UV_INDEX_HIGH) * 8
        elif uv_index < self.config.UV_INDEX_EXTREME:
            return 34 + (uv_index - self.config.UV_INDEX_VERY_HIGH) * 12
        else:
            return min(100, 70 + (uv_index - self.config.UV_INDEX_EXTREME) * 10)
    
    def _get_risk_level(
        self,
        score: float,
        moderate_threshold: float,
        high_threshold: float,
        critical_threshold: float
    ) -> str:
        """
        Determine risk level from score
        
        Args:
            score: Risk score
            moderate_threshold: Threshold for moderate risk
            high_threshold: Threshold for high risk
            critical_threshold: Threshold for critical risk
        
        Returns:
            Risk level string
        """
        if score < moderate_threshold:
            return "low"
        elif score < high_threshold:
            return "moderate"
        elif score < critical_threshold:
            return "high"
        else:
            return "critical"
    
    def _calculate_pitch_zone_risks(
        self,
        pitch_zones: Dict[str, Any],
        weather_data: Dict[str, Any],
        base_risk: float
    ) -> Dict[str, Any]:
        """
        Calculate risk for each pitch zone
        
        Args:
            pitch_zones: Pitch zone definitions
            weather_data: Weather conditions
            base_risk: Base risk score
        
        Returns:
            Dictionary of zone risks
        """
        zone_risks = {}
        
        for zone_id, zone_data in pitch_zones.items():
            # Adjust risk based on zone characteristics
            sun_exposure = zone_data.get("sun_exposure", 0.5)
            airflow = zone_data.get("airflow_quality", 0.5)
            
            # Higher sun exposure increases risk
            zone_risk = base_risk * (0.8 + sun_exposure * 0.4)
            
            # Better airflow reduces risk
            zone_risk *= (1.2 - airflow * 0.4)
            
            zone_risk = min(100, max(0, zone_risk))
            
            zone_risks[zone_id] = {
                "zone_name": zone_data.get("name", zone_id),
                "risk_score": round(zone_risk, 2),
                "risk_level": self._get_risk_level(
                    zone_risk,
                    self.config.PLAYER_FATIGUE_MODERATE,
                    self.config.PLAYER_FATIGUE_HIGH,
                    self.config.PLAYER_FATIGUE_CRITICAL
                ),
                "sun_exposure": sun_exposure,
                "airflow_quality": airflow
            }
        
        return zone_risks
    
    def _calculate_seating_zone_risks(
        self,
        seating_blocks: Dict[str, Any],
        sun_exposed_areas: Dict[str, Any],
        weather_data: Dict[str, Any],
        base_risk: float
    ) -> Dict[str, Any]:
        """
        Calculate risk for each seating zone
        
        Args:
            seating_blocks: Seating block definitions
            sun_exposed_areas: Sun exposure data
            weather_data: Weather conditions
            base_risk: Base risk score
        
        Returns:
            Dictionary of zone risks
        """
        zone_risks = {}
        
        for block_id, block_data in seating_blocks.items():
            # Check if block is in sun-exposed areas
            is_exposed = block_id in sun_exposed_areas
            sun_exposure = 0.8 if is_exposed else 0.3
            
            # Get airflow and roof coverage
            airflow = block_data.get("airflow_quality", 0.5)
            has_roof = block_data.get("has_roof", False)
            
            # Calculate zone-specific risk
            zone_risk = base_risk * (0.7 + sun_exposure * 0.6)
            
            # Roof provides protection
            if has_roof:
                zone_risk *= 0.6
            
            # Better airflow reduces risk
            zone_risk *= (1.3 - airflow * 0.6)
            
            zone_risk = min(100, max(0, zone_risk))
            
            zone_risks[block_id] = {
                "zone_name": block_data.get("name", block_id),
                "risk_score": round(zone_risk, 2),
                "risk_level": self._get_risk_level(
                    zone_risk,
                    self.config.FAN_RISK_MODERATE,
                    self.config.FAN_RISK_HIGH,
                    self.config.FAN_RISK_CRITICAL
                ),
                "sun_exposure": sun_exposure,
                "airflow_quality": airflow,
                "has_roof": has_roof
            }
        
        return zone_risks


# Global risk engine instance
risk_engine = RiskEngine()
