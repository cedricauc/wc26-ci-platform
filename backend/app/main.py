"""
Main FastAPI application for HeatAware Hub
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from typing import List, Optional
import shutil
from pathlib import Path

from .config import settings
from .models import schemas
from .models.db_init import init_database, check_database_connection, get_db, get_table_counts
from .api.weather_api import weather_api
from .services.data_ingestion import data_service
from .services.pdf_ingestion import pdf_ingestion_service
from .ml.risk_engine import risk_engine
from .ml.recommendations_engine import recommendations_engine

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Climate Intelligence for FIFA World Cup 2026",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=schemas.HealthCheck)
async def health_check():
    """Health check endpoint"""
    return schemas.HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Climate Intelligence for FIFA World Cup 2026",
        "docs": "/docs"
    }


# Weather endpoints
@app.get("/api/v1/weather/current")
async def get_current_weather(latitude: float, longitude: float):
    """
    Get current weather for a location
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
    
    Returns:
        Current weather data
    """
    try:
        weather_data = await weather_api.get_current_weather(latitude, longitude)
        
        if not weather_data:
            raise HTTPException(status_code=404, detail="Weather data not available")
        
        return weather_data
    except Exception as e:
        logger.error(f"Error fetching current weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/weather/forecast")
async def get_weather_forecast(
    latitude: float,
    longitude: float,
    target_time: Optional[str] = None
):
    """
    Get weather forecast for a location
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        target_time: Optional target time (ISO format)
    
    Returns:
        Weather forecast data
    """
    try:
        target_dt = None
        if target_time:
            target_dt = datetime.fromisoformat(target_time.replace('Z', '+00:00'))
        
        forecast_data = await weather_api.get_forecast(
            latitude, 
            longitude,
            target_dt
        )
        
        if not forecast_data:
            raise HTTPException(status_code=404, detail="Forecast data not available")
        
        return forecast_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error fetching forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Risk analysis endpoints
@app.post("/api/v1/risk-analysis/calculate")
async def calculate_risk(request: schemas.RiskCalculationRequest):
    """
    Calculate risk analysis for a match
    
    Args:
        request: Risk calculation request containing latitude, longitude, match_time, and optional stadium_data
    
    Returns:
        Risk analysis results
    """
    try:
        # Parse match time
        match_dt = datetime.fromisoformat(request.match_time.replace('Z', '+00:00'))
        
        # Get weather data
        weather_data = await weather_api.get_match_weather(
            request.latitude,
            request.longitude,
            match_dt
        )
        
        if not weather_data:
            raise HTTPException(
                status_code=404,
                detail="Weather data not available for this match"
            )
        
        # Extract stadium data if provided
        pitch_zones = None
        seating_blocks = None
        sun_exposed_areas = None
        
        if request.stadium_data:
            pitch_zones = request.stadium_data.get("pitch_zones")
            seating_blocks = request.stadium_data.get("seating_blocks")
            sun_exposed_areas = request.stadium_data.get("sun_exposed_areas")
        
        # Calculate player risk
        player_risk = risk_engine.calculate_player_risk(
            weather_data,
            match_duration=90,
            pitch_zones=pitch_zones
        )
        
        # Calculate fan risk
        fan_risk = risk_engine.calculate_fan_risk(
            weather_data,
            seating_blocks=seating_blocks,
            sun_exposed_areas=sun_exposed_areas
        )
        
        # Generate recommendations
        player_recommendations = recommendations_engine.generate_player_recommendations(
            player_risk,
            weather_data,
            request.match_time
        )
        
        fan_recommendations = recommendations_engine.generate_fan_recommendations(
            fan_risk,
            weather_data,
            request.match_time
        )
        
        return {
            "weather": weather_data,
            "player_risk": player_risk,
            "fan_risk": fan_risk,
            "player_recommendations": player_recommendations,
            "fan_recommendations": fan_recommendations,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
    except Exception as e:
        logger.error(f"Error calculating risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risk-analysis/match/{match_id}")
async def get_match_risk_analysis(match_id: int):
    """
    Get risk analysis for a specific match
    
    Args:
        match_id: Match ID
    
    Returns:
        Risk analysis for the match
    """
    # This would query the database for match and stadium data
    # For now, return a placeholder
    raise HTTPException(
        status_code=501,
        detail="Database integration pending. Use /calculate endpoint with coordinates."
    )


# Stadium map endpoints
@app.get("/api/v1/stadium/{stadium_name}/map")
async def get_stadium_map(stadium_name: str):
    """
    Get stadium map data with zones
    
    Args:
        stadium_name: Stadium name
    
    Returns:
        Stadium map with zones for visualization
    """
    try:
        stadium = data_service.get_stadium_by_name(stadium_name)
        
        if not stadium:
            raise HTTPException(status_code=404, detail="Stadium not found")
        
        # Prepare map data for frontend
        zones = []
        
        # Add seating zones
        for zone_id, zone_data in stadium.get('seating_blocks', {}).items():
            zones.append({
                'zone_id': zone_id,
                'zone_type': 'seating',
                'zone_name': zone_data.get('name', zone_id),
                'has_roof': zone_data.get('has_roof', False),
                'airflow_quality': zone_data.get('airflow_quality', 0.5),
                'sun_exposure': zone_data.get('sun_exposure_afternoon', 0.5)
            })
        
        # Add pitch zones
        for zone_id, zone_data in stadium.get('pitch_zones', {}).items():
            zones.append({
                'zone_id': zone_id,
                'zone_type': 'pitch',
                'zone_name': zone_data.get('name', zone_id),
                'sun_exposure': zone_data.get('sun_exposure', 0.5),
                'airflow_quality': zone_data.get('airflow_quality', 0.5)
            })
        
        return {
            'stadium_name': stadium['name'],
            'address': stadium['address'],
            'capacity': stadium['capacity'],
            'roof_coverage': stadium['roof_coverage'],
            'zones': zones,
            'sun_exposed_areas': stadium.get('sun_exposed_areas', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stadium map: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stadium/{stadium_name}/zones")
async def get_stadium_zones(stadium_name: str):
    """
    Get stadium zone definitions
    
    Args:
        stadium_name: Stadium name
    
    Returns:
        Stadium zones with detailed data
    """
    try:
        zones = data_service.get_stadium_zones(stadium_name)
        
        if not zones:
            raise HTTPException(status_code=404, detail="Stadium not found")
        
        return zones
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stadium zones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Match endpoints
@app.get("/api/v1/matches")
async def list_matches(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    stadium_name: Optional[str] = None,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """
    List matches with optional filters from database
    
    Args:
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        stadium_name: Filter by stadium name
        limit: Maximum number of matches
        db: Database session
    
    Returns:
        List of matches with team and stadium details
    """
    try:
        from .models.database import Match, Team, Stadium
        
        # Build base query
        query = db.query(Match)
        
        # Apply filters
        if date_from:
            query = query.filter(Match.match_date >= date_from)
        
        if date_to:
            query = query.filter(Match.match_date <= date_to)
        
        # For stadium filter, we need to join
        if stadium_name:
            query = query.join(Stadium, Match.stadium_id == Stadium.id)
            query = query.filter(Stadium.name.ilike(f"%{stadium_name}%"))
        
        # Order by date and limit
        query = query.order_by(Match.match_date.asc(), Match.kickoff_time.asc())
        
        if limit:
            query = query.limit(limit)
        
        matches_db = query.all()
        
        # Format matches for response
        matches = []
        for match in matches_db:
            # Get related objects
            home_team = db.query(Team).filter(Team.id == match.home_team_id).first()
            away_team = db.query(Team).filter(Team.id == match.away_team_id).first()
            stadium = db.query(Stadium).filter(Stadium.id == match.stadium_id).first()
            
            match_data = {
                "id": match.id,
                "match_number": match.match_number,
                "home_team": home_team.name if home_team else "TBD",
                "away_team": away_team.name if away_team else "TBD",
                "home_team_code": home_team.code if home_team else "TBD",
                "away_team_code": away_team.code if away_team else "TBD",
                "stadium": stadium.name if stadium else "TBD",
                "latitude": float(stadium.latitude) if stadium and stadium.latitude else None,
                "longitude": float(stadium.longitude) if stadium and stadium.longitude else None,
                "match_date": match.match_date.isoformat() if match.match_date else None,
                "kickoff_time": match.kickoff_time.isoformat() if match.kickoff_time else None,
                "stage": match.stage,
                "group_name": match.group_name,
                "status": match.status
            }
            matches.append(match_data)
        
        return {
            "matches": matches,
            "count": len(matches)
        }
    except Exception as e:
        logger.error(f"Error listing matches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/matches/{match_id}")
async def get_match_details(match_id: int):
    """
    Get detailed match information
    
    Args:
        match_id: Match ID (match_number)
    
    Returns:
        Match details with stadium data
    """
    try:
        match = data_service.get_match_with_stadium(match_id)
        
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        return match
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting match details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/matches/{match_id}/preview")
async def get_match_preview(match_id: int):
    """
    Get match preview with weather and risk forecast
    
    Args:
        match_id: Match ID (match_number)
    
    Returns:
        Match preview card data with weather and risk analysis
    """
    try:
        # Get match with stadium data
        match = data_service.get_match_with_stadium(match_id)
        
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Get weather forecast
        match_time = datetime.fromisoformat(match['kickoff_datetime'])

        stadium = match.get('stadium_data')
        if not stadium:
            raise HTTPException(status_code=500, detail="Stadium data missing for this match")

        weather_data = await weather_api.get_match_weather(
            stadium['latitude'],
            stadium['longitude'],
            match_time
        )
        
        if not weather_data:
            raise HTTPException(
                status_code=404,
                detail="Weather data not available for this match"
            )
        # Get Games name
        
        # Get stadium zones
        stadium_data = match.get('stadium_data', {})
        pitch_zones = stadium_data.get('pitch_zones')
        seating_blocks = stadium_data.get('seating_blocks')
        sun_exposed_areas = stadium_data.get('sun_exposed_areas')
        
        # Calculate risks
        player_risk = risk_engine.calculate_player_risk(
            weather_data,
            match_duration=90,
            pitch_zones=pitch_zones
        )
        
        fan_risk = risk_engine.calculate_fan_risk(
            weather_data,
            seating_blocks=seating_blocks,
            sun_exposed_areas=sun_exposed_areas
        )
        
        # Generate recommendations
        player_recommendations = recommendations_engine.generate_player_recommendations(
            player_risk,
            weather_data,
            match['kickoff_datetime']
        )
        
        fan_recommendations = recommendations_engine.generate_fan_recommendations(
            fan_risk,
            weather_data,
            match['kickoff_datetime']
        )
        
        # Get top 3 recommendations for preview
        key_recommendations = []
        if player_recommendations:
            key_recommendations.append(player_recommendations[0]['title'])
        if fan_recommendations:
            key_recommendations.append(fan_recommendations[0]['title'])
        
        return {
            "match": match,
            "weather_forecast": weather_data,
            "player_risk": player_risk,
            "fan_risk": fan_risk,
            "key_recommendations": key_recommendations,
            "player_recommendations": player_recommendations[:3],
            "fan_recommendations": fan_recommendations[:3]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating match preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Recommendations endpoints
@app.get("/api/v1/recommendations/{match_id}")
async def get_match_recommendations(
    match_id: int,
    target: Optional[str] = None
):
    """
    Get recommendations for a match
    
    Args:
        match_id: Match ID
        target: Filter by target (player, fan, staff)
    
    Returns:
        List of recommendations
    """
    raise HTTPException(
        status_code=501,
        detail="Database integration pending"
    )


# PDF Ingestion endpoints
@app.post("/api/v1/ingest/team-pdf", response_model=schemas.PDFUploadResponse)
async def ingest_team_pdf(
    file: UploadFile = File(...),
    uploaded_by: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload and ingest a team information PDF
    
    Args:
        file: PDF file containing team information
        uploaded_by: Optional username of uploader
        db: Database session
    
    Returns:
        Upload confirmation with document ID and processing results
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file
        upload_path = Path(pdf_ingestion_service.upload_dir) / f"team_{datetime.utcnow().timestamp()}_{file.filename}"
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Team PDF uploaded: {file.filename} -> {upload_path}")
        
        # Process PDF and insert into database
        result = await pdf_ingestion_service.ingest_pdf(
            file_path=str(upload_path),
            filename=file.filename,
            document_type="team",
            db=db,
            uploaded_by=uploaded_by
        )
        
        return schemas.PDFUploadResponse(
            document_id=result['document_id'],
            filename=result['filename'],
            document_type=result['document_type'],
            status=result['status'],
            message=f"Team PDF processed successfully. Created {result.get('extraction_summary', {}).get('entities_inserted', 0)} entities."
        )
        
    except Exception as e:
        logger.error(f"Error uploading team PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ingest/stadium-pdf", response_model=schemas.PDFUploadResponse)
async def ingest_stadium_pdf(
    file: UploadFile = File(...),
    uploaded_by: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload and ingest a stadium information PDF
    
    Args:
        file: PDF file containing stadium information
        uploaded_by: Optional username of uploader
        db: Database session
    
    Returns:
        Upload confirmation with document ID and processing results
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file
        upload_path = Path(pdf_ingestion_service.upload_dir) / f"stadium_{datetime.utcnow().timestamp()}_{file.filename}"
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Stadium PDF uploaded: {file.filename} -> {upload_path}")
        
        # Process PDF and insert into database
        result = await pdf_ingestion_service.ingest_pdf(
            file_path=str(upload_path),
            filename=file.filename,
            document_type="stadium",
            db=db,
            uploaded_by=uploaded_by
        )
        
        return schemas.PDFUploadResponse(
            document_id=result['document_id'],
            filename=result['filename'],
            document_type=result['document_type'],
            status=result['status'],
            message=f"Stadium PDF processed successfully. Created {result.get('extraction_summary', {}).get('entities_inserted', 0)} entities."
        )
        
    except Exception as e:
        logger.error(f"Error uploading stadium PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ingest/game-pdf", response_model=schemas.PDFUploadResponse)
async def ingest_game_pdf(
    file: UploadFile = File(...),
    uploaded_by: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload and ingest a game schedule PDF
    
    Args:
        file: PDF file containing game/match schedule
        uploaded_by: Optional username of uploader
        db: Database session
    
    Returns:
        Upload confirmation with document ID and processing results
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file
        upload_path = Path(pdf_ingestion_service.upload_dir) / f"game_{datetime.utcnow().timestamp()}_{file.filename}"
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Game PDF uploaded: {file.filename} -> {upload_path}")
        
        # Process PDF and insert into database
        result = await pdf_ingestion_service.ingest_pdf(
            file_path=str(upload_path),
            filename=file.filename,
            document_type="game",
            db=db,
            uploaded_by=uploaded_by
        )
        
        return schemas.PDFUploadResponse(
            document_id=result['document_id'],
            filename=result['filename'],
            document_type=result['document_type'],
            status=result['status'],
            message=f"Game schedule PDF processed successfully. Created {result.get('extraction_summary', {}).get('entities_inserted', 0)} entities."
        )
        
    except Exception as e:
        logger.error(f"Error uploading game PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/teams", response_model=List[schemas.Team])
async def get_teams(limit: int = 50):
    """
    Get list of all teams
    
    Args:
        limit: Maximum number of teams to return
    
    Returns:
        List of teams
    """
    # Placeholder - would query database in production
    return []


@app.get("/api/v1/stadiums", response_model=List[schemas.Stadium])
async def get_stadiums(limit: int = 50):
    """
    Get list of all stadiums
    
    Args:
        limit: Maximum number of stadiums to return
    
    Returns:
        List of stadiums
    """
    # Placeholder - would query database in production
    return []


@app.get("/api/v1/games")
async def get_games(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50
):
    """
    Get list of all games/matches
    
    Args:
        date_from: Filter by start date (YYYY-MM-DD)
        date_to: Filter by end date (YYYY-MM-DD)
        limit: Maximum number of games to return
    
    Returns:
        List of games
    """
    # Placeholder - would query database in production
    return {"games": [], "count": 0}


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database
    try:
        logger.info("Initializing database connection...")
        init_database()
        
        # Check connection
        if check_database_connection():
            logger.info("Database connection established successfully")
            
            # Log table counts
            counts = get_table_counts()
            logger.info(f"Database table counts: {counts}")
        else:
            logger.warning("Database connection check failed - some features may not work")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.warning("Application will continue but database features will be unavailable")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down application")
    await weather_api.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
