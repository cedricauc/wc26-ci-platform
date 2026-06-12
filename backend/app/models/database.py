"""
Database models for HeatAware Hub
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Stadium(Base):
    """Stadium model with geolocation and architectural data"""
    __tablename__ = "stadiums"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    
    # Geolocation
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, default=0.0)
    orientation = Column(Float, nullable=True)  # Stadium orientation in degrees
    
    # Capacity and structure
    capacity = Column(Integer, nullable=False)
    roof_coverage = Column(Float, default=0.0)  # Percentage of covered area
    
    # Architectural data (JSON)
    seating_blocks = Column(JSON, nullable=True)  # Seating block definitions
    pitch_zones = Column(JSON, nullable=True)  # Pitch zone definitions
    sun_exposed_areas = Column(JSON, nullable=True)  # Areas with direct sun exposure
    airflow_zones = Column(JSON, nullable=True)  # Airflow characteristics
    
    # Stadium plan
    plan_url = Column(String(500), nullable=True)
    plan_data = Column(JSON, nullable=True)  # Parsed stadium plan from Docling
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    matches = relationship("Match", back_populates="stadium")


class Team(Base):
    """Team model"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(3), nullable=False, unique=True)  # FIFA code (e.g., USA, BRA)
    flag_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")


class Match(Base):
    """Match model with schedule and context"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    match_number = Column(Integer, nullable=False, unique=True)
    
    # Teams
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Stadium
    stadium_id = Column(Integer, ForeignKey("stadiums.id"), nullable=False)
    
    # Schedule
    match_date = Column(DateTime, nullable=False, index=True)
    kickoff_time = Column(DateTime, nullable=False)
    
    # Match context
    stage = Column(String(50), nullable=False)  # Group, Round of 16, Quarter, Semi, Final
    group_name = Column(String(10), nullable=True)  # Group A, B, C, etc.
    expected_attendance = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(20), default="scheduled")  # scheduled, live, completed, cancelled
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stadium = relationship("Stadium", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    weather_data = relationship("WeatherData", back_populates="match")
    risk_analyses = relationship("RiskAnalysis", back_populates="match")


class WeatherData(Base):
    """Weather data for matches"""
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    
    # Timestamp
    forecast_time = Column(DateTime, nullable=False)
    data_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Weather conditions
    temperature = Column(Float, nullable=False)  # °C
    feels_like = Column(Float, nullable=False)  # °C
    humidity = Column(Float, nullable=False)  # %
    heat_index = Column(Float, nullable=False)  # °C
    
    # Additional metrics
    uv_index = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)  # m/s
    wind_direction = Column(Float, nullable=True)  # degrees
    cloud_cover = Column(Float, nullable=True)  # %
    precipitation = Column(Float, default=0.0)  # mm
    
    # Weather description
    condition = Column(String(50), nullable=True)  # Clear, Cloudy, Rain, etc.
    description = Column(String(255), nullable=True)
    
    # Data source
    source = Column(String(50), default="openweather")
    is_forecast = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    match = relationship("Match", back_populates="weather_data")


class RiskAnalysis(Base):
    """Risk analysis results for matches"""
    __tablename__ = "risk_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    
    # Analysis timestamp
    analysis_time = Column(DateTime, default=datetime.utcnow)
    
    # Overall risk scores (0-100)
    player_risk_score = Column(Float, nullable=False)
    fan_risk_score = Column(Float, nullable=False)
    
    # Risk levels
    player_risk_level = Column(String(20), nullable=False)  # Low, Moderate, High, Critical
    fan_risk_level = Column(String(20), nullable=False)
    
    # Detailed analysis (JSON)
    pitch_zone_risks = Column(JSON, nullable=True)  # Risk per pitch zone
    seating_zone_risks = Column(JSON, nullable=True)  # Risk per seating block
    micro_climate_data = Column(JSON, nullable=True)  # Micro-climate modeling results
    
    # Contributing factors
    heat_stress_factor = Column(Float, nullable=True)
    humidity_factor = Column(Float, nullable=True)
    sun_exposure_factor = Column(Float, nullable=True)
    airflow_factor = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    match = relationship("Match", back_populates="risk_analyses")
    recommendations = relationship("Recommendation", back_populates="risk_analysis")


class Recommendation(Base):
    """Recommendations for players and fans"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_analysis_id = Column(Integer, ForeignKey("risk_analyses.id"), nullable=False)
    
    # Target audience
    target = Column(String(20), nullable=False)  # player, fan, staff
    
    # Recommendation type
    category = Column(String(50), nullable=False)  # cooling, hydration, safety, tactical
    priority = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Specific guidance (JSON)
    details = Column(JSON, nullable=True)
    
    # Timing
    timing = Column(String(100), nullable=True)  # When to apply (e.g., "30 minutes before kickoff")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    risk_analysis = relationship("RiskAnalysis", back_populates="recommendations")


class PDFDocument(Base):
    """PDF document tracking for ingestion"""
    __tablename__ = "pdf_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Document metadata
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    document_type = Column(String(50), nullable=False)  # team, stadium, game
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Docling extraction results
    raw_extraction = Column(JSON, nullable=True)  # Raw Docling output
    normalized_data = Column(JSON, nullable=True)  # Normalized/parsed data
    
    # Processing metadata
    extraction_started_at = Column(DateTime, nullable=True)
    extraction_completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Entities created from this document
    entities_created = Column(JSON, nullable=True)  # {"teams": [1,2], "stadiums": [3], "matches": [4,5]}
    
    # Metadata
    uploaded_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

