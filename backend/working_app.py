from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

# MongoDB configuration
MONGODB_URL = "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/"
DATABASE_NAME = "job_recommender"

# Collections
CANDIDATES_COLLECTION = "candidates"
JOBS_COLLECTION = "jobs"
PROJECTS_COLLECTION = "projects"

# Global database client
client = None
database = None

async def connect_to_mongo():
    """Create database connection"""
    global client, database
    client = AsyncIOMotorClient(MONGODB_URL)
    database = client[DATABASE_NAME]
    print(f"Connected to MongoDB database: {DATABASE_NAME}")

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(title="LnD Nexus API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "LnD Nexus API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}

@app.get("/candidates/public")
async def get_candidates_public():
    """Get all active candidates - public endpoint (no authentication required)"""
    try:
        collection = database[CANDIDATES_COLLECTION]
        candidates = await collection.find({}).to_list(length=None)
        
        # Remove sensitive fields and clean up the response
        for candidate in candidates:
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
                candidate["id"] = str(candidate.get("email", "unknown"))
            
            # Add default values for missing fields that frontend expects
            if not candidate.get("availability"):
                candidate["availability"] = "available"
                
            if not candidate.get("profile_views"):
                candidate["profile_views"] = 0
                
            if not candidate.get("job_search_status"):
                candidate["job_search_status"] = "open_to_opportunities"
        
        print(f"Retrieved {len(candidates)} candidates from database")
        return candidates
        
    except Exception as e:
        print(f"Error in get_candidates_public: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve candidates: {str(e)}")

@app.get("/jobs/public")
async def get_jobs_public():
    """Get all active jobs - public endpoint (no authentication required)"""
    try:
        collection = database[JOBS_COLLECTION]
        jobs = await collection.find({"is_active": True}).to_list(length=None)
        
        # Remove sensitive fields and clean up the response
        for job in jobs:
            job.pop("_id", None)  # Remove MongoDB _id
            job.pop("embedding", None)  # Remove embedding vector
            
            # Convert datetime objects to strings if they exist
            if "created_at" in job and job["created_at"]:
                if hasattr(job["created_at"], 'isoformat'):
                    job["created_at"] = job["created_at"].isoformat()
                else:
                    job["created_at"] = str(job["created_at"])
                    
            if "posted_date" in job and job["posted_date"]:
                if hasattr(job["posted_date"], 'isoformat'):
                    job["posted_date"] = job["posted_date"].isoformat()
                else:
                    job["posted_date"] = str(job["posted_date"])
        
        print(f"Retrieved {len(jobs)} active jobs from database")
        return jobs
        
    except Exception as e:
        print(f"Error in get_jobs_public: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jobs: {str(e)}")

@app.get("/projects/public")
async def get_projects_public():
    """Get all active projects - public endpoint (no authentication required)"""
    try:
        collection = database[PROJECTS_COLLECTION]
        projects = await collection.find({"is_active": True}).to_list(length=None)
        
        # Remove sensitive fields and clean up the response
        for project in projects:
            project.pop("_id", None)  # Remove MongoDB _id
            project.pop("embedding", None)  # Remove embedding vector if exists
            
            # Convert datetime objects to strings if they exist
            if "created_at" in project and project["created_at"]:
                if hasattr(project["created_at"], 'isoformat'):
                    project["created_at"] = project["created_at"].isoformat()
                else:
                    project["created_at"] = str(project["created_at"])
        
        print(f"Retrieved {len(projects)} active projects from database")
        return projects
        
    except Exception as e:
        print(f"Error in get_projects_public: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve projects: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 