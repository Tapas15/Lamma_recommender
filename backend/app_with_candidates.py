#!/usr/bin/env python3
"""
Enhanced backend app that includes the working candidates endpoint
This file imports the main app and adds the missing candidates endpoint
"""

# Import the main app with all existing endpoints
from backend.app import app
from utils.database import Database, CANDIDATES_COLLECTION
from fastapi import HTTPException

# Add the working candidates endpoint
@app.get("/candidates/public")
async def get_candidates_public_working():
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
        print(f"Error in get_candidates_public_working: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve candidates: {str(e)}")

# Export the enhanced app
__all__ = ["app"] 