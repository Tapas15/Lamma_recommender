#!/usr/bin/env python
"""
Setup script for Next.js frontend environment variables
"""
import os

def setup_frontend_env():
    """Create .env.local file for Next.js frontend"""
    frontend_path = os.path.join("frontend", "lnd-nexus")
    
    if not os.path.exists(frontend_path):
        print("Frontend directory not found, skipping environment setup.")
        return False
    
    env_file_path = os.path.join(frontend_path, ".env.local")
    
    env_content = """# Next.js Environment Variables
# These variables are available in the browser (prefixed with NEXT_PUBLIC_)

# LibreTranslate API URL
NEXT_PUBLIC_LIBRETRANSLATE_URL=http://localhost:5000

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
"""
    
    try:
        with open(env_file_path, "w") as f:
            f.write(env_content)
        print(f"✓ Created frontend environment file: {env_file_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to create frontend environment file: {str(e)}")
        return False

if __name__ == "__main__":
    setup_frontend_env() 