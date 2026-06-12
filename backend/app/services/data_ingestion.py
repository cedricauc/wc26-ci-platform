"""
Data ingestion service for loading match schedules and stadium data
"""
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import logging


from ..models.db_init import SessionLocal
from ..models.database import Team, Stadium, Match


logger = logging.getLogger(__name__)


class DataIngestionService:
    """Service for ingesting match, team, and stadium data from the database"""

    def __init__(self):
        self._matches_cache = None
        self._stadiums_cache = None
        self._teams_cache = None

    # ---------------------------
    # Helpers
    # ---------------------------

    def _session(self) -> Session:
        return SessionLocal()

    def _to_dict(self, obj) -> Dict[str, Any]:
        """Convert SQLAlchemy model to a plain dict"""
        return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}

    # ---------------------------
    # Matches
    # ---------------------------

    def load_matches(self) -> List[Dict[str, Any]]:
        if self._matches_cache is not None:
            return self._matches_cache

        try:
            db = self._session()
            rows = db.query(Match).all()

            matches = []
            for m in rows:
                d = self._to_dict(m)

                # Build kickoff datetime if fields exist
                if "match_date" in d and "kickoff_time" in d:
                    # Normalize match_date
                    match_date = d.get("match_date")
                    if isinstance(match_date, str):
                        match_date = datetime.fromisoformat(match_date)

                    # Normalize kickoff_time
                    kickoff_time = d.get("kickoff_time")
                    if isinstance(kickoff_time, str):
                        kickoff_time = datetime.fromisoformat(kickoff_time)

                    # Final normalized fields
                    d["match_date"] = match_date.date().isoformat()
                    d["kickoff_datetime"] = kickoff_time.isoformat()

                d.setdefault("status", "scheduled")
                matches.append(d)

            self._matches_cache = matches
            logger.info(f"Loaded {len(matches)} matches from DB")
            return matches

        except Exception as e:
            logger.error(f"Error loading matches from DB: {e}")
            return []

    # ---------------------------
    # Stadiums
    # ---------------------------

    def load_stadiums(self) -> List[Dict[str, Any]]:
        if self._stadiums_cache is not None:
            return self._stadiums_cache

        try:
            db = self._session()
            rows = db.query(Stadium).all()

            stadiums = [self._to_dict(s) for s in rows]
            self._stadiums_cache = stadiums

            logger.info(f"Loaded {len(stadiums)} stadiums from DB")
            return stadiums

        except Exception as e:
            logger.error(f"Error loading stadiums from DB: {e}")
            return []

    # ---------------------------
    # Teams
    # ---------------------------

    def load_teams(self) -> List[str]:
        if self._teams_cache is not None:
            return self._teams_cache

        try:
            db = self._session()
            rows = db.query(Team).all()

            teams = sorted(
                [{"id": t.id, "name": t.name, "code": t.code} for t in rows],
                key=lambda x: x["name"]
            )
            self._teams_cache = teams

            logger.info(f"Loaded {len(teams)} teams from DB")
            return teams

        except Exception as e:
            logger.error(f"Error loading teams from DB: {e}")
            return []
        
    
    def extract_unique_teams(self) -> List[str]:
        if self._teams_cache is not None:
            return self._teams_cache

        try:
            db = self._session()
            rows = db.query(Team).all()

            names = sorted([t.name for t in rows])
            self._teams_cache = names

            logger.info(f"Loaded {len(names)} teams from DB")
            return names

        except Exception as e:
            logger.error(f"Error loading teams from DB: {e}")
            return []

    # ---------------------------
    # Query helpers
    # ---------------------------
    def get_team_by_id(self, team_id: int):
        teams = self.load_teams()
        return next((t for t in teams if t["id"] == team_id), None)

    def get_match_by_id(self, match_id: int):
        matches = self.load_matches()
        return next((m for m in matches if m["match_number"] == match_id), None)

    def get_stadium_by_name(self, stadium_name: str):
        stadiums = self.load_stadiums()
        return next((s for s in stadiums if s["name"] == stadium_name), None)
    
    def get_stadium_by_id(self, stadium_id: int):
        stadiums = self.load_stadiums()
        return next((s for s in stadiums if s["id"] == stadium_id), None)

    def get_matches_by_date(self, date: str):
        matches = self.load_matches()
        return [m for m in matches if m["match_date"] == date]

    def get_matches_by_stadium(self, stadium_name: str):
        matches = self.load_matches()
        return [m for m in matches if m["stadium"] == stadium_name]

    def get_upcoming_matches(self, limit: int = 10):
        matches = self.load_matches()
        now = datetime.utcnow()

        upcoming = [
            m for m in matches
            if datetime.fromisoformat(m["kickoff_datetime"]) > now
        ]

        upcoming.sort(key=lambda x: x["kickoff_datetime"])
        return upcoming[:limit]

    def get_match_with_stadium(self, match_id: int):
        match = self.get_match_by_id(match_id)
        if not match:
            return None

        stadium = self.get_stadium_by_id(match["stadium_id"])
        if stadium:
            match["stadium_data"] = stadium

        home_team = self.get_team_by_id(match["home_team_id"])
        if home_team:
            match["home_team"] = home_team["name"]

        away_team = self.get_team_by_id(match["away_team_id"])
        if away_team:
            match["away_team"] = away_team["name"]

        return match

    def get_stadium_zones(self, stadium_name: str):
        stadium = self.get_stadium_by_name(stadium_name)
        if not stadium:
            return None

        return {
            "seating_blocks": stadium.get("seating_blocks", {}),
            "pitch_zones": stadium.get("pitch_zones", {}),
            "sun_exposed_areas": stadium.get("sun_exposed_areas", []),
        }

    def clear_cache(self):
        self._matches_cache = None
        self._stadiums_cache = None
        self._teams_cache = None
        logger.info("Data cache cleared")


# Global instance
data_service = DataIngestionService()
