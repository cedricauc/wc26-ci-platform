# Database Setup Guide

This guide explains how to set up the PostgreSQL database for HeatAware Hub.

## Prerequisites

- PostgreSQL 12 or higher installed
- Python 3.9+ with dependencies installed (`pip install -r requirements.txt`)

## Quick Start

### 1. Install PostgreSQL

**Windows:**
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Run the installer and remember your postgres user password

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database

Connect to PostgreSQL and create the database:

```bash
# Connect as postgres user
psql -U postgres

# Or on Linux:
sudo -u postgres psql
```

Then run these SQL commands:

```sql
-- Create database
CREATE DATABASE heataware;

-- Create user (optional, for production)
CREATE USER heataware_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE heataware TO heataware_user;

-- Exit
\q
```

### 3. Configure Environment

Edit `backend/.env` and update the DATABASE_URL:

```env
# For default postgres user
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/heataware

# Or for custom user
DATABASE_URL=postgresql://heataware_user:your_password@localhost:5432/heataware
```

### 4. Initialize Database Tables

The application will automatically create all tables when it starts. Just run:

```bash
cd backend
uvicorn app.main:app --reload
```

The startup logs will show:
```
INFO - Initializing database...
INFO - Database tables created successfully
INFO - Tables: stadiums, teams, matches, weather_data, risk_analyses, recommendations, pdf_documents
INFO - Database connection established successfully
```

## Database Schema

The application creates the following tables:

### Core Tables

1. **teams** - Team information
   - id, name, code (FIFA code), flag_url
   - Stores all participating teams

2. **stadiums** - Stadium information
   - id, name, city, country, latitude, longitude
   - capacity, roof_coverage, orientation
   - seating_blocks, pitch_zones (JSON)
   - Stores stadium architectural data

3. **matches** - Match schedule
   - id, match_number, home_team_id, away_team_id
   - stadium_id, match_date, kickoff_time
   - stage, group_name, status
   - Links teams and stadiums

### Analysis Tables

4. **weather_data** - Weather forecasts and observations
   - match_id, temperature, humidity, heat_index
   - uv_index, wind_speed, precipitation
   - Stores weather data for matches

5. **risk_analyses** - Heat risk analysis results
   - match_id, player_risk_score, fan_risk_score
   - pitch_zone_risks, seating_zone_risks (JSON)
   - Stores calculated risk assessments

6. **recommendations** - Safety recommendations
   - risk_analysis_id, target (player/fan/staff)
   - category, priority, title, description
   - Stores generated recommendations

### Document Management

7. **pdf_documents** - PDF ingestion tracking
   - filename, document_type, status
   - raw_extraction, normalized_data (JSON)
   - Tracks PDF processing

## Database Operations

### Check Connection

```python
from app.models.db_init import check_database_connection

if check_database_connection():
    print("Database is connected!")
```

### Get Table Counts

```python
from app.models.db_init import get_table_counts

counts = get_table_counts()
print(counts)
# {'teams': 32, 'stadiums': 16, 'matches': 104, ...}
```

