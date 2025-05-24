"""
CORS middleware configuration for the FastAPI backend.
This allows requests from the Next.js frontend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app: FastAPI) -> None:
    """
    Add CORS middleware to the FastAPI app.
    
    Args:
        app: The FastAPI app instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3005", "http://127.0.0.1:3000", "http://127.0.0.1:3005"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 