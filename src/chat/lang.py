import re

def detect_language(text):
    """Simple language detection for English, Amharic, and Amhar-glish"""
    text = text.lower().strip()
    
    # Check for Amharic characters
    amharic_chars = re.findall(r'[\u1200-\u137F]', text)
    if amharic_chars:
        return "amharic"
    
    # Check for Amhar-glish patterns (common transliterations)
    amhar_glish_indicators = [
        'selam', 'ameseginalehu', 'tena yistilin', 'ende', 'neger', 
        'bizu', 'bota', 'aydel', 'hulu', 'sint', 'antem', 'gobez'
    ]
    
    if any(indicator in text for indicator in amhar_glish_indicators):
        return "amhar-glish"
    
    return "english"

def normalize_amhar_glish(text):
    """Normalize Amhar-glish spelling variations"""
    replacements = {
        r'\bselam\b': 'selam',
        r'\bameseginalehu\b': 'ameseginalehu',
        r'\btena yistilin\b': 'tena yistilin',
        r'\bende\b': 'ende',
        r'\bneger\b': 'neger',
        r'\bbizu\b': 'bizu',
        r'\bbota\b': 'bota',
        r'\baydel\b': 'aydel',
        r'\bhulu\b': 'hulu',
        r'\bsint\b': 'sint',
        r'\bantem\b': 'antem',
        r'\bgobez\b': 'gobez'
    }
    
    normalized = text.lower()
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized)
    
    return normalized