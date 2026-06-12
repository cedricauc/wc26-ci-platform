"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class MatchStage(str, Enum):
    """Match stage enumeration"""
    GROUP = "group"
    ROUND_16 = "round_of_16"
    QUARTER = "quarter_final"
    SEMI = "semi_final"
    FINAL = "final"


class MatchStatus(str, Enum):
    """Match status enumeration"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Stadium Schemas
class StadiumBase(BaseModel):
    """Base stadium schema"""
    name: str
    address: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: float = 0.0
    orientation: Optional[float] = None
    capacity: int = Field(..., gt=0)
    roof_coverage: float = Field(0.0, ge=0, le=100)


class StadiumCreate(StadiumBase):
    """Schema for creating a stadium"""
    seating_blocks: Optional[Dict[str, Any]] = None
    pitch_zones: Optional[Dict[str, Any]] = None
    sun_exposed_areas: Optional[Dict[str, Any]] = None
    airflow_zones: Optional[Dict[str, Any]] = None
    plan_url: Optional[str] = None
    plan_data: Optional[Dict[str, Any]] = None


class Stadium(StadiumBase):
    """Stadium response schema"""
    id: int
    seating_blocks: Optional[Dict[str, Any]] = None
    pitch_zones: Optional[Dict[str, Any]] = None
    sun_exposed_areas: Optional[Dict[str, Any]] = None
    airflow_zones: Optional[Dict[str, Any]] = None
    plan_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Team Schemas
class TeamBase(BaseModel):
    """Base team schema"""
    name: str
    code: str = Field(..., min_length=3, max_length=3)
    flag_url: Optional[str] = None


class TeamCreate(TeamBase):
    """Schema for creating a team"""
    pass


class Team(TeamBase):
    """Team response schema"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Weather Schemas
class WeatherDataBase(BaseModel):
    """Base weather data schema"""
    temperature: float
    feels_like: float
    humidity: float = Field(..., ge=0, le=100)
    heat_index: float
    uv_index: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = Field(None, ge=0, le=360)
    cloud_cover: Optional[float] = Field(None, ge=0, le=100)
    precipitation: float = 0.0
    condition: Optional[str] = None
    description: Optional[str] = None


class WeatherDataCreate(WeatherDataBase):
    """Schema for creating weather data"""
    match_id: int
    forecast_time: datetime
    source: str = "openweather"
    is_forecast: bool = True


class WeatherData(WeatherDataBase):
    """Weather data response schema"""
    id: int
    match_id: int
    forecast_time: datetime
    data_timestamp: datetime
    source: str
    is_forecast: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Match Schemas
class MatchBase(BaseModel):
    """Base match schema"""
    match_number: int
    home_team_id: int
    away_team_id: int
    stadium_id: int
    match_date: datetime
    kickoff_time: datetime
    stage: MatchStage
    group_name: Optional[str] = None
    expected_attendance: Optional[int] = None


class MatchCreate(MatchBase):
    """Schema for creating a match"""
    pass


class Match(MatchBase):
    """Match response schema"""
    id: int
    status: MatchStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MatchDetail(Match):
    """Detailed match response with relationships"""
    stadium: Stadium
    home_team: Team
    away_team: Team
    weather_data: Optional[List[WeatherData]] = []
    
    class Config:
        from_attributes = True


# Risk Analysis Schemas
class ZoneRisk(BaseModel):
    """Risk data for a specific zone"""
    zone_id: str
    zone_name: str
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    temperature: float
    sun_exposure: float = Field(..., ge=0, le=100)
    airflow_quality: float = Field(..., ge=0, le=100)
    recommendations: List[str] = []


class RiskAnalysisBase(BaseModel):
    """Base risk analysis schema"""
    player_risk_score: float = Field(..., ge=0, le=100)
    fan_risk_score: float = Field(..., ge=0, le=100)
    player_risk_level: RiskLevel
    fan_risk_level: RiskLevel


class RiskAnalysisCreate(RiskAnalysisBase):
    """Schema for creating risk analysis"""
    match_id: int
    pitch_zone_risks: Optional[Dict[str, Any]] = None
    seating_zone_risks: Optional[Dict[str, Any]] = None
    micro_climate_data: Optional[Dict[str, Any]] = None
    heat_stress_factor: Optional[float] = None
    humidity_factor: Optional[float] = None
    sun_exposure_factor: Optional[float] = None
    airflow_factor: Optional[float] = None


