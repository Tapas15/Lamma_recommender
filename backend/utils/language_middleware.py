import json
import os
from typing import Dict, List, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Supported languages
SUPPORTED_LANGUAGES = ["en", "ar"]
DEFAULT_LANGUAGE = "en"

# Directory for translation files
TRANSLATIONS_DIR = os.path.join(os.path.dirname(__file__), "translations")
os.makedirs(TRANSLATIONS_DIR, exist_ok=True)

# Load translation files
_translations: Dict[str, Dict[str, str]] = {}

def _load_translations():
    """Load all translation files into memory"""
    for lang in SUPPORTED_LANGUAGES:
        trans_file = os.path.join(TRANSLATIONS_DIR, f"{lang}.json")
        if os.path.exists(trans_file):
            with open(trans_file, "r", encoding="utf-8") as f:
                _translations[lang] = json.load(f)
        else:
            # Create empty translation file if it doesn't exist
            _translations[lang] = {}
            with open(trans_file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

# Load translations on module import
_load_translations()

# Load image translations
_image_translations: Dict[str, Dict[str, str]] = {}

def _load_image_translations():
    """Load all image translation files into memory"""
    for lang in SUPPORTED_LANGUAGES:
        trans_file = os.path.join(TRANSLATIONS_DIR, f"{lang}_images.json")
        if os.path.exists(trans_file):
            with open(trans_file, "r", encoding="utf-8") as f:
                _image_translations[lang] = json.load(f)
        else:
            # Create empty translation file if it doesn't exist
            _image_translations[lang] = {}
            with open(trans_file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

# Load image translations on module import
_load_image_translations()

def get_translation(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """Get a translation for a key in the specified language"""
    if lang not in _translations:
        lang = DEFAULT_LANGUAGE
    
    # Get nested keys
    parts = key.split(".")
    current = _translations[lang]
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            # Return the key if translation not found
            return key
    
    if isinstance(current, str):
        return current
    return key

def get_image_translation(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """Get an image path translation for a key in the specified language"""
    if lang not in _image_translations:
        lang = DEFAULT_LANGUAGE
    
    return _image_translations[lang].get(key, "")

def translate_response(response_data: Dict, lang: str) -> Dict:
    """Translate response data based on translation keys"""
    if isinstance(response_data, dict):
        translated_data = {}
        for key, value in response_data.items():
            if isinstance(value, dict):
                translated_data[key] = translate_response(value, lang)
            elif isinstance(value, list):
                translated_data[key] = [
                    translate_response(item, lang) if isinstance(item, (dict, list)) else item
                    for item in value
                ]
            elif isinstance(value, str) and value.startswith("__t:"):
                # Handle translation keys (format: "__t:key.path")
                trans_key = value[4:]
                translated_data[key] = get_translation(trans_key, lang)
            elif isinstance(value, str) and value.startswith("__img:"):
                # Handle image translation keys (format: "__img:key.path")
                img_key = value[6:]
                translated_data[key] = get_image_translation(img_key, lang)
            else:
                translated_data[key] = value
        return translated_data
    elif isinstance(response_data, list):
        return [
            translate_response(item, lang) if isinstance(item, (dict, list)) else item
            for item in response_data
        ]
    return response_data

class LanguageMiddleware(BaseHTTPMiddleware):
    """Middleware to handle language preferences and translate responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Get language preference from various sources
        lang = self._get_language_preference(request)
        
        # Set language in request state for route handlers
        request.state.lang = lang
        
        # Call next middleware or route handler
        response = await call_next(request)
        
        # Return unmodified response for non-JSON responses
        if response.headers.get("content-type", "").lower() != "application/json":
            return response
        
        # Parse JSON response
        response_body = await response.body()
        response_data = json.loads(response_body)
        
        # Translate response data
        translated_data = translate_response(response_data, lang)
        
        # Create new response with translated data
        translated_body = json.dumps(translated_data).encode("utf-8")
        
        # Create new response with same status code and headers
        new_response = Response(
            content=translated_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type="application/json",
        )
        
        return new_response
    
    def _get_language_preference(self, request: Request) -> str:
        """Get language preference from various sources"""
        # Check for explicit language parameter in query or form
        lang = request.query_params.get("lang")
        
        if not lang:
            # Check cookie
            lang = request.cookies.get("lang")
        
        if not lang:
            # Check Accept-Language header
            accept_lang = request.headers.get("Accept-Language", "")
            if accept_lang:
                # Extract language code from Accept-Language
                parts = accept_lang.split(",")
                for part in parts:
                    code = part.split(";")[0].strip().lower()
                    if code in SUPPORTED_LANGUAGES:
                        lang = code
                        break
        
        # Fallback to default language
        if not lang or lang not in SUPPORTED_LANGUAGES:
            lang = DEFAULT_LANGUAGE
        
        return lang

# Helper function to get current language from request
def get_current_language(request: Request) -> str:
    """Get the current language from the request"""
    return getattr(request.state, "lang", DEFAULT_LANGUAGE)

# Function to add translations
def add_translation(key: str, value: str, lang: str = DEFAULT_LANGUAGE) -> None:
    """Add a new translation to the specified language"""
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {lang}")
    
    # Split key into parts
    parts = key.split(".")
    
    # Navigate through nested dictionary
    current = _translations.setdefault(lang, {})
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    
    # Set the value
    current[parts[-1]] = value
    
    # Save to file
    trans_file = os.path.join(TRANSLATIONS_DIR, f"{lang}.json")
    with open(trans_file, "w", encoding="utf-8") as f:
        json.dump(_translations[lang], f, ensure_ascii=False, indent=2)

# Function to add image translations
def add_image_translation(key: str, value: str, lang: str = DEFAULT_LANGUAGE) -> None:
    """Add a new image translation to the specified language"""
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {lang}")
    
    # Add the image translation
    _image_translations.setdefault(lang, {})[key] = value
    
    # Save to file
    trans_file = os.path.join(TRANSLATIONS_DIR, f"{lang}_images.json")
    with open(trans_file, "w", encoding="utf-8") as f:
        json.dump(_image_translations[lang], f, ensure_ascii=False, indent=2) 