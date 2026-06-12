# PDF Document Ingestion System

## Overview

The PDF Document Ingestion System uses **Docling** to parse FIFA World Cup PDF documents (match schedules, stadium details, team information), extract structured data, normalize it, and store it in the database.

## Architecture

### Components

1. **Document Ingestion UI** (`frontend/src/views/DocumentUploadView.vue`)
   - Upload interface for Teams, Stadiums, and Games PDFs
   - Real-time upload status and feedback
   - Supports drag-and-drop file selection

2. **Ingestion API Service** (`backend/app/services/pdf_ingestion.py`)
   - Orchestrates the complete ingestion pipeline
   - Manages file uploads and storage
   - Coordinates extraction and database insertion

3. **Docling Extraction Service** (`backend/app/services/docling_service.py`)
   - Uses Docling AI to extract structured data from PDFs
   - Handles tables, paragraphs, key-value pairs, and OCR
   - Fallback to PyPDF2 when Docling is unavailable

4. **PDF Parser Service** (`backend/app/services/pdf_parser.py`)
   - Normalizes extracted data into database entities
   - Intelligent pattern matching and data validation
   - Handles various PDF formats and structures

5. **Database Layer** (`backend/app/models/database.py`)
   - Stores Teams, Stadiums, Matches, and PDF documents
   - Tracks extraction status and results
   - Maintains entity relationships

## API Endpoints

### Upload Endpoints

#### POST `/api/v1/ingest/team-pdf`
Upload a PDF containing team information.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: PDF file (required)
  - `uploaded_by`: Username (optional)

**Response:**
```json
{
  "document_id": 1,
  "filename": "teams.pdf",
  "document_type": "team",
  "status": "uploaded",
  "message": "Team PDF uploaded successfully..."
}
```

#### POST `/api/v1/ingest/stadium-pdf`
Upload a PDF containing stadium information.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: PDF file (required)
  - `uploaded_by`: Username (optional)

**Response:**
```json
{
  "document_id": 2,
  "filename": "stadiums.pdf",
  "document_type": "stadium",
  "status": "uploaded",
  "message": "Stadium PDF uploaded successfully..."
}
```

#### POST `/api/v1/ingest/game-pdf`
Upload a PDF containing match schedule.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: PDF file (required)
  - `uploaded_by`: Username (optional)

**Response:**
```json
{
  "document_id": 3,
  "filename": "schedule.pdf",
  "document_type": "game",
  "status": "uploaded",
  "message": "Game schedule PDF uploaded successfully..."
}
```

### Retrieval Endpoints

#### GET `/api/v1/teams`
Get list of all teams.

**Query Parameters:**
- `limit`: Maximum number of teams (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Brazil",
    "code": "BRA",
    "flag_url": null,
    "created_at": "2026-06-09T08:00:00Z"
  }
]
```

#### GET `/api/v1/stadiums`
Get list of all stadiums.

**Query Parameters:**
- `limit`: Maximum number of stadiums (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "name": "MetLife Stadium",
    "city": "East Rutherford",
    "country": "USA",
    "latitude": 40.8128,
    "longitude": -74.0742,
    "capacity": 82500,
    "roof_coverage": 0.0,
    "created_at": "2026-06-09T08:00:00Z"
  }
]
```

#### GET `/api/v1/games`
Get list of all matches.

**Query Parameters:**
- `date_from`: Filter by start date (YYYY-MM-DD)
- `date_to`: Filter by end date (YYYY-MM-DD)
- `limit`: Maximum number of games (default: 50)

**Response:**
```json
{
  "games": [
    {
      "id": 1,
      "match_number": 1,
      "home_team": "Mexico",
      "away_team": "South Africa",
      "stadium": "Estadio Azteca",
      "match_date": "2026-06-11T15:00:00Z",
      "stage": "group",
      "group_name": "Group A"
    }
  ],
  "count": 1
}
```

## Docling Extraction Pipeline

### Input PDFs

1. **Match Schedule PDFs**
   - Tables with match fixtures
   - Date, time, teams, stadium information
   - Group/stage classifications

2. **Stadium Information PDFs**
   - Stadium names and locations
   - Capacity and coordinates
   - Architectural details


## Normalization Layer

The parser maps Docling JSON to database entities:

### Team Extraction
- Extract team names from tables or paragraphs
- Identify FIFA codes (3-letter abbreviations)
- Parse group assignments
- Extract coach names

### Stadium Extraction
- Extract stadium names and locations
- Parse capacity numbers (handles commas)
- Identify coordinates if present
- Extract roof coverage percentages


### Game Extraction
- Parse match schedules from tables
- Extract team names (home/away)
- Parse dates and times
- Link to stadiums
- Identify match stages/groups

## Validation Rules

