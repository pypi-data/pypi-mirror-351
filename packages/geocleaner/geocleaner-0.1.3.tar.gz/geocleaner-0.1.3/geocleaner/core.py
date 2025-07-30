# geocleaner/core.py
import re
import unicodedata
from typing import Optional

LOCATION_ABBREVIATIONS = {
    "st": "Street",
    "ave": "Avenue",
    "rd": "Road",
    "blvd": "Boulevard",
    "ny": "New York",
    "ca": "California",
    "tx": "Texas",
    "usa": "United States",
    "dr": "Drive",
    "ln": "Lane",
    "pkwy": "Parkway"
}

COMMON_TYPOS = {
    "centre": "Center",
    "bombay": "Mumbai",
    "madras": "Chennai",
    "sao paulo": "São Paulo",
    "hongkong": "Hong Kong"
}

HYPHEN_PATTERN = re.compile(r'-+')
SPECIAL_CHARS_PATTERN = re.compile(r"[^\w\s',-]", re.UNICODE)
WHITESPACE_PATTERN = re.compile(r'\s+')

def smart_capitalize(word: str) -> str:
    """Capitalize hyphenated words and preserve apostrophes."""
    return '-'.join([part.capitalize() for part in word.split('-')])

def clean_location(location_str: str) -> Optional[str]:
    """
    Clean and standardize location strings with advanced processing.
    
    >>> clean_location("123 main st, ny")
    '123 Main Street, New York'
    >>> clean_location("bombay airport, INDIA")
    'Mumbai Airport, India'
    >>> clean_location("san josé--los_ángeles")
    'San José-Los Ángeles'
    >>> clean_location("   ") is None
    True
    """
    if not location_str:
        return None

    # Normalization pipeline
    cleaned = unicodedata.normalize('NFKC', location_str)
    cleaned = HYPHEN_PATTERN.sub('-', cleaned)
    cleaned = cleaned.replace('_', ' ')
    cleaned = SPECIAL_CHARS_PATTERN.sub('', cleaned)
    cleaned = WHITESPACE_PATTERN.sub(' ', cleaned).strip().lower()

    if not cleaned or not any(c.isalpha() for c in cleaned):
        return None

    # Token processing
    tokens = re.findall(r"[\w'-]+|,", cleaned)
    processed = []
    
    for token in tokens:
        if token == ',':
            processed.append(',')
            continue
            
        # Convert to lowercase for consistent lookups
        lower_token = token.lower()
        
        # 1. Fix common typos
        corrected = COMMON_TYPOS.get(lower_token, lower_token)
        
        # 2. Expand abbreviations
        expanded = LOCATION_ABBREVIATIONS.get(corrected, corrected)
        processed.append(expanded)

    # Reconstruct string with proper formatting
    output = []
    for item in processed:
        if item == ',':
            # Handle commas with proper spacing
            if output and output[-1].endswith(' '):
                output.append(', ')
            else:
                output.append(' , ')
        else:
            # Process multi-word expansions
            parts = [smart_capitalize(part) for part in item.split()]
            output.append(' '.join(parts) + ' ')

    # Final cleanup
    result = ''.join(output)
    result = re.sub(r'\s*,\s*', ', ', result)  # Normalize comma spacing
    result = re.sub(r'\s+', ' ', result).strip()  # Remove extra spaces
    
    return result if any(c.isalpha() for c in result) else None
