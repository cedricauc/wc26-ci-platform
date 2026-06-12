"""
Recommendations engine for generating player and fan guidance
"""
from typing import Dict, Any, List
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class RecommendationsEngine:
    """Engine for generating heat-related recommendations"""
    
    def __init__(self):
        self.config = settings
    
    def generate_player_recommendations(
        self,
        risk_analysis: Dict[str, Any],
        weather_data: Dict[str, Any],
        match_time: str
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations for players
        
        Args:
            risk_analysis: Player risk analysis results
            weather_data: Weather conditions
            match_time: Match kickoff time
        
        Returns:
            List of recommendations
        """
        recommendations = []
        risk_score = risk_analysis.get("risk_score", 0)
        risk_level = risk_analysis.get("risk_level", "low")
        temp = weather_data.get("temperature", 25)
        humidity = weather_data.get("humidity", 50)
        heat_index = weather_data.get("heat_index", temp)
        
        # Hydration recommendations
        if risk_score > 30:
            hydration_rec = self._generate_hydration_recommendation(
                risk_level, temp, humidity
            )
            recommendations.append(hydration_rec)
        
        # Cooling break recommendations
        if risk_analysis.get("cooling_breaks_recommended", False):
            cooling_rec = self._generate_cooling_break_recommendation(
                risk_level, heat_index
            )
            recommendations.append(cooling_rec)
        
        # Pre-match preparation
        if risk_score > 40:
            prep_rec = self._generate_prematch_recommendation(risk_level)
            recommendations.append(prep_rec)
        
        # Tactical adjustments
        if risk_score > 60:
            tactical_rec = self._generate_tactical_recommendation(risk_level)
            recommendations.append(tactical_rec)
        
        # Recovery recommendations
        if risk_score > 50:
            recovery_rec = self._generate_recovery_recommendation(risk_level)
            recommendations.append(recovery_rec)
        
        # Zone-specific warnings
        zone_risks = risk_analysis.get("zone_risks", {})
        if zone_risks:
            zone_rec = self._generate_zone_recommendation(zone_risks)
            if zone_rec:
                recommendations.append(zone_rec)
        
        return recommendations
    
    def generate_fan_recommendations(
        self,
        risk_analysis: Dict[str, Any],
        weather_data: Dict[str, Any],
        match_time: str
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations for fans
        
        Args:
            risk_analysis: Fan risk analysis results
            weather_data: Weather conditions
            match_time: Match kickoff time
        
        Returns:
            List of recommendations
        """
        recommendations = []
        risk_score = risk_analysis.get("risk_score", 0)
        risk_level = risk_analysis.get("risk_level", "low")
        temp = weather_data.get("temperature", 25)
        uv_index = weather_data.get("uv_index", 5)
        
        # General safety recommendations
        if risk_score > 35:
            safety_rec = self._generate_fan_safety_recommendation(
                risk_level, temp
            )
            recommendations.append(safety_rec)
        
        # Hydration for fans
        if risk_score > 30:
            hydration_rec = self._generate_fan_hydration_recommendation(
                risk_level, temp
            )
            recommendations.append(hydration_rec)
        
        # Sun protection
        if uv_index > self.config.UV_INDEX_HIGH:
            sun_rec = self._generate_sun_protection_recommendation(uv_index)
            recommendations.append(sun_rec)
        
        # Arrival time recommendations
        if risk_score > 50:
            arrival_rec = self._generate_arrival_time_recommendation(
                risk_level, match_time
            )
            recommendations.append(arrival_rec)
        
        # High-risk seating alerts
        high_risk_zones = risk_analysis.get("high_risk_zones", [])
        if high_risk_zones:
            seating_rec = self._generate_seating_alert(high_risk_zones)
            recommendations.append(seating_rec)
        
        # Clothing recommendations
        if risk_score > 40:
            clothing_rec = self._generate_clothing_recommendation(risk_level)
            recommendations.append(clothing_rec)
        
        return recommendations
    
    def _generate_hydration_recommendation(
        self,
        risk_level: str,
        temp: float,
        humidity: float
    ) -> Dict[str, Any]:
        """Generate hydration recommendation for players"""
        if risk_level == "critical":
            return {
                "target": "player",
                "category": "hydration",
                "priority": "critical",
                "title": "Critical Hydration Protocol",
                "description": f"Extreme conditions ({temp}°C, {humidity}% humidity). Implement aggressive hydration strategy.",
                "details": {
                    "pre_match": "500ml 2 hours before, 250ml 15 minutes before",
                    "during_match": "150-200ml every 15 minutes",
                    "halftime": "400-500ml with electrolytes",
                    "post_match": "1.5L within first hour"
                },
                "timing": "Start 2 hours before kickoff"
            }
        elif risk_level == "high":
            return {
                "target": "player",
                "category": "hydration",
                "priority": "high",
                "title": "Enhanced Hydration Required",
                "description": f"High heat conditions ({temp}°C). Increase fluid intake significantly.",
                "details": {
                    "pre_match": "400ml 2 hours before, 200ml 15 minutes before",
                    "during_match": "100-150ml every 15 minutes",
                    "halftime": "300-400ml with electrolytes"
                },
                "timing": "Start 2 hours before kickoff"
            }
        else:
            return {
                "target": "player",
                "category": "hydration",
                "priority": "medium",
                "title": "Standard Hydration Protocol",
                "description": f"Moderate conditions ({temp}°C). Maintain regular hydration.",
                "details": {
                    "pre_match": "300ml 1 hour before",
                    "during_match": "100ml every 20 minutes",
                    "halftime": "250ml"
                },
                "timing": "Start 1 hour before kickoff"
            }
    
    def _generate_cooling_break_recommendation(
        self,
        risk_level: str,
        heat_index: float
    ) -> Dict[str, Any]:
        """Generate cooling break recommendation"""
        if risk_level == "critical":
            return {
                "target": "player",
                "category": "cooling",
                "priority": "critical",
                "title": "Mandatory Cooling Breaks",
                "description": f"Heat index {heat_index}°C requires cooling breaks.",
                "details": {
                    "frequency": "Every 20-25 minutes",
                    "duration": "90-120 seconds",
                    "actions": [
                        "Move to shaded area",
                        "Apply cooling towels to neck and head",
                        "Drink cold fluids",
                        "Use cooling vests if available"
                    ]
                },
                "timing": "25th and 70th minute minimum"
            }
        else:
            return {
                "target": "player",
                "category": "cooling",
                "priority": "high",
                "title": "Cooling Breaks Recommended",
                "description": f"Heat index {heat_index}°C suggests cooling breaks.",
                "details": {
                    "frequency": "At natural stoppages",
                    "duration": "60 seconds",
                    "actions": [
                        "Seek shade when possible",
                        "Use cooling towels",
                        "Hydrate"
                    ]
                },
                "timing": "Halftime and as needed"
            }
    
    def _generate_prematch_recommendation(
        self,
        risk_level: str
    ) -> Dict[str, Any]:
        """Generate pre-match preparation recommendation"""
        return {
            "target": "player",
            "category": "preparation",
            "priority": "high" if risk_level in ["high", "critical"] else "medium",
            "title": "Pre-Match Heat Preparation",
            "description": "Optimize body for heat stress before kickoff.",
            "details": {
                "timing": "2-3 hours before match",
                "actions": [
                    "Stay in air-conditioned environment",
                    "Light pre-cooling (cold towels)",
                    "Avoid direct sun exposure",
                    "Consume light, easily digestible meal",
                    "Begin hydration protocol"
                ]
            },
            "timing": "2-3 hours before kickoff"
        }
    
    def _generate_tactical_recommendation(
        self,
        risk_level: str
    ) -> Dict[str, Any]:
        """Generate tactical adjustment recommendation"""
        return {
            "target": "player",
            "category": "tactical",
            "priority": "high",
            "title": "Tactical Adjustments for Heat",
            "description": "Modify playing style to manage heat stress.",
            "details": {
                "tempo": "Reduce overall tempo by 10-15%",
                "pressing": "Limit high-intensity pressing periods",
                "rotation": "Increase substitution frequency",
                "positioning": "Utilize shaded areas when possible",
                "recovery": "Take advantage of all stoppages"
            },
            "timing": "Throughout match"
        }
    
    def _generate_recovery_recommendation(
        self,
        risk_level: str
    ) -> Dict[str, Any]:
        """Generate post-match recovery recommendation"""
        return {
            "target": "player",
            "category": "recovery",
            "priority": "high" if risk_level == "critical" else "medium",
            "title": "Post-Match Heat Recovery",
            "description": "Critical recovery protocol after heat exposure.",
            "details": {
                "immediate": [
                    "Move to cool environment",
                    "Continue hydration (1.5L in first hour)",
                    "Cold water immersion if available",
                    "Monitor for heat illness symptoms"
                ],
                "24_hours": [
                    "Maintain elevated hydration",
                    "Light recovery activities only",
                    "Monitor body temperature",
                    "Ensure adequate sleep"
                ]
            },
            "timing": "Immediately after final whistle"
        }
    
    def _generate_zone_recommendation(
        self,
        zone_risks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate zone-specific recommendation"""
        high_risk_zones = [
            zone_id for zone_id, data in zone_risks.items()
            if data.get("risk_score", 0) > 70
        ]
        
        if not high_risk_zones:
            return None
        
        return {
            "target": "player",
            "category": "tactical",
            "priority": "medium",
            "title": "High-Risk Pitch Zones",
            "description": f"Zones {', '.join(high_risk_zones)} have elevated heat risk.",
            "details": {
                "zones": high_risk_zones,
                "guidance": "Minimize time in these areas, rotate positions more frequently"
            },
            "timing": "Throughout match"
        }
    
    def _generate_fan_safety_recommendation(
        self,
        risk_level: str,
        temp: float
    ) -> Dict[str, Any]:
        """Generate general safety recommendation for fans"""
        if risk_level in ["high", "critical"]:
            return {
                "target": "fan",
                "category": "safety",
                "priority": "high",
                "title": "Heat Safety Alert",
                "description": f"High temperatures ({temp}°C) pose health risks. Take precautions.",
                "details": {
                    "actions": [
                        "Stay hydrated throughout the match",
                        "Seek shade during breaks",
                        "Watch for heat illness symptoms",
                        "Take breaks in air-conditioned areas",
                        "Avoid alcohol consumption"
                    ],
                    "warning_signs": [
                        "Dizziness or lightheadedness",
                        "Excessive sweating or no sweating",
                        "Nausea",
                        "Rapid heartbeat",
                        "Confusion"
                    ]
                },
                "timing": "Throughout match"
            }
        else:
            return {
                "target": "fan",
                "category": "safety",
                "priority": "medium",
                "title": "Heat Awareness",
                "description": f"Warm conditions ({temp}°C). Stay comfortable and hydrated.",
                "details": {
                    "actions": [
                        "Drink water regularly",
                        "Wear light clothing",
                        "Use sun protection"
                    ]
                },
                "timing": "Throughout match"
            }
    
    def _generate_fan_hydration_recommendation(
        self,
        risk_level: str,
        temp: float
    ) -> Dict[str, Any]:
        """Generate hydration recommendation for fans"""
        return {
            "target": "fan",
            "category": "hydration",
            "priority": "high" if risk_level in ["high", "critical"] else "medium",
            "title": "Fan Hydration Guide",
            "description": f"Stay hydrated in {temp}°C conditions.",
            "details": {
                "before_match": "Drink 500ml water before entering stadium",
                "during_match": "250ml every 30 minutes minimum",
                "recommendations": [
                    "Bring refillable water bottle",
                    "Locate water fountains upon arrival",
                    "Avoid excessive caffeine and alcohol",
                    "Choose water over sugary drinks"
                ]
            },
            "timing": "Start before entering stadium"
        }
    
    def _generate_sun_protection_recommendation(
        self,
        uv_index: float
    ) -> Dict[str, Any]:
        """Generate sun protection recommendation"""
        priority = "high" if uv_index > self.config.UV_INDEX_VERY_HIGH else "medium"
        
        return {
            "target": "fan",
            "category": "safety",
            "priority": priority,
            "title": f"High UV Index Alert (UV {uv_index})",
            "description": "Strong UV radiation requires protection.",
            "details": {
                "essential": [
                    "Apply SPF 30+ sunscreen",
                    "Wear hat or cap",
                    "Use sunglasses",
                    "Seek shade when possible"
                ],
                "reapplication": "Reapply sunscreen every 2 hours"
            },
            "timing": "Before entering stadium"
        }
    
    def _generate_arrival_time_recommendation(
        self,
        risk_level: str,
        match_time: str
    ) -> Dict[str, Any]:
        """Generate arrival time recommendation"""
        return {
            "target": "fan",
            "category": "planning",
            "priority": "medium",
            "title": "Optimal Arrival Time",
            "description": "Minimize heat exposure by timing your arrival.",
            "details": {
                "recommendation": "Arrive 30-45 minutes before kickoff",
                "reasoning": "Reduces time in direct sun and heat",
                "tips": [
                    "Use air-conditioned transport",
                    "Enter stadium promptly",
                    "Locate your seat and nearby facilities",
                    "Avoid prolonged outdoor queuing"
                ]
            },
            "timing": "Plan arrival accordingly"
        }
    
    def _generate_seating_alert(
        self,
        high_risk_zones: List[str]
    ) -> Dict[str, Any]:
        """Generate high-risk seating alert"""
        return {
            "target": "fan",
            "category": "safety",
            "priority": "high",
            "title": "High-Risk Seating Areas",
            "description": f"Sections {', '.join(high_risk_zones)} have elevated heat exposure.",
            "details": {
                "affected_sections": high_risk_zones,
                "recommendations": [
                    "Take extra hydration precautions",
                    "Take frequent breaks in shaded areas",
                    "Consider relocating if feeling unwell",
                    "Watch for heat illness symptoms"
                ],
                "alternatives": "Seek covered or shaded seating if available"
            },
            "timing": "Before and during match"
        }
    
    def _generate_clothing_recommendation(
        self,
        risk_level: str
    ) -> Dict[str, Any]:
        """Generate clothing recommendation"""
        return {
            "target": "fan",
            "category": "preparation",
            "priority": "medium",
            "title": "Recommended Attire",
            "description": "Dress appropriately for hot conditions.",
            "details": {
                "recommended": [
                    "Light-colored, loose-fitting clothing",
                    "Breathable fabrics (cotton, moisture-wicking)",
                    "Wide-brimmed hat or cap",
                    "Comfortable, breathable footwear"
                ],
                "avoid": [
                    "Dark colors",
                    "Tight or restrictive clothing",
                    "Heavy fabrics"
                ]
            },
            "timing": "Before leaving for stadium"
        }


# Global recommendations engine instance
recommendations_engine = RecommendationsEngine()

