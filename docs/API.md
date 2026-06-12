# HeatAware Hub API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication for most endpoints. Authentication will be added in future versions for protected resources.

## Response Format

### Success Response
```json
{
  "data": { ... },
  "timestamp": "2026-06-07T15:00:00Z"
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2026-06-07T15:00:00Z"
}
```

## Endpoints

### Health Check

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-06-07T15:00:00Z",
  "version": "1.0.0"
}
```

---

## Weather Endpoints

### Get Current Weather

#### GET /api/v1/weather/current
Get current weather conditions for a location.

**Parameters:**
- `latitude` (float, required): Location latitude (-90 to 90)
- `longitude` (float, required): Location longitude (-180 to 180)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/weather/current?latitude=40.7128&longitude=-74.0060"
```

**Response:**
```json
{
  "temperature": 28.5,
  "feels_like": 31.2,
  "humidity": 65,
  "heat_index": 32.1,
  "wind_speed": 3.5,
  "wind_direction": 180,
  "cloud_cover": 40,
  "condition": "Clear",
  "description": "clear sky",
  "timestamp": "2026-06-07T15:00:00Z",
  "sunrise": "2026-06-07T05:30:00Z",
  "sunset": "2026-06-07T20:15:00Z"
}
```

### Get Weather Forecast

#### GET /api/v1/weather/forecast
Get weather forecast for a location.

**Parameters:**
- `latitude` (float, required): Location latitude
- `longitude` (float, required): Location longitude
- `target_time` (string, optional): Target time in ISO format

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/weather/forecast?latitude=40.7128&longitude=-74.0060&target_time=2026-06-15T18:00:00Z"
```

**Response:**
```json
[
  {
    "temperature": 30.0,
    "feels_like": 33.5,
    "humidity": 70,
    "heat_index": 35.2,
    "uv_index": 8.5,
    "wind_speed": 4.0,
    "cloud_cover": 30,
    "precipitation": 0,
    "condition": "Clear",
    "forecast_time": "2026-06-15T18:00:00Z",
    "pop": 10
  }
]
```

---

## Risk Analysis Endpoints

### Calculate Risk

#### POST /api/v1/risk-analysis/calculate
Calculate heat risk analysis for a match.

**Request Body:**
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "match_time": "2026-06-15T18:00:00Z",
  "stadium_data": {
    "pitch_zones": {
      "center": {
        "name": "Center Circle",
        "sun_exposure": 0.9,
        "airflow_quality": 0.5
      }
    },
    "seating_blocks": {
      "section_a": {
        "name": "Section A",
        "has_roof": false,
        "airflow_quality": 0.6
      }
    },
    "sun_exposed_areas": ["section_a", "section_b"]
  }
}
```

**Response:**
```json
{
  "weather": {
    "temperature": 32.0,
    "humidity": 68,
    "heat_index": 38.5,
    "uv_index": 9.0
  },
  "player_risk": {
    "risk_score": 72.5,
    "risk_level": "high",
    "heat_stress_factor": 65.0,
    "humidity_factor": 52.0,
    "uv_factor": 45.0,
    "wind_factor": 0.85,
    "zone_risks": {
      "center": {
        "zone_name": "Center Circle",
        "risk_score": 78.3,
        "risk_level": "high",
        "sun_exposure": 0.9,
        "airflow_quality": 0.5
      }
    },
    "cooling_breaks_recommended": true
  },
  "fan_risk": {
    "risk_score": 68.2,
    "risk_level": "high",
    "heat_stress_factor": 62.0,
    "humidity_factor": 52.0,
    "uv_factor": 54.0,
    "zone_risks": {
      "section_a": {
        "zone_name": "Section A",
        "risk_score": 75.5,
        "risk_level": "high",
        "sun_exposure": 0.8,
        "airflow_quality": 0.6,
        "has_roof": false
      }
    },
    "high_risk_zones": ["section_a"]
  },
  "player_recommendations": [
    {
      "target": "player",
      "category": "hydration",
      "priority": "high",
      "title": "Enhanced Hydration Required",
      "description": "High heat conditions (32.0°C). Increase fluid intake significantly.",
      "details": {
        "pre_match": "400ml 2 hours before, 200ml 15 minutes before",
        "during_match": "100-150ml every 15 minutes",
        "halftime": "300-400ml with electrolytes"
      },
      "timing": "Start 2 hours before kickoff"
    }
  ],
  "fan_recommendations": [
    {
      "target": "fan",
      "category": "safety",
      "priority": "high",
      "title": "Heat Safety Alert",
      "description": "High temperatures (32.0°C) pose health risks. Take precautions.",
      "details": {
        "actions": [
          "Stay hydrated throughout the match",
          "Seek shade during breaks",
          "Watch for heat illness symptoms"
        ]
      },
      "timing": "Throughout match"
    }
  ],
  "analysis_timestamp": "2026-06-07T15:00:00Z"
}
```

