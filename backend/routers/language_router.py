from fastapi import APIRouter, Request, Response, HTTPException
from pydantic import BaseModel
from typing import Dict, List

from ..utils.language_middleware import (
    get_current_language,
    add_translation,
    add_image_translation,
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
)

router = APIRouter(
    prefix="/api/language",
    tags=["language"],
)

class LanguageInfo(BaseModel):
    code: str
    name: str
    is_rtl: bool

class SetLanguageRequest(BaseModel):
    language: str

class TranslationRequest(BaseModel):
    key: str
    value: str
    language: str

class ImageTranslationRequest(BaseModel):
    key: str
    path: str
    language: str

@router.get("/supported", response_model=List[LanguageInfo])
async def get_supported_languages():
    """Get a list of supported languages"""
    return [
        LanguageInfo(code="en", name="English", is_rtl=False),
        LanguageInfo(code="ar", name="العربية", is_rtl=True),
    ]

@router.get("/current")
async def get_language(request: Request):
    """Get the current language"""
    return {"language": get_current_language(request)}

@router.post("/set")
async def set_language(req: SetLanguageRequest, response: Response):
    """Set the language via cookie"""
    if req.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {req.language}")
    
    # Set cookie with the language preference
    response.set_cookie(
        key="lang",
        value=req.language,
        max_age=60 * 60 * 24 * 30,  # 30 days
        httponly=True,
        samesite="lax",
    )
    
    return {"message": "__t:language.set_success", "language": req.language}

@router.post("/add-translation")
async def add_new_translation(req: TranslationRequest):
    """Add a new translation for a key"""
    try:
        add_translation(req.key, req.value, req.language)
        return {"message": "__t:language.translation_added"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/add-image-translation")
async def add_new_image_translation(req: ImageTranslationRequest):
    """Add a new image translation for a key"""
    try:
        add_image_translation(req.key, req.path, req.language)
        return {"message": "__t:language.image_translation_added"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/translations/{language}")
async def get_translations(language: str):
    """Get all translations for a language"""
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
    
    # Import here to avoid circular imports
    from ..utils.language_middleware import _translations
    
    return _translations.get(language, {})

@router.get("/image-translations/{language}")
async def get_image_translations(language: str):
    """Get all image translations for a language"""
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
    
    # Import here to avoid circular imports
    from ..utils.language_middleware import _image_translations
    
    return _image_translations.get(language, {}) 