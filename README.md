# HeatAware Hub

**Climate Intelligence for Every Match**

A Human Performance & Behavior app that analyzes weather during FIFA 2026 World Cup games, detects fatigue/stress risk, and provides recommendations to players and fans.

## Overview

HeatAware Hub ingests the full FIFA World Cup 2026 match schedule along with stadium locations, architectural layouts, match times, and weather data. It analyzes heat, humidity, sun exposure, and environmental factors to detect high-risk zones for fans and players, displaying them on an interactive 2D stadium map with tailored recommendations.

## Features

### Core Capabilities
- **Real-time Weather Integration**: Connects to OpenWeather API for live and forecasted conditions
- **Micro-climate Modeling**: Computes heat accumulation, shade patterns, and airflow per stadium zone
- **Risk Analysis**: Separate scoring for players and fans (Low/Moderate/High/Critical)
- **Interactive 2D Stadium Maps**: Color-coded heat-risk overlays with zone-specific insights
- **Smart Recommendations**: Cooling breaks, hydration timing, and safety guidance

### For Players
- Fatigue and dehydration risk assessment
- Cooling break suggestions based on heat index
- Tactical adjustments for extreme heat
- Pitch zone risk mapping

### For Fans
- High-risk seating area alerts
- Hydration and shade guidance
- Safe zone recommendations
- Arrival time suggestions

## Technology Stack

### Frontend
- **Vue.js**: UI framework
- **PixiJS**: Stadium overlays and zone highlighting
- **Tailwind CSS**: Styling

### Backend
- **Python FastAPI**: API orchestration and data processing
- **PostgreSQL**: Structured match/stadium data
- **Redis**: Caching for weather calls and risk computations

### Integrations
- **OpenWeather API**: Real-time and forecast weather data
- **Docling**: Parse stadium and game schedule PDFs

### AI/ML
- Python models for fatigue prediction, stress scoring, and environmental impact modeling

## Project Structure

```
heataware-hub/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Data models
│   │   ├── services/    # Business logic
│   │   └── ml/          # ML models for risk analysis
│   ├── requirements.txt
│   └── main.py
├── frontend/            # Vue.js frontend
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── router/      # Client-Side Navigation
│   │   ├── views/       # Page views
│   │   └── services/    # API services
│   ├── package.json
│   └── vite.config.js
├── data/                # Sample data and schemas
└── docs/                # Documentation
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost/heataware
REDIS_URL=redis://localhost:6379
OPENWEATHER_API_KEY=your_api_key_here
```

### Run it

Run the server with:

<div class="termy">

```console
$ python -m uvicorn app.main:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [8384] using StatReload
INFO:     Started server process [52628]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Interactive API docs

Now go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)


### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Endpoints

- `GET /api/matches` - List all World Cup matches
- `GET /api/matches/{id}` - Get match details with weather
- `GET /api/stadiums/{id}` - Get stadium information
- `GET /api/stadiums/{id}/map` - Get interactive stadium map data
- `GET /api/risk-analysis/{match_id}` - Get risk analysis for a match
- `GET /api/recommendations/{match_id}` - Get recommendations

## Data Models

### Match Schedule
- Date, time, teams
- Stadium reference
- Weather forecast link

### Stadium Data
- Geolocation (lat, lon, altitude)
- Architectural plan (seating blocks, pitch zones)
- Roof coverage and sun-exposed areas
- Airflow zones

### Risk Scoring
- Player fatigue risk (0-100)
- Fan exposure risk (0-100)
- Zone-specific risk levels
- Real-time updates

## Security & Compliance

- GDPR-compliant data handling
- No personal data collection from fans
- Secure API authentication
- Rate limiting on weather API calls

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Contact

For questions or support, please open an issue on GitHub.

---

**FIFA World Cup 2026** - Bringing climate intelligence to the beautiful game.
