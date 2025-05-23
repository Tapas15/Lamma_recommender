#!/usr/bin/env python
"""
Test script to verify that the backend modules can be imported correctly.
This helps diagnose Python import path issues.
"""

try:
    print("Testing imports...")
    
    # Try importing the app module
    import app
    print("✓ Successfully imported app")
    
    # Try importing utils modules directly
    from utils import models, extended_models, database, embedding
    print("✓ Successfully imported utils modules directly")
    
    # Try importing with relative imports
    from .utils import models as rel_models
    from .utils import extended_models as rel_extended_models
    from .utils import database as rel_database
    from .utils import embedding as rel_embedding
    print("✓ Successfully imported utils modules with relative imports")
    
    print("All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTroubleshooting tips:")
    print("1. Make sure __init__.py exists in both backend/ and backend/utils/ directories")
    print("2. Try running the script with the -m flag: python -m backend.test_imports")
    print("3. Make sure your PYTHONPATH includes the parent directory of 'backend'")
    print("4. Check that all required dependencies are installed") 