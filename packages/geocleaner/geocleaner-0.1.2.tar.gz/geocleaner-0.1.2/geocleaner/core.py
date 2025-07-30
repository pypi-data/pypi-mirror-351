# geocleaner/core.py

import re

ABBREVIATION_MAP = {
    r"\bSt\.?$": "Street",
    r"\bRd\.?$": "Road",
    r"\bAve\.?$": "Avenue",
    r"\bBlvd\.?$": "Boulevard",
    r"\bDr\.?$": "Drive",
    r"\bLn\.?$": "Lane",
    r"\bCt\.?$": "Court",
    r"\bPl\.?$": "Place",
    r"\bSq\.?$": "Square",
    r"\bPkwy\.?$": "Parkway",
    r"\bCir\.?$": "Circle",
    r"\bHwy\.?$": "Highway"
}

def clean_location(location_str):
    """
    Cleans a single location string by:
    - Trimming leading/trailing whitespace
    - Replacing multiple spaces with one
    - Title-casing
    - Expanding common street abbreviations
    """
    location_str = location_str.strip()
    location_str = re.sub(r"\s+", " ", location_str)  # collapse multiple spaces
    location_str = location_str.title()
    for pattern, replacement in ABBREVIATION_MAP.items():
        location_str = re.sub(pattern, replacement, location_str)
    return location_str

def clean_locations(location_list):
    return [clean_location(loc) for loc in location_list]
