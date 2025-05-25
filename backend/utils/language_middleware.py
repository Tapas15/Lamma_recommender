from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

# Define supported languages
SUPPORTED_LANGUAGES = ["en", "ar"]
DEFAULT_LANGUAGE = "en"

# Load translations
translations: Dict[str, Dict[str, str]] = {}

def load_translations():
    """Load translation files for all supported languages"""
    global translations
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(current_dir, "translations")
    
    # Create translations directory if it doesn't exist
    os.makedirs(translations_dir, exist_ok=True)
    
    # Load translations for each supported language
    for lang in SUPPORTED_LANGUAGES:
        translation_file = os.path.join(translations_dir, f"{lang}.json")
        
        # Create default translation files if they don't exist
        if not os.path.exists(translation_file):
            if lang == "en":
                # English translations (default)
                default_translations = {
                    "welcome": "Welcome to the Job Recommender API",
                    "error.not_found": "Resource not found",
                    "error.unauthorized": "Unauthorized access",
                    "error.validation": "Validation error",
                    "success.created": "Resource created successfully",
                    "success.updated": "Resource updated successfully",
                    "success.deleted": "Resource deleted successfully",
                }
            elif lang == "ar":
                # Arabic translations
                default_translations = {
                    "welcome": "مرحبًا بك في واجهة برمجة تطبيقات توصية الوظائف",
                    "error.not_found": "المورد غير موجود",
                    "error.unauthorized": "وصول غير مصرح به",
                    "error.validation": "خطأ في التحقق من الصحة",
                    "success.created": "تم إنشاء المورد بنجاح",
                    "success.updated": "تم تحديث المورد بنجاح",
                    "success.deleted": "تم حذف المورد بنجاح",
                }
            else:
                default_translations = {}
                
            # Save default translations to file
            with open(translation_file, "w", encoding="utf-8") as f:
                json.dump(default_translations, f, ensure_ascii=False, indent=2)
        
        # Load translations from file
        try:
            with open(translation_file, "r", encoding="utf-8") as f:
                translations[lang] = json.load(f)
        except Exception as e:
            print(f"Error loading translations for {lang}: {str(e)}")
            translations[lang] = {}

# Load translations when module is imported
load_translations()

def get_translation(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """Get translation for a key in the specified language"""
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
        
    return translations.get(lang, {}).get(key, key)

class LanguageMiddleware(BaseHTTPMiddleware):
    """Middleware to handle language selection based on Accept-Language header or query parameter"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Get language from query parameter first (highest priority)
        lang = request.query_params.get("lang")
        
        # If not in query params, try to get from header
        if not lang:
            accept_language = request.headers.get("Accept-Language", "")
            # Parse the Accept-Language header
            if accept_language:
                # Extract the first language code
                lang_parts = accept_language.split(",")[0].strip().split(";")[0].strip()
                # Get just the language code (e.g., "en" from "en-US")
                lang = lang_parts.split("-")[0].lower()
        
        # If language is not supported, use default
        if lang not in SUPPORTED_LANGUAGES:
            lang = DEFAULT_LANGUAGE
        
        # Add language to request state
        request.state.lang = lang
        
        # Process the request
        response = await call_next(request)
        
        # Add language header to response
        response.headers["Content-Language"] = lang
        
        return response

# Function to be used in API endpoints
def get_language(request: Request) -> str:
    """Get the language from the request state"""
    return getattr(request.state, "lang", DEFAULT_LANGUAGE) 