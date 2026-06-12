# HeatAware Hub - Setup Guide

This guide will help you set up and run the HeatAware Hub application locally.

## Prerequisites

### Backend Requirements
- Python 3.10 or higher
- PostgreSQL 14 or higher
- Redis 7 or higher
- pip (Python package manager)

### Frontend Requirements
- Node.js 18 or higher
- npm or yarn

### API Keys
- OpenWeather API key (get one at https://openweathermap.org/api)

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your configuration
# IMPORTANT: Add your OpenWeather API key
```

Required environment variables:
- `OPENWEATHER_API_KEY`: Your OpenWeather API key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Random secret key for JWT tokens

### 5. Set Up Database

#### Create PostgreSQL Database
```sql
CREATE DATABASE heataware;
CREATE USER heataware_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE heataware TO heataware_user;
```

#### Run Migrations (when implemented)
```bash
# This will be added when Alembic migrations are set up
alembic upgrade head
```

### 6. Start Redis
```bash
# Windows (if installed as service)
redis-server

# Linux/Mac
redis-server
```

### 7. Run the Backend Server
```bash
# Development mode with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the main.py directly
python app/main.py
```

The API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment (Optional)
Create a `.env` file in the frontend directory:
```
VITE_API_BASE_URL=http://localhost:8000
```

### 4. Run Development Server
```bash
npm run dev
```

The frontend will be available at: http://localhost:5173

## Testing the Application

### 1. Health Check
Visit http://localhost:8000/health to verify the backend is running.

### 2. Try the Risk Calculator
1. Open http://localhost:5173 in your browser
2. Enter coordinates (e.g., 40.7128, -74.0060 for New York)
3. Select a match time
4. Click "Calculate Risk"

### 3. API Testing
Use the Swagger UI at http://localhost:8000/docs to test API endpoints directly.

## Sample API Requests

### Get Current Weather
```bash
curl "http://localhost:8000/api/v1/weather/current?latitude=40.7128&longitude=-74.0060"
```

### Calculate Risk
```bash
curl -X POST "http://localhost:8000/api/v1/risk-analysis/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "match_time": "2026-06-15T18:00:00Z"
  }'
```

## Troubleshooting

### Backend Issues

#### Import Errors
Make sure you're in the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### Database Connection Errors
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists and user has permissions

#### Redis Connection Errors
- Verify Redis is running: `redis-cli ping` (should return PONG)
- Check REDIS_URL in .env

#### OpenWeather API Errors
- Verify your API key is valid
- Check you haven't exceeded rate limits (60 calls/minute on free tier)
- Ensure OPENWEATHER_API_KEY is set in .env

### Frontend Issues

#### Module Not Found Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### API Connection Errors
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Ensure proxy is configured in vite.config.js

#### Build Errors
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

## Development Workflow

### Backend Development
1. Make changes to Python files
2. Server auto-reloads (if using --reload flag)
3. Test changes via Swagger UI or frontend

### Frontend Development
1. Make changes to Vue files
2. Vite hot-reloads automatically
3. View changes in browser immediately

### Adding New Features
1. Backend: Add models, services, and API endpoints
2. Frontend: Add components, views, and API calls
3. Test integration between frontend and backend

## Production Deployment

### Backend
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend
```bash
# Build for production
npm run build

# Serve with a static file server
# The dist/ folder contains the built files
```

## Next Steps

1. **Add Sample Data**: Create sample stadium and match data
2. **Implement Database Migrations**: Set up Alembic for schema management
3. **Add Authentication**: Implement user authentication if needed
4. **Deploy**: Deploy to cloud platform (AWS, Azure, GCP)
5. **Monitor**: Set up logging and monitoring

## Support

For issues or questions:
- Check the main README.md
- Review API documentation at /docs
- Open an issue on GitHub

---

**Happy Coding! 🚀**