from fastapi import APIRouter, Request
from backend.utils.language_middleware import get_language, get_translation

# Create a router for language endpoints
router = APIRouter(
    prefix="/languages",
    tags=["languages"],
    responses={404: {"description": "Not found"}},
)

@router.get("")
async def get_languages(request: Request):
    """Get available languages and current language"""
    current_lang = get_language(request)
    return {
        "available_languages": ["en", "ar"],
        "current_language": current_lang,
    }

@router.get("/translate/{key}")
async def translate(key: str, request: Request):
    """Get translation for a specific key"""
    lang = get_language(request)
    return {"key": key, "translation": get_translation(key, lang)} 