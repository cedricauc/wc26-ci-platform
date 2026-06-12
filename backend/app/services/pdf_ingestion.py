"""
PDF Ingestion Service - Orchestrates PDF upload, extraction, and database insertion
"""
import logging
import os
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from difflib import get_close_matches
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, literal

from ..models.database import PDFDocument, Team, Stadium, Match
from .docling_service import docling_service
from .pdf_parser import pdf_parser

logger = logging.getLogger(__name__)


class PDFIngestionService:
    """Service for ingesting PDF documents into the database"""
    
    def __init__(self, upload_dir: str = "backend/data/uploads"):
        """
        Initialize ingestion service
        
        Args:
            upload_dir: Directory to store uploaded PDFs
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def ingest_pdf(
        self,
        file_path: str,
        filename: str,
        document_type: str,
        db: Session,
        uploaded_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete PDF ingestion pipeline
        
        Args:
            file_path: Path to the uploaded PDF file
            filename: Original filename
            document_type: Type of document (team, stadium, game)
            db: Database session
            uploaded_by: User who uploaded the document
            
        Returns:
            Dictionary with ingestion results
        """
        start_time = time.time()
        
        # Create PDF document record
        file_size = os.path.getsize(file_path)
        pdf_doc = PDFDocument(
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            document_type=document_type,
            status="processing",
            uploaded_by=uploaded_by,
            extraction_started_at=datetime.utcnow()
        )
        db.add(pdf_doc)
        db.commit()
        db.refresh(pdf_doc)
        
        try:
            # Step 1: Extract data using Docling
            logger.info(f"Extracting data from {filename} using Docling")
            extracted_data = docling_service.extract_from_pdf(file_path)
            
            # Store raw extraction
            pdf_doc.raw_extraction = extracted_data
            db.commit()
            
            # Step 2: Parse and normalize data
            logger.info(f"Parsing {document_type} data from extraction")

            if document_type == "stadium":
                parsed_entities = pdf_parser.parse_stadium_pdf(extracted_data)
                entities_created = await self._insert_stadiums(parsed_entities, db)
            elif document_type == "game":
                parsed_entities = pdf_parser.parse_game_pdf(extracted_data)
                entities_created = await self._insert_games(parsed_entities, db)
            else:
                raise ValueError(f"Unknown document type: {document_type}")
            
            # Step 3: Update PDF document record
            pdf_doc.normalized_data = {
                "parsed_count": len(parsed_entities),
                "entities": parsed_entities
            }
            pdf_doc.entities_created = entities_created
            pdf_doc.status = "completed"
            pdf_doc.extraction_completed_at = datetime.utcnow()
            db.commit()
            
            processing_time = time.time() - start_time
            
            logger.info(f"Successfully ingested {filename}. Created {sum(len(v) for v in entities_created.values())} entities in {processing_time:.2f}s")
            
            return {
                "document_id": pdf_doc.id,
                "filename": filename,
                "document_type": document_type,
                "status": "completed",
                "entities_created": entities_created,
                "extraction_summary": {
                    "tables_found": len(extracted_data.get('tables', [])),
                    "paragraphs_found": len(extracted_data.get('paragraphs', [])),
                    "entities_parsed": len(parsed_entities),
                    "entities_inserted": sum(len(v) for v in entities_created.values())
                },
                "processing_time_seconds": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error ingesting PDF {filename}: {e}")
            
            # Update document record with error
            pdf_doc.status = "failed"
            pdf_doc.error_message = str(e)
            pdf_doc.extraction_completed_at = datetime.utcnow()
            db.commit()
            
            return {
                "document_id": pdf_doc.id,
                "filename": filename,
                "document_type": document_type,
                "status": "failed",
                "error_message": str(e),
                "processing_time_seconds": time.time() - start_time
            }
    
    async def _insert_stadiums(self, stadiums: List[Dict[str, Any]], db: Session) -> Dict[str, List[int]]:
        """Insert parsed stadiums into database"""
        created_ids = []
        
        for stadium_data in stadiums:
            try:
                # Check if stadium already exists
                existing_stadium = db.query(Stadium).filter(
                    Stadium.name == stadium_data['name']
                ).first()
                
                if existing_stadium:
                    logger.info(f"Stadium {stadium_data['name']} already exists, skipping")
                    created_ids.append(existing_stadium.id)
                    continue
                
                # Create new stadium
                stadium = Stadium(
                    name=stadium_data['name'],
                    address=stadium_data.get('address', 'Unknown'),
                    latitude=stadium_data.get('latitude', 0.0),
                    longitude=stadium_data.get('longitude', 0.0),
                    capacity=stadium_data.get('capacity', 50000),
                    roof_coverage=stadium_data.get('roof_coverage', 0.0)
                )
                db.add(stadium)
                db.commit()
                db.refresh(stadium)
                
                created_ids.append(stadium.id)
                logger.info(f"Created stadium: {stadium.name} (ID: {stadium.id})")
                
            except Exception as e:
                logger.error(f"Error inserting stadium {stadium_data.get('name')}: {e}")
                db.rollback()
        
        return {"stadiums": created_ids}
    
    async def _insert_games(self, games: List[Dict[str, Any]], db: Session) -> Dict[str, List[int]]:
        """Insert parsed games into database"""
        created_ids = []

        # Compile once outside the loop
        tbd_pattern = re.compile(
            r'^\s*(tbd|tba|winner|runner.?up|match\s*\d+|group\s+[a-l])\b',
            re.IGNORECASE
        )

        max_match_number = db.query(func.max(Match.match_number)).scalar() or 0
        next_match_number = max_match_number + 1

        for game_data in games:
            try:
                home_team_name = game_data.get('home_team', '')
                away_team_name = game_data.get('away_team', '')

                # Skip TBD/placeholder games
                if tbd_pattern.match(home_team_name) or tbd_pattern.match(away_team_name):
                    logger.info(f"Skipping TBD/placeholder game: '{home_team_name}' v '{away_team_name}'")
                    continue

                home_team = self._find_or_create_team(home_team_name, db)
                away_team = self._find_or_create_team(away_team_name, db)

                if not home_team or not away_team:
                    logger.warning(f"Could not find/create teams for game: {game_data}")
                    continue

                # Find stadium — strip leading junk like "- -", "Group X" before lookup
                stadium = None
                stadium_name = game_data.get('stadium')

                if stadium_name:
                    # 1. Strip leading dashes/spaces
                    stadium_name = re.sub(r'^[\s\-–—]+', '', stadium_name)
                    
                    # 2. Strip "Group X" prefix (with optional dash, with or without space before venue)
                    stadium_name = re.sub(r'^Group\s+[A-L]\b\s*[-–—]?\s*', '', stadium_name, flags=re.IGNORECASE)
                    
                    # 3. Strip any remaining leading dashes/spaces
                    stadium_name = re.sub(r'^[\s\-–—]+', '', stadium_name)
                    
                    # 4. If multiple venues concatenated (e.g. "Los Angeles Stadium BC Place Vancouver"),
                    #    take only the FIRST venue found
                    venue_pattern = re.compile(
                        r'([\w\s\'\-çÇéÉüÜ]+?(?:Stadium|Arena|Field|Place|Estadio)(?:\s+\w+)?)',
                        re.IGNORECASE
                    )
                    venue_match = venue_pattern.match(stadium_name)
                    if venue_match:
                        stadium_name = venue_match.group(1).strip()

                    # 5. Final cleanup
                    stadium_name = stadium_name.strip(" -–")
                    
                    logger.info(f"Looking for stadium (cleaned): '{stadium_name}'")

                if not stadium_name:
                    logger.warning(f"Empty stadium name after cleaning, skipping game")
                    continue

                # Lookup
                stadium = db.query(Stadium).filter(Stadium.name.ilike(stadium_name)).first()
                if not stadium:
                    stadium = db.query(Stadium).filter(or_(
                        Stadium.name.ilike(f"%{stadium_name}%"),
                        func.lower(literal(stadium_name.lower())).contains(func.lower(Stadium.name))
                    )).first()
                if not stadium:
                    all_stadiums = db.query(Stadium).all()
                    all_names = [s.name for s in all_stadiums]
                    matches = get_close_matches(stadium_name, all_names, n=1, cutoff=0.6)
                    if matches:
                        stadium = next((s for s in all_stadiums if s.name == matches[0]), None)

                if not stadium:
                    logger.warning(
                        f"Skipping '{home_team_name}' v '{away_team_name}': "
                        f"stadium '{stadium_name}' not found in DB"
                    )
                    continue

                match_date = self._parse_match_datetime(
                    game_data.get('match_date'),
                    game_data.get('kickoff_time')
                )

                match_number = game_data.get('match_number')
                if not match_number:
                    match_number = next_match_number
                    next_match_number += 1

                existing_match = db.query(Match).filter(
                    Match.match_number == match_number
                ).first()
                if existing_match:
                    logger.info(f"Match {match_number} already exists, skipping")
                    created_ids.append(existing_match.id)
                    continue

                duplicate_query = db.query(Match).filter(
                    Match.home_team_id == home_team.id,
                    Match.away_team_id == away_team.id,
                )
                if stadium:
                    duplicate_query = duplicate_query.filter(Match.stadium_id == stadium.id)
                duplicate_match = duplicate_query.first()

                if duplicate_match:
                    stadium_label = stadium.name if stadium else "unknown stadium"
                    logger.info(f"Match {home_team.name} vs {away_team.name} at {stadium_label} already exists, skipping")
                    created_ids.append(duplicate_match.id)
                    continue

                match = Match(
                    match_number=match_number,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    stadium_id=stadium.id if stadium else None,
                    match_date=match_date,
                    kickoff_time=match_date.replace(hour=16, minute=0, second=0, microsecond=0) if match_date else None,
                    stage=game_data.get('stage', 'group'),
                    group_name=game_data.get('group_name'),
                    status="scheduled"
                )
                db.add(match)
                db.commit()
                db.refresh(match)

                created_ids.append(match.id)
                logger.info(f"Created match: {home_team.name} vs {away_team.name} (ID: {match.id})")

            except Exception as e:
                logger.error(f"Error inserting game '{game_data.get('home_team')}' v '{game_data.get('away_team')}': {e}", exc_info=True)
                db.rollback()

        return {"matches": created_ids}
    
    def _find_or_create_team(self, team_name: Optional[str], db: Session) -> Optional[Team]:
        """Find existing team or create new one"""
        if not team_name:
            return None

        # 1. Exact match (case-insensitive)
        team = db.query(Team).filter(Team.name.ilike(team_name)).first()
        if team:
            return team

        # 2. Partial match — DB name contains search term or vice versa
        team = db.query(Team).filter(or_(
            Team.name.ilike(f"%{team_name}%"),
            func.lower(literal(team_name.lower())).contains(func.lower(Team.name))
        )).first()
        if team:
            return team

        all_teams = db.query(Team).all()
        all_names = [t.name for t in all_teams]

        def token_sort(s: str) -> str:
            return ' '.join(sorted(s.lower().split()))

        # 3. Exact token-sort match (handles "DR Congo" vs "Congo DR")
        sorted_input = token_sort(team_name)
        for t in all_teams:
            if token_sort(t.name) == sorted_input:
                logger.info(f"Token-sort exact matched '{team_name}' → '{t.name}'")
                return t

        # 4. Fuzzy match — HIGH cutoff (0.85) to avoid "USA"→"Tunisia" disasters
        matches = get_close_matches(team_name, all_names, n=1, cutoff=0.85)
        if matches:
            team = next((t for t in all_teams if t.name == matches[0]), None)
            if team:
                logger.info(f"Fuzzy-matched team '{team_name}' → '{team.name}'")
                return team

        # 5. Token-sort fuzzy — also HIGH cutoff
        sorted_names = {token_sort(t.name): t for t in all_teams}
        matches = get_close_matches(sorted_input, sorted_names.keys(), n=1, cutoff=0.85)
        if matches:
            team = sorted_names[matches[0]]
            logger.info(f"Token-sort fuzzy matched '{team_name}' → '{team.name}'")
            return team

        # 6. Create new team
        try:
            import unicodedata
            normalized = unicodedata.normalize('NFKD', team_name)
            ascii_name = normalized.encode('ascii', 'ignore').decode('ascii').strip()
            base_code = (ascii_name[:3] if ascii_name else team_name[:3]).upper()

            code = base_code
            suffix = 1
            while db.query(Team).filter(Team.code == code).first():
                code = f"{base_code[:2]}{suffix}"
                suffix += 1

            team = Team(name=team_name, code=code)
            db.add(team)
            db.commit()
            db.refresh(team)
            logger.info(f"Auto-created team: {team.name} (code: {code})")
            return team
        except Exception as e:
            logger.error(f"Error creating team {team_name}: {e}")
            db.rollback()
            return None
    
    def _parse_match_datetime(self, date_str: Optional[str], time_str: Optional[str]) -> Optional[datetime]:
        """Parse match date and time strings"""
        if not date_str:
            logger.warning("No date string provided, returning None")
            return None

        for fmt in [
            '%Y-%m-%d',    # 2025-06-11
            '%d-%m-%Y',    # 11-06-2025
            '%d/%m/%Y',    # 11/06/2025  ← was missing, causing month/day swap
            '%m/%d/%Y',    # 06/11/2025
            '%Y/%m/%d',    # 2025/06/11
            '%d %B %Y',    # 11 June 2025
            '%B %d, %Y',   # June 11, 2025
            '%d %b %Y',    # 11 Jun 2025
        ]:
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt)

                if time_str:
                    time_str_clean = time_str.strip().upper()
                    try:
                        if 'PM' in time_str_clean or 'AM' in time_str_clean:
                            time_obj = datetime.strptime(time_str_clean, '%I:%M %p')
                        else:
                            time_obj = datetime.strptime(time_str_clean, '%H:%M')
                        date_obj = date_obj.replace(hour=time_obj.hour, minute=time_obj.minute)
                    except ValueError:
                        logger.warning(f"Could not parse time '{time_str}', using midnight")

                logger.info(f"Parsed date '{date_str}' + time '{time_str}' → {date_obj} (fmt: {fmt})")
                return date_obj

            except ValueError:
                continue

        logger.error(f"Could not parse date '{date_str}' with any known format, returning None")
        return None  # ← None instead of utcnow() so the caller knows it failed
    
    def get_document_status(self, document_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """Get status of a PDF document"""
        pdf_doc = db.query(PDFDocument).filter(PDFDocument.id == document_id).first()
        
        if not pdf_doc:
            return None
        
        return {
            "id": pdf_doc.id,
            "filename": pdf_doc.filename,
            "document_type": pdf_doc.document_type,
            "status": pdf_doc.status,
            "file_size": pdf_doc.file_size,
            "entities_created": pdf_doc.entities_created,
            "error_message": pdf_doc.error_message,
            "created_at": pdf_doc.created_at.isoformat(),
            "extraction_started_at": pdf_doc.extraction_started_at.isoformat() if pdf_doc.extraction_started_at else None,
            "extraction_completed_at": pdf_doc.extraction_completed_at.isoformat() if pdf_doc.extraction_completed_at else None
        }
    
    def list_documents(self, db: Session, document_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List all PDF documents"""
        query = db.query(PDFDocument)
        
        if document_type:
            query = query.filter(PDFDocument.document_type == document_type)
        
        documents = query.order_by(PDFDocument.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "document_type": doc.document_type,
                "status": doc.status,
                "file_size": doc.file_size,
                "entities_created": doc.entities_created,
                "created_at": doc.created_at.isoformat()
            }
            for doc in documents
        ]


# Singleton instance
pdf_ingestion_service = PDFIngestionService()