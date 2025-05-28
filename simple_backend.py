from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/")
DATABASE_NAME = "job_recommender"  # Using the actual database name from your setup
CANDIDATES_COLLECTION = "candidates"

@app.get("/")
async def root():
    return {"message": "Simple Backend Running", "database": DATABASE_NAME}

@app.get("/candidates/public")
async def get_candidates():
    try:
        print("Connecting to MongoDB...")
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        # Test connection first
        await client.admin.command('ping')
        print("Database connection successful!")
        
        # Count candidates first
        count = await db[CANDIDATES_COLLECTION].count_documents({})
        print(f"Found {count} candidates in database")
        
        # Get all candidates
        candidates = await db[CANDIDATES_COLLECTION].find({}).to_list(length=None)
        print(f"Retrieved {len(candidates)} candidates from database")
        
        # Clean up the data for frontend
        result = []
        for i, candidate in enumerate(candidates, 1):
            print(f"Processing candidate {i}: {candidate.get('full_name', 'Unknown')}")
            
            # Remove MongoDB _id and sensitive fields
            candidate.pop("_id", None)
            candidate.pop("password", None)
            candidate.pop("hashed_password", None)
            candidate.pop("embedding", None)
            
            # Ensure required fields exist
            if not candidate.get("id"):
                candidate["id"] = str(candidate.get("email", f"candidate_{i}"))
            
            # Convert datetime to string if needed
            if "created_at" in candidate and hasattr(candidate["created_at"], 'isoformat'):
                candidate["created_at"] = candidate["created_at"].isoformat()
            
            # Add default values for missing fields that frontend expects
            if not candidate.get("availability"):
                candidate["availability"] = "available"
                
            if not candidate.get("profile_views"):
                candidate["profile_views"] = 0
                
            if not candidate.get("job_search_status"):
                candidate["job_search_status"] = "open_to_opportunities"
            
            result.append(candidate)
        
        # Close connection properly
        client.close()
        print(f"Returning {len(result)} candidates to frontend")
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    print("Starting simple backend...")
    uvicorn.run(app, host="127.0.0.1", port=8000) 