from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime
import uvicorn

load_dotenv()

app = FastAPI(title="L&D Nexus Candidates API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/")
DATABASE_NAME = "job_recommender"  # Using the correct database name
CANDIDATES_COLLECTION = "candidates"

print(f"Connecting to MongoDB: {MONGODB_URL}")
print(f"Database: {DATABASE_NAME}")

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

@app.get("/")
async def root():
    return {"message": "L&D Nexus Candidates API is running", "database": DATABASE_NAME}

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        await client.admin.command('ping')
        candidate_count = await db[CANDIDATES_COLLECTION].count_documents({})
        return {
            "status": "healthy",
            "database_connected": True,
            "candidates_count": candidate_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database_connected": False,
            "error": str(e)
        }

@app.get("/candidates/public")
async def get_candidates_public():
    """Get all active candidates - public endpoint (no authentication required)"""
    try:
        print("Fetching candidates from MongoDB...")
        print(f"Collection: {CANDIDATES_COLLECTION}")
        
        # Get all candidates from the database
        candidates_cursor = db[CANDIDATES_COLLECTION].find({})
        candidates = await candidates_cursor.to_list(length=None)
        
        print(f"Found {len(candidates)} candidates in database")
        
        if not candidates:
            print("No candidates found in database")
            return []
        
        # Process candidates to remove sensitive fields and clean up the response
        processed_candidates = []
        for candidate in candidates:
            # Remove sensitive fields
            candidate.pop("_id", None)  # Remove MongoDB _id
            candidate.pop("embedding", None)  # Remove embedding vector
            candidate.pop("password", None)  # Remove password hash
            candidate.pop("hashed_password", None)  # Remove any hashed password
            
            # Convert datetime objects to strings if they exist
            if "created_at" in candidate and candidate["created_at"]:
                if hasattr(candidate["created_at"], 'isoformat'):
                    candidate["created_at"] = candidate["created_at"].isoformat()
                else:
                    candidate["created_at"] = str(candidate["created_at"])
                    
            if "last_active" in candidate and candidate["last_active"]:
                if hasattr(candidate["last_active"], 'isoformat'):
                    candidate["last_active"] = candidate["last_active"].isoformat()
                else:
                    candidate["last_active"] = str(candidate["last_active"])
            
            # Ensure we have required fields for the frontend
            if not candidate.get("id"):
                candidate["id"] = candidate.get("_id", str(candidate.get("email", "unknown")))
            
            # Add default values for missing fields that frontend expects
            if not candidate.get("availability"):
                candidate["availability"] = "available"
                
            if not candidate.get("profile_views"):
                candidate["profile_views"] = 0
                
            if not candidate.get("job_search_status"):
                candidate["job_search_status"] = "open_to_opportunities"
            
            processed_candidates.append(candidate)
            print(f"Processed candidate: {candidate.get('full_name', 'Unknown')}")
                
        print(f"Returning {len(processed_candidates)} processed candidates")
        return processed_candidates
        
    except Exception as e:
        print(f"Error in get_candidates_public: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve candidates: {str(e)}")

@app.get("/candidates/count")
async def get_candidates_count():
    """Get the count of candidates in the database"""
    try:
        count = await db[CANDIDATES_COLLECTION].count_documents({})
        return {"count": count}
    except Exception as e:
        print(f"Error getting candidate count: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get candidate count: {str(e)}")

if __name__ == "__main__":
    print("Starting L&D Nexus Candidates Server...")
    print(f"MongoDB URL: {MONGODB_URL}")
    print(f"Database: {DATABASE_NAME}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 