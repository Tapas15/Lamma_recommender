#!/usr/bin/env python
"""
Database initialization script.
Run this script directly to initialize all MongoDB collections and indexes.
"""

import asyncio
import os
from dotenv import load_dotenv
from utils.database import Database, init_db

load_dotenv()

async def initialize_database():
    """Initialize all collections and indexes in the database"""
    print("Starting database initialization...")
    
    # Connect to MongoDB
    await Database.connect_db()
    
    try:
        # Initialize collections and indexes
        await init_db()
        print("Database initialization completed successfully.")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise
    finally:
        # Close the connection
        await Database.close_db()
        
if __name__ == "__main__":
    # Run the initialization
    asyncio.run(initialize_database()) 