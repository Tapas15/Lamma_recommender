from typing import List, Dict, Any, Union
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration for Ollama
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

def get_embedding(text: str) -> List[float]:
    """Get embedding from local Ollama model"""
    if not text:
        return []
        
    try:
        # API details for Ollama
        url = f"{OLLAMA_API_BASE}/api/embeddings"
        
        # Request data - Ollama uses 'prompt' instead of 'input'
        data = {
            "model": OLLAMA_MODEL,
            "prompt": text
        }
        
        response = requests.post(url, json=data)
        
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        
        # Extract embedding from the response - Ollama returns embedding directly
        if "embedding" in data:
            return data["embedding"]
        else:
            print("Unexpected response format from Ollama API")
            print(f"Response: {data}")
            return []
    except Exception as e:
        print(f"Error getting embedding from Ollama: {e}")
        # Return empty embedding in case of error
        return [] 