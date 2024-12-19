# translation_service/main.py
import os
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deep_translator import GoogleTranslator, exceptions
import httpx
import logging
import time
from functools import lru_cache

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Translation Service API",
    description="A robust translation service with rate limiting and error handling",
    version="1.0.0"
)

# CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute window
MAX_REQUESTS_PER_WINDOW = 100
request_timestamps = {}

# API request models
class TranslationRequest(BaseModel):
    text: str
    source_lang: Optional[str] = None
    target_lang: str

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str

# Rate limiting dependency
def rate_limit(request: Request):
    client_ip = request.client.host
    current_time = time.time()
    
    global request_timestamps
    request_timestamps = {
        ip: timestamps 
        for ip, timestamps in request_timestamps.items() 
        if current_time - timestamps[-1] < RATE_LIMIT_WINDOW
    }
    
    if client_ip in request_timestamps:
        if len(request_timestamps[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
            raise HTTPException(
                status_code=429, 
                detail="Too many requests. Please try again later."
            )
        request_timestamps[client_ip].append(current_time)
    else:
        request_timestamps[client_ip] = [current_time]
    
    return True

# Cached list of supported languages
@lru_cache(maxsize=1)
def get_supported_languages() -> List[Dict[str, str]]:
    """
    Retrieve and cache supported languages.
    """
    return [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "den", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "ja", "name": "Japanese"},
        {"code": "zh-CN", "name": "Chinese (Simplified)"},
        {"code": "arab", "name": "Arabic"},
        {"code": "ru", "name": "Russian"},
        {"code": "pt", "name": "Portuguese"}
    ]

@app.get("/languages", response_model=List[Dict[str, str]])
def list_supported_languages():
    """
    Endpoint to list all supported languages
    """
    return get_supported_languages()

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(
    translation_request: TranslationRequest, 
    _: bool = Depends(rate_limit)
):
    """
    Translate text using Google Translator with comprehensive error handling
    """
    try:
        # Validate input
        if not translation_request.text:
            raise HTTPException(
                status_code=400, 
                detail="Text to translate cannot be empty"
            )
        
        # Detect source language if not provided
        if not translation_request.source_lang:
            try:
                source_lang = GoogleTranslator().detect(translation_request.text)
            except Exception:
                source_lang = 'auto'
        else:
            source_lang = translation_request.source_lang
        
        # Perform translation
        translator = GoogleTranslator(
            source=source_lang, 
            target=translation_request.target_lang
        )
        
        translated_text = translator.translate(translation_request.text)
        
        # Log translation event
        logger.info(f"Translation: {source_lang} -> {translation_request.target_lang}")
        
        return TranslationResponse(
            original_text=translation_request.text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=translation_request.target_lang
        )
    
    except exceptions.LanguageNotSupportedException:
        raise HTTPException(
            status_code=400, 
            detail="One of the specified languages is not supported"
        )
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Translation service error: {str(e)}"
        )

# Health check endpoint
@app.get("/health")
def health_check():
    """
    Simple health check endpoint for testing
    """
    return {"status": "healthy"}