class RiskAnalysis(RiskAnalysisBase):
    """Risk analysis response schema"""
    id: int
    match_id: int
    analysis_time: datetime
    pitch_zone_risks: Optional[Dict[str, Any]] = None
    seating_zone_risks: Optional[Dict[str, Any]] = None
    micro_climate_data: Optional[Dict[str, Any]] = None
    heat_stress_factor: Optional[float] = None
    humidity_factor: Optional[float] = None
    sun_exposure_factor: Optional[float] = None
    airflow_factor: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Recommendation Schemas
class RecommendationBase(BaseModel):
    """Base recommendation schema"""
    target: str = Field(..., pattern="^(player|fan|staff)$")
    category: str
    priority: str = Field(..., pattern="^(low|medium|high|critical)$")
    title: str
    description: str
    details: Optional[Dict[str, Any]] = None
    timing: Optional[str] = None


class RecommendationCreate(RecommendationBase):
    """Schema for creating recommendation"""
    risk_analysis_id: int


class Recommendation(RecommendationBase):
    """Recommendation response schema"""
    id: int
    risk_analysis_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Stadium Map Schemas
class StadiumMapZone(BaseModel):
    """Stadium map zone data"""
    zone_id: str
    zone_type: str  # pitch, seating, concourse
    coordinates: List[List[float]]  # Polygon coordinates
    risk_level: RiskLevel
    risk_score: float
    temperature: float
    metadata: Optional[Dict[str, Any]] = None


class StadiumMap(BaseModel):
    """Complete stadium map with risk overlay"""
    stadium_id: int
    match_id: int
    zones: List[StadiumMapZone]
    legend: Dict[str, str]
    last_updated: datetime


# API Response Schemas
class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime


class MatchPreview(BaseModel):
    """Match preview card data"""
    match: MatchDetail
    weather_forecast: Optional[WeatherData] = None
    predicted_risk: RiskAnalysis
    key_recommendations: List[str]


class LiveMatchUpdate(BaseModel):
    """Live match update data"""
    match_id: int
    current_time: datetime
    current_weather: WeatherData
    current_risk: RiskAnalysis
    active_alerts: List[str]
    updated_recommendations: List[Recommendation]


# Risk Calculation Request Schema
class RiskCalculationRequest(BaseModel):
    """Request schema for risk calculation endpoint"""
    latitude: float = Field(..., ge=-90, le=90, description="Stadium latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Stadium longitude")
    match_time: str = Field(..., description="Match kickoff time in ISO format")
    stadium_data: Optional[Dict[str, Any]] = Field(None, description="Optional stadium architectural data including pitch_zones, seating_blocks, and sun_exposed_areas")
    
    @validator('match_time')
    def validate_match_time(cls, v):
        """Validate match_time is a valid ISO format datetime"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('match_time must be in ISO format (e.g., 2026-06-11T14:00:00Z)')
        return v


# PDF Document Ingestion Schemas
class PDFDocumentBase(BaseModel):
    """Base PDF document schema"""
    filename: str
    document_type: str = Field(..., pattern="^(team|stadium|game)$")


class PDFDocumentCreate(PDFDocumentBase):
    """Schema for creating PDF document record"""
    file_size: int
    file_path: str
    uploaded_by: Optional[str] = None


class PDFDocument(PDFDocumentBase):
    """PDF document response schema"""
    id: int
    file_path: str
    file_size: int
    status: str
    raw_extraction: Optional[Dict[str, Any]] = None
    normalized_data: Optional[Dict[str, Any]] = None
    extraction_started_at: Optional[datetime] = None
    extraction_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    entities_created: Optional[Dict[str, List[int]]] = None
    uploaded_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PDFUploadResponse(BaseModel):
    """Response after PDF upload"""
    document_id: int
    filename: str
    document_type: str
    status: str
    message: str


class PDFIngestionResult(BaseModel):
    """Result of PDF ingestion and processing"""
    document_id: int
    filename: str
    document_type: str
    status: str
    entities_created: Dict[str, List[int]]
    extraction_summary: Dict[str, Any]
    processing_time_seconds: float
    error_message: Optional[str] = None


class TeamExtracted(BaseModel):
    """Extracted team data from PDF"""
    name: str
    code: Optional[str] = None
    group: Optional[str] = None
    coach: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class StadiumExtracted(BaseModel):
    """Extracted stadium data from PDF"""
    name: str
    city: str
    country: str
    capacity: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    roof_coverage: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class GameExtracted(BaseModel):
    """Extracted game data from PDF"""
    match_number: Optional[int] = None
    home_team: str
    away_team: str
    stadium: str
    match_date: str
    kickoff_time: Optional[str] = None
    stage: Optional[str] = None
    group_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

