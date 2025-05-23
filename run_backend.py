#!/usr/bin/env python
"""
Run script for the Job Recommender API backend.
This script ensures that the backend module is properly imported.
"""
import uvicorn
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file (first from root, then fallback to backend/utils)
root_env_path = ".env"
backend_env_path = os.path.join("backend", "utils", ".env")

if os.path.exists(root_env_path):
    load_dotenv(dotenv_path=root_env_path)
    print(f"Loaded environment from {root_env_path}")
elif os.path.exists(backend_env_path):
    load_dotenv(dotenv_path=backend_env_path)
    print(f"Loaded environment from {backend_env_path}")
else:
    print("Warning: No .env file found. Using default environment variables.")

if __name__ == "__main__":
    # Set encoding environment variable to UTF-8 to avoid encoding issues on Windows
    if os.name == 'nt':  # Windows
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
    print("Starting Job Recommender API backend...")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True, log_level="info") 