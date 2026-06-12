"""
PDF Parser Service - Normalizes Docling extraction into database entities
"""
import logging
import re
import time
from typing import Dict, Any, List, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

logger = logging.getLogger(__name__)


class PDFParserService:
    """Service for parsing extracted PDF data into structured entities"""
    
    # Venue-terminator words — when one of these precedes a new "Team v Team", we split
    _VENUE_TERMINATORS = re.compile(
        r'\b(Stadium|Arena|Field|Place|Estadio|Vancouver|Monterrey|Guadalajara)\b',
        re.IGNORECASE
    )

    # Known junk lines to discard entirely
    _JUNK_RE = re.compile(
        r'^(FIFA\s+(Store|World)|Shop\s+now|Fantasy|Tap\s+to|Who\s+will|SUBMIT|'
        r'Play\s+Zone|Bracket|26\s+Superstar|Latest\s+FIFA|Group\s+[A-L]\s+runners|'
        r'Match\s+\d+\s+-\s+Group|Winner\s+match)',
        re.IGNORECASE
    )

    def __init__(self):
        """Initialize parser with patterns and rules"""
        # Common patterns for extraction
        self.team_code_pattern = re.compile(r'\b([A-Z]{3})\b')
        self.date_patterns = [
            re.compile(r'(\d{4}[-/]\d{2}[-/]\d{2})'),  # YYYY-MM-DD or YYYY/MM/DD
            re.compile(r'(\d{2}[-/]\d{2}[-/]\d{4})'),  # DD-MM-YYYY or DD/MM/YYYY
            re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})', re.IGNORECASE),
            # Pattern for "Sunday, 21 June 2026" format
            re.compile(r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', re.IGNORECASE)
        ]
        self.time_pattern = re.compile(r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?')
        self.capacity_pattern = re.compile(r'capacity[:\s]+(\d{1,3}(?:,\d{3})*)', re.IGNORECASE)
        self.coordinate_pattern = re.compile(r'(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)')

        # Geocoder for resolving stadium addresses to lat/lng
        self._geolocator = Nominatim(user_agent="pdf_parser_service")

    def _clean_address(self, address: str) -> str:
        """Fix common OCR artifacts and normalize address string."""
        # Fix broken words with unexpected spaces (e.g. "T oronto" -> "Toronto")
        address = re.sub(r'\b([A-Z])\s+([a-z])', r'\1\2', address)
        # Collapse multiple spaces/newlines
        address = re.sub(r'\s+', ' ', address).strip()
        return address
    
    def _clean_team_name(self, name: str) -> str:
        if not name:
            return ""

        # Strip everything from the first isolated dash separator onward
        # e.g. "Paraguay - - Los Angeles Stadium" → "Paraguay"
        # e.g. "South Africa - Group A - ..." → "South Africa"
        name = re.sub(r'\s+-.*$', '', name)

        # Remove accidental Group text
        name = re.sub(r'\s+Group\s+[A-Z]\b.*$', '', name, flags=re.IGNORECASE)

        # Remove stadium bleed
        name = re.sub(
            r'\s+(Stadium|Arena|Field|Place|Estadio).*$',
            '',
            name,
            flags=re.IGNORECASE
        )

        # Collapse whitespace
        name = re.sub(r'\s+', ' ', name)

        # Strip lone 3-letter code suffix from multi-word names
        name = re.sub(r'\s+[A-Z]{3}$', lambda m: m.group(0) if len(name.split()) == 1 else '', name)

        return name.strip()

    def _geocode_address(self, address: str) -> Dict[str, float]:
        """Try geocoding with progressively simplified address forms."""
        address = self._clean_address(address)

        # Build fallback candidates: full address, then drop leading components one by one
        candidates = [address]

        # Also try stripping postal/zip code (common Nominatim failure point)
        no_postal = re.sub(r'\b[A-Z0-9]{2,4}\s?[A-Z0-9]{3}\b', '', address)  # Canadian: M6K 3C3
        no_postal = re.sub(r'\bC\.P\.?\s*\d{5}\b', '', no_postal)             # Mexican: C.P. 67140
        no_postal = re.sub(r',?\s*\d{5}\b', '', no_postal)                    # Generic 5-digit
        no_postal = re.sub(r'\s+', ' ', no_postal).strip().strip(',')
        if no_postal != address:
            candidates.append(no_postal)

        # Try dropping everything before the city (last 2 comma-separated parts)
        parts = [p.strip() for p in address.split(',')]
        if len(parts) >= 3:
            candidates.append(', '.join(parts[-3:]))  # last 3 parts
        if len(parts) >= 2:
            candidates.append(', '.join(parts[-2:]))  # city + country only

        for candidate in candidates:
            try:
                time.sleep(1)
                location = self._geolocator.geocode(candidate, timeout=10)
                if location:
                    return {'latitude': location.latitude, 'longitude': location.longitude}
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                logger.warning(f"Geocoding failed for '{candidate}': {e}")

        logger.warning(f"Could not geocode address after all attempts: '{address}'")
        return {}
    
    def parse_stadium_pdf(self, extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse stadium information from extracted PDF data
        
        Args:
            extracted_data: Docling extraction result
            
        Returns:
            List of stadium dictionaries
        """
        stadiums = []
        
        try:
            # Extract from tables
            for table in extracted_data.get('tables', []):
                stadiums.extend(self._parse_stadium_table(table))
            
            # Extract from paragraphs
            paragraphs = extracted_data.get('paragraphs', [])
            stadiums.extend(self._parse_stadium_paragraphs(paragraphs))
            
            # Deduplicate stadiums by name
            stadiums = self._deduplicate_stadiums(stadiums)
            
            logger.info(f"Parsed {len(stadiums)} stadiums from PDF")
            
        except Exception as e:
            logger.error(f"Error parsing stadium PDF: {e}")
        
        return stadiums
    
    def _is_fixture_line(self, line: str) -> bool:
        """
        Return True only if this line starts a genuine fixture.
        Rejects lines where the word before 'v' is a known continuation
        prefix (e.g. 'New', 'Saudi', 'Bosnia') — those are split team names.
        """
        m = re.search(r"(.+?)\s+v\s+", line, re.IGNORECASE)
        if not m:
            return False

        # The last word before " v " — if it's a known prefix it's a split name
        pre_v = m.group(1).strip()

        # Also reject if pre_v is a single very short word (likely a fragment)
        if len(pre_v.split()) == 1 and len(pre_v) <= 4:
            return False

        return True

    def _split_line_on_fixtures(self, line: str) -> List[str]:
        """
        Split a single raw line that may contain multiple concatenated fixtures.
        
        Strategy: find every occurrence of " v " and decide whether the text
        before it starts a new fixture by checking if the immediately preceding
        context ends with a venue terminator (or start of string).
        
        e.g.:
        "Mexico v South Africa - Group A - Mexico City Stadium Korea Republic v Czechia..."
        → ["Mexico v South Africa - Group A - Mexico City Stadium",
            "Korea Republic v Czechia..."]
        """
        # Find all " v " positions
        v_positions = [m.start() for m in re.finditer(r'\s+v\s+', line, re.IGNORECASE)]
        
        if len(v_positions) <= 1:
            return [line]
        
        split_points = [0]  # always start from beginning
        
        for vpos in v_positions[1:]:  # skip the first " v " — that's the main fixture
            # Look at the text between the previous split point and this " v "
            # Find the last venue terminator before this " v "
            prefix = line[split_points[-1]:vpos]
            term_match = None
            for m in self._VENUE_TERMINATORS.finditer(prefix):
                term_match = m
            
            if term_match:
                # Split just after the venue terminator word ends
                split_at = split_points[-1] + term_match.end()
                # Skip any trailing whitespace/dashes after the terminator
                while split_at < len(line) and line[split_at] in ' \t-–':
                    split_at += 1
                split_points.append(split_at)
        
        # Build parts from split points
        parts = []
        for i, start in enumerate(split_points):
            end = split_points[i + 1] if i + 1 < len(split_points) else len(line)
            part = line[start:end].strip()
            if part:
                parts.append(part)
        
        return parts if parts else [line]

    def _is_fixture_line(self, line: str) -> bool:
        """True if this line begins a fixture (has ' v ' with a real team before it)."""
        m = re.match(r'^(.+?)\s+v\s+', line, re.IGNORECASE)
        if not m:
            return False
        pre = m.group(1).strip()
        # Must have at least one word and not be a fragment like "Match 73 - Group A runners-up"
        if re.search(r'\b(Match\s+\d+|runners.up|third\s+place|winners?)\b', pre, re.IGNORECASE):
            return False
        return True

    def parse_game_pdf(self, extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        games = []
        current_date = None
        current_block: List[str] = []

        paragraphs = extracted_data.get("paragraphs", [])

        for para in paragraphs:
            text = (para.get("text") or "").strip()
            if not text:
                continue

            for raw_line in text.split("\n"):
                raw_line = raw_line.strip()
                if not raw_line:
                    continue

                # Discard junk lines early
                if self._JUNK_RE.match(raw_line):
                    continue

                # Date header?
                parsed_date = self._extract_date_from_text(raw_line)
                if parsed_date:
                    if current_block:
                        games.extend(self._parse_game_block(current_block, current_date))
                        current_block = []
                    current_date = parsed_date
                    continue

                # Split line in case it contains two concatenated fixtures
                sub_lines = self._split_line_on_fixtures(raw_line)

                for sub_line in sub_lines:
                    sub_line = sub_line.strip()
                    if not sub_line or self._JUNK_RE.match(sub_line):
                        continue

                    if self._is_fixture_line(sub_line):
                        if current_block:
                            games.extend(self._parse_game_block(current_block, current_date))
                        current_block = [sub_line]
                    else:
                        current_block.append(sub_line)

        if current_block:
            games.extend(self._parse_game_block(current_block, current_date))

        games = self._deduplicate_games(games)
        logger.info(f"Parsed {len(games)} games")
        return games
    
    def _parse_stadium_table(self, table: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse stadiums from a table structure"""
        stadiums = []
        
        try:
            headers = table.get('headers', [])
            rows = table.get('rows', [])
            
            # Identify column indices
            name_idx = self._find_column_index(headers, ['stadium', 'name', 'venue'])
            address_idx = self._find_column_index(headers, ['address', 'location'])
            capacity_idx = self._find_column_index(headers, ['capacity', 'seats'])
            
            for row in rows:
                if not row or len(row) == 0:
                    continue
                
                stadium = {}
                
                # Extract stadium name
                if name_idx is not None and name_idx < len(row):
                    stadium['name'] = str(row[name_idx]).strip()
                elif len(row) > 0:
                    stadium['name'] = str(row[0]).strip()
                
                # Extract address
                if address_idx is not None and address_idx < len(row):
                    stadium['address'] = str(row[address_idx]).strip()
                elif len(row) > 1:
                    stadium['address'] = str(row[1]).strip()
                
                # Extract capacity
                if capacity_idx is not None and capacity_idx < len(row):
                    capacity_str = str(row[capacity_idx]).strip()
                    stadium['capacity'] = self._parse_capacity(capacity_str)
                
                if stadium.get('name'):
                    stadiums.append(stadium)
                    
        except Exception as e:
            logger.warning(f"Error parsing stadium table: {e}")
        
        return stadiums
    
    def _parse_stadium_paragraphs(self, paragraphs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        stadiums = []

        stadium_capacity_pattern = re.compile(r'Stadium\s+capacity\s*:\s*([\d,]+)', re.IGNORECASE)
        address_pattern = re.compile(r'Address\s*:\s*(.+?)(?=Stadium\s+capacity|Click\s+here|Please\s+note|\Z)', re.IGNORECASE | re.DOTALL)

        # Known non-stadium section headers to ignore
        _ignore_headers = {
            'stadium information', 'here are the relevant details',
            'latest fifa world cup', 'fifa world cup 2026'
        }

        i = 0
        while i < len(paragraphs):
            item = paragraphs[i]
            item_type = str(item.get('type', ''))
            text = item.get('text', '').strip()

            # Stadium names are SECTION_HEADERs
            if 'section_header' in item_type.lower():
                # Skip known non-stadium headers
                if any(ignore in text.lower() for ignore in _ignore_headers):
                    i += 1
                    continue

                # Skip headers that are not stadium names (no venue keyword and no following data)
                venue_keywords = ["stadium", "arena", "field", "park", "place", "bc place"]
                is_venue = any(kw in text.lower() for kw in venue_keywords)

                if not is_venue:
                    i += 1
                    continue

                stadium = {'name': text}

                # Look ahead at the following TEXT items for address and capacity
                j = i + 1
                while j < len(paragraphs):
                    next_item = paragraphs[j]
                    next_type = str(next_item.get('type', ''))
                    next_text = next_item.get('text', '').strip()

                    # Stop when we hit the next section header
                    if 'section_header' in next_type.lower():
                        break

                    # Extract address
                    addr_match = address_pattern.search(next_text)
                    if addr_match and 'address' not in stadium:
                        stadium['address'] = addr_match.group(1).strip()

                    # Extract capacity
                    cap_match = stadium_capacity_pattern.search(next_text)
                    if cap_match and 'capacity' not in stadium:
                        stadium['capacity'] = self._parse_capacity(cap_match.group(1))

                    j += 1

                # Only add if we got at least address or capacity
                if stadium.get('address') or stadium.get('capacity'):
                    # ✅ Geocode if we have a valid address
                    if stadium.get('address'):
                        coords = self._geocode_address(stadium['address'])
                        stadium.update(coords)  # adds 'lat' and 'lng' if found

                    stadiums.append(stadium)

                i = j  # jump to where the lookahead stopped
            else:
                i += 1

        return stadiums


    def _parse_game_block(
        self,
        block: List[str],
        match_date: Optional[str]
    ) -> List[Dict[str, Any]]:

        if not block:
            return []

        logger.info(f"game pdf block {block})")

        game = {"match_date": match_date}

        match = re.match(r"(.+?)\s+v\s+(.+)", block[0], re.IGNORECASE)
        if not match:
            return []

        game["home_team"] = self._clean_team_name(match.group(1))

        away_raw = match.group(2)
        full_remainder = away_raw + " " + " ".join(
            line.strip(" -–") for line in block[1:]
        )

        # Extract group
        group_match = re.search(r"Group\s+([A-L])\b", full_remainder, re.IGNORECASE)
        if group_match:
            game["group_name"] = f"Group {group_match.group(1).upper()}"

        # Strip group text from away_raw before cleaning team name
        away_cleaned = re.sub(
            r"\s*-?\s*Group\s+[A-L]\b.*$", "", away_raw, flags=re.IGNORECASE
        )
        game["away_team"] = self._clean_team_name(away_cleaned)

        # Strip group from full remainder before stadium search
        remainder_no_group = re.sub(
            r"\s*-?\s*Group\s+[A-L]\b\s*-?\s*", " ", full_remainder, flags=re.IGNORECASE
        ).strip()

        # Extract FIRST stadium only — stop at the first venue keyword
        venue_re = re.compile(
            r"((?:[\w\u00c0-\u00ff\s\'\-]+?\s+)?(?:Stadium|Arena|Field|Place|Estadio))",
            re.IGNORECASE
        )
        venue_match = venue_re.search(remainder_no_group)
        if venue_match:
            game["stadium"] = venue_match.group(1).strip(" -–")

        return [game]
    
    def _find_column_index(self, headers: List[str], keywords: List[str]) -> Optional[int]:
        """Find column index by matching keywords"""
        for i, header in enumerate(headers):
            header_lower = str(header).lower()
            for keyword in keywords:
                if keyword.lower() in header_lower:
                    return i
        return None
    
    def _parse_capacity(self, capacity_str: str) -> Optional[int]:
        """Parse capacity string to integer"""
        try:
            # Remove commas and non-digit characters
            capacity_clean = re.sub(r'[^\d]', '', capacity_str)
            return int(capacity_clean) if capacity_clean else None
        except:
            return None
    
    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """
        Extract date from text, supporting multiple formats
        Returns date in YYYY-MM-DD format
        """
        # Month name to number mapping
        month_map = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12',
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09',
            'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        # Try pattern: "Sunday, 21 June 2026"
        match = re.search(
            r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            text,
            re.IGNORECASE
        )
        if match:
            day = match.group(1).zfill(2)
            month = month_map.get(match.group(2).lower(), '01')
            year = match.group(3)
            return f"{year}-{month}-{day}"
        
        # Try pattern: "21 June 2026" (without day of week)
        match = re.search(
            r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            text,
            re.IGNORECASE
        )
        if match:
            day = match.group(1).zfill(2)
            month = month_map.get(match.group(2).lower(), '01')
            year = match.group(3)
            return f"{year}-{month}-{day}"
        
        # Try pattern: "YYYY-MM-DD"
        match = re.search(r'(\d{4})[-/](\d{2})[-/](\d{2})', text)
        if match:
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        
        # Try pattern: "DD-MM-YYYY" or "DD/MM/YYYY"
        match = re.search(r'(\d{2})[-/](\d{2})[-/](\d{4})', text)
        if match:
            return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
        
        return None
    
    def _deduplicate_teams(self, teams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate teams"""
        seen = set()
        unique_teams = []
        
        for team in teams:
            name = team.get('name', '').lower()
            if name and name not in seen:
                seen.add(name)
                unique_teams.append(team)
        
        return unique_teams
    
    def _deduplicate_stadiums(self, stadiums: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate stadiums"""
        seen = set()
        unique_stadiums = []
        
        for stadium in stadiums:
            name = stadium.get('name', '').lower()
            if name and name not in seen:
                seen.add(name)
                unique_stadiums.append(stadium)
        
        return unique_stadiums
    
    def _deduplicate_games(self, games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate games"""
        seen = set()
        unique_games = []

        for game in games:
            key = (
                game.get("home_team", "").lower(),
                game.get("away_team", "").lower(),
                game.get("group_name", ""),
                game.get("stadium", "")
            )

            if key not in seen:
                seen.add(key)
                unique_games.append(game)
            
        return unique_games


# Singleton instance
pdf_parser = PDFParserService()