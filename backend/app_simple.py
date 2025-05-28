from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.database import Database, CANDIDATES_COLLECTION
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Job Recommender API - Simple")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await Database.connect_db()

@app.get("/")
async def root():
    return {"message": "Job Recommender API - Simple Version"}

@app.get("/candidates/public")
async def get_candidates_public():
    """Get all active candidates - public endpoint (no authentication required)"""
    try:
        candidates = (
            await Database.get_collection(CANDIDATES_COLLECTION)
            .find({})
            .to_list(length=None)
        )
        # Remove sensitive fields and clean up the response
        for candidate in candidates:
            candidate.pop("_id", None)  # Remove MongoDB _id
            candidate.pop("embedding", None)  # Remove embedding vector
            candidate.pop("password", None)  # Remove password hash
            candidate.pop("hashed_password", None)  # Remove any hashed password
            
            # Convert datetime objects to strings if they exist
            if "created_at" in candidate and candidate["created_at"]:
                candidate["created_at"] = candidate["created_at"].isoformat() if hasattr(candidate["created_at"], 'isoformat') else str(candidate["created_at"])
            if "last_active" in candidate and candidate["last_active"]:
                candidate["last_active"] = candidate["last_active"].isoformat() if hasattr(candidate["last_active"], 'isoformat') else str(candidate["last_active"])
                
        return candidates
    except Exception as e:
        print(f"Error in get_candidates_public: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve candidates: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 