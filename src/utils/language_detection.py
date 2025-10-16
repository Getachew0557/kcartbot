"""Language detection and translation utilities."""

import re
from typing import Dict, List, Tuple


class LanguageDetector:
    """Language detection for Ethiopian languages."""
    
    def __init__(self):
        # Amharic character ranges
        self.amharic_ranges = [
            (0x1200, 0x137F),  # Ethiopic
            (0x1380, 0x139F),  # Ethiopic Supplement
            (0x2D80, 0x2DDF),  # Ethiopic Extended
            (0xAB00, 0xAB2F),  # Ethiopic Extended-A
        ]
        
        # Common Amharic words in Latin script
        self.amharic_latin_words = {
            "salam", "tena", "yistilign", "ameseginalehu", "dehna", "metu",
            "enkuan", "betam", "konjo", "gobez", "tiru", "buna", "injera",
            "wot", "kitfo", "tibs", "doro", "ayib", "tej", "tella"
        }
        
        # Common English words
        self.english_words = {
            "hello", "hi", "thank", "please", "yes", "no", "good", "bad",
            "price", "order", "product", "delivery", "payment", "cash"
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text."""
        text = text.lower().strip()
        
        if not text:
            return "en"
        
        # Check for Amharic characters
        if self._has_amharic_characters(text):
            return "am"
        
        # Check for Amharic Latin words
        words = re.findall(r'\b\w+\b', text)
        amharic_latin_count = sum(1 for word in words if word in self.amharic_latin_words)
        english_count = sum(1 for word in words if word in self.english_words)
        
        if amharic_latin_count > english_count:
            return "am-latn"
        else:
            return "en"
    
    def _has_amharic_characters(self, text: str) -> bool:
        """Check if text contains Amharic characters."""
        for char in text:
            char_code = ord(char)
            for start, end in self.amharic_ranges:
                if start <= char_code <= end:
                    return True
        return False
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language name from code."""
        names = {
            "en": "English",
            "am": "Amharic (አማርኛ)",
            "am-latn": "Amhar-glish"
        }
        return names.get(lang_code, "English")
    
    def is_supported_language(self, lang_code: str) -> bool:
        """Check if language is supported."""
        return lang_code in ["en", "am", "am-latn"]


class LanguageTranslator:
    """Simple language translation utilities."""
    
    def __init__(self):
        # Basic translations for common terms
        self.translations = {
            "en": {
                "welcome": "Welcome to KcartBot!",
                "customer": "customer",
                "supplier": "supplier",
                "order": "order",
                "price": "price",
                "delivery": "delivery",
                "payment": "payment"
            },
            "am": {
                "welcome": "እንኳን ደህና መጡ KcartBot!",
                "customer": "ደንበኛ",
                "supplier": "አቅራቢ",
                "order": "ትዕዛዝ",
                "price": "ዋጋ",
                "delivery": "ማድረስ",
                "payment": "ክፍያ"
            },
            "am-latn": {
                "welcome": "Enkwan dehna metu KcartBot!",
                "customer": "denebant",
                "supplier": "aqribi",
                "order": "te'ezaz",
                "price": "waga",
                "delivery": "madres",
                "payment": "kifiya"
            }
        }
    
    def translate_term(self, term: str, target_lang: str) -> str:
        """Translate a term to target language."""
        if target_lang in self.translations and term in self.translations[target_lang]:
            return self.translations[target_lang][term]
        return term
    
    def get_greeting(self, lang: str) -> str:
        """Get greeting in specified language."""
        greetings = {
            "en": "Hello! How can I help you today?",
            "am": "ሰላም! ዛሬ እንዴት ልረዳዎ እችላለሁ?",
            "am-latn": "Salam! Zare endet liredawo echelalew?"
        }
        return greetings.get(lang, greetings["en"])
    
    def get_farewell(self, lang: str) -> str:
        """Get farewell in specified language."""
        farewells = {
            "en": "Thank you for using KcartBot! Have a great day!",
            "am": "KcartBot ስለጠቀሙ አመሰግናለሁ! መልካም ቀን ይሁንልዎ!",
            "am-latn": "KcartBot sele-tekemu ameseginalehu! Melkam qen yihonlo!"
        }
        return farewells.get(lang, farewells["en"])


# Global instances
language_detector = LanguageDetector()
language_translator = LanguageTranslator()