### Get Match Risk Analysis

#### GET /api/v1/risk-analysis/match/{match_id}
Get risk analysis for a specific match (requires database integration).

**Status:** 501 Not Implemented (pending database integration)

---

## Match Endpoints

### List Matches

#### GET /api/v1/matches
List all matches with optional filters.

**Parameters:**
- `date_from` (string, optional): Start date filter (ISO format)
- `date_to` (string, optional): End date filter (ISO format)
- `stadium_id` (integer, optional): Filter by stadium

**Status:** 501 Not Implemented (pending database integration)

### Get Match Details

#### GET /api/v1/matches/{match_id}
Get detailed information about a specific match.

**Status:** 501 Not Implemented (pending database integration)

### Get Match Preview

#### GET /api/v1/matches/{match_id}/preview
Get match preview with weather forecast and risk analysis.

**Status:** 501 Not Implemented (pending database integration)

---

## Stadium Endpoints

### Get Stadium Map

#### GET /api/v1/stadium/{stadium_id}/map
Get interactive stadium map data with zones.

**Status:** 501 Not Implemented (pending database integration)

### Get Stadium Zones

#### GET /api/v1/stadium/{stadium_id}/zones
Get stadium zone definitions with risk data.

**Status:** 501 Not Implemented (pending database integration)

---

## Recommendations Endpoints

### Get Match Recommendations

#### GET /api/v1/recommendations/{match_id}
Get recommendations for a specific match.

**Parameters:**
- `target` (string, optional): Filter by target audience (player, fan, staff)

**Status:** 501 Not Implemented (pending database integration)

---

## Risk Levels

The API uses four risk levels:

| Level | Score Range | Description |
|-------|-------------|-------------|
| **Low** | 0-40 | Minimal heat stress risk |
| **Moderate** | 40-65 | Moderate heat stress, precautions recommended |
| **High** | 65-85 | High heat stress, significant precautions required |
| **Critical** | 85-100 | Extreme heat stress, maximum precautions essential |

## Risk Factors

### Player Risk Factors
- **Heat Stress Factor**: Impact of heat index on performance
- **Humidity Factor**: Effect of humidity on heat dissipation
- **UV Factor**: Sun exposure impact
- **Wind Factor**: Cooling effect of wind
- **Exertion Multiplier**: Physical activity impact (1.5x for players)

### Fan Risk Factors
- **Heat Stress Factor**: Impact of heat index on comfort
- **Humidity Factor**: Effect of humidity on comfort
- **UV Factor**: Sun exposure impact (1.2x for stationary fans)
- **Exposure Multiplier**: Extended exposure time (1.2x for fans)

## Rate Limits

- OpenWeather API: 60 calls per minute (free tier)
- Internal API: No rate limits currently (will be added in production)

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |
| 501 | Not Implemented - Feature pending |

## Examples

### Complete Risk Analysis Workflow

```bash
# 1. Get current weather
curl "http://localhost:8000/api/v1/weather/current?latitude=40.7128&longitude=-74.0060"

# 2. Calculate risk for upcoming match
curl -X POST "http://localhost:8000/api/v1/risk-analysis/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "match_time": "2026-06-15T18:00:00Z"
  }'
```

### Using with JavaScript/Axios

```javascript
import axios from 'axios';

// Calculate risk
const response = await axios.post(
  'http://localhost:8000/api/v1/risk-analysis/calculate',
  {
    latitude: 40.7128,
    longitude: -74.0060,
    match_time: '2026-06-15T18:00:00Z'
  }
);

console.log('Player Risk:', response.data.player_risk.risk_level);
console.log('Fan Risk:', response.data.fan_risk.risk_level);
```

## Interactive Documentation

For interactive API testing, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support

For API issues or questions:
- Check the setup guide: docs/SETUP.md
- Review the main README.md
- Open an issue on GitHub