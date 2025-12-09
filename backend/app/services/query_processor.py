"""Query preprocessing and optimization utilities."""
import re
from typing import List
import unicodedata

# Hungarian character normalization map
HUNGARIAN_NORMALIZATION = {
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ö': 'o', 'ő': 'o',
    'ú': 'u', 'ü': 'u', 'ű': 'u',
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ö': 'O', 'Ő': 'O',
    'Ú': 'U', 'Ü': 'U', 'Ű': 'U'
}

# Common synonyms for phonebook queries
QUERY_SYNONYMS = {
    'dékán': ['dékán', 'dekan', 'dékan'],
    'tanszék': ['tanszék', 'department', 'osztály', 'tanszékvezető'],
    'kar': ['kar', 'faculty', 'kari'],
    'intézet': ['intézet', 'institute', 'institut'],
    'telefon': ['telefon', 'phone', 'tel', 'telefonszám'],
    'email': ['email', 'e-mail', 'e-mail cím', 'cím'],
    'név': ['név', 'name'],
}

def normalize_query(query: str) -> str:
    """
    Normalize query text for better matching.
    
    Args:
        query: Original query string
        
    Returns:
        Normalized query string
    """
    # Convert to lowercase
    normalized = query.lower().strip()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Normalize Hungarian characters (optional - can help with typos)
    # Uncomment if you want aggressive normalization
    # for old_char, new_char in HUNGARIAN_NORMALIZATION.items():
    #     normalized = normalized.replace(old_char, new_char)
    
    return normalized

def extract_keywords(query: str) -> List[str]:
    """
    Extract important keywords from query.
    
    Args:
        query: Query string
        
    Returns:
        List of extracted keywords
    """
    # Remove common stop words
    stop_words = {'a', 'az', 'azt', 'van', 'volt', 'lesz', 'ki', 'mi', 'hol', 
                  'melyik', 'mely', 'hogy', 'mint', 'és', 'vagy', 'de', 'is'}
    
    words = query.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return keywords

def expand_query_with_synonyms(query: str) -> List[str]:
    """
    Generate query variations using synonyms.
    
    Args:
        query: Original query string
        
    Returns:
        List of query variations
    """
    variations = [query]
    query_lower = query.lower()
    
    for word, synonyms in QUERY_SYNONYMS.items():
        if word in query_lower:
            for synonym in synonyms:
                if synonym != word:
                    variation = query_lower.replace(word, synonym)
                    if variation not in variations:
                        variations.append(variation)
    
    return variations

def preprocess_query(query: str, use_synonyms: bool = False) -> str:
    """
    Preprocess query for better search results.
    
    Args:
        query: Original query string
        use_synonyms: Whether to expand query with synonyms
        
    Returns:
        Preprocessed query string
    """
    # Normalize query
    processed = normalize_query(query)
    
    # Optionally expand with synonyms (can be expensive, use sparingly)
    if use_synonyms:
        variations = expand_query_with_synonyms(processed)
        # Use the first variation (most similar to original)
        processed = variations[0] if variations else processed
    
    return processed

