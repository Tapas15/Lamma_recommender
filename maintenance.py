#!/usr/bin/env python
"""
Database maintenance script.
Can be scheduled to run periodically to ensure all collections are properly maintained.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.database import Database, init_db, DATABASE_NAME
from utils.database import (
    USERS_COLLECTION, JOBS_COLLECTION, RECOMMENDATIONS_COLLECTION, 
    CANDIDATES_COLLECTION, EMPLOYERS_COLLECTION, PROJECTS_COLLECTION, 
    JOB_APPLICATIONS_COLLECTION, SAVED_JOBS_COLLECTION, PROJECT_APPLICATIONS_COLLECTION,
    SAVED_PROJECTS_COLLECTION, FEEDBACK_COLLECTION, NOTIFICATIONS_COLLECTION,
    VECTOR_INDEXES_COLLECTION
)

load_dotenv()

async def check_collections():
    """Check all collections and ensure they exist with proper indexes"""
    print(f"[{datetime.now().isoformat()}] Starting database maintenance...")
    
    # Connect to MongoDB
    await Database.connect_db()
    
    try:
        # Get the database
        db = Database.get_db()
        
        print(f"Using database: {DATABASE_NAME}")
        
        # List existing collections
        collections = await db.list_collection_names()
        print(f"Found {len(collections)} collections: {', '.join(collections)}")
        
        # Expected collections
        expected_collections = [
            USERS_COLLECTION,
            JOBS_COLLECTION,
            RECOMMENDATIONS_COLLECTION,
            CANDIDATES_COLLECTION,
            EMPLOYERS_COLLECTION,
            PROJECTS_COLLECTION,
            JOB_APPLICATIONS_COLLECTION,
            SAVED_JOBS_COLLECTION,
            PROJECT_APPLICATIONS_COLLECTION,
            SAVED_PROJECTS_COLLECTION,
            FEEDBACK_COLLECTION,
            NOTIFICATIONS_COLLECTION,
            VECTOR_INDEXES_COLLECTION
        ]
        
        # Check for missing collections
        missing_collections = [coll for coll in expected_collections if coll not in collections]
        if missing_collections:
            print(f"Missing collections: {', '.join(missing_collections)}")
            print("Running init_db to create missing collections...")
            await init_db()
        else:
            print("All expected collections exist.")
        
        # Verify embedding vectors
        # Check if any documents are missing embeddings
        try:
            jobs_without_embedding = await Database.get_collection(JOBS_COLLECTION).count_documents(
                {"embedding": {"$exists": False}}
            )
            candidates_without_embedding = await Database.get_collection(CANDIDATES_COLLECTION).count_documents(
                {"embedding": {"$exists": False}}
            )
            projects_without_embedding = await Database.get_collection(PROJECTS_COLLECTION).count_documents(
                {"embedding": {"$exists": False}}
            )
            
            print(f"Jobs without embeddings: {jobs_without_embedding}")
            print(f"Candidates without embeddings: {candidates_without_embedding}")
            print(f"Projects without embeddings: {projects_without_embedding}")
        except Exception as e:
            print(f"Error checking embeddings: {e}")
        
        print(f"[{datetime.now().isoformat()}] Database maintenance completed.")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Error during database maintenance: {e}")
        raise
    finally:
        # Close the connection
        await Database.close_db()

if __name__ == "__main__":
    # Run the maintenance script
    asyncio.run(check_collections()) 