### Stadium Validation
- Stadium names must be unique
- City and country are required
- Capacity must be positive integer
- Coordinates must be valid lat/lng

### Game Validation
- Home and away teams must exist (auto-created if not)
- Stadium must exist in database
- Match dates must be valid
- Duplicate match numbers are skipped

## Processing Flow

```
1. User uploads PDF via frontend
   ↓
2. Backend receives file and saves to disk
   ↓
3. Create PDFDocument record (status: "processing")
   ↓
4. Run Docling extraction
   ↓
5. Store raw extraction in database
   ↓
6. Parse and normalize data
   ↓
7. Validate entities
   ↓
8. Insert/update database records
   ↓
9. Update PDFDocument (status: "completed")
   ↓
10. Return results to frontend
```

## Database Schema

### PDFDocument Table
```sql
CREATE TABLE pdf_documents (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    document_type VARCHAR(50) NOT NULL,  -- team, stadium, game
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed
    raw_extraction JSON,
    normalized_data JSON,
    extraction_started_at TIMESTAMP,
    extraction_completed_at TIMESTAMP,
    error_message TEXT,
    entities_created JSON,  -- {"teams": [1,2], "stadiums": [3]}
    uploaded_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Usage Examples

### Frontend Usage

```javascript
// Upload a team PDF
const formData = new FormData()
formData.append('file', pdfFile)
formData.append('uploaded_by', 'admin')

const response = await axios.post(
  'http://localhost:8000/api/v1/ingest/team-pdf',
  formData,
  {
    headers: { 'Content-Type': 'multipart/form-data' }
  }
)

console.log(response.data)
// {
//   "document_id": 1,
//   "filename": "teams.pdf",
//   "status": "uploaded",
//   "message": "Team PDF uploaded successfully..."
// }
```

### Backend Usage

```python
from app.services.pdf_ingestion import pdf_ingestion_service

# Ingest a PDF
result = await pdf_ingestion_service.ingest_pdf(
    file_path="/path/to/teams.pdf",
    filename="teams.pdf",
    document_type="team",
    db=db_session,
    uploaded_by="admin"
)

print(result)
# {
#   "document_id": 1,
#   "status": "completed",
#   "entities_created": {"teams": [1, 2, 3]},
#   "processing_time_seconds": 2.5
# }
```

## Error Handling

### Common Errors

1. **Invalid File Type**
   - Status: 400
   - Message: "Only PDF files are allowed"

2. **Extraction Failed**
   - Status: 500
   - Document status: "failed"
   - Error message stored in database

3. **Validation Failed**
   - Entities with validation errors are skipped
   - Partial success possible (some entities created)

4. **Database Error**
   - Transaction rolled back
   - Error logged and returned

## Configuration

### Environment Variables

```bash
# Upload directory
UPLOAD_DIR=backend/data/uploads

# Docling settings
DOCLING_OCR_ENABLED=true
DOCLING_TABLE_EXTRACTION=true

# Database connection
DATABASE_URL=postgresql://user:pass@localhost/worldcup
```

## Testing

### Manual Testing

1. Navigate to http://localhost:5173/upload
2. Select a PDF file for teams, stadiums, or games
3. Click "Upload & Process"
4. Verify success message
5. Check database for created entities

### API Testing with cURL

```bash
# Upload team PDF
curl -X POST http://localhost:8000/api/v1/ingest/team-pdf \
  -F "file=@teams.pdf" \
  -F "uploaded_by=admin"

# Get teams
curl http://localhost:8000/api/v1/teams

# Get stadiums
curl http://localhost:8000/api/v1/stadiums

# Get games
curl http://localhost:8000/api/v1/games?limit=10
```

## Troubleshooting

### Docling Not Available
- System falls back to PyPDF2
- Limited extraction capabilities
- Install Docling: `pip install docling`

### Upload Directory Not Found
- Directory is auto-created on startup
- Check permissions: `chmod 755 backend/data/uploads`

### Database Connection Issues
- Verify DATABASE_URL in .env
- Check database is running
- Ensure migrations are applied

### Extraction Produces No Results
- Check PDF format (scanned vs text-based)
- Enable OCR for scanned documents
- Verify PDF is not password-protected

## Future Enhancements

1. **Async Processing**
   - Background job queue for large PDFs
   - Progress tracking and notifications

2. **Advanced Validation**
   - ML-based entity matching
   - Fuzzy name matching for teams/stadiums

3. **Batch Upload**
   - Upload multiple PDFs at once
   - Bulk processing with progress bar

4. **Admin Dashboard**
   - View all uploaded documents
   - Retry failed extractions
   - Manual data correction

5. **Export Functionality**
   - Export extracted data to CSV/JSON
   - Generate reports on ingestion statistics
