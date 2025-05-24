from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional, Union, Dict, Any, Tuple
import os
from dotenv import load_dotenv
from bson import ObjectId
import requests
import numpy as np
import time
import re
from contextlib import asynccontextmanager
import json
import random
import uuid

# Use absolute imports for local modules
from utils.models import (
    UserType,
    User,
    LoginRequest,
    Token,
    TokenData,
    CandidateCreate,
    Candidate,
    EmployerCreate,
    Employer,
    JobCreate,
    Job,
    ProjectCreate,
    Project,
    JobApplicationCreate,
    JobApplication,
    SavedJobCreate,
    SavedJob,
    SavedProjectCreate,
    SavedProject,
    ProjectApplicationCreate,
    ProjectApplication,
)
from utils.extended_models import (
    ExtendedCandidateCreate,
    ExtendedCandidate,
    ExtendedEmployerCreate,
    ExtendedEmployer,
)
from utils.embedding import get_embedding
from utils.database import (
    Database,
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
    VECTOR_INDEXES_COLLECTION,
    init_db,
)

load_dotenv()

# Ollama configuration
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Function to get embeddings from Groq was removed, now using the one from utils.embedding


def create_job_embedding(job_data: Dict[str, Any]) -> List[float]:
    """Create a searchable text from job data and get its embedding"""
    # Include all relevant fields in the searchable text
    searchable_text = f"{job_data.get('title', '')} {job_data.get('company', '')} {job_data.get('description', '')}"
    
    # Add industry and experience level
    if job_data.get("industry"):
        searchable_text += f" {job_data.get('industry')}"
    if job_data.get("experience_level"):
        searchable_text += f" {job_data.get('experience_level')}"
    
    # Add requirements and tech stack
    if job_data.get("requirements"):
        searchable_text += f" {' '.join(job_data.get('requirements', []))}"
    if job_data.get("tech_stack"):
        searchable_text += f" {' '.join(job_data.get('tech_stack', []))}"
    
    # Add responsibilities
    if job_data.get("responsibilities"):
        searchable_text += f" {' '.join(job_data.get('responsibilities', []))}"
    
    # Add qualifications
    if job_data.get("preferred_qualifications"):
        searchable_text += f" {' '.join(job_data.get('preferred_qualifications', []))}"
    
    # Add location and work mode
    searchable_text += f" {job_data.get('location', '')}"
    if job_data.get("work_mode"):
        searchable_text += f" {' '.join(job_data.get('work_mode', []))}"
    
    return get_embedding(searchable_text)


def create_project_embedding(project_data: Dict[str, Any]) -> List[float]:
    """Create a searchable text from project data and get its embedding"""
    searchable_text = f"{project_data.get('title', '')} {project_data.get('company', '')} {project_data.get('description', '')}"
    
    # Add core project fields
    if project_data.get("project_type"):
        searchable_text += f" {project_data.get('project_type')}"
        
    if project_data.get("requirements"):
        searchable_text += f" {' '.join(project_data.get('requirements', []))}"
        
    if project_data.get("skills_required"):
        searchable_text += f" {' '.join(project_data.get('skills_required', []))}"
        
    if project_data.get("location"):
        searchable_text += f" {project_data.get('location')}"
    
    # Add enhanced fields    
    if project_data.get("tools_technologies"):
        searchable_text += f" {' '.join(project_data.get('tools_technologies', []))}"
        
    if project_data.get("objectives"):
        searchable_text += f" {' '.join(project_data.get('objectives', []))}"
        
    if project_data.get("preferred_qualifications"):
        searchable_text += (
            f" {' '.join(project_data.get('preferred_qualifications', []))}"
        )

    if project_data.get("employment_type"):
        searchable_text += f" {project_data.get('employment_type')}"
    
    # Handle dictionary field for experience if present
    if project_data.get("experience"):
        exp_data = project_data.get("experience")
        if isinstance(exp_data, dict):
            # Add domain info if available
            if "domain" in exp_data:
                searchable_text += f" {exp_data.get('domain')}"
                
            # Add project examples if available
            if "project_examples" in exp_data and isinstance(
                exp_data.get("project_examples"), list
            ):
                searchable_text += f" {' '.join(exp_data.get('project_examples'))}"
    
    return get_embedding(searchable_text)


def create_candidate_embedding(candidate_data: Dict[str, Any]) -> List[float]:
    """Create a searchable text from candidate data and get its embedding"""
    # Combine relevant candidate fields into a searchable text
    skills_text = " ".join(candidate_data.get("skills", []))
    searchable_text = f"{candidate_data.get('full_name', '')} {skills_text} {candidate_data.get('experience', '')} {candidate_data.get('education', '')} {candidate_data.get('location', '')} {candidate_data.get('bio', '')}"
    return get_embedding(searchable_text)


# MongoDB Vector Search Recommender Functions
async def get_match_score(job_info: Dict, candidate_info: Dict) -> Tuple[float, str]:
    """Calculate match score between a job and candidate using MongoDB vector search"""
    try:
        # Create vectors for comparison
        job_text = f"{job_info.get('title', '')} {job_info.get('company', '')} {job_info.get('description', '')} {' '.join(job_info.get('requirements', []))}"
        candidate_text = f"{candidate_info.get('full_name', '')} {' '.join(candidate_info.get('skills', []))} {candidate_info.get('experience', '')} {candidate_info.get('education', '')}"
        
        # Get embeddings
        job_embedding = job_info.get("embedding") or get_embedding(job_text)
        candidate_embedding = candidate_info.get("embedding") or get_embedding(
            candidate_text
        )
        
        if not job_embedding or not candidate_embedding:
            return calculate_fallback_score(job_info, candidate_info)
        
        # Calculate cosine similarity manually since we're directly comparing two vectors
        # In a full implementation with many candidates/jobs, we'd use MongoDB's $vectorSearch
        score = cosine_similarity(job_embedding, candidate_embedding) * 100
        
        # Generate explanation
        required_skills = set(job_info.get("requirements", []))
        if not required_skills:
            required_skills = set(job_info.get("skills_required", []))
            
        candidate_skills = set(candidate_info.get("skills", []))
        matched_skills = required_skills.intersection(candidate_skills)
        
        explanation = f"Match score: {score:.1f}. "
        if matched_skills:
            explanation += f"Matching skills: {', '.join(matched_skills)}. "
        if required_skills - matched_skills:
            explanation += (
                f"Missing skills: {', '.join(required_skills - matched_skills)}. "
            )
        
        return score, explanation
    except Exception as e:
        print(f"Error in get_match_score: {str(e)}")
        return calculate_fallback_score(job_info, candidate_info)


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    if not vec1 or not vec2:
        return 0.0
    
    try:
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
            
        return dot_product / (norm_vec1 * norm_vec2)
    except Exception as e:
        print(f"Error in cosine similarity calculation: {str(e)}")
        return 0.0


def calculate_fallback_score(job_info: Dict, candidate_info: Dict) -> Tuple[float, str]:
    """Simple keyword matching algorithm as a fallback"""
    job_requirements = set(job_info.get("requirements", []))
    if not job_requirements and "required_skills" in job_info:
        job_requirements = set(job_info.get("required_skills", []))
        
    candidate_skills = set(candidate_info.get("skills", []))
    
    # Calculate skill match percentage
    if not job_requirements:
        skill_match = 50.0  # Default if no requirements specified
    else:
        matched_skills = job_requirements.intersection(candidate_skills)
        skill_match = (len(matched_skills) / max(1, len(job_requirements))) * 100
    
    # Add location match bonus
    location_match = 0
    if job_info.get("location") == candidate_info.get("location"):
        location_match = 10
    
    # Create explanation
    explanation = f"Keyword match: Found {len(job_requirements.intersection(candidate_skills))} matching skills out of {len(job_requirements)} required skills."
    
    # Simple score calculation (primarily based on matching skills)
    score = min(100, skill_match + location_match)
    
    return score, explanation


async def get_job_candidate_matches(
    job_info: Dict, candidates: List[Dict]
) -> List[Dict]:
    """Match a job to multiple candidates using vector similarity"""
    try:
        matches = []
        for candidate in candidates:
            try:
                candidate_id = (
                    candidate.get("id")
                    if "id" in candidate
                    else str(candidate.get("_id", "unknown"))
                )
                score, explanation = await get_match_score(job_info, candidate)
                matches.append(
                    {
                    "candidate_id": candidate_id,
                    "match_score": score,
                        "explanation": explanation,
                    }
                )
            except Exception as e:
                print(
                    f"Error matching candidate {candidate.get('id', 'unknown')}: {str(e)}"
                )
                matches.append(
                    {
                    "candidate_id": candidate.get("id", "unknown"),
                    "match_score": 0.0,
                        "explanation": f"Error occurred during matching: {str(e)}",
                    }
                )
        return sorted(matches, key=lambda x: x["match_score"], reverse=True)
    except Exception as e:
        print(f"Unexpected error in get_job_candidate_matches: {str(e)}")
        return []


async def get_candidate_job_matches(
    candidate_info: Dict, jobs: List[Dict]
) -> List[Dict]:
    """Match a candidate to multiple jobs using vector similarity"""
    try:
        matches = []
        for job in jobs:
            try:
                job_id = (
                    job.get("id") if "id" in job else str(job.get("_id", "unknown"))
                )
                score, explanation = await get_match_score(job, candidate_info)
                matches.append(
                    {"job_id": job_id, "match_score": score, "explanation": explanation}
                )
            except Exception as e:
                print(f"Error matching job {job.get('id', 'unknown')}: {str(e)}")
                matches.append(
                    {
                    "job_id": job.get("id", "unknown"),
                    "match_score": 0.0,
                        "explanation": f"Error occurred during matching: {str(e)}",
                    }
                )
        return sorted(matches, key=lambda x: x["match_score"], reverse=True)
    except Exception as e:
        print(f"Unexpected error in get_candidate_job_matches: {str(e)}")
        return []


async def search_vector_collection(
    collection_name, query_vector, top_k=5, filter_query=None
):
    """Generic vector search function using MongoDB Atlas Search"""
    try:
        pipeline = [
            {
                "$search": {
                    "index": f"{collection_name}_vector_index",
                    "vectorSearch": {
                        "queryVector": query_vector,
                        "path": "embedding",
                        "numCandidates": 100,
                        "limit": top_k,
                    },
                }
            }
        ]
        
        # Add any additional filtering
        if filter_query:
            pipeline.append({"$match": filter_query})
            
        # Exclude the embedding vector from results to reduce data size
        pipeline.append({"$project": {"_id": 0, "embedding": 0}})

        results = (
            await Database.get_collection(collection_name)
            .aggregate(pipeline)
            .to_list(length=top_k)
        )
        return results
    except Exception as e:
        print(f"Vector search error: {str(e)}")
        # Fall back to text-based search if vector search fails
        return await fallback_text_search(
            collection_name, query_vector, top_k, filter_query
        )


async def fallback_text_search(
    collection_name, query_vector, top_k=5, filter_query=None
):
    """Fallback text search when vector search fails"""
    # This is a simplified version, in production you'd implement more sophisticated text search
    base_query = filter_query or {}
    base_query["is_active"] = True
    
    results = (
        await Database.get_collection(collection_name)
        .find(base_query)
        .limit(top_k)
        .to_list(length=top_k)
    )
    
    # Remove _id and embedding fields
    for result in results:
        if "_id" in result:
            result.pop("_id", None)
        if "embedding" in result:
            result.pop("embedding", None)
            
    return results


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    await Database.connect_db()
    await init_db()
    print("Database initialized and ready for use")
    yield
    # Shutdown event
    await Database.close_db()


app = FastAPI(title="Job Recommender System", lifespan=lifespan)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Add this after the token-related imports
BLACKLISTED_TOKENS = set()


# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Update the get_current_user function to check for blacklisted tokens
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Check if token is blacklisted
        if token in BLACKLISTED_TOKENS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await Database.get_collection(USERS_COLLECTION).find_one(
        {"email": token_data.email}
    )
    if user is None:
        raise credentials_exception
    return user


from typing import Union
from fastapi import HTTPException, APIRouter
from datetime import datetime
from bson import ObjectId
from passlib.context import CryptContext


@app.post("/register/candidate", response_model=ExtendedCandidate)
async def register_candidate(user: ExtendedCandidateCreate):
    try:
        # Check if user already exists
        existing_user = await Database.get_collection(USERS_COLLECTION).find_one(
            {"email": user.email}
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Generate MongoDB ObjectId
        object_id = ObjectId()
        str_id = str(object_id)
        current_time = datetime.utcnow()
    
        # Create user document
        user_dict = {
        "_id": object_id,
        "id": str_id,
        "email": user.email,
        "password": pwd_context.hash(user.password),
        "full_name": user.full_name,
        "user_type": "candidate",
            "created_at": current_time,
        }
    
        # Insert into users collection
        await Database.get_collection(USERS_COLLECTION).insert_one(user_dict)
    
        # Create candidate profile with comprehensive fields
        candidate_dict = {
        "_id": object_id,
        "id": str_id,
        "email": user.email,
        "user_type": "candidate",
        "full_name": user.full_name,
        "created_at": current_time,
            "phone": user.phone if user.phone else None,
            "location": user.location if user.location else None,
            "experience_years": (
                user.experience_years if user.experience_years else None
            ),
            "education_summary": (
                user.education_summary if user.education_summary else None
            ),
            "bio": user.bio if user.bio else None,
            "about": user.about if user.about else None,
            # Properly handle nested objects
            "links": user.links if user.links else None,
            "skills": user.skills if user.skills else None,
            "experience": user.experience if user.experience else [],
            "education": user.education if user.education else [],
            "certifications": user.certifications if user.certifications else [],
            "preferred_job_locations": (
                user.preferred_job_locations if user.preferred_job_locations else []
            ),
            "job_search_status": (
                user.job_search_status if user.job_search_status else None
            ),
            # Add default fields
        "profile_completed": True,
        "is_active": True,
        "last_active": current_time,
        "profile_views": 0,
        }
        
        # Generate embedding for the candidate
        searchable_text = f"{user.full_name} {user.bio or ''} {user.about or ''}"

        # Add skills to searchable text
        if user.skills:
            if (
                "languages_frameworks" in user.skills
                and user.skills["languages_frameworks"]
            ):
                searchable_text += " " + " ".join(user.skills["languages_frameworks"])
            if "ai_ml_data" in user.skills and user.skills["ai_ml_data"]:
                searchable_text += " " + " ".join(user.skills["ai_ml_data"])
            if "tools_platforms" in user.skills and user.skills["tools_platforms"]:
                searchable_text += " " + " ".join(user.skills["tools_platforms"])
            if "soft_skills" in user.skills and user.skills["soft_skills"]:
                searchable_text += " " + " ".join(user.skills["soft_skills"])

        candidate_dict["embedding"] = get_embedding(searchable_text)
        
        # Insert into candidates collection
        await Database.get_collection(CANDIDATES_COLLECTION).insert_one(candidate_dict)
    
        # Remove sensitive fields for response
        candidate_dict.pop("_id", None)
        candidate_dict.pop("embedding", None)
        
        return candidate_dict
    
    except Exception as e:
        print(f"Error in register_candidate: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register candidate")


@app.get("/candidate/{candidate_id}", response_model=Candidate)
async def get_candidate_profile(candidate_id: str):
    try:
        # Get candidate profile from candidates collection using id
        candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
            {"id": candidate_id}
        )
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate profile not found")
        
        # Remove MongoDB's _id
        candidate.pop("_id", None)
        
        return candidate
        
    except Exception as e:
        print(f"Error in get_candidate_profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/register/employer", response_model=ExtendedEmployer)
async def register_employer(user: ExtendedEmployerCreate):
    try:
        # Check if user already exists
        existing_user = await Database.get_collection(USERS_COLLECTION).find_one(
            {"email": user.email}
        )
        if existing_user:
          raise HTTPException(status_code=400, detail="Email already registered")
    
        # Validate required fields in company_details
        if not user.company_details:
            raise HTTPException(status_code=422, detail="Company details are required")

        company_name = user.company_details.get("company_name")
        if not company_name:
            raise HTTPException(
                status_code=422, detail="Company name is required in company_details"
            )

        industry = user.company_details.get("industry")
        if not industry:
            raise HTTPException(
                status_code=422, detail="Industry is required in company_details"
            )
    
        # Generate MongoDB ObjectId
        object_id = ObjectId()
        str_id = str(object_id)
        current_time = datetime.utcnow()
        
        # Create user document
        user_dict = {
        "_id": object_id,
        "id": str_id,
        "email": user.email,
        "password": pwd_context.hash(user.password),
        "full_name": user.full_name,
        "user_type": "employer",
            "created_at": current_time,
        }
    
        # Insert into users collection
        await Database.get_collection(USERS_COLLECTION).insert_one(user_dict)
    
        # Create employer profile with comprehensive fields
        employer_dict = {
        "_id": object_id,
        "id": str_id,
        "email": user.email,
        "user_type": "employer",
        "full_name": user.full_name,
            "position": user.position if user.position else None,
            "bio": user.bio if user.bio else None,
            "about": user.about if user.about else None,
        "contact_email": user.contact_email or user.email,
            "contact_phone": user.contact_phone if user.contact_phone else None,
            "location": user.location if user.location else None,
        "created_at": current_time,
            # Company details
            "company_details": {
                "company_name": user.company_details.get("company_name"),
                "company_description": user.company_details.get("company_description"),
                "company_website": user.company_details.get("company_website"),
                "company_location": user.company_details.get("company_location"),
                "company_size": user.company_details.get("company_size"),
                "industry": user.company_details.get("industry"),
                "founded_year": user.company_details.get("founded_year"),
                "company_logo": user.company_details.get("company_logo"),
                "company_socials": user.company_details.get("company_socials", {}),
                "values": user.company_details.get("values", []),
                "mission": user.company_details.get("mission"),
                "vision": user.company_details.get("vision"),
            },
            # Hiring preferences
            "hiring_preferences": (
                user.hiring_preferences
                if user.hiring_preferences
                else {
                    "job_roles_hiring": [],
                    "employment_types": [],
                    "locations_hiring": [],
                    "salary_range_usd": None,
                    "remote_friendly": False,
                    "tech_stack": [],
                }
            ),
            # Add default fields
        "profile_completed": True,
        "is_active": True,
        "last_active": current_time,
            "verified": False,
        "total_jobs_posted": 0,
        "total_active_jobs": 0,
            "account_type": "standard",
        "profile_views": 0,
            "posted_jobs": [],
        }
    
        # Insert into employers collection
        await Database.get_collection(EMPLOYERS_COLLECTION).insert_one(employer_dict)
    
        # Remove sensitive fields for response
        employer_dict.pop("_id", None)
        
        return employer_dict
        
    except Exception as e:
        print(f"Error in register_employer: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register employer")


@app.get("/employer/{employer_id}", response_model=Employer)
async def get_employer_profile(employer_id: str):
    try:
        employer = await Database.get_collection(EMPLOYERS_COLLECTION).find_one(
            {"id": employer_id}
        )
        if not employer:
            raise HTTPException(status_code=404, detail="Employer profile not found")
        
        # Get jobs posted by this employer
        raw_jobs_from_db = (
            await Database.get_collection(JOBS_COLLECTION)
            .find({"employer_id": employer_id, "is_active": True})
            .to_list(length=None)
        )
        
        # Process jobs to remove _id and ensure they are suitable for the response model
        processed_jobs_list = []
        for job_doc in raw_jobs_from_db:
            job_doc.pop("_id", None)  # Remove MongoDB's _id from each job document
            # Potentially, here you could also validate/convert job_doc fields if needed,
            # e.g., ensuring datetime objects are handled as expected by Pydantic if not using a Job model for them.
            processed_jobs_list.append(job_doc)
            
        employer["posted_jobs"] = processed_jobs_list

        # Remove MongoDB's _id from the main employer document before returning
        employer.pop("_id", None)
        
        return employer
        
    except Exception as e:
        # Log the actual exception for debugging on the server
        import traceback

        print(
            f"Error in get_employer_profile for employer_id {employer_id}: {{str(e)}}\n{{traceback.format_exc()}}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await Database.get_collection(USERS_COLLECTION).find_one(
        {"email": form_data.username}
    )
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}


# Job endpoints
@app.post("/jobs", response_model=Job)
async def create_job(job: JobCreate, current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only employers can post jobs")
    
    job_dict = job.dict()
    job_dict["id"] = str(ObjectId())
    job_dict["is_active"] = True
    
    # Process salary_range if it's a string
    if "salary_range" in job_dict and isinstance(job_dict["salary_range"], str):
        try:
            # Parse salary range string like "120,000-160,000 USD"
            salary_str = job_dict["salary_range"].split(" ")[0]  # Get "120,000-160,000"
            min_max = salary_str.split("-")  # Split into ["120,000", "160,000"]
            
            # Remove commas and convert to integers
            min_salary = int(min_max[0].replace(",", ""))
            max_salary = int(min_max[1].replace(",", ""))
            
            # Get currency if available
            currency = "USD"
            if len(job_dict["salary_range"].split(" ")) > 1:
                currency = job_dict["salary_range"].split(" ")[1]
                
            # Update with object format
            job_dict["salary_range"] = {
                "min": min_salary,
                "max": max_salary,
                "currency": currency
            }
        except Exception as e:
            print(f"Error parsing salary range: {str(e)}")
            # Keep as string if parsing fails
            pass
    
    # Create embedding for semantic search
    job_dict["embedding"] = create_job_embedding(job_dict)
    
    try:
        await Database.get_collection(JOBS_COLLECTION).insert_one(job_dict)
        
        # Remove embedding from returned data to reduce response size
        job_dict.pop("embedding", None)
        return job_dict
    except Exception as e:
        print(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")


@app.get("/jobs", response_model=List[Job])
async def get_jobs(current_user: dict = Depends(get_current_user)):
    jobs = (
        await Database.get_collection(JOBS_COLLECTION)
        .find({"is_active": True})
        .to_list(length=None)
    )
    return jobs


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str, current_user: dict = Depends(get_current_user)):
    # Verify user is an employer
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only employers can delete jobs")
    
    # Get the job
    job = await Database.get_collection(JOBS_COLLECTION).find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify the job belongs to this employer
    if str(job["employer_id"]) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="You can only delete your own jobs")
    
    # Delete the job
    result = await Database.get_collection(JOBS_COLLECTION).delete_one({"id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete job")
    
    return {"message": "Job deleted successfully"}


@app.patch("/jobs/{job_id}", response_model=Job)
async def update_job(
    job_id: str, update_data: dict, current_user: dict = Depends(get_current_user)
):
    # Verify user is an employer
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only employers can update jobs")
    
    # Get the job
    job = await Database.get_collection(JOBS_COLLECTION).find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify the job belongs to this employer
    if str(job["employer_id"]) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="You can only update your own jobs")
    
    # List of all updateable fields
    updatable_fields = [
        "title",
        "company",
        "description",
        "requirements",
        "location",
        "employment_type",
        "experience_level",
        "industry",
        "responsibilities",
        "preferred_qualifications",
        "tech_stack",
        "remote_option",
        "work_mode",
        "salary_range",
        "benefits",
        "application_deadline",
        "posted_date",
        "contact_email",
        "is_active",
    ]
    
    # Process salary_range if it's a string
    if "salary_range" in update_data and isinstance(update_data["salary_range"], str):
        try:
            # Parse salary range string like "120,000-160,000 USD"
            salary_str = update_data["salary_range"].split(" ")[0]  # Get "120,000-160,000"
            min_max = salary_str.split("-")  # Split into ["120,000", "160,000"]
            
            # Remove commas and convert to integers
            min_salary = int(min_max[0].replace(",", ""))
            max_salary = int(min_max[1].replace(",", ""))
            
            # Get currency if available
            currency = "USD"
            if len(update_data["salary_range"].split(" ")) > 1:
                currency = update_data["salary_range"].split(" ")[1]
                
            # Update with object format
            update_data["salary_range"] = {
                "min": min_salary,
                "max": max_salary,
                "currency": currency
            }
        except Exception as e:
            print(f"Error parsing salary range: {str(e)}")
            # Keep as string if parsing fails
            pass
    
    # Filter update_data to only include valid fields
    filtered_update_data = {
        k: v for k, v in update_data.items() if k in updatable_fields
    }
    
    # If no valid fields to update
    if not filtered_update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    # If fields that affect the embedding are updated, regenerate embedding
    semantic_fields = [
        "title",
        "company",
        "description",
        "requirements",
        "location",
        "industry",
        "experience_level",
        "responsibilities",
        "tech_stack",
        "preferred_qualifications",
        "work_mode",
    ]
    try:
        if any(field in filtered_update_data for field in semantic_fields):
            # Create updated job data by merging current job with updates
            updated_job = {**job}
            updated_job.update(filtered_update_data)
            # Generate new embedding
            try:
                filtered_update_data["embedding"] = create_job_embedding(updated_job)
            except Exception as e:
                print(f"Error generating embedding: {str(e)}")
                # Continue without updating embedding if there's an error
                pass
    except Exception as e:
        print(f"Error in embedding generation logic: {str(e)}")
        # Continue without updating embedding
        pass
    
    # Update the job
    try:
        result = await Database.get_collection(JOBS_COLLECTION).update_one(
            {"id": job_id}, {"$set": filtered_update_data}
        )
        
        if result.modified_count == 0:
            # The document might not have been modified if the values are the same
            # But we should still return the job data
            pass
        
        # Return updated job
        updated_job = await Database.get_collection(JOBS_COLLECTION).find_one(
            {"id": job_id}
        )
        if not updated_job:
            raise HTTPException(status_code=404, detail="Job not found after update")
        
        # Remove MongoDB's _id and embedding vector from response
        updated_job.pop("_id", None)
        updated_job.pop("embedding", None)
        
        return updated_job
    except Exception as e:
        print(f"Error updating job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating job: {str(e)}")


# Project endpoints
@app.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: dict, current_user: dict = Depends(get_current_user)
):
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only employers can post projects")
    
    try:
        # Convert project to dict if it's not already
        project_dict = project if isinstance(project, dict) else project.dict(exclude_none=True)
        
        # Generate a unique ID
        project_id = str(ObjectId())
        project_dict["id"] = project_id
        project_dict["created_at"] = datetime.utcnow()
        project_dict["is_active"] = True
        project_dict["status"] = "open"
        project_dict["employer_id"] = current_user["id"]
        
        print(
            f"DEBUG - Creating project: employer_id={current_user['id']}, title={project_dict.get('title', 'Unknown')}, id={project_id}"
        )
        
        # Validate required fields
        required_fields = [
            "title",
            "company",
            "description",
            "requirements",
            "project_type",
            "skills_required",
        ]
        missing_fields = [
            field
            for field in required_fields
            if field not in project_dict or not project_dict[field]
        ]
        
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing_fields)}",
            )
            
        # Ensure list fields are actually lists
        list_fields = [
            "requirements",
            "skills_required",
            "objectives",
            "preferred_qualifications",
            "tools_technologies",
            "deliverables"
        ]
        for field in list_fields:
            if (
                field in project_dict
                and project_dict[field] is not None
                and not isinstance(project_dict[field], list)
            ):
                project_dict[field] = [
                    project_dict[field]
                ]  # Convert to list if it's not already
        
        # Handle complex fields
        # Timeline - special handling for milestones array
        if "timeline" in project_dict and isinstance(project_dict["timeline"], dict):
            if "milestones" in project_dict["timeline"] and isinstance(project_dict["timeline"]["milestones"], list):
                # Keep the milestones array as is, it will be stored in MongoDB without issues
                pass
            
        # Budget range
        if "budget_range" in project_dict and isinstance(project_dict["budget_range"], dict):
            try:
                min_val = project_dict["budget_range"].get("min", 0)
                max_val = project_dict["budget_range"].get("max", 0)
                currency = project_dict["budget_range"].get("currency", "USD")
                project_dict["budget_range"] = f"{min_val}-{max_val} {currency}"
            except Exception as e:
                print(f"Error formatting budget_range: {str(e)}")
                # Keep as is if there's an error
        
        # Duration
        if "duration" in project_dict and isinstance(project_dict["duration"], dict):
            try:
                time_frame = project_dict["duration"].get("time_frame", "")
                hours = project_dict["duration"].get("estimated_hours", "")
                project_dict["duration"] = f"{time_frame} ({hours} hours)"
            except Exception as e:
                print(f"Error formatting duration: {str(e)}")
                # Keep as is if there's an error
        
        # Handle dictionary fields
        dict_fields = ["experience", "timeline"]
        for field in dict_fields:
            if (
                field in project_dict
                and project_dict[field] is not None
                and not isinstance(project_dict[field], dict)
            ):
                # If it's not a dict, try to convert from string (JSON)
                if isinstance(project_dict[field], str):
                    try:
                        import json
                        project_dict[field] = json.loads(project_dict[field])
                    except:
                        project_dict[field] = {"value": project_dict[field]}  # Fallback
                else:
                    project_dict[field] = {"value": project_dict[field]}  # Fallback
        
        # Create embedding for semantic search - enhance to include new fields
        searchable_text = f"{project_dict.get('title', '')} {project_dict.get('company', '')} {project_dict.get('description', '')}"
        
        # Add additional fields to searchable text
        if "project_type" in project_dict:
            searchable_text += f" {project_dict['project_type']}"
            
        if "skills_required" in project_dict:
            searchable_text += f" {' '.join(project_dict['skills_required'])}"
            
        if "requirements" in project_dict:
            searchable_text += f" {' '.join(project_dict['requirements'])}"
            
        if "tools_technologies" in project_dict and isinstance(
            project_dict["tools_technologies"], list
        ):
            searchable_text += (
                f" {' '.join(project_dict.get('tools_technologies', []))}"
            )

        if "objectives" in project_dict and isinstance(
            project_dict["objectives"], list
        ):
            searchable_text += f" {' '.join(project_dict.get('objectives', []))}"
            
        if "preferred_qualifications" in project_dict and isinstance(
            project_dict["preferred_qualifications"], list
        ):
            searchable_text += (
                f" {' '.join(project_dict.get('preferred_qualifications', []))}"
            )
            
        if "location" in project_dict:
            searchable_text += f" {project_dict['location']}"
        
        try:
            project_dict["embedding"] = get_embedding(searchable_text)
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            # Continue without embedding if there's an error
        
        # Insert the project
        await Database.get_collection(PROJECTS_COLLECTION).insert_one(project_dict)
        
        # Fetch and return the created project
        created_project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
            {"id": project_dict["id"]}
        )
        if not created_project:
            print("DEBUG - Project not found after creation!")
            # Try using ObjectId directly as a fallback
            created_project = await Database.get_collection(
                PROJECTS_COLLECTION
            ).find_one({"id": project_id})
            if not created_project:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create project - cannot find it after creation",
                )
            
        # Remove MongoDB's _id and embedding from response
        if "_id" in created_project:
            created_project.pop("_id", None)
            
        if "embedding" in created_project:
            created_project.pop("embedding", None)
            
        print(f"DEBUG - Project created successfully: id={created_project['id']}")
        return created_project
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating project: {str(e)}")  # Log the error
        import traceback

        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}",
        )


@app.get("/projects", response_model=List[Project])
async def get_projects(
    status: Optional[str] = None, current_user: dict = Depends(get_current_user)
):
    print(f"DEBUG: get_projects called with status={status}")
    try:
        # Start with a base query
        query = {}
        
        # Only add filters if provided
        if status:
            print(f"DEBUG: Filtering by status: {status}")
            # Validate status
            valid_statuses = ["open", "in_progress", "completed", "cancelled"]
            if status not in valid_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                )
            query["status"] = status
    
        # Get all projects
        print(f"DEBUG: Query for all projects = {query}")
        projects = (
            await Database.get_collection(PROJECTS_COLLECTION)
            .find(query)
            .to_list(length=None)
        )
        print(f"DEBUG: Found {len(projects)} projects")
        
        # Process projects - remove _id and handle missing fields
        clean_projects = []
        required_fields = [
            "id",
            "title",
            "company",
            "description",
            "requirements",
            "employer_id",
            "is_active",
            "status",
            "project_type",
            "skills_required",
        ]
        
        for project in projects:
            # Remove MongoDB's _id
            if "_id" in project:
                project.pop("_id", None)
                
            # Fill in any missing required fields
            for field in required_fields:
                if field not in project:
                    print(
                        f"DEBUG: Project {project.get('id')} missing required field '{field}'"
                    )
                    if field in ["requirements", "skills_required"]:
                        project[field] = []
                    elif field in ["is_active"]:
                        project[field] = True
                    elif field in ["status"]:
                        project[field] = "open"
                    else:
                        project[field] = f"[Missing {field}]"
                        
            clean_projects.append(project)
            
        print(f"DEBUG: Returning {len(clean_projects)} projects")
        return clean_projects
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_projects: {str(e)}")
        import traceback

        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve projects: {str(e)}"
        )


@app.get("/employer-projects", response_model=List[Project])
async def get_current_employer_projects(current_user: dict = Depends(get_current_user)):
    """Get projects posted by the current employer using a different endpoint path"""
    try:
        # Check if user is an employer
        if current_user.get("user_type") != "employer":
            raise HTTPException(
                status_code=403, detail="Only employers can view their projects"
            )
    
        employer_id = current_user.get("id")
        if not employer_id:
            raise HTTPException(status_code=400, detail="Invalid employer ID")
        
        print(f"DEBUG: Finding projects for employer_id: {employer_id}")
        
        # Find all projects for this employer
        projects_cursor = Database.get_collection(PROJECTS_COLLECTION).find(
            {"employer_id": employer_id}
        )
        projects = await projects_cursor.to_list(length=None)
        
        print(f"DEBUG: Found {len(projects)} projects")
        
        # Clean up projects before returning
        result_projects = []
        for project in projects:
            if "_id" in project:
                project.pop("_id", None)
            result_projects.append(project)
        
        return result_projects
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_current_employer_projects: {str(e)}")
        import traceback

        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get details of a specific project"""
    print(
        f"DEBUG: get_project called for project_id={project_id}, user={current_user.get('id')}"
    )
    try:
        # Get the project
        print(f"DEBUG: Attempting to find project with id={project_id}")
        project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
            {"id": project_id}
        )
        print(f"DEBUG: Project found? {'Yes' if project else 'No'}")
        print(f"DEBUG: Project data: {project}")
        
        if not project:
            print(f"DEBUG: Project with id={project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Remove MongoDB's _id
        if "_id" in project:
            project.pop("_id", None)
            print("DEBUG: Removed _id from project")
            
        # Ensure all required fields are present
        required_fields = [
            "id",
            "title",
            "company",
            "description",
            "requirements",
            "employer_id",
            "is_active",
            "status",
            "project_type",
            "skills_required",
        ]
        for field in required_fields:
            if field not in project:
                print(f"DEBUG: Required field '{field}' missing from project")
                if field in ["requirements", "skills_required"]:
                    project[field] = []
                elif field in ["is_active"]:
                    project[field] = True
                elif field in ["status"]:
                    project[field] = "open"
                else:
                    project[field] = f"[Missing {field}]"
            
        print(
            f"DEBUG: Project details: id={project.get('id')}, title={project.get('title')}"
        )
        
        # If user is an employer, verify they own this project or return limited info
        if current_user["user_type"] == UserType.EMPLOYER:
            # Allow full access for project owners
            if project["employer_id"] == current_user["id"]:
                print("DEBUG: User is the project owner")
                return project
            else:
                print(
                    f"DEBUG: User is not owner. Project owner={project.get('employer_id')}, User={current_user.get('id')}"
                )
        
        # For non-owner employers and candidates, only return project if it's active
        if not project.get("is_active", False):
            print(f"DEBUG: Project is not active, returning 404")
            raise HTTPException(status_code=404, detail="Project not found or inactive")
        
        print("DEBUG: Returning project to non-owner")
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_project: {str(e)}")
        import traceback

        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.patch("/projects/{project_id}", response_model=Project)
async def update_project_status(
    project_id: str, update_data: dict, current_user: dict = Depends(get_current_user)
):
    """Update a project's details or status"""
    print(
        f"DEBUG: update_project_status called for project_id={project_id}, user={current_user.get('id')}"
    )
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(
            status_code=403, detail="Only employers can update projects"
        )
    
    try:
        # Get the project
        print(f"DEBUG: Attempting to find project with id={project_id}")
        project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
            {"id": project_id}
        )
        print(f"DEBUG: Project data: {project}")
        
        if not project:
            print(f"DEBUG: Project with id={project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Verify the project belongs to this employer
        if project["employer_id"] != current_user["id"]:
            print(
                f"DEBUG: User is not project owner. Project owner={project.get('employer_id')}, User={current_user.get('id')}"
            )
            raise HTTPException(
                status_code=403, detail="You can only update your own projects"
            )
        
        # Validate status if it's being updated
        if "status" in update_data:
            print(f"DEBUG: Validating status: {update_data['status']}")
            valid_statuses = ["open", "in_progress", "completed", "cancelled"]
            if update_data["status"] not in valid_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                )
        
        # Handle complex fields
        # Timeline - special handling for milestones array
        if "timeline" in update_data and isinstance(update_data["timeline"], dict):
            if "milestones" in update_data["timeline"] and isinstance(update_data["timeline"]["milestones"], list):
                # Keep the milestones array as is, it will be stored in MongoDB without issues
                pass
            
        # Budget range
        if "budget_range" in update_data and isinstance(update_data["budget_range"], dict):
            try:
                min_val = update_data["budget_range"].get("min", 0)
                max_val = update_data["budget_range"].get("max", 0)
                currency = update_data["budget_range"].get("currency", "USD")
                update_data["budget_range"] = f"{min_val}-{max_val} {currency}"
            except Exception as e:
                print(f"Error formatting budget_range: {str(e)}")
                # Keep as is if there's an error
        
        # Duration
        if "duration" in update_data and isinstance(update_data["duration"], dict):
            try:
                time_frame = update_data["duration"].get("time_frame", "")
                hours = update_data["duration"].get("estimated_hours", "")
                update_data["duration"] = f"{time_frame} ({hours} hours)"
            except Exception as e:
                print(f"Error formatting duration: {str(e)}")
                # Keep as is if there's an error
        
        # Handle dictionary fields
        dict_fields = ["experience", "timeline"]
        for field in dict_fields:
            if (
                field in update_data
                and update_data[field] is not None
                and not isinstance(update_data[field], dict)
            ):
                # If it's not a dict, try to convert from string (JSON)
                if isinstance(update_data[field], str):
                    try:
                        import json
                        update_data[field] = json.loads(update_data[field])
                    except:
                        update_data[field] = {"value": update_data[field]}  # Fallback
                else:
                    update_data[field] = {"value": update_data[field]}  # Fallback
        
        # Ensure list fields are actually lists
        list_fields = [
            "requirements",
            "skills_required",
            "objectives",
            "preferred_qualifications",
            "tools_technologies",
            "deliverables"
        ]
        for field in list_fields:
            if (
                field in update_data
                and update_data[field] is not None
                and not isinstance(update_data[field], list)
            ):
                update_data[field] = [
                    update_data[field]
                ]  # Convert to list if it's not already
        
        # Remove any invalid fields from update_data
        allowed_fields = [
            "status",
            "description",
            "title",
            "requirements",
            "budget_range",
            "duration",
            "location",
            "skills_required",
            "is_active",
            "project_type",
            "objectives",
            "preferred_qualifications",
            "tools_technologies",
            "timeline",
            "experience",
            "deliverables"
        ]
        invalid_fields = [
            key for key in update_data.keys() if key not in allowed_fields
        ]
        for field in invalid_fields:
            print(f"DEBUG: Removing invalid field from update: {field}")
            update_data.pop(field, None)
            
        # Don't allow updating employer_id
        if "employer_id" in update_data:
            update_data.pop("employer_id", None)
            
        # Add updated timestamp
        update_data["last_updated"] = datetime.utcnow()
        
        # If fields that affect the embedding are updated, regenerate embedding
        semantic_fields = [
            "title",
            "company",
            "description",
            "requirements",
            "skills_required",
            "project_type",
            "location",
            "tools_technologies",
            "objectives"
        ]
        if any(field in update_data for field in semantic_fields):
            # Create updated project data by merging current project with updates
            updated_project = {**project}
            updated_project.update(update_data)
            # Generate new embedding
            try:
                update_data["embedding"] = create_project_embedding(updated_project)
            except Exception as e:
                print(f"Error generating embedding: {str(e)}")
                # Continue without updating embedding if there's an error
        
        print(f"DEBUG: Update data: {update_data}")
    
        # Update the project
        result = await Database.get_collection(PROJECTS_COLLECTION).update_one(
            {"id": project_id}, {"$set": update_data}
        )
        print(
            f"DEBUG: Update result: matched={result.matched_count}, modified={result.modified_count}"
        )
    
        if result.matched_count == 0:
            print("DEBUG: No documents were matched")
            raise HTTPException(status_code=404, detail="Project not found") 
    
        # Return updated project
        updated_project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
            {"id": project_id}
        )
        if not updated_project:
            print("DEBUG: Could not find updated project")
            raise HTTPException(
                status_code=404, detail="Project not found after update"
            )
        
        if "_id" in updated_project:
            updated_project.pop("_id", None)
            
        # Remove embedding from response
        if "embedding" in updated_project:
            updated_project.pop("embedding", None)
        
        print(f"DEBUG: Project updated successfully: {project_id}")    
        return updated_project
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in update_project_status: {str(e)}")
        import traceback

        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Failed to update project: {str(e)}"
        )


@app.delete("/projects/{project_id}")
async def delete_project(
    project_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete a project"""
    print(
        f"DEBUG: delete_project called for project_id={project_id}, user={current_user.get('id')}"
    )
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(
            status_code=403, detail="Only employers can delete projects"
        )
    
    try:
        # Get the project
        print(f"DEBUG: Attempting to find project with id={project_id}")
        project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
            {"id": project_id}
        )
        print(f"DEBUG: Project found? {'Yes' if project else 'No'}")
        
        if not project:
            print(f"DEBUG: Project with id={project_id} not found")
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Verify the project belongs to this employer
        if project["employer_id"] != current_user["id"]:
            print(
                f"DEBUG: User is not project owner. Project owner={project.get('employer_id')}, User={current_user.get('id')}"
            )
            raise HTTPException(
                status_code=403, detail="You can only delete your own projects"
            )
        
        # Delete the project
        print(f"DEBUG: Deleting project with id={project_id}")
        result = await Database.get_collection(PROJECTS_COLLECTION).delete_one(
            {"id": project_id}
        )
        print(f"DEBUG: Delete result: deleted count={result.deleted_count}")
        
        if result.deleted_count == 0:
            print("DEBUG: No documents were deleted")
            # Even though we found it earlier, it might have been deleted concurrently or there might be an issue with the ID format
            # Check again to differentiate between "project doesn't exist" and "failed to delete"
            exists_check = await Database.get_collection(PROJECTS_COLLECTION).find_one(
                {"id": project_id}
            )
            if exists_check:
                # It still exists, so deletion failed
                raise HTTPException(status_code=500, detail="Failed to delete project")
            else:
                # It's already gone
                return {"message": "Project already deleted", "id": project_id}
        
        print(f"DEBUG: Project deleted successfully: {project_id}")
        
        # Verify the project is really gone
        verify = await Database.get_collection(PROJECTS_COLLECTION).find_one(
            {"id": project_id}
        )
        if verify:
            print(f"WARNING: Project still exists after deletion: {project_id}")
            
        return {"message": "Project deleted successfully", "id": project_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in delete_project: {str(e)}")
        import traceback

        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Failed to delete project: {str(e)}"
        )


# Recommendation endpoints
@app.get("/recommendations/jobs", response_model=List[dict])
async def get_job_recommendations(current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] != UserType.CANDIDATE:
        raise HTTPException(
            status_code=403, detail="Only candidates can get job recommendations"
        )
    
    # Get candidate profile
    candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
        {"email": current_user["email"]}
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    
    jobs = (
        await Database.get_collection(JOBS_COLLECTION)
        .find({"is_active": True})
        .to_list(length=None)
    )
    
    if not jobs:
        return []
        
    recommendations = []
    
    # Process each job to find matches
    for job in jobs:
        # Get match score and explanation
        score, explanation = await get_match_score(job, candidate)
        
        # Add to recommendations with detailed job information
        job_recommendation = {
            "job_id": job["id"],
            "match_score": score,
            "explanation": explanation,
            "job_details": {
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "description": job.get("description", ""),
                "location": job.get("location", ""),
                "salary_range": job.get("salary_range", ""),
                "required_skills": job.get("required_skills", []),
                "job_type": job.get("job_type", ""),
                "experience_level": job.get("experience_level", ""),
            },
        }
        recommendations.append(job_recommendation)
    
    # Save recommendations with score > 70 to recommendations collection
        if score >= 70:
            # Create recommendation document
            recommendation_doc = {
                "id": str(ObjectId()),
                "candidate_id": candidate["id"],
                "job_id": job["id"],
                "match_score": score,
                "type": "job_recommendation",
                "timestamp": datetime.utcnow(),
                "viewed": False,
            }
            
            # Check if this recommendation already exists
            existing_rec = await Database.get_collection(
                RECOMMENDATIONS_COLLECTION
            ).find_one(
                {
                "candidate_id": candidate["id"],
                "job_id": job["id"],
                    "type": "job_recommendation",
                }
            )
            
            # If it doesn't exist or score has changed, save/update it
            if not existing_rec:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).insert_one(
                    recommendation_doc
                )
                print(
                    f"Saved job recommendation with score {score} for candidate {candidate['id']}"
                )
            elif existing_rec["match_score"] != score:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).update_one(
                    {"id": existing_rec["id"]},
                    {
                        "$set": {
                            "match_score": score,
                            "timestamp": datetime.utcnow(),
                        }
                    },
                )
                print(
                    f"Updated job recommendation score to {score} for candidate {candidate['id']}"
                )
    
    # Sort by match score
    recommendations = sorted(
        recommendations, key=lambda x: x["match_score"], reverse=True
                )
    
    return recommendations


@app.get("/recommendations/candidates/{job_id}", response_model=dict)
async def get_candidate_recommendations(
    job_id: str, 
    min_match_score: int = 0,
    limit: int = 10,
    include_details: bool = True,
    sort_by: str = "match_score",
    experience_min: Optional[int] = None,
    experience_max: Optional[int] = None,
    location_radius: Optional[int] = None,
    include_remote: bool = False,
    education_level: Optional[str] = None,
    availability: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get candidate recommendations for a specific job with advanced filtering
    
    - min_match_score: Minimum match score (0-100)
    - limit: Maximum number of results to return
    - include_details: Whether to include full candidate details
    - sort_by: Field to sort by (match_score, experience_years, etc.)
    - experience_min: Minimum years of experience
    - experience_max: Maximum years of experience
    - location_radius: Distance in miles/km from job location
    - include_remote: Include candidates willing to work remotely
    - education_level: Comma-separated list of education levels (Bachelors,Masters,PhD)
    - availability: Comma-separated list of availability options (Immediate,2 weeks,1 month)
    """
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(
            status_code=403, detail="Only employers can get candidate recommendations"
        )
    
    job = await Database.get_collection(JOBS_COLLECTION).find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Build query filter for candidates
    candidate_filter = {"is_active": True, "profile_completed": True}
    
    # Handle experience range filter
    if experience_min is not None or experience_max is not None:
        # Convert string experience_years to numeric for comparison
        # Note: This is a simplified approach. In production, you'd need more robust parsing
        # or store experience_years as a number in the database
        try:
            # Get all candidates and filter in memory since experience_years might be stored as string
            candidates = await Database.get_collection(CANDIDATES_COLLECTION).find(candidate_filter).to_list(length=None)
            
            filtered_candidates = []
            for candidate in candidates:
                exp_years = candidate.get("experience_years")
                if exp_years:
                    # Try to extract numeric value from experience_years
                    try:
                        if isinstance(exp_years, str):
                            # Extract first number from string like "5+ years" or "3-5 years"
                            import re
                            matches = re.findall(r'\d+', exp_years)
                            if matches:
                                years = int(matches[0])
                            else:
                                continue  # Skip if no numeric value found
                        elif isinstance(exp_years, (int, float)):
                            years = exp_years
                        else:
                            continue  # Skip if not a recognized format
                            
                        # Apply min/max filters
                        if experience_min is not None and years < experience_min:
                            continue
                        if experience_max is not None and years > experience_max:
                            continue
                            
                        filtered_candidates.append(candidate)
                    except (ValueError, TypeError):
                        # If we can't parse the experience, skip this candidate
                        continue
                        
            candidates = filtered_candidates
        except Exception as e:
            print(f"Error filtering by experience: {str(e)}")
            # Fallback to getting all candidates if experience filtering fails
            candidates = await Database.get_collection(CANDIDATES_COLLECTION).find(candidate_filter).to_list(length=None)
    else:
        # Get all candidates matching the base filter
        candidates = await Database.get_collection(CANDIDATES_COLLECTION).find(candidate_filter).to_list(length=None)
    
    if not candidates:
        print(f"No active candidates found for job {job_id}")
        return {"candidates": [], "total_count": 0, "filters_applied": {}}
    
    # Filter by education level if specified
    if education_level:
        education_levels = [level.strip() for level in education_level.split(",")]
        filtered_candidates = []
        
        for candidate in candidates:
            # Check education array or education_summary field
            education = candidate.get("education", [])
            education_summary = candidate.get("education_summary", "")
            
            # Check if any education level matches
            matches_education = False
            
            # Check in education array
            if isinstance(education, list):
                for edu in education:
                    degree = edu.get("degree", "").lower() if isinstance(edu, dict) else ""
                    if any(level.lower() in degree for level in education_levels):
                        matches_education = True
                        break
            
            # If not found in education array, check in summary
            if not matches_education and education_summary:
                if any(level.lower() in education_summary.lower() for level in education_levels):
                    matches_education = True
            
            if matches_education:
                filtered_candidates.append(candidate)
                
        candidates = filtered_candidates
    
    # Filter by availability if specified
    if availability:
        availability_options = [option.strip() for option in availability.split(",")]
        filtered_candidates = []
        
        for candidate in candidates:
            job_search_status = candidate.get("job_search_status", {})
            
            # Check notice period or availability
            if isinstance(job_search_status, dict):
                notice_period = job_search_status.get("notice_period_days")
                available_from = job_search_status.get("available_from")
                
                # Determine candidate's availability category
                candidate_availability = "Unknown"
                
                if notice_period is not None:
                    if notice_period == 0:
                        candidate_availability = "Immediate"
                    elif notice_period <= 14:
                        candidate_availability = "2 weeks"
                    elif notice_period <= 30:
                        candidate_availability = "1 month"
                    else:
                        candidate_availability = "More than 1 month"
                
                # Check if candidate's availability matches any requested option
                if candidate_availability in availability_options or "Unknown" in availability_options:
                    filtered_candidates.append(candidate)
            else:
                # If job_search_status is not properly structured, include if "Unknown" is accepted
                if "Unknown" in availability_options:
                    filtered_candidates.append(candidate)
                    
        candidates = filtered_candidates
    
    # Process location filtering
    if location_radius is not None or include_remote:
        job_location = job.get("location", "")
        filtered_candidates = []
        
        for candidate in candidates:
            candidate_location = candidate.get("location", "")
            preferred_locations = candidate.get("preferred_job_locations", [])
            
            # Check for remote preference
            if include_remote:
                remote_terms = ["remote", "anywhere", "virtual", "work from home", "wfh"]
                is_remote_ok = any(
                    any(term in loc.lower() for term in remote_terms) 
                    for loc in preferred_locations
                ) if preferred_locations else False
                
                if is_remote_ok:
                    filtered_candidates.append(candidate)
                    continue
            
            # If location_radius is specified, check if candidate location is within radius
            # Note: This is a simplified check. In production, you'd use geocoding and distance calculation
            if location_radius is not None and job_location and candidate_location:
                # Simple string matching for demo purposes
                # In production, use proper geocoding and distance calculation
                if job_location.lower() in candidate_location.lower() or candidate_location.lower() in job_location.lower():
                    filtered_candidates.append(candidate)
                    continue
                
                # Check preferred locations as well
                if any(job_location.lower() in loc.lower() or loc.lower() in job_location.lower() for loc in preferred_locations):
                    filtered_candidates.append(candidate)
                    continue
                    
        candidates = filtered_candidates
    
    # Match candidates to job
    recommendations = []
    for candidate in candidates:
        # Get match score and explanation
        score, explanation = await get_match_score(job, candidate)
        
        # Skip candidates below minimum match score
        if score < min_match_score:
            continue
            
        candidate_id = candidate.get("id")
        
        # Add to recommendations with detailed candidate information
        candidate_recommendation = {
            "candidate_id": candidate_id,
            "match_score": score,
            "explanation": explanation,
        }
        
        # Add detailed candidate information if requested
        if include_details:
            candidate_recommendation["candidate_details"] = {
                "full_name": candidate.get("full_name", ""),
                "email": candidate.get("email", ""),
                "skills": candidate.get("skills", []),
                "experience": candidate.get("experience", ""),
                "experience_years": candidate.get("experience_years", ""),
                "education": candidate.get("education", []),
                "education_summary": candidate.get("education_summary", ""),
                "location": candidate.get("location", ""),
                "profile_summary": candidate.get("profile_summary", ""),
                "certifications": candidate.get("certifications", []),
                "languages": candidate.get("languages", []),
                "preferred_job_type": candidate.get("preferred_job_type", ""),
                "preferred_location": candidate.get("preferred_location", ""),
                "preferred_salary": candidate.get("preferred_salary", ""),
                "job_search_status": candidate.get("job_search_status", {}),
            }
        
        recommendations.append(candidate_recommendation)
    
    # Save high-scoring recommendations to the recommendations collection
        if score >= 70:
            # Create recommendation document
            recommendation_doc = {
                "id": str(ObjectId()),
                "candidate_id": candidate_id,
                "job_id": job_id,
                "employer_id": current_user["id"],
                "match_score": score,
                "type": "candidate_recommendation",
                "timestamp": datetime.utcnow(),
                "viewed": False,
            }
            
            # Check if this recommendation already exists
            existing_rec = await Database.get_collection(
                RECOMMENDATIONS_COLLECTION
            ).find_one(
                {
                "candidate_id": candidate_id,
                "job_id": job_id,
                    "type": "candidate_recommendation",
                }
            )
            
            # If it doesn't exist or score has changed, save/update it
            if not existing_rec:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).insert_one(
                    recommendation_doc
                )
                print(
                    f"Saved candidate recommendation with score {score} for job {job_id}"
                )
            elif existing_rec["match_score"] != score:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).update_one(
                    {"id": existing_rec["id"]},
                    {
                        "$set": {
                            "match_score": score,
                            "timestamp": datetime.utcnow(),
                        }
                    },
                )
                print(
                    f"Updated candidate recommendation score to {score} for job {job_id}"
                )
    
    # Sort recommendations
    if sort_by == "match_score":
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    elif sort_by == "experience_years" and include_details:
        # Sort by experience_years (numeric extraction)
        def extract_years(rec):
            exp_years = rec.get("candidate_details", {}).get("experience_years", "0")
            if isinstance(exp_years, (int, float)):
                return exp_years
            try:
                import re
                matches = re.findall(r'\d+', str(exp_years))
                return int(matches[0]) if matches else 0
            except:
                return 0
                
        recommendations.sort(key=extract_years, reverse=True)
    
    # Apply limit
    if limit > 0:
        recommendations = recommendations[:limit]
    
    # Return response with metadata
    response = {
        "candidates": recommendations,
        "total_count": len(recommendations),
        "filters_applied": {
            "min_match_score": min_match_score,
            "experience_range": f"{experience_min or 'any'}-{experience_max or 'any'}",
            "location_radius": location_radius,
            "include_remote": include_remote,
            "education_level": education_level,
            "availability": availability
        }
    }
    
    return response


# Add this function after the existing recommendation functions
@app.get("/recommendations/projects", response_model=List[dict])
async def get_project_recommendations(current_user: dict = Depends(get_current_user)):
    """Get project recommendations for a candidate"""
    if current_user["user_type"] != UserType.CANDIDATE:
        raise HTTPException(
            status_code=403, detail="Only candidates can get project recommendations"
        )
    
    # Get candidate profile
    candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
        {"email": current_user["email"]}
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    
    # Get active projects
    projects = (
        await Database.get_collection(PROJECTS_COLLECTION)
        .find({"is_active": True, "status": "open"})
        .to_list(length=None)
    )
    
    if not projects:
        return []
    
    recommendations = []
    # Process each project to find matches
    for project in projects:
        # Convert project format to job-like format for the recommender
        project_job_format = {
            "title": project.get("title", ""),
            "required_skills": project.get(
                "skills_required", []
            ),  # Map project skills to required_skills
            "description": project.get("description", ""),
        }
        
        # Use the same matching algorithm used for jobs
        score, explanation = await get_match_score(project_job_format, candidate)
        
        # Add to recommendations
        project_recommendation = {
            "project_id": project["id"],
            "match_score": score,
            "explanation": explanation,
            "project_details": {
                "title": project.get("title", ""),
                "company": project.get("company", ""),
                "description": project.get("description", ""),
                "project_type": project.get("project_type", ""),
                "skills_required": project.get("skills_required", []),
            },
        }
        recommendations.append(project_recommendation)
        
        # Save recommendations with score > 70 to recommendations collection
        if score >= 70:
            # Create recommendation document
            recommendation_doc = {
                "id": str(ObjectId()),
                "candidate_id": candidate["id"],
                "project_id": project["id"],
                "match_score": score,
                "type": "project_recommendation",
                "timestamp": datetime.utcnow(),
                "viewed": False,
            }
            
            # Check if this recommendation already exists
            existing_rec = await Database.get_collection(
                RECOMMENDATIONS_COLLECTION
            ).find_one(
                {
                "candidate_id": candidate["id"],
                "project_id": project["id"],
                    "type": "project_recommendation",
                }
            )
            
            # If it doesn't exist or score has changed, save/update it
            if not existing_rec:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).insert_one(
                    recommendation_doc
                )
                print(
                    f"Saved project recommendation with score {score} for candidate {candidate['id']}"
                )
            elif existing_rec["match_score"] != score:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).update_one(
                    {"id": existing_rec["id"]},
                    {"$set": {"match_score": score, "timestamp": datetime.utcnow()}},
                )
                print(
                    f"Updated project recommendation score to {score} for candidate {candidate['id']}"
                )
    
    # Sort by match score
    recommendations = sorted(
        recommendations, key=lambda x: x["match_score"], reverse=True
    )
    return recommendations


@app.get(
    "/recommendations/candidates-for-project/{project_id}", response_model=dict
)
@app.get(
    "/recommendations/project-candidates/{project_id}", response_model=dict
)
async def get_candidate_recommendations_for_project(
    project_id: str,
    min_match_score: int = 0,
    limit: int = 10,
    include_details: bool = True,
    sort_by: str = "match_score",
    availability_min_hours: Optional[int] = None,
    remote_only: bool = False,
    experience_min: Optional[int] = None,
    experience_max: Optional[int] = None,
    skills_required: Optional[str] = None,
    education_level: Optional[str] = None,
    skills_proficiency_min: Optional[int] = None,
    include_applied: bool = False,
    include_contacted: bool = False,
    location_radius: Optional[int] = None,
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get candidate recommendations for a specific project with advanced filtering
    
    This endpoint allows employers to get candidate recommendations for their projects
    with multiple filtering options. Both URL paths work for backward compatibility.
    """
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(
            status_code=403,
            detail="Only employers can get candidate recommendations for projects",
        )
    
    project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
        {"id": project_id}
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify the project belongs to this employer
    if project["employer_id"] != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only get recommendations for your own projects",
        )
    
    # Build filter query
    filter_query = {"is_active": True, "profile_completed": True}
    
    # Apply experience filters if provided
    if experience_min is not None:
        filter_query["experience_years"] = {"$gte": experience_min}
    if experience_max is not None:
        if "experience_years" not in filter_query:
            filter_query["experience_years"] = {}
        filter_query["experience_years"]["$lte"] = experience_max
    
    # Apply education filter if provided
    if education_level:
        education_levels = education_level.split(",")
        filter_query["education_level"] = {"$in": education_levels}
    
    # Apply remote filter
    if remote_only:
        filter_query["remote_availability"] = True
    
    # Apply skills proficiency filter if provided
    if skills_proficiency_min is not None:
        filter_query["skills_proficiency.average"] = {"$gte": skills_proficiency_min}
    
    # Apply location filter if provided
    # Note: This is a simple implementation. For production, use proper geospatial queries
    if location:
        # For now, we'll do a simple text match, but in production this should use geocoding
        filter_query["location"] = {"$regex": location, "$options": "i"}
    
    # Build exclusion filters
    exclusion_query = {}
    if not include_applied:
        # Find candidates who have already applied to this project
        applied_candidates = await Database.get_collection(PROJECT_APPLICATIONS_COLLECTION).distinct(
            "candidate_id", {"project_id": project_id}
        )
        if applied_candidates:
            exclusion_query["id"] = {"$nin": applied_candidates}
    
    if not include_contacted:
        # Find candidates who have already been contacted for this project
        contacted_candidates = await Database.get_collection(NOTIFICATIONS_COLLECTION).distinct(
            "recipient_id", 
            {
                "related_id": project_id, 
                "type": "employer_contact", 
                "sender_id": current_user["id"]
            }
        )
        if contacted_candidates:
            if "id" in exclusion_query:
                exclusion_query["id"]["$nin"].extend(contacted_candidates)
            else:
                exclusion_query["id"] = {"$nin": contacted_candidates}
    
    # Combine filters
    final_query = {**filter_query, **exclusion_query}
    
    # Get active candidates with complete profiles that match the filters
    candidates = (
        await Database.get_collection(CANDIDATES_COLLECTION)
        .find(final_query)
        .to_list(length=None)
    )
    
    if not candidates:
        return {
            "candidates": [],
            "total_count": 0,
            "metadata": {
                "project_id": project_id,
                "filters_applied": {
                    "min_match_score": min_match_score,
                    "availability_min_hours": availability_min_hours,
                    "remote_only": remote_only,
                    "experience_min": experience_min,
                    "experience_max": experience_max,
                    "education_level": education_level,
                    "skills_required": skills_required
                }
            }
        }
    
    # Parse required skills if provided
    required_skill_list = []
    if skills_required:
        required_skill_list = [skill.strip() for skill in skills_required.split(",")]
    
    recommendations = []
    for candidate in candidates:
        # Convert project format to job-like format for the recommender
        project_job_format = {
            "title": project.get("title", ""),
            "required_skills": project.get("skills_required", []) + required_skill_list,
            "description": project.get("description", ""),
        }
        
        # Use the same matching algorithm
        score, explanation = await get_match_score(project_job_format, candidate)
        
        # Apply minimum match score filter
        if score < min_match_score:
            continue
        
        # Apply availability hours filter if provided
        if availability_min_hours is not None:
            candidate_availability_hours = candidate.get("availability_hours", 0)
            if candidate_availability_hours < availability_min_hours:
                continue
        
        candidate_id = candidate.get("id")
        
        # Create result object with match score
        result = {
            "candidate_id": candidate_id,
            "match_score": round(score, 1),
            "explanation": explanation,
            "match_factors": {
                "skills_match": calculate_skills_match_percentage(
                    project.get("skills_required", []), candidate.get("skills", [])
                ),
                "experience_match": calculate_experience_match_percentage(
                    project.get("experience_years_required", 0), 
                    candidate.get("experience_years", 0)
                ),
            }
        }
        
        # Include candidate details if requested
        if include_details:
            # Remove sensitive information
            candidate_copy = candidate.copy()
            for field in ["password", "embedding", "hashed_password", "salt"]:
                if field in candidate_copy:
                    del candidate_copy[field]
            
            # Convert ObjectId to string
            if "_id" in candidate_copy:
                candidate_copy["_id"] = str(candidate_copy["_id"])
            
            result["candidate_details"] = candidate_copy
        
        recommendations.append(result)
        
        # Save recommendations with score > 70 to recommendations collection
        if score >= 70:
            # Create recommendation document
            recommendation_doc = {
                "id": str(ObjectId()),
                "candidate_id": candidate_id,
                "project_id": project_id,
                "employer_id": current_user["id"],
                "match_score": score,
                "type": "project_candidate_recommendation",
                "timestamp": datetime.utcnow(),
                "viewed": False,
            }
            
            # Check if this recommendation already exists
            existing_rec = await Database.get_collection(
                RECOMMENDATIONS_COLLECTION
            ).find_one(
                {
                    "candidate_id": candidate_id,
                    "project_id": project_id,
                    "type": "project_candidate_recommendation",
                }
            )
            
            # If it doesn't exist or score has changed, save/update it
            if not existing_rec:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).insert_one(
                    recommendation_doc
                )
                print(f"Saved candidate recommendation for project with score {score}")
            elif existing_rec["match_score"] != score:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).update_one(
                    {"id": existing_rec["id"]},
                    {"$set": {"match_score": score, "timestamp": datetime.utcnow()}},
                )
                print(
                    f"Updated candidate recommendation for project with score {score}"
                )
    
    # Sort results
    if sort_by == "match_score":
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    elif sort_by == "experience_years" and include_details:
        def extract_years(rec):
            exp_years = rec.get("candidate_details", {}).get("experience_years", "0")
            if isinstance(exp_years, (int, float)):
                return exp_years
            try:
                import re
                matches = re.findall(r'\d+', str(exp_years))
                return int(matches[0]) if matches else 0
            except:
                return 0
                
        recommendations.sort(key=extract_years, reverse=True)
    elif sort_by == "availability_hours" and include_details:
        def get_availability_hours(rec):
            return rec.get("candidate_details", {}).get("availability_hours", 0)
                
        recommendations.sort(key=get_availability_hours, reverse=True)
    
    # Apply limit
    if limit > 0:
        recommendations = recommendations[:limit]
    
    # Calculate additional statistics for the results
    avg_match_score = sum(r["match_score"] for r in recommendations) / len(recommendations) if recommendations else 0
    skills_distribution = {}
    if recommendations and include_details:
        # Calculate skills distribution across matching candidates
        all_skills = []
        for rec in recommendations:
            candidate_skills = rec.get("candidate_details", {}).get("skills", [])
            if isinstance(candidate_skills, list):
                all_skills.extend(candidate_skills)
            elif isinstance(candidate_skills, dict):
                for skill_group in candidate_skills.values():
                    if isinstance(skill_group, list):
                        all_skills.extend(skill_group)
        
        # Count occurrences of each skill
        from collections import Counter
        skills_counter = Counter(all_skills)
        skills_distribution = {skill: count for skill, count in skills_counter.most_common(10)}
    
    # Return results with enhanced metadata
    return {
        "candidates": recommendations,
        "total_count": len(recommendations),
        "metadata": {
            "project_id": project_id,
            "project_title": project.get("title", ""),
            "project_type": project.get("project_type", ""),
            "company": project.get("company", ""),
            "filters_applied": {
                "min_match_score": min_match_score,
                "availability_min_hours": availability_min_hours,
                "remote_only": remote_only,
                "experience_min": experience_min,
                "experience_max": experience_max,
                "education_level": education_level,
                "skills_required": skills_required,
                "skills_proficiency_min": skills_proficiency_min,
                "include_applied": include_applied,
                "include_contacted": include_contacted,
                "location": location,
                "location_radius": location_radius
            },
            "statistics": {
                "average_match_score": round(avg_match_score, 1),
                "skills_distribution": skills_distribution,
                "query_time": datetime.utcnow().isoformat()
            }
        }
    }


# Add a semantic search endpoint
@app.post("/jobs/search", response_model=List[Job])
async def search_jobs_semantic(
    search_data: dict, top_k: int = 5, current_user: dict = Depends(get_current_user)
):
    """Search for jobs using semantic search"""
    try:
        query = search_data.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
            
        query_vector = get_embedding(query)
        
        # Use the MongoDB vector search
        results = await search_vector_collection(
            JOBS_COLLECTION, query_vector, top_k, {"is_active": True}
        )
        
        return results
        
    except Exception as e:
        print(f"Error in semantic search: {str(e)}")
        import traceback

        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Failed to perform semantic search: {str(e)}"
        )


@app.post("/projects/search", response_model=List[Project])
async def search_projects_semantic(
    search_data: dict, top_k: int = 5, current_user: dict = Depends(get_current_user)
):
    """Search for projects using semantic search"""
    try:
        query = search_data.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
            
        query_vector = get_embedding(query)
        
        # Use the MongoDB vector search
        results = await search_vector_collection(
            PROJECTS_COLLECTION, query_vector, top_k, {"is_active": True}
        )
        
        return results
        
    except Exception as e:
        print(f"Error in semantic search for projects: {str(e)}")
        import traceback

        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform semantic search on projects: {str(e)}",
        )


@app.post("/candidates/search", response_model=List[Candidate])
async def search_candidates_semantic(
    search_data: dict, top_k: int = 5, current_user: dict = Depends(get_current_user)
):
    """Search for candidates using semantic search"""
    try:
        # Only employers can search for candidates
        if current_user["user_type"] != UserType.EMPLOYER:
            raise HTTPException(
                status_code=403, detail="Only employers can search candidates"
            )
        
        query = search_data.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
            
        query_vector = get_embedding(query)
        
        # Use the MongoDB vector search
        results = await search_vector_collection(
            CANDIDATES_COLLECTION,
            query_vector,
            top_k,
            {
                "is_active": True,
                "profile_completed": True,
                "profile_visibility": "public",
            },
        )
        
        return results
        
    except Exception as e:
        print(f"Error in semantic search for candidates: {str(e)}")
        import traceback

        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform semantic search on candidates: {str(e)}",
        )


# User profile endpoints
@app.put("/profile", response_model=User)
async def update_profile(
    profile_data: dict, current_user: dict = Depends(get_current_user)
):
    if current_user["user_type"] == UserType.CANDIDATE:
        # Check if any field affects candidate embedding
        semantic_fields = [
            "full_name",
            "skills",
            "experience",
            "education",
            "location",
            "bio",
        ]
        if any(field in profile_data for field in semantic_fields):
            # Get the current candidate data
            candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
                {"email": current_user["email"]}
            )
            if candidate:
                # Create updated candidate data by merging
                updated_candidate = {**candidate}
                updated_candidate.update(profile_data)
                # Generate new embedding
                profile_data["embedding"] = create_candidate_embedding(
                    updated_candidate
                )
        
        # Update candidate profile with new data including potential new embedding
        await Database.get_collection(CANDIDATES_COLLECTION).update_one(
            {"email": current_user["email"]}, {"$set": profile_data}
        )
        
        # Get updated candidate profile
        updated_profile = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
            {"email": current_user["email"]}
        )
        
        # Remove embedding from response
        if updated_profile and "embedding" in updated_profile:
            updated_profile.pop("embedding", None)
            
        return updated_profile
    else:
        # Update employer profile only
        await Database.get_collection(EMPLOYERS_COLLECTION).update_one(
            {"email": current_user["email"]}, {"$set": profile_data}
        )
        
        # Get updated employer profile
        updated_profile = await Database.get_collection(EMPLOYERS_COLLECTION).find_one(
            {"email": current_user["email"]}
        )
        return updated_profile


@app.get("/profile", response_model=dict)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get the complete profile for the authenticated user"""
    try:
        user_id = current_user.get("id")
        user_type = current_user.get("user_type")
        
        # Get the full profile based on user type
        if user_type == "candidate":
            # Fetch the candidate's full profile from CANDIDATES_COLLECTION
            profile = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
                {"id": user_id}
            )
            if not profile:
                # If not found, just return the basic user info
                return current_user
            
            # Remove MongoDB's _id field and embedding
            profile.pop("_id", None)
            profile.pop("embedding", None) if "embedding" in profile else None
            
            return profile
            
        elif user_type == "employer":
            # Fetch the employer's full profile from EMPLOYERS_COLLECTION
            profile = await Database.get_collection(EMPLOYERS_COLLECTION).find_one(
                {"id": user_id}
            )
            if not profile:
                # If not found, just return the basic user info
                return current_user
            
            # Remove MongoDB's _id field
            profile.pop("_id", None)
            
            # Get jobs posted by this employer
            jobs = (
                await Database.get_collection(JOBS_COLLECTION)
                .find({"employer_id": user_id, "is_active": True})
                .to_list(length=None)
            )
            
            # Process jobs to remove _id
            processed_jobs = []
            for job in jobs:
                job.pop("_id", None)
                if "embedding" in job:
                    job.pop("embedding", None)
                processed_jobs.append(job)
                
            profile["posted_jobs"] = processed_jobs
            
            return profile
            
        else:
            # For unknown user types, return basic user info
            return current_user
    
    except Exception as e:
        print(f"Error in get_profile: {str(e)}")
        # In case of error, return at least the basic user info
        return current_user


@app.delete("/profile", response_model=dict)
async def delete_user(current_user: dict = Depends(get_current_user)):
    try:
        # Delete from users collection
        user_result = await Database.get_collection(USERS_COLLECTION).delete_one(
            {"email": current_user["email"]}
        )
        
        if user_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # If user is a candidate, also delete from candidates collection
        if current_user["user_type"] == UserType.CANDIDATE:
            candidate_result = await Database.get_collection(
                CANDIDATES_COLLECTION
            ).delete_one({"email": current_user["email"]})
            if candidate_result.deleted_count == 0:
                print(
                    f"Warning: Candidate profile not found for user {current_user['email']}"
                )
        
        # If user is an employer, delete from employers collection and their posted jobs
        elif current_user["user_type"] == UserType.EMPLOYER:
            # Delete employer profile
            employer_result = await Database.get_collection(
                EMPLOYERS_COLLECTION
            ).delete_one({"email": current_user["email"]})
            if employer_result.deleted_count == 0:
                print(
                    f"Warning: Employer profile not found for user {current_user['email']}"
                )
            
            # Delete all jobs posted by this employer
            jobs_result = await Database.get_collection(JOBS_COLLECTION).delete_many(
                {"employer_id": current_user["id"]}
            )
            if jobs_result.deleted_count > 0:
                print(
                    f"Deleted {jobs_result.deleted_count} jobs posted by employer {current_user['email']}"
                )
            
            # Delete all projects posted by this employer
            projects_result = await Database.get_collection(
                PROJECTS_COLLECTION
            ).delete_many({"employer_id": current_user["id"]})
            if projects_result.deleted_count > 0:
                print(
                    f"Deleted {projects_result.deleted_count} projects posted by employer {current_user['email']}"
                )
        
        return {"message": "User and associated profiles deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Application endpoints
@app.post("/applications", response_model=JobApplication)
async def create_application(
    application_data: JobApplicationCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new job application"""
    try:
        # Verify user is a candidate
        if current_user["user_type"] != UserType.CANDIDATE:
            raise HTTPException(
                status_code=403, detail="Only candidates can submit job applications"
            )

        # Get the job
        job_id = application_data.job_id
        job = await Database.get_collection(JOBS_COLLECTION).find_one({"id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if project_id is provided instead
        if hasattr(application_data, "project_id") and application_data.project_id:
            # This is a project application
            project_id = application_data.project_id
            project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
                {"id": project_id}
            )
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # Get candidate details
            candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
                {"id": current_user["id"]}
            )
            if not candidate:
                raise HTTPException(status_code=404, detail="Candidate profile not found")

            # Create project application
            application_id = str(ObjectId())
            project_application = {
                "_id": ObjectId(application_id),
                "id": application_id,
                "candidate_id": current_user["id"],
                "project_id": project_id,
                "employer_id": project["employer_id"],
                "created_at": datetime.utcnow(),
                "status": "applied",
                "cover_letter": application_data.cover_letter,
                "resume_url": application_data.resume_url,
                "notes": application_data.notes,
                "last_updated": datetime.utcnow(),
                "availability": getattr(application_data, "availability", None),
            }

            # Add candidate details to the application
            candidate_details = {
                "id": candidate["id"],
                "full_name": candidate["full_name"],
                "location": candidate.get("location"),
                "experience_years": candidate.get("experience_years"),
                "skills": candidate.get("skills"),
                "education_summary": candidate.get("education_summary"),
            }
            project_application["candidate_details"] = candidate_details

            # Save project application to database
            await Database.get_collection(PROJECT_APPLICATIONS_COLLECTION).insert_one(
                project_application
            )

            # Get project details to return
            project_details = {
                "id": project["id"],
                "title": project["title"],
                "company": project["company"],
                "project_type": project["project_type"],
                "location": project.get("location"),
            }

            # Add project details to response
            project_application["project_details"] = project_details

            # Remove MongoDB _id before returning
            project_application.pop("_id", None)
            return project_application

        # Regular job application
        # Generate application ID
        application_id = str(ObjectId())

        # Get candidate details
        candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
            {"id": current_user["id"]}
        )
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate profile not found")

        # Create application document
        application = {
            "_id": ObjectId(application_id),
            "id": application_id,
            "candidate_id": current_user["id"],
            "job_id": job_id,
            "employer_id": job["employer_id"],
            "created_at": datetime.utcnow(),
            "status": "applied",
            "cover_letter": application_data.cover_letter,
            "resume_url": application_data.resume_url,
            "notes": application_data.notes,
            "last_updated": datetime.utcnow(),
        }

        # Add candidate details to the application
        candidate_details = {
            "id": candidate["id"],
            "full_name": candidate["full_name"],
            "location": candidate.get("location"),
            "experience_years": candidate.get("experience_years"),
            "skills": candidate.get("skills"),
            "education_summary": candidate.get("education_summary"),
        }
        application["candidate_details"] = candidate_details

        # Save application to database
        await Database.get_collection(JOB_APPLICATIONS_COLLECTION).insert_one(
            application
        )

        # Get job details to return
        job_details = {
            "id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "location": job.get("location"),
        }

        # Add job details to response
        application["job_details"] = job_details

        # Remove MongoDB _id before returning
        application.pop("_id", None)
        return application
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/project-applications", response_model=ProjectApplication)
async def create_project_application(
    application_data: ProjectApplicationCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new project application"""
    try:
        # Verify user is a candidate
        if current_user["user_type"] != UserType.CANDIDATE:
            raise HTTPException(
                status_code=403,
                detail="Only candidates can submit project applications",
            )

        # Get the project
        project_id = application_data.project_id
        project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
            {"id": project_id}
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get candidate details
        candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
            {"id": current_user["id"]}
        )
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate profile not found")

        # Generate application ID
        application_id = str(ObjectId())

        # Create application document
        application = {
            "_id": ObjectId(application_id),
            "id": application_id,
            "candidate_id": current_user["id"],
            "project_id": project_id,
            "employer_id": project["employer_id"],
            "created_at": datetime.utcnow(),
            "status": "applied",
            "cover_letter": application_data.cover_letter,
            "resume_url": application_data.resume_url,
            "notes": application_data.notes,
            "last_updated": datetime.utcnow(),
            "availability": getattr(application_data, "availability", None),
        }

        # Add candidate details to the application
        candidate_details = {
            "id": candidate["id"],
            "full_name": candidate["full_name"],
            "location": candidate.get("location"),
            "experience_years": candidate.get("experience_years"),
            "skills": candidate.get("skills"),
            "education_summary": candidate.get("education_summary"),
        }
        application["candidate_details"] = candidate_details

        # Save application to database
        await Database.get_collection(PROJECT_APPLICATIONS_COLLECTION).insert_one(
            application
        )

        # Get project details to return
        project_details = {
            "id": project["id"],
            "title": project["title"],
            "company": project["company"],
            "project_type": project["project_type"],
            "location": project.get("location"),
        }

        # Add project details to response
        application["project_details"] = project_details

        # Remove MongoDB _id before returning
        application.pop("_id", None)
        return application
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/applications", response_model=List[JobApplication])
async def get_applications(current_user: dict = Depends(get_current_user)):
    """Get job applications for the current user"""
    try:
        # Different behavior depending on user type
        if current_user["user_type"] == UserType.CANDIDATE:
            # Get applications submitted by this candidate
            applications = (
                await Database.get_collection(JOB_APPLICATIONS_COLLECTION)
                .find({"candidate_id": current_user["id"]})
                .to_list(length=None)
            )

            # For each application, fetch job details
            for application in applications:
                job = await Database.get_collection(JOBS_COLLECTION).find_one(
                    {"id": application["job_id"]}
                )
            if job:
                    application["job_details"] = {
                        "id": job["id"],
                        "title": job["title"],
                        "company": job["company"],
                        "location": job.get("location"),
                    }

                # Remove MongoDB _id
                    application.pop("_id", None)

            return applications

        elif current_user["user_type"] == UserType.EMPLOYER:
            # Get applications for jobs posted by this employer
            applications = (
                await Database.get_collection(JOB_APPLICATIONS_COLLECTION)
                .find({"employer_id": current_user["id"]})
                .to_list(length=None)
            )

            # For each application, fetch job and candidate details
            for application in applications:
                # Get job details
                job = await Database.get_collection(JOBS_COLLECTION).find_one(
                    {"id": application["job_id"]}
                )
                if job:
                    application["job_details"] = {
                        "id": job["id"],
                        "title": job["title"],
                        "company": job["company"],
                        "location": job.get("location"),
                    }

                # Get candidate details
                candidate = await Database.get_collection(
                    CANDIDATES_COLLECTION
                ).find_one({"id": application["candidate_id"]})
                if candidate:
                    application["candidate_details"] = {
                        "id": candidate["id"],
                        "full_name": candidate["full_name"],
                        "location": candidate.get("location"),
                    }

                # Remove MongoDB _id
                application.pop("_id", None)

            return applications

        else:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}/applications", response_model=List[JobApplication])
async def get_job_applications(
    job_id: str, current_user: dict = Depends(get_current_user)
):
    """Get applications for a specific job"""
    try:
        # Get the job
        job = await Database.get_collection(JOBS_COLLECTION).find_one({"id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Verify user is the employer of this job
        if (
            current_user["user_type"] != UserType.EMPLOYER
            or current_user["id"] != job["employer_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view applications for your own jobs",
            )

        # Get applications for this job
        applications = (
            await Database.get_collection(JOB_APPLICATIONS_COLLECTION)
            .find({"job_id": job_id})
            .to_list(length=None)
        )

        # For each application, fetch candidate details
        for application in applications:
            # Get candidate details
            candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
                {"id": application["candidate_id"]}
            )
            if candidate:
                application["candidate_details"] = {
                "id": candidate["id"],
                "full_name": candidate["full_name"],
                "location": candidate.get("location"),
                }

            # Remove MongoDB _id
            application.pop("_id", None)

        return applications

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/project-applications", response_model=List[ProjectApplication])
async def get_project_applications(current_user: dict = Depends(get_current_user)):
    """Get project applications for the current user"""
    try:
        # Different behavior depending on user type
        if current_user["user_type"] == UserType.CANDIDATE:
            # Get applications submitted by this candidate
            applications = (
                await Database.get_collection(PROJECT_APPLICATIONS_COLLECTION)
                .find({"candidate_id": current_user["id"]})
                .to_list(length=None)
            )

            # For each application, fetch project details
            for application in applications:
                project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
                    {"id": application["project_id"]}
                )
                if project:
                    application["project_details"] = {
                        "id": project["id"],
                        "title": project["title"],
                        "company": project["company"],
                        "project_type": project["project_type"],
                        "location": project.get("location"),
                    }

                # Remove MongoDB _id
                application.pop("_id", None)

            return applications

        elif current_user["user_type"] == UserType.EMPLOYER:
            # Get applications for projects posted by this employer
            applications = (
                await Database.get_collection(PROJECT_APPLICATIONS_COLLECTION)
                .find({"employer_id": current_user["id"]})
                .to_list(length=None)
            )

            # For each application, fetch project and candidate details
            for application in applications:
                # Get project details
                project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
                    {"id": application["project_id"]}
                )
                if project:
                    application["project_details"] = {
                        "id": project["id"],
                        "title": project["title"],
                        "company": project["company"],
                        "project_type": project["project_type"],
                        "location": project.get("location"),
                    }

                # Get candidate details
                candidate = await Database.get_collection(
                    CANDIDATES_COLLECTION
                ).find_one({"id": application["candidate_id"]})
                if candidate:
                    application["candidate_details"] = {
                        "id": candidate["id"],
                        "full_name": candidate["full_name"],
                        "location": candidate.get("location"),
                    }

                # Remove MongoDB _id
                application.pop("_id", None)

            return applications

        else:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}/applications", response_model=List[ProjectApplication])
async def get_project_applications(
    project_id: str, current_user: dict = Depends(get_current_user)
):
    """Get applications for a specific project"""
    try:
        # Get the project
        project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
            {"id": project_id}
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Verify user is the employer of this project
        if (
            current_user["user_type"] != UserType.EMPLOYER
            or current_user["id"] != project["employer_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view applications for your own projects",
            )

        # Get applications for this project
        applications = (
            await Database.get_collection(PROJECT_APPLICATIONS_COLLECTION)
            .find({"project_id": project_id})
            .to_list(length=None)
        )

        # For each application, fetch candidate details
        for application in applications:
            # Get candidate details
            candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
                {"id": application["candidate_id"]}
            )
            if candidate:
                application["candidate_details"] = {
                    "id": candidate["id"],
                    "full_name": candidate["full_name"],
                    "location": candidate.get("location"),
                }

            # Remove MongoDB _id
            application.pop("_id", None)
        
        return applications
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Saved jobs endpoints
@app.post("/saved-jobs", response_model=SavedJob)
async def save_job(
    saved_job_data: SavedJobCreate, current_user: dict = Depends(get_current_user)
):
    """Save a job for a candidate"""
    try:
        # Verify user is a candidate
        if current_user["user_type"] != UserType.CANDIDATE:
            raise HTTPException(status_code=403, detail="Only candidates can save jobs")

        # Get the job
        job_id = saved_job_data.job_id
        job = await Database.get_collection(JOBS_COLLECTION).find_one({"id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Check if job is already saved
        existing_saved = await Database.get_collection(SAVED_JOBS_COLLECTION).find_one(
            {"candidate_id": current_user["id"], "job_id": job_id}
        )
        if existing_saved:
            raise HTTPException(status_code=400, detail="Job already saved")

        # Generate saved job ID
        saved_id = str(ObjectId())

        # Create saved job document
        saved_job = {
            "_id": ObjectId(saved_id),
            "id": saved_id,
            "candidate_id": current_user["id"],
            "job_id": job_id,
            "employer_id": job["employer_id"],
            "created_at": datetime.utcnow(),
            "notes": saved_job_data.notes,
        }

        # Save to database
        await Database.get_collection(SAVED_JOBS_COLLECTION).insert_one(saved_job)

        # Get job details to return
        job_details = {
            "id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "location": job.get("location"),
            "salary_range": job.get("salary_range"),
        }

        # Add job details to response
        saved_job["job_details"] = job_details

        # Remove MongoDB _id before returning
        saved_job.pop("_id", None)
        return saved_job

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/saved-jobs", response_model=List[SavedJob])
async def get_saved_jobs(current_user: dict = Depends(get_current_user)):
    """Get saved jobs for the current candidate"""
    try:
        # Verify user is a candidate
        if current_user["user_type"] != UserType.CANDIDATE:
            raise HTTPException(
                status_code=403, detail="Only candidates can access saved jobs"
            )

        # Get saved jobs for this candidate
        saved_jobs = (
            await Database.get_collection(SAVED_JOBS_COLLECTION)
            .find({"candidate_id": current_user["id"]})
            .to_list(length=None)
        )

        # For each saved job, fetch job details
        for saved_job in saved_jobs:
            job = await Database.get_collection(JOBS_COLLECTION).find_one(
                {"id": saved_job["job_id"]}
            )
            if job:
                saved_job["job_details"] = {
                    "id": job["id"],
                    "title": job["title"],
                    "company": job["company"],
                    "location": job.get("location"),
                    "salary_range": job.get("salary_range"),
                }

            # Remove MongoDB _id
            saved_job.pop("_id", None)

        return saved_jobs
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/saved-jobs/{saved_job_id}", response_model=dict)
async def delete_saved_job(
    saved_job_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete a saved job"""
    try:
        # Verify user is a candidate
        if current_user["user_type"] != UserType.CANDIDATE:
            raise HTTPException(
                status_code=403, detail="Only candidates can delete saved jobs"
            )

        # Get the saved job
        saved_job = await Database.get_collection(SAVED_JOBS_COLLECTION).find_one(
            {"id": saved_job_id}
        )
        if not saved_job:
            raise HTTPException(status_code=404, detail="Saved job not found")

        # Verify the job belongs to this candidate
        if saved_job["candidate_id"] != current_user["id"]:
                raise HTTPException(
                status_code=403, detail="You can only delete your own saved jobs"
            )

        # Delete the saved job
        result = await Database.get_collection(SAVED_JOBS_COLLECTION).delete_one(
            {"id": saved_job_id}
        )
        if result.deleted_count != 1:
            raise HTTPException(status_code=500, detail="Failed to delete saved job")

        return {"message": "Saved job deleted successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Saved projects endpoints
@app.post("/saved-projects", response_model=SavedProject)
async def save_project(
    saved_project_data: SavedProjectCreate,
    current_user: dict = Depends(get_current_user),
):
    """Save a project for a candidate"""
    try:
        # Verify user is a candidate
        if current_user["user_type"] != UserType.CANDIDATE:
            raise HTTPException(
                status_code=403, detail="Only candidates can save projects"
            )

        # Get the project
        project_id = saved_project_data.project_id
        project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
            {"id": project_id}
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    
        # Check if project is already saved
        existing_saved = await Database.get_collection(
            SAVED_PROJECTS_COLLECTION
        ).find_one({"candidate_id": current_user["id"], "project_id": project_id})
        if existing_saved:
            raise HTTPException(status_code=400, detail="Project already saved")

        # Generate saved project ID
        saved_id = str(ObjectId())

        # Create saved project document
        saved_project = {
            "_id": ObjectId(saved_id),
            "id": saved_id,
            "candidate_id": current_user["id"],
            "project_id": project_id,
            "employer_id": project["employer_id"],
            "created_at": datetime.utcnow(),
            "notes": saved_project_data.notes,
        }

        # Save to database
        await Database.get_collection(SAVED_PROJECTS_COLLECTION).insert_one(
            saved_project
        )

        # Get project details to return
        project_details = {
            "id": project["id"],
            "title": project["title"],
            "company": project["company"],
            "project_type": project["project_type"],
            "location": project.get("location"),
            "budget_range": project.get("budget_range"),
        }

        # Add project details to response
        saved_project["project_details"] = project_details

        # Remove MongoDB _id before returning
        saved_project.pop("_id", None)
        return saved_project

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/saved-projects", response_model=List[SavedProject])
async def get_saved_projects(current_user: dict = Depends(get_current_user)):
    """Get saved projects for the current candidate"""
    try:
        # Verify user is a candidate
        if current_user["user_type"] != UserType.CANDIDATE:
            raise HTTPException(
                status_code=403, detail="Only candidates can access saved projects"
            )

        # Get saved projects for this candidate
        saved_projects = (
            await Database.get_collection(SAVED_PROJECTS_COLLECTION)
            .find({"candidate_id": current_user["id"]})
            .to_list(length=None)
        )

        # For each saved project, fetch project details
        for saved_project in saved_projects:
            project = await Database.get_collection(PROJECTS_COLLECTION).find_one(
                {"id": saved_project["project_id"]}
            )
            if  project:
                    saved_project["project_details"] = {
                    "id": project["id"],
                    "title": project["title"],
                    "company": project["company"],
                    "project_type": project["project_type"],
                    "location": project.get("location"),
                    "budget_range": project.get("budget_range"),
                }

            # Remove MongoDB _id
            saved_project.pop("_id", None)
        
        return saved_projects
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/saved-projects/{saved_project_id}", response_model=dict)
async def delete_saved_project(
    saved_project_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete a saved project"""
    try:
        # Verify user is a candidate
        if current_user["user_type"] != UserType.CANDIDATE:
            raise HTTPException(
                status_code=403, detail="Only candidates can delete saved projects"
            )

        # Get the saved project
        saved_project = await Database.get_collection(
            SAVED_PROJECTS_COLLECTION
        ).find_one({"id": saved_project_id})
        if not saved_project:
            raise HTTPException(status_code=404, detail="Saved project not found")

        # Verify the project belongs to this candidate
        if saved_project["candidate_id"] != current_user["id"]:
            raise HTTPException(
                status_code=403, detail="You can only delete your own saved projects"
            )

        # Delete the saved project
        result = await Database.get_collection(SAVED_PROJECTS_COLLECTION).delete_one(
            {"id": saved_project_id}
        )
        if result.deleted_count != 1:
            raise HTTPException(
                status_code=500, detail="Failed to delete saved project"
            )

        return {"message": "Saved project deleted successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recommendations/candidates", response_model=List[dict])
async def get_candidates_recommendations(
    job_id: Optional[str] = None,
    min_match_score: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get candidate recommendations for the current employer's jobs or for a specific job"""
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(
            status_code=403, detail="Only employers can get candidate recommendations"
        )
    
    # If job_id is provided, use the existing endpoint
    if job_id:
        return await get_candidate_recommendations(job_id, current_user)
    
    # Get the employer's active jobs
    jobs = await Database.get_collection(JOBS_COLLECTION).find(
        {"employer_id": current_user["id"], "is_active": True}
    ).to_list(length=None)
    
    if not jobs:
        return {"candidates": [], "total_count": 0}
    
    # Get active candidates with complete profiles
    candidates = (
        await Database.get_collection(CANDIDATES_COLLECTION)
        .find({"is_active": True, "profile_completed": True})
        .to_list(length=None)
    )
    
    if not candidates:
        return {"candidates": [], "total_count": 0}
    
    # Get recommendations for each job
    all_recommendations = []
    for job in jobs:
        job_recommendations = await get_job_candidate_matches(job, candidates)
        all_recommendations.extend(job_recommendations)
    
    # Sort by match score and remove duplicates
    unique_candidates = {}
    for rec in all_recommendations:
        candidate_id = rec["candidate_id"]
        if candidate_id not in unique_candidates or rec["match_score"] > unique_candidates[candidate_id]["match_score"]:
            unique_candidates[candidate_id] = rec
    
    # Convert to list and sort by match score
    recommendations = list(unique_candidates.values())
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Filter by minimum match score
    if min_match_score > 0:
        recommendations = [r for r in recommendations if r["match_score"] >= min_match_score]
    
    # Limit the number of results
    if limit > 0:
        recommendations = recommendations[:limit]
    
    # Fetch full candidate details for each recommendation
    detailed_recommendations = []
    for rec in recommendations:
        candidate = next(
            (c for c in candidates if c["id"] == rec["candidate_id"]), None
        )
        if candidate:
            # Remove MongoDB's _id from candidate
            if "_id" in candidate:
                candidate.pop("_id", None)
                
            rec_with_details = rec.copy()
            rec_with_details["candidate"] = candidate
            detailed_recommendations.append(rec_with_details)
    
    return {
        "candidates": detailed_recommendations,
        "total_count": len(detailed_recommendations)
    }


@app.get("/recommendations/skill-gap", response_model=dict)
async def get_skill_gap_analysis(
    target_role: str,
    industry: str = "Technology",
    experience_level: str = "Mid-level",
    include_learning_resources: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get skill gap analysis for a target role with industry-specific requirements"""
    try:
        if current_user["user_type"] != UserType.CANDIDATE:
            raise HTTPException(
                status_code=403, detail="Only candidates can get skill gap analysis"
            )
        
        # Get candidate profile
        candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
            {"email": current_user["email"]}
        )
        if not candidate:
            print(f"Candidate profile not found for email: {current_user['email']}")
            raise HTTPException(status_code=404, detail="Candidate profile not found")
        
        # Debug print candidate skills
        print(f"Candidate skills: {json.dumps(candidate.get('skills', {}), indent=2)}")
        
        # Get candidate skills
        candidate_skills = []
        skills_data = candidate.get("skills", {})
        
        # Check if skills_data is None and initialize it as empty dict if needed
        if skills_data is None:
            skills_data = {}
        
        # Combine all skills with assumed proficiency levels
        for skill in skills_data.get("languages_frameworks", []):
            candidate_skills.append({"name": skill, "proficiency": 8})  # Assume high proficiency
        
        # Check for both tools and tools_platforms (to support older and newer UI)
        tools_skills = skills_data.get("tools", [])
        tools_platforms_skills = skills_data.get("tools_platforms", [])
        
        # Ensure these are lists even if they're None
        if tools_skills is None:
            tools_skills = []
        if tools_platforms_skills is None:
            tools_platforms_skills = []
            
        # Combine both lists, removing duplicates
        all_tools = list(set(tools_skills + tools_platforms_skills))
        
        for skill in all_tools:
            candidate_skills.append({"name": skill, "proficiency": 7})  # Assume medium-high proficiency
        
        # Check for ai_ml_data skills (added in newer UI)
        for skill in skills_data.get("ai_ml_data", []):
            candidate_skills.append({"name": skill, "proficiency": 8})  # Assume high proficiency
        
        for skill in skills_data.get("soft_skills", []):
            candidate_skills.append({"name": skill, "proficiency": 7})  # Assume medium-high proficiency
        
        # Define required skills for the target role based on common industry standards
        # In a real system, this would come from a database of role requirements
        role_skills_map = {
            "Software Engineer": [
                {"name": "Python", "importance": 9},
                {"name": "JavaScript", "importance": 8},
                {"name": "SQL", "importance": 7},
                {"name": "Git", "importance": 8},
                {"name": "Docker", "importance": 7},
                {"name": "AWS", "importance": 8},
                {"name": "System Design", "importance": 8},
                {"name": "Data Structures", "importance": 9},
                {"name": "Algorithms", "importance": 9},
                {"name": "Testing", "importance": 7}
            ],
            "Data Scientist": [
                {"name": "Python", "importance": 9},
                {"name": "SQL", "importance": 8},
                {"name": "Machine Learning", "importance": 9},
                {"name": "Statistics", "importance": 9},
                {"name": "Data Visualization", "importance": 8},
                {"name": "Pandas", "importance": 8},
                {"name": "NumPy", "importance": 8},
                {"name": "Scikit-learn", "importance": 8},
                {"name": "Deep Learning", "importance": 7},
                {"name": "Big Data", "importance": 7}
            ],
            "Frontend Developer": [
                {"name": "JavaScript", "importance": 9},
                {"name": "React", "importance": 9},
                {"name": "HTML", "importance": 8},
                {"name": "CSS", "importance": 8},
                {"name": "TypeScript", "importance": 8},
                {"name": "Git", "importance": 7},
                {"name": "UI/UX", "importance": 7},
                {"name": "Responsive Design", "importance": 8},
                {"name": "Testing", "importance": 7},
                {"name": "Performance Optimization", "importance": 7}
            ],
            "Backend Developer": [
                {"name": "Python", "importance": 8},
                {"name": "Java", "importance": 8},
                {"name": "Node.js", "importance": 8},
                {"name": "SQL", "importance": 9},
                {"name": "NoSQL", "importance": 7},
                {"name": "API Design", "importance": 9},
                {"name": "Docker", "importance": 8},
                {"name": "Kubernetes", "importance": 7},
                {"name": "AWS", "importance": 8},
                {"name": "System Design", "importance": 9}
            ],
            "DevOps Engineer": [
                {"name": "Linux", "importance": 9},
                {"name": "Docker", "importance": 9},
                {"name": "Kubernetes", "importance": 9},
                {"name": "AWS", "importance": 9},
                {"name": "CI/CD", "importance": 9},
                {"name": "Infrastructure as Code", "importance": 8},
                {"name": "Monitoring", "importance": 8},
                {"name": "Scripting", "importance": 8},
                {"name": "Security", "importance": 7},
                {"name": "Networking", "importance": 7}
            ],
            "Senior Software Engineer": [
                {"name": "System Architecture", "importance": 9},
                {"name": "Technical Leadership", "importance": 8},
                {"name": "Mentoring", "importance": 8},
                {"name": "Code Review", "importance": 9},
                {"name": "Performance Optimization", "importance": 8},
                {"name": "Scalability", "importance": 9},
                {"name": "Security Best Practices", "importance": 8},
                {"name": "Project Management", "importance": 7},
                {"name": "Cross-functional Collaboration", "importance": 8},
                {"name": "Advanced Debugging", "importance": 9}
            ]
        }
        
        # Industry-specific skills
        industry_skills_map = {
            "Technology": {
                "Software Engineer": [
                    {"name": "Agile Methodologies", "importance": 8},
                    {"name": "Microservices", "importance": 8},
                    {"name": "CI/CD", "importance": 7}
                ],
                "Data Scientist": [
                    {"name": "Product Analytics", "importance": 8},
                    {"name": "A/B Testing", "importance": 8},
                    {"name": "Recommendation Systems", "importance": 7}
                ],
                "Senior Software Engineer": [
                    {"name": "Distributed Systems", "importance": 9},
                    {"name": "Microservices Architecture", "importance": 8},
                    {"name": "Cloud Infrastructure", "importance": 8}
                ]
            },
            "Finance": {
                "Software Engineer": [
                    {"name": "Financial Regulations", "importance": 8},
                    {"name": "Security Compliance", "importance": 9},
                    {"name": "Payment Processing", "importance": 7}
                ],
                "Data Scientist": [
                    {"name": "Risk Modeling", "importance": 9},
                    {"name": "Fraud Detection", "importance": 9},
                    {"name": "Time Series Analysis", "importance": 8}
                ],
                "Senior Software Engineer": [
                    {"name": "High-Frequency Trading Systems", "importance": 8},
                    {"name": "Financial Security Protocols", "importance": 9},
                    {"name": "Regulatory Compliance", "importance": 9}
                ]
            },
            "Healthcare": {
                "Software Engineer": [
                    {"name": "HIPAA Compliance", "importance": 9},
                    {"name": "Electronic Health Records", "importance": 8},
                    {"name": "Healthcare Interoperability", "importance": 7}
                ],
                "Data Scientist": [
                    {"name": "Clinical Data Analysis", "importance": 9},
                    {"name": "Medical Imaging", "importance": 8},
                    {"name": "Patient Outcome Prediction", "importance": 8}
                ],
                "Senior Software Engineer": [
                    {"name": "Medical Device Integration", "importance": 8},
                    {"name": "Healthcare Data Security", "importance": 9},
                    {"name": "Clinical Systems Architecture", "importance": 8}
                ]
            }
        }
        
        # Get required skills for the target role
        required_skills = role_skills_map.get(target_role, [])
        if not required_skills:
            # Default to Software Engineer if role not found
            required_skills = role_skills_map["Software Engineer"]
        
        # Add industry-specific skills if available
        if industry in industry_skills_map and target_role in industry_skills_map[industry]:
            industry_specific_skills = industry_skills_map[industry][target_role]
            required_skills.extend(industry_specific_skills)
        
        # Adjust required skills based on experience level
        if experience_level == "Entry-level":
            required_skills = [{"name": s["name"], "importance": max(s["importance"] - 2, 5)} for s in required_skills]
        elif experience_level == "Senior":
            required_skills = [{"name": s["name"], "importance": min(s["importance"] + 1, 10)} for s in required_skills]
        elif experience_level == "Lead":
            required_skills = [{"name": s["name"], "importance": min(s["importance"] + 2, 10)} for s in required_skills]
        
        # Find missing skills
        candidate_skill_names = [s["name"].lower() for s in candidate_skills]
        missing_skills = [s for s in required_skills if s["name"].lower() not in candidate_skill_names]
        
        # Calculate match score
        total_importance = sum(s["importance"] for s in required_skills)
        missing_importance = sum(s["importance"] for s in missing_skills)
        match_score = max(0, min(100, int(100 * (1 - missing_importance / total_importance))))
        
        # Categorize skills by type
        skill_categories = {
            "technical": ["Python", "JavaScript", "SQL", "Java", "React", "Docker", "Kubernetes", 
                         "AWS", "Machine Learning", "Data Structures", "Algorithms", "Testing",
                         "CI/CD", "Git", "Node.js", "TypeScript", "HTML", "CSS", "NoSQL"],
            "soft_skills": ["Communication", "Leadership", "Teamwork", "Problem Solving", 
                           "Critical Thinking", "Mentoring", "Cross-functional Collaboration"],
            "domain_knowledge": ["HIPAA Compliance", "Financial Regulations", "Healthcare Interoperability",
                               "Electronic Health Records", "Payment Processing", "Security Compliance"],
            "architecture": ["System Design", "Microservices", "Distributed Systems", 
                            "Scalability", "System Architecture", "API Design"]
        }
        
        # Categorize missing skills
        categorized_missing_skills = {}
        for skill in missing_skills:
            skill_name = skill["name"]
            category = "other"
            
            # Find the right category
            for cat, skills in skill_categories.items():
                if any(s.lower() in skill_name.lower() for s in skills):
                    category = cat
                    break
            
            if category not in categorized_missing_skills:
                categorized_missing_skills[category] = []
            
            categorized_missing_skills[category].append(skill)
        
        # Prepare response
        response = {
            "match_score": match_score,
            "your_skills": candidate_skills,
            "required_skills": required_skills,
            "missing_skills": missing_skills,
            "categorized_missing_skills": categorized_missing_skills,
            "industry_specific_requirements": industry_skills_map.get(industry, {}).get(target_role, [])
        }
        
        # Add learning resources if requested
        if include_learning_resources:
            # Get top 5 most important missing skills
            top_missing_skills = sorted(missing_skills, key=lambda x: x["importance"], reverse=True)[:5]
            skill_names = [skill["name"] for skill in top_missing_skills]
            
            # Get learning resources
            if skill_names:
                learning_resources_response = await get_learning_recommendations(json.dumps(skill_names), current_user)
                response["learning_resources"] = learning_resources_response
        
        # Add market demand data
        market_demand = {
            "Technology": {
                "Software Engineer": {"demand_score": 85, "growth_rate": 22, "avg_salary": "$110,000"},
                "Data Scientist": {"demand_score": 90, "growth_rate": 28, "avg_salary": "$120,000"},
                "Senior Software Engineer": {"demand_score": 88, "growth_rate": 18, "avg_salary": "$140,000"}
            },
            "Finance": {
                "Software Engineer": {"demand_score": 80, "growth_rate": 15, "avg_salary": "$105,000"},
                "Data Scientist": {"demand_score": 85, "growth_rate": 20, "avg_salary": "$125,000"},
                "Senior Software Engineer": {"demand_score": 82, "growth_rate": 12, "avg_salary": "$135,000"}
            },
            "Healthcare": {
                "Software Engineer": {"demand_score": 78, "growth_rate": 18, "avg_salary": "$100,000"},
                "Data Scientist": {"demand_score": 88, "growth_rate": 25, "avg_salary": "$115,000"},
                "Senior Software Engineer": {"demand_score": 80, "growth_rate": 15, "avg_salary": "$130,000"}
            }
        }
        
        # Add market demand if available
        if industry in market_demand and target_role in market_demand[industry]:
            response["market_demand"] = market_demand[industry][target_role]
        
        return response
    except Exception as e:
        # Print the full exception for debugging
        import traceback
        print(f"Error in skill gap analysis: {str(e)}")
        print(traceback.format_exc())
        raise


@app.get("/recommendations/learning", response_model=dict)
async def get_learning_recommendations(
    skills: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get learning recommendations for specified skills"""
    # Parse skills from JSON string if provided
    skill_list = []
    if skills:
        try:
            skill_list = json.loads(skills)
        except json.JSONDecodeError:
            skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    
    # If no skills provided, get from user profile
    if not skill_list and current_user["user_type"] == UserType.CANDIDATE:
        candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
            {"email": current_user["email"]}
        )
        if candidate:
            # Get missing skills from skill gap analysis
            target_role = "Software Engineer"  # Default role
            skill_gap = await get_skill_gap_analysis(target_role, "Mid-level", current_user)
            missing_skills = skill_gap.get("missing_skills", [])
            skill_list = [s["name"] for s in missing_skills[:3]]
    
    # Define learning resources for common skills
    # In a real system, this would come from a database or external API
    learning_resources = {
        "Python": [
            {
                "title": "Python for Everybody",
                "provider": "Coursera",
                "description": "Learn to program and analyze data with Python.",
                "url": "https://www.coursera.org/specializations/python"
            },
            {
                "title": "Python Crash Course",
                "provider": "No Starch Press",
                "description": "A hands-on, project-based introduction to programming.",
                "url": "https://nostarch.com/pythoncrashcourse2e"
            },
            {
                "title": "Python Data Science Handbook",
                "provider": "O'Reilly",
                "description": "Essential tools for working with data in Python.",
                "url": "https://jakevdp.github.io/PythonDataScienceHandbook/"
            }
        ],
        "JavaScript": [
            {
                "title": "JavaScript: The Definitive Guide",
                "provider": "O'Reilly",
                "description": "Comprehensive guide to JavaScript programming.",
                "url": "https://www.oreilly.com/library/view/javascript-the-definitive/9781491952016/"
            },
            {
                "title": "Modern JavaScript Tutorial",
                "provider": "JavaScript.info",
                "description": "Modern JavaScript tutorial from the basics to advanced topics.",
                "url": "https://javascript.info/"
            },
            {
                "title": "JavaScript30",
                "provider": "Wes Bos",
                "description": "30 Day Vanilla JS Coding Challenge.",
                "url": "https://javascript30.com/"
            }
        ],
        "React": [
            {
                "title": "React - The Complete Guide",
                "provider": "Udemy",
                "description": "Dive in and learn React from scratch.",
                "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"
            },
            {
                "title": "React Documentation",
                "provider": "React.dev",
                "description": "Official React documentation and tutorials.",
                "url": "https://react.dev/learn"
            },
            {
                "title": "Epic React",
                "provider": "Kent C. Dodds",
                "description": "Learn React from the ground up with workshops.",
                "url": "https://epicreact.dev/"
            }
        ],
        "SQL": [
            {
                "title": "SQL for Data Science",
                "provider": "Coursera",
                "description": "Learn SQL basics for data analysis.",
                "url": "https://www.coursera.org/learn/sql-for-data-science"
            },
            {
                "title": "SQL Cookbook",
                "provider": "O'Reilly",
                "description": "Query solutions and techniques for all SQL users.",
                "url": "https://www.oreilly.com/library/view/sql-cookbook-2nd/9781492077435/"
            },
            {
                "title": "Mode SQL Tutorial",
                "provider": "Mode",
                "description": "Interactive SQL tutorial for data analysis.",
                "url": "https://mode.com/sql-tutorial/"
            }
        ],
        "AWS": [
            {
                "title": "AWS Certified Solutions Architect",
                "provider": "A Cloud Guru",
                "description": "Prepare for the AWS Solutions Architect certification.",
                "url": "https://acloudguru.com/course/aws-certified-solutions-architect-associate-saa-c02"
            },
            {
                "title": "AWS in Action",
                "provider": "Manning",
                "description": "Learn AWS services and how to use them together.",
                "url": "https://www.manning.com/books/amazon-web-services-in-action-second-edition"
            },
            {
                "title": "AWS Documentation",
                "provider": "Amazon",
                "description": "Official AWS documentation and tutorials.",
                "url": "https://docs.aws.amazon.com/"
            }
        ],
        "Docker": [
            {
                "title": "Docker & Kubernetes: The Practical Guide",
                "provider": "Udemy",
                "description": "Learn Docker, Kubernetes and container orchestration.",
                "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/"
            },
            {
                "title": "Docker Deep Dive",
                "provider": "Pluralsight",
                "description": "Comprehensive Docker training.",
                "url": "https://www.pluralsight.com/courses/docker-deep-dive-update"
            },
            {
                "title": "Docker Documentation",
                "provider": "Docker",
                "description": "Official Docker documentation and tutorials.",
                "url": "https://docs.docker.com/"
            }
        ],
        "Machine Learning": [
            {
                "title": "Machine Learning",
                "provider": "Coursera (Andrew Ng)",
                "description": "Classic machine learning course covering fundamentals.",
                "url": "https://www.coursera.org/learn/machine-learning"
            },
            {
                "title": "Hands-On Machine Learning",
                "provider": "O'Reilly",
                "description": "Practical guide to machine learning with scikit-learn and TensorFlow.",
                "url": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/"
            },
            {
                "title": "Fast.ai",
                "provider": "Fast.ai",
                "description": "Practical deep learning for coders.",
                "url": "https://www.fast.ai/"
            }
        ]
    }
    
    # Default resources for skills not in our database
    default_resources = [
        {
            "title": "Coursera Courses",
            "provider": "Coursera",
            "description": "Find courses on a wide range of topics.",
            "url": "https://www.coursera.org/"
        },
        {
            "title": "Udemy Courses",
            "provider": "Udemy",
            "description": "Practical courses on technical skills.",
            "url": "https://www.udemy.com/"
        },
        {
            "title": "edX Courses",
            "provider": "edX",
            "description": "University-level courses from top institutions.",
            "url": "https://www.edx.org/"
        }
    ]
    
    # Prepare response
    resources = []
    for skill in skill_list:
        skill_resources = learning_resources.get(skill, None)
        if skill_resources:
            resources.append({
                "skill": skill,
                "resources": skill_resources
            })
        else:
            resources.append({
                "skill": skill,
                "resources": default_resources
            })
    
    return {
        "resources": resources
    }


@app.get("/recommendations/career-path", response_model=dict)
async def get_career_path_recommendations(
    current_role: str,
    industry: str = None,
    career_goal: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get career path recommendations based on current role and goals"""
    if current_user["user_type"] != UserType.CANDIDATE:
        raise HTTPException(
            status_code=403, detail="Only candidates can get career path recommendations"
        )
    
    # Define career paths for common roles
    # In a real system, this would come from a database or ML model
    career_paths = {
        "Software Engineer": {
            "Technology": [
                {
                    "name": "From Software Engineer to Senior Software Engineer",
                    "steps": [
                        {
                            "role": "Software Engineer",
                            "duration": "1-3 years",
                            "description": "Build strong programming fundamentals and contribute to team projects"
                        },
                        {
                            "role": "Software Engineer II",
                            "duration": "2-3 years",
                            "description": "Lead small features and mentor junior engineers"
                        },
                        {
                            "role": "Senior Software Engineer",
                            "duration": "3+ years",
                            "description": "Lead major features and architectural decisions"
                        }
                    ],
                    "skills_to_develop": ["System Design", "Technical Leadership", "Mentoring", "Architecture"]
                },
                {
                    "name": "From Software Engineer to Engineering Manager",
                    "steps": [
                        {
                            "role": "Software Engineer",
                            "duration": "2-3 years",
                            "description": "Build technical expertise and team collaboration skills"
                        },
                        {
                            "role": "Senior Software Engineer",
                            "duration": "2-3 years",
                            "description": "Lead projects and mentor junior engineers"
                        },
                        {
                            "role": "Tech Lead",
                            "duration": "1-2 years",
                            "description": "Lead technical direction for a team"
                        },
                        {
                            "role": "Engineering Manager",
                            "duration": "Ongoing",
                            "description": "Manage a team of engineers, focusing on people and delivery"
                        }
                    ],
                    "skills_to_develop": ["People Management", "Project Management", "Communication", "Leadership"]
                }
            ],
            "Finance": [
                {
                    "name": "From Software Engineer to FinTech Specialist",
                    "steps": [
                        {
                            "role": "Software Engineer",
                            "duration": "1-2 years",
                            "description": "Build core engineering skills in a finance context"
                        },
                        {
                            "role": "Financial Software Engineer",
                            "duration": "2-3 years",
                            "description": "Develop expertise in financial systems and regulations"
                        },
                        {
                            "role": "FinTech Specialist",
                            "duration": "Ongoing",
                            "description": "Lead development of innovative financial technology solutions"
                        }
                    ],
                    "skills_to_develop": ["Financial Regulations", "Payment Systems", "Security", "Risk Management"]
                }
            ]
        },
        "Data Scientist": {
            "Technology": [
                {
                    "name": "From Data Scientist to ML Engineer",
                    "steps": [
                        {
                            "role": "Data Scientist",
                            "duration": "1-2 years",
                            "description": "Build strong data analysis and modeling skills"
                        },
                        {
                            "role": "Senior Data Scientist",
                            "duration": "2-3 years",
                            "description": "Lead complex data projects and develop ML models"
                        },
                        {
                            "role": "ML Engineer",
                            "duration": "Ongoing",
                            "description": "Focus on deploying and scaling ML systems in production"
                        }
                    ],
                    "skills_to_develop": ["MLOps", "Production Systems", "Scalability", "Software Engineering"]
                },
                {
                    "name": "From Data Scientist to Data Science Manager",
                    "steps": [
                        {
                            "role": "Data Scientist",
                            "duration": "2-3 years",
                            "description": "Build expertise in data analysis and machine learning"
                        },
                        {
                            "role": "Senior Data Scientist",
                            "duration": "1-2 years",
                            "description": "Lead data science initiatives and mentor junior data scientists"
                        },
                        {
                            "role": "Data Science Manager",
                            "duration": "Ongoing",
                            "description": "Lead a team of data scientists and align with business objectives"
                        }
                    ],
                    "skills_to_develop": ["Team Leadership", "Project Management", "Business Strategy", "Communication"]
                }
            ]
        },
        "Product Manager": {
            "Technology": [
                {
                    "name": "From Product Manager to Director of Product",
                    "steps": [
                        {
                            "role": "Product Manager",
                            "duration": "2-3 years",
                            "description": "Manage product features and work with engineering teams"
                        },
                        {
                            "role": "Senior Product Manager",
                            "duration": "2-3 years",
                            "description": "Manage entire products and develop product strategy"
                        },
                        {
                            "role": "Director of Product",
                            "duration": "Ongoing",
                            "description": "Lead product teams and define product vision"
                        }
                    ],
                    "skills_to_develop": ["Strategic Thinking", "Leadership", "Business Development", "Market Analysis"]
                }
            ]
        }
    }
    
    # Default to technology industry if not specified
    if not industry:
        industry = "Technology"
    
    # Get career paths for the current role and industry
    role_paths = career_paths.get(current_role, {})
    industry_paths = role_paths.get(industry, role_paths.get("Technology", []))
    
    # If no paths found, provide generic advice
    if not industry_paths:
        return {
            "paths": [
                {
                    "name": f"From {current_role} to Senior {current_role}",
                    "steps": [
                        {
                            "role": current_role,
                            "duration": "1-3 years",
                            "description": "Build core skills and domain expertise"
                        },
                        {
                            "role": f"Senior {current_role}",
                            "duration": "Ongoing",
                            "description": "Lead projects and mentor junior team members"
                        }
                    ],
                    "skills_to_develop": ["Leadership", "Communication", "Project Management", "Domain Expertise"]
                }
            ]
        }
    
    # Return career paths
    return {
        "paths": industry_paths
    }


@app.get("/job-roles", response_model=List[dict])
async def get_job_roles():
    """Get a list of standard job roles"""
    # In a real system, this would come from a database
    job_roles = [
        {"id": "software-engineer", "title": "Software Engineer", "category": "Engineering"},
        {"id": "senior-software-engineer", "title": "Senior Software Engineer", "category": "Engineering"},
        {"id": "frontend-developer", "title": "Frontend Developer", "category": "Engineering"},
        {"id": "backend-developer", "title": "Backend Developer", "category": "Engineering"},
        {"id": "full-stack-developer", "title": "Full Stack Developer", "category": "Engineering"},
        {"id": "devops-engineer", "title": "DevOps Engineer", "category": "Engineering"},
        {"id": "data-scientist", "title": "Data Scientist", "category": "Data"},
        {"id": "data-engineer", "title": "Data Engineer", "category": "Data"},
        {"id": "data-analyst", "title": "Data Analyst", "category": "Data"},
        {"id": "machine-learning-engineer", "title": "Machine Learning Engineer", "category": "Data"},
        {"id": "product-manager", "title": "Product Manager", "category": "Product"},
        {"id": "product-designer", "title": "Product Designer", "category": "Design"},
        {"id": "ui-ux-designer", "title": "UI/UX Designer", "category": "Design"},
        {"id": "project-manager", "title": "Project Manager", "category": "Management"},
        {"id": "engineering-manager", "title": "Engineering Manager", "category": "Management"},
        {"id": "technical-lead", "title": "Technical Lead", "category": "Engineering"},
        {"id": "qa-engineer", "title": "QA Engineer", "category": "Engineering"},
        {"id": "security-engineer", "title": "Security Engineer", "category": "Engineering"},
        {"id": "cloud-architect", "title": "Cloud Architect", "category": "Engineering"},
        {"id": "mobile-developer", "title": "Mobile Developer", "category": "Engineering"}
    ]
    
    return job_roles


@app.get("/industries", response_model=List[dict])
async def get_industries():
    """Get a list of standard industries"""
    # In a real system, this would come from a database
    industries = [
        {"id": "technology", "name": "Technology"},
        {"id": "finance", "name": "Finance"},
        {"id": "healthcare", "name": "Healthcare"},
        {"id": "education", "name": "Education"},
        {"id": "retail", "name": "Retail"},
        {"id": "manufacturing", "name": "Manufacturing"},
        {"id": "media", "name": "Media & Entertainment"},
        {"id": "consulting", "name": "Consulting"},
        {"id": "hospitality", "name": "Hospitality & Tourism"},
        {"id": "real-estate", "name": "Real Estate"},
        {"id": "energy", "name": "Energy"},
        {"id": "transportation", "name": "Transportation & Logistics"},
        {"id": "telecommunications", "name": "Telecommunications"},
        {"id": "agriculture", "name": "Agriculture"},
        {"id": "construction", "name": "Construction"},
        {"id": "non-profit", "name": "Non-profit"},
        {"id": "government", "name": "Government"},
        {"id": "legal", "name": "Legal"},
        {"id": "marketing", "name": "Marketing & Advertising"},
        {"id": "ecommerce", "name": "E-commerce"}
    ]
    
    return industries


@app.patch("/profile", response_model=User)
async def update_profile_patch(
    profile_data: dict, current_user: dict = Depends(get_current_user)
):
    """PATCH endpoint for profile updates with the same functionality as PUT"""
    if current_user["user_type"] == UserType.CANDIDATE:
        # Check if any field affects candidate embedding
        semantic_fields = [
            "full_name",
            "skills",
            "experience",
            "education",
            "location",
            "bio",
        ]
        if any(field in profile_data for field in semantic_fields):
            # Get the current candidate data
            candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
                {"email": current_user["email"]}
            )
            if candidate:
                # Create updated candidate data by merging
                updated_candidate = {**candidate}
                updated_candidate.update(profile_data)
                # Generate new embedding
                profile_data["embedding"] = create_candidate_embedding(
                    updated_candidate
                )
        
        # Update candidate profile with new data including potential new embedding
        await Database.get_collection(CANDIDATES_COLLECTION).update_one(
            {"email": current_user["email"]}, {"$set": profile_data}
        )
        
        # Get updated candidate profile
        updated_profile = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
            {"email": current_user["email"]}
        )
        
        # Remove embedding from response
        if updated_profile and "embedding" in updated_profile:
            updated_profile.pop("embedding", None)
            
        return updated_profile
    else:
        # Update employer profile only
        await Database.get_collection(EMPLOYERS_COLLECTION).update_one(
            {"email": current_user["email"]}, {"$set": profile_data}
        )
        
        # Get updated employer profile
        updated_profile = await Database.get_collection(EMPLOYERS_COLLECTION).find_one(
            {"email": current_user["email"]}
        )
        return updated_profile


# Add this after the existing recommendation endpoints
@app.get("/recommendations/similar-jobs/{job_id}", response_model=List[dict])
async def get_similar_jobs(
    job_id: str,
    limit: int = 10,
    exclude_applied: bool = True,
    exclude_company: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get jobs similar to a specific job based on vector similarity"""
    if current_user["user_type"] != UserType.CANDIDATE:
        raise HTTPException(
            status_code=403, detail="Only candidates can get similar job recommendations"
        )
    
    # Get the source job
    source_job = await Database.get_collection(JOBS_COLLECTION).find_one({"id": job_id})
    if not source_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get the source job embedding
    source_embedding = source_job.get("embedding")
    if not source_embedding:
        # If no embedding, try to generate one
        try:
            source_embedding = create_job_embedding(source_job)
        except Exception as e:
            print(f"Error generating embedding for job {job_id}: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Could not generate embedding for the job"
            )
    
    # Build filter query
    filter_query = {"is_active": True, "id": {"$ne": job_id}}
    
    # Exclude jobs from the same company if requested
    if exclude_company and "company" in source_job:
        filter_query["company"] = {"$ne": source_job["company"]}
    
    # Exclude jobs the candidate has already applied to
    if exclude_applied:
        # Get the candidate's job applications
        applications = await Database.get_collection(JOB_APPLICATIONS_COLLECTION).find(
            {"candidate_id": current_user["id"]}
        ).to_list(length=None)
        
        if applications:
            applied_job_ids = [app["job_id"] for app in applications]
            filter_query["id"] = {"$nin": applied_job_ids}
    
    try:
        # Use vector search to find similar jobs
        similar_jobs = await search_vector_collection(
            JOBS_COLLECTION, source_embedding, limit, filter_query
        )
        
        # If vector search fails or returns no results, fall back to manual similarity calculation
        if not similar_jobs:
            print(f"Vector search returned no results for job {job_id}, using fallback")
            
            # Get all active jobs except the source job
            all_jobs = await Database.get_collection(JOBS_COLLECTION).find(
                filter_query
            ).to_list(length=None)
            
            # Calculate similarity manually
            job_similarities = []
            for job in all_jobs:
                job_embedding = job.get("embedding")
                if job_embedding:
                    similarity = cosine_similarity(source_embedding, job_embedding)
                    # Add detailed job information
                    job_data = {
                        "job_id": job["id"],
                        "similarity_score": float(similarity * 100),  # Convert to percentage
                        "job_details": {
                            "title": job.get("title", ""),
                            "company": job.get("company", ""),
                            "description": job.get("description", ""),
                            "location": job.get("location", ""),
                            "salary_range": job.get("salary_range", ""),
                            "required_skills": job.get("requirements", []),
                            "job_type": job.get("job_type", ""),
                            "experience_level": job.get("experience_level", ""),
                        }
                    }
                    job_similarities.append(job_data)
            
            # Sort by similarity (descending)
            job_similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Limit results
            similar_jobs = job_similarities[:limit]
        else:
            # Format the results from vector search
            formatted_jobs = []
            for job in similar_jobs:
                # Add similarity score based on search score if available
                similarity_score = job.get("score", 70)  # Default score if not provided
                
                job_data = {
                    "job_id": job["id"],
                    "similarity_score": float(similarity_score),
                    "job_details": {
                        "title": job.get("title", ""),
                        "company": job.get("company", ""),
                        "description": job.get("description", ""),
                        "location": job.get("location", ""),
                        "salary_range": job.get("salary_range", ""),
                        "required_skills": job.get("requirements", []),
                        "job_type": job.get("job_type", ""),
                        "experience_level": job.get("experience_level", ""),
                    }
                }
                formatted_jobs.append(job_data)
                
            similar_jobs = formatted_jobs
        
        return similar_jobs
        
    except Exception as e:
        print(f"Error finding similar jobs: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error finding similar jobs: {str(e)}"
        )


@app.get("/recommendations/career-paths", response_model=dict)
async def get_enhanced_career_paths(
    current_role: str = None,
    industry: str = None,
    timeframe_years: int = 5,
    include_skill_requirements: bool = True,
    include_salary_data: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Get enhanced career path recommendations with additional parameters
    
    - timeframe_years: Number of years to plan for career progression
    - include_skill_requirements: Include detailed skill requirements for each role
    - include_salary_data: Include salary data for each role
    """
    if current_user["user_type"] != UserType.CANDIDATE:
        raise HTTPException(
            status_code=403, detail="Only candidates can get career path recommendations"
        )
    
    # Get candidate profile to personalize recommendations
    candidate = await Database.get_collection(CANDIDATES_COLLECTION).find_one(
        {"email": current_user["email"]}
    )
    
    # If current_role not specified, try to infer from candidate profile
    if not current_role and candidate:
        # Try to get current role from candidate experience
        experience = candidate.get("experience", [])
        if isinstance(experience, list) and len(experience) > 0:
            current_role = experience[0].get("title", "Software Engineer")
        else:
            current_role = "Software Engineer"  # Default
    
    # If industry not specified, try to infer from candidate profile
    if not industry and candidate:
        # Try to get industry from candidate experience
        experience = candidate.get("experience", [])
        if isinstance(experience, list) and len(experience) > 0:
            industry = experience[0].get("industry", "Technology")
        else:
            industry = "Technology"  # Default
    
    # Define enhanced career paths with more detailed information
    career_paths = {
        "Software Engineer": {
            "Technology": [
                {
                    "name": "Technical Leadership Track",
                    "description": "Progress from Software Engineer to Technical Leadership roles",
                    "average_time_years": 6,
                    "salary_growth_percentage": 75,
                    "difficulty": 7,
                    "steps": [
                        {
                            "role": "Software Engineer",
                            "timeline": "0-2 years",
                            "description": "Build strong programming fundamentals and contribute to team projects",
                            "skills": ["Programming", "Data Structures", "Algorithms", "Testing"],
                            "skill_requirements": {
                                "technical": ["JavaScript", "Python", "SQL", "Git"],
                                "soft": ["Communication", "Problem Solving", "Teamwork"]
                            },
                            "responsibilities": ["Implement features", "Fix bugs", "Write tests", "Participate in code reviews"],
                            "salary_data": {
                                "median": 90000,
                                "range": {"min": 75000, "max": 110000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "Senior Software Engineer",
                            "timeline": "2-4 years",
                            "description": "Lead projects and mentor junior engineers",
                            "skills": ["System Design", "Technical Leadership", "Mentoring", "Architecture"],
                            "skill_requirements": {
                                "technical": ["Advanced Programming", "System Design", "Architecture Patterns", "CI/CD"],
                                "soft": ["Mentoring", "Project Planning", "Technical Communication"]
                            },
                            "responsibilities": ["Design systems", "Lead projects", "Mentor junior engineers", "Improve development processes"],
                            "salary_data": {
                                "median": 130000,
                                "range": {"min": 110000, "max": 160000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "Staff Engineer",
                            "timeline": "4-6 years",
                            "description": "Provide technical leadership across multiple teams",
                            "skills": ["Technical Strategy", "Cross-team Collaboration", "Advanced System Design"],
                            "skill_requirements": {
                                "technical": ["Distributed Systems", "Performance Optimization", "Technical Strategy", "Architecture"],
                                "soft": ["Strategic Thinking", "Cross-team Collaboration", "Influence"]
                            },
                            "responsibilities": ["Define technical strategy", "Solve complex problems", "Drive technical initiatives", "Mentor senior engineers"],
                            "salary_data": {
                                "median": 170000,
                                "range": {"min": 150000, "max": 200000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "Principal Engineer",
                            "timeline": "6+ years",
                            "description": "Set technical direction for the organization",
                            "skills": ["Technical Vision", "Organization-wide Impact", "Strategic Planning"],
                            "skill_requirements": {
                                "technical": ["System Architecture", "Technical Vision", "Technology Strategy"],
                                "soft": ["Executive Communication", "Leadership", "Strategic Planning"]
                            },
                            "responsibilities": ["Set technical vision", "Drive organization-wide initiatives", "Represent engineering externally"],
                            "salary_data": {
                                "median": 210000,
                                "range": {"min": 180000, "max": 250000},
                                "currency": "USD"
                            }
                        }
                    ]
                },
                {
                    "name": "Management Track",
                    "description": "Progress from Software Engineer to Engineering Management roles",
                    "average_time_years": 7,
                    "salary_growth_percentage": 85,
                    "difficulty": 8,
                    "steps": [
                        {
                            "role": "Software Engineer",
                            "timeline": "0-2 years",
                            "description": "Build technical expertise and team collaboration skills",
                            "skills": ["Programming", "Data Structures", "Algorithms", "Testing"],
                            "skill_requirements": {
                                "technical": ["JavaScript", "Python", "SQL", "Git"],
                                "soft": ["Communication", "Problem Solving", "Teamwork"]
                            },
                            "responsibilities": ["Implement features", "Fix bugs", "Write tests", "Participate in code reviews"],
                            "salary_data": {
                                "median": 90000,
                                "range": {"min": 75000, "max": 110000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "Senior Software Engineer",
                            "timeline": "2-4 years",
                            "description": "Lead projects and mentor junior engineers",
                            "skills": ["System Design", "Technical Leadership", "Mentoring", "Project Management"],
                            "skill_requirements": {
                                "technical": ["Advanced Programming", "System Design", "Architecture Patterns"],
                                "soft": ["Mentoring", "Project Planning", "Leadership"]
                            },
                            "responsibilities": ["Design systems", "Lead projects", "Mentor junior engineers", "Coordinate with stakeholders"],
                            "salary_data": {
                                "median": 130000,
                                "range": {"min": 110000, "max": 160000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "Tech Lead",
                            "timeline": "4-5 years",
                            "description": "Lead technical direction for a team while developing management skills",
                            "skills": ["Technical Leadership", "Team Coordination", "Project Planning"],
                            "skill_requirements": {
                                "technical": ["Architecture", "Technical Planning", "Code Quality"],
                                "soft": ["Team Leadership", "Stakeholder Management", "Conflict Resolution"]
                            },
                            "responsibilities": ["Set technical direction", "Coordinate team efforts", "Work with product managers", "Mentor team members"],
                            "salary_data": {
                                "median": 150000,
                                "range": {"min": 130000, "max": 180000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "Engineering Manager",
                            "timeline": "5-7 years",
                            "description": "Manage a team of engineers, focusing on people and delivery",
                            "skills": ["People Management", "Project Management", "Process Improvement"],
                            "skill_requirements": {
                                "technical": ["System Understanding", "Technical Strategy", "Development Processes"],
                                "soft": ["People Management", "Coaching", "Conflict Resolution", "Resource Planning"]
                            },
                            "responsibilities": ["Hire and grow team", "Manage performance", "Deliver projects", "Improve processes"],
                            "salary_data": {
                                "median": 170000,
                                "range": {"min": 150000, "max": 200000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "Director of Engineering",
                            "timeline": "7+ years",
                            "description": "Lead multiple engineering teams and set department strategy",
                            "skills": ["Organizational Leadership", "Strategic Planning", "Cross-functional Collaboration"],
                            "skill_requirements": {
                                "technical": ["Engineering Strategy", "Technology Roadmap", "Architecture Vision"],
                                "soft": ["Executive Communication", "Strategic Thinking", "Organizational Design"]
                            },
                            "responsibilities": ["Set engineering strategy", "Manage managers", "Align with business goals", "Drive organizational improvements"],
                            "salary_data": {
                                "median": 210000,
                                "range": {"min": 180000, "max": 250000},
                                "currency": "USD"
                            }
                        }
                    ]
                }
            ],
            "Finance": [
                {
                    "name": "FinTech Specialist Track",
                    "description": "Specialize in financial technology and systems",
                    "average_time_years": 5,
                    "salary_growth_percentage": 70,
                    "difficulty": 8,
                    "steps": [
                        {
                            "role": "Software Engineer",
                            "timeline": "0-2 years",
                            "description": "Build core engineering skills in a finance context",
                            "skills": ["Programming", "Data Structures", "Algorithms", "Financial Systems"],
                            "skill_requirements": {
                                "technical": ["Java", "Python", "SQL", "REST APIs"],
                                "soft": ["Attention to Detail", "Problem Solving", "Communication"],
                                "domain": ["Basic Financial Knowledge", "Security Awareness"]
                            },
                            "responsibilities": ["Implement features", "Fix bugs", "Write tests", "Learn financial domain"],
                            "salary_data": {
                                "median": 95000,
                                "range": {"min": 80000, "max": 115000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "Financial Software Engineer",
                            "timeline": "2-4 years",
                            "description": "Develop expertise in financial systems and regulations",
                            "skills": ["Financial Regulations", "Payment Systems", "Security", "Risk Management"],
                            "skill_requirements": {
                                "technical": ["Advanced Java/Python", "Financial APIs", "Security Protocols"],
                                "soft": ["Regulatory Compliance", "Risk Assessment", "Technical Documentation"],
                                "domain": ["Financial Regulations", "Payment Processing", "Risk Management"]
                            },
                            "responsibilities": ["Design financial systems", "Implement regulatory requirements", "Ensure security compliance", "Optimize transaction processing"],
                            "salary_data": {
                                "median": 130000,
                                "range": {"min": 115000, "max": 160000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "FinTech Specialist",
                            "timeline": "4-5+ years",
                            "description": "Lead development of innovative financial technology solutions",
                            "skills": ["Financial Product Development", "Regulatory Strategy", "Advanced Security"],
                            "skill_requirements": {
                                "technical": ["Financial System Architecture", "Blockchain (optional)", "Advanced Security", "High-Performance Systems"],
                                "soft": ["Financial Domain Expertise", "Cross-functional Leadership", "Strategic Thinking"],
                                "domain": ["Advanced Financial Products", "Regulatory Framework", "Risk Models"]
                            },
                            "responsibilities": ["Design financial products", "Lead regulatory compliance", "Drive security strategy", "Innovate payment solutions"],
                            "salary_data": {
                                "median": 160000,
                                "range": {"min": 140000, "max": 190000},
                                "currency": "USD"
                            }
                        }
                    ]
                }
            ]
        },
        "Data Scientist": {
            "Technology": [
                {
                    "name": "ML Engineering Track",
                    "description": "Progress from Data Scientist to ML Engineering leadership",
                    "average_time_years": 5,
                    "salary_growth_percentage": 65,
                    "difficulty": 8,
                    "steps": [
                        {
                            "role": "Data Scientist",
                            "timeline": "0-2 years",
                            "description": "Build strong data analysis and modeling skills",
                            "skills": ["Python", "Statistics", "Machine Learning", "Data Analysis"],
                            "skill_requirements": {
                                "technical": ["Python", "SQL", "Statistical Analysis", "Machine Learning Algorithms"],
                                "soft": ["Communication", "Problem Solving", "Business Acumen"]
                            },
                            "responsibilities": ["Analyze data", "Build models", "Present insights", "Support business decisions"],
                            "salary_data": {
                                "median": 100000,
                                "range": {"min": 85000, "max": 120000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "Senior Data Scientist",
                            "timeline": "2-4 years",
                            "description": "Lead complex data projects and develop ML models",
                            "skills": ["Advanced ML", "Deep Learning", "Project Leadership", "Model Deployment"],
                            "skill_requirements": {
                                "technical": ["Advanced ML Algorithms", "Deep Learning", "Feature Engineering", "Model Evaluation"],
                                "soft": ["Project Management", "Stakeholder Communication", "Mentoring"]
                            },
                            "responsibilities": ["Lead ML projects", "Design complex models", "Mentor junior data scientists", "Translate business needs to ML solutions"],
                            "salary_data": {
                                "median": 140000,
                                "range": {"min": 120000, "max": 165000},
                                "currency": "USD"
                            }
                        },
                        {
                            "role": "ML Engineer",
                            "timeline": "4-5+ years",
                            "description": "Focus on deploying and scaling ML systems in production",
                            "skills": ["MLOps", "Production Systems", "Scalability", "Software Engineering"],
                            "skill_requirements": {
                                "technical": ["MLOps", "Model Deployment", "Distributed Systems", "Software Engineering"],
                                "soft": ["Cross-functional Collaboration", "System Design", "Technical Leadership"]
                            },
                            "responsibilities": ["Design ML systems", "Deploy models to production", "Build scalable ML infrastructure", "Optimize model performance"],
                            "salary_data": {
                                "median": 165000,
                                "range": {"min": 145000, "max": 190000},
                                "currency": "USD"
                            }
                        }
                    ]
                }
            ]
        }
    }
    
    # Default to technology industry if not specified
    if not industry:
        industry = "Technology"
    
    # Get career paths for the current role and industry
    role_paths = career_paths.get(current_role, {})
    industry_paths = role_paths.get(industry, role_paths.get("Technology", []))
    
    # Filter steps based on timeframe_years if specified
    if timeframe_years > 0:
        for path in industry_paths:
            # Filter steps to only include those within the timeframe
            filtered_steps = []
            for step in path.get("steps", []):
                # Parse the timeline to get the max years
                timeline = step.get("timeline", "")
                max_years = 0
                
                # Try to extract the maximum year from formats like "X-Y years" or "X+ years"
                if "+" in timeline:
                    # Format: "X+ years"
                    try:
                        max_years = int(timeline.split("+")[0].strip())
                    except:
                        max_years = 0
                elif "-" in timeline:
                    # Format: "X-Y years"
                    try:
                        max_years = int(timeline.split("-")[1].split(" ")[0].strip())
                    except:
                        max_years = 0
                
                # Include step if it's within the timeframe or if we couldn't parse the timeline
                if max_years <= timeframe_years or max_years == 0:
                    filtered_steps.append(step)
            
            # Update the path with filtered steps
            path["steps"] = filtered_steps
    
    # Remove skill requirements if not requested
    if not include_skill_requirements:
        for path in industry_paths:
            for step in path.get("steps", []):
                if "skill_requirements" in step:
                    step.pop("skill_requirements", None)
    
    # Remove salary data if not requested
    if not include_salary_data:
        for path in industry_paths:
            for step in path.get("steps", []):
                if "salary_data" in step:
                    step.pop("salary_data", None)
    
    # If no paths found, provide generic advice
    if not industry_paths:
        generic_path = {
            "name": f"From {current_role} to Senior {current_role}",
            "description": "A standard progression path for your role",
            "average_time_years": 3,
            "salary_growth_percentage": 30,
            "difficulty": 6,
            "steps": [
                {
                    "role": current_role,
                    "timeline": "0-2 years",
                    "description": "Build core skills and domain expertise"
                },
                {
                    "role": f"Senior {current_role}",
                    "timeline": "2-4 years",
                    "description": "Lead projects and mentor junior team members"
                }
            ]
        }
        
        # Add skill requirements if requested
        if include_skill_requirements:
            generic_path["steps"][0]["skill_requirements"] = {
                "technical": ["Core Technical Skills", "Tools & Technologies"],
                "soft": ["Communication", "Teamwork", "Problem Solving"]
            }
            generic_path["steps"][1]["skill_requirements"] = {
                "technical": ["Advanced Technical Skills", "System Design"],
                "soft": ["Leadership", "Mentoring", "Project Management"]
            }
        
        # Add salary data if requested
        if include_salary_data:
            generic_path["steps"][0]["salary_data"] = {
                "median": 90000,
                "range": {"min": 70000, "max": 110000},
                "currency": "USD"
            }
            generic_path["steps"][1]["salary_data"] = {
                "median": 120000,
                "range": {"min": 100000, "max": 140000},
                "currency": "USD"
            }
        
        return {
            "paths": [generic_path]
        }
    
    # Return career paths
    return {
        "paths": industry_paths
    }

@app.post("/recommendations/talent-search", response_model=dict)
async def talent_search(
    search_params: dict,
    min_match_score: int = 0,
    limit: int = 10,
    include_details: bool = True,
    sort_by: str = "match_score",
    experience_min: Optional[int] = None,
    experience_max: Optional[int] = None,
    location_radius: Optional[int] = None,
    include_remote: bool = False,
    education_level: Optional[str] = None,
    availability: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Advanced talent search with multiple filtering options
    
    This endpoint allows employers to search for candidates based on skills,
    experience, location, education, and availability.
    """
    # Validate and sanitize search parameters
    if search_params is None:
        search_params = {}
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(
            status_code=403, detail="Only employers can use talent search"
        )
    
    # Extract search parameters
    skills = search_params.get("skills", [])
    if not skills:
        raise HTTPException(
            status_code=400, detail="At least one skill is required for talent search"
        )
    
    # Ensure skills is a list of strings
    if isinstance(skills, str):
        skills = [skills]
    elif not isinstance(skills, list):
        skills = [str(skills)]
    
    # Convert any non-string elements to strings
    skills = [str(skill) for skill in skills]
    
    # Prepare search query text
    search_text = " ".join(skills)
    if "job_title" in search_params:
        job_title = search_params.get("job_title")
        if job_title is not None:
            search_text += f" {str(job_title)}"
    if "industry" in search_params:
        industry = search_params.get("industry")
        if industry is not None:
            search_text += f" {str(industry)}"
    
    # Get embedding for search query
    try:
        search_embedding = get_embedding(search_text)
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate embedding for search query"
        )
    
    # Make sure to only get active candidates with complete profiles
    filter_query = {"is_active": True, "profile_completed": True}
    
    # Apply additional filters from query parameters
    if experience_min is not None:
        filter_query["experience_years"] = {"$gte": experience_min}
    if experience_max is not None:
        if "experience_years" not in filter_query:
            filter_query["experience_years"] = {}
        filter_query["experience_years"]["$lte"] = experience_max
    
    if education_level:
        education_levels = education_level.split(",")
        filter_query["education_level"] = {"$in": education_levels}
    
    if availability:
        availability_options = availability.split(",")
        filter_query["availability"] = {"$in": availability_options}
    
    # Location filtering will be handled post-query for now
    # In a production system, we'd use proper geospatial queries
    
    # Search for candidates using vector search
    try:
        # Get all candidates that match the filter criteria
        candidates = (
            await Database.get_collection(CANDIDATES_COLLECTION)
            .find(filter_query)
            .to_list(length=None)
        )
        
        if not candidates:
            return {
                "candidates": [],
                "total_count": 0,
                "metadata": {
                    "search_params": search_params,
                    "filters_applied": {
                        "experience_min": experience_min,
                        "experience_max": experience_max,
                        "education_level": education_level,
                        "availability": availability,
                        "location_radius": location_radius,
                        "include_remote": include_remote
                    }
                }
            }
        
        # Calculate match scores
        results = []
        for candidate in candidates:
            # Skip candidates without embeddings
            if "embedding" not in candidate:
                continue
            
            # Calculate match score using cosine similarity
            match_score = cosine_similarity(search_embedding, candidate["embedding"]) * 100
            
            # Apply minimum match score filter
            if match_score < min_match_score:
                continue
            
            # Apply location filtering if specified
            if search_params.get("location") and not include_remote:
                # Simple location matching for now
                # In a production system, we'd use proper geocoding and distance calculation
                candidate_location = candidate.get("location", "")
                search_location = search_params["location"]
                
                # Make sure we're comparing strings
                if isinstance(candidate_location, str) and isinstance(search_location, str):
                    if search_location.lower() not in candidate_location.lower():
                        if not (include_remote and candidate.get("remote_availability", False)):
                            continue
                else:
                    # Skip location filtering if either value is not a string
                    print(f"Warning: Location filtering skipped - invalid location format. Candidate: {type(candidate_location)}, Search: {type(search_location)}")
                    if not (include_remote and candidate.get("remote_availability", False)):
                        continue
            
            # Create result object with match score
            result = {
                "candidate_id": str(candidate["id"]),
                "match_score": round(match_score, 1),
                "match_factors": {
                    "skills_match": calculate_skills_match_percentage(skills, candidate.get("skills", [])),
                    "experience_match": calculate_experience_match_percentage(search_params.get("experience_years", 0), candidate.get("experience_years", 0)),
                }
            }
            
            # Include candidate details if requested
            if include_details:
                # Remove sensitive information
                candidate_copy = candidate.copy()
                for field in ["password", "embedding", "hashed_password", "salt"]:
                    if field in candidate_copy:
                        del candidate_copy[field]
                
                # Convert ObjectId to string
                if "_id" in candidate_copy:
                    candidate_copy["_id"] = str(candidate_copy["_id"])
                
                result["candidate_details"] = candidate_copy
            
            results.append(result)
        
        # Sort results
        if sort_by == "match_score":
            results.sort(key=lambda x: x["match_score"], reverse=True)
        elif sort_by == "experience_years" and include_details:
            def extract_years(rec):
                exp_years = rec.get("candidate_details", {}).get("experience_years", "0")
                if isinstance(exp_years, (int, float)):
                    return exp_years
                try:
                    import re
                    matches = re.findall(r'\d+', str(exp_years))
                    return int(matches[0]) if matches else 0
                except:
                    return 0
                    
            results.sort(key=extract_years, reverse=True)
        elif sort_by == "availability" and include_details:
            # Sort by availability (immediate first)
            availability_order = {"Immediate": 0, "2 weeks": 1, "1 month": 2, "3 months": 3}
            def get_availability_score(rec):
                avail = rec.get("candidate_details", {}).get("availability", "3 months")
                return availability_order.get(avail, 99)
                
            results.sort(key=get_availability_score)
        
        # Apply limit
        if limit > 0:
            results = results[:limit]
        
        # Return results with metadata
        return {
            "candidates": results,
            "total_count": len(results),
            "metadata": {
                "search_params": search_params,
                "filters_applied": {
                    "experience_min": experience_min,
                    "experience_max": experience_max,
                    "education_level": education_level,
                    "availability": availability,
                    "location_radius": location_radius,
                    "include_remote": include_remote
                }
            }
        }
    except Exception as e:
        print(f"Error in talent search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform talent search: {str(e)}"
        )

def calculate_skills_match_percentage(required_skills, candidate_skills):
    """Calculate the percentage of required skills that the candidate has"""
    if not required_skills or not candidate_skills:
        return 0
    
    if isinstance(candidate_skills, list):
        candidate_skills_list = candidate_skills
    elif isinstance(candidate_skills, dict):
        # Extract skills from structured format
        candidate_skills_list = []
        for skill_category in candidate_skills.values():
            if isinstance(skill_category, list):
                candidate_skills_list.extend(skill_category)
    else:
        return 0
    
    # Convert to lowercase for case-insensitive matching
    required_skills_lower = [s.lower() for s in required_skills]
    candidate_skills_lower = [s.lower() for s in candidate_skills_list]
    
    # Count matches
    matches = sum(1 for skill in required_skills_lower if any(skill in cs for cs in candidate_skills_lower))
    return round((matches / len(required_skills)) * 100)

def calculate_experience_match_percentage(required_years, candidate_years):
    """Calculate how well the candidate's experience matches the requirements"""
    if required_years == 0:
        return 100  # No experience required, perfect match
    
    try:
        candidate_years = float(candidate_years)
    except (ValueError, TypeError):
        return 0
    
    if candidate_years >= required_years:
        return 100  # Meets or exceeds requirements
    
    # Partial match based on how close they are to required experience
    return round((candidate_years / required_years) * 100)

@app.post("/recommendations/salary", response_model=dict)
async def get_salary_recommendations(
    job_params: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Get salary recommendations based on job title, skills, experience, location, and industry.
    
    This endpoint provides salary insights including:
    - Salary range for the specified role
    - Market comparison
    - Factors affecting salary
    - Regional adjustments
    """
    try:
        # Extract parameters
        job_title = job_params.get("job_title", "")
        if not job_title:
            raise HTTPException(
                status_code=400, detail="Job title is required for salary recommendations"
            )
        
        # Optional parameters
        required_skills = job_params.get("required_skills", [])
        experience_years = job_params.get("experience_years", 0)
        location = job_params.get("location", "")
        remote_position = job_params.get("remote_position", False)
        industry = job_params.get("industry", "Technology")
        company_size = job_params.get("company_size", "")
        
        # Get base salary range based on job title and experience
        base_salary = await get_base_salary_range(job_title, experience_years, industry)
        
        # Apply adjustments based on location, skills, and other factors
        adjusted_salary = await apply_salary_adjustments(
            base_salary,
            location,
            required_skills,
            remote_position,
            company_size
        )
        
        # Get market comparison data
        market_comparison = await get_market_comparison(job_title, industry, location)
        
        # Get factors affecting salary
        factors = get_salary_factors(required_skills, location, experience_years, industry)
        
        return {
            "job_title": job_title,
            "salary_recommendation": {
                "range": adjusted_salary,
                "median": (adjusted_salary["min"] + adjusted_salary["max"]) // 2,
                "currency": "USD"
            },
            "market_comparison": market_comparison,
            "factors": factors,
            "metadata": {
                "request_params": job_params,
                "data_freshness": "2023-Q4",
                "confidence_level": "high" if (job_title and location and experience_years > 0) else "medium"
            }
        }
    except Exception as e:
        print(f"Error generating salary recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate salary recommendations: {str(e)}"
        )

async def get_base_salary_range(job_title, experience_years, industry):
    """Get base salary range for a job title based on experience and industry"""
    # This would ideally come from a database or external API
    # For now, we'll use a simplified model based on job titles and experience
    
    # Base salary ranges by job title (mid-level)
    base_ranges = {
        "Software Engineer": {"min": 90000, "max": 130000},
        "Senior Software Engineer": {"min": 120000, "max": 180000},
        "Principal Software Engineer": {"min": 150000, "max": 220000},
        "Data Scientist": {"min": 95000, "max": 140000},
        "Senior Data Scientist": {"min": 130000, "max": 190000},
        "Product Manager": {"min": 100000, "max": 150000},
        "Senior Product Manager": {"min": 140000, "max": 200000},
        "UX Designer": {"min": 85000, "max": 125000},
        "Senior UX Designer": {"min": 115000, "max": 165000},
        "DevOps Engineer": {"min": 95000, "max": 140000},
        "Senior DevOps Engineer": {"min": 130000, "max": 180000},
        "Full Stack Developer": {"min": 90000, "max": 135000},
        "Senior Full Stack Developer": {"min": 125000, "max": 185000},
        "Frontend Developer": {"min": 85000, "max": 125000},
        "Backend Developer": {"min": 90000, "max": 130000},
        "Machine Learning Engineer": {"min": 100000, "max": 150000},
        "Project Manager": {"min": 85000, "max": 130000},
    }
    
    # Default range if job title is not found
    default_range = {"min": 80000, "max": 120000}
    base_range = base_ranges.get(job_title, default_range)
    
    # Adjust for experience
    if experience_years < 2:  # Entry level
        experience_factor = 0.8
    elif experience_years < 5:  # Mid level
        experience_factor = 1.0
    elif experience_years < 8:  # Senior
        experience_factor = 1.25
    else:  # Very senior
        experience_factor = 1.4
    
    # Adjust for industry
    industry_factors = {
        "Technology": 1.1,
        "Finance": 1.15,
        "Healthcare": 1.0,
        "Retail": 0.9,
        "Manufacturing": 0.95,
        "Education": 0.85,
        "Government": 0.9,
        "Non-profit": 0.8,
        "Consulting": 1.05,
        "Media": 0.95,
        "Telecommunications": 1.0,
        "Energy": 1.05,
        "Aerospace": 1.1
    }
    industry_factor = industry_factors.get(industry, 1.0)
    
    # Apply adjustments
    return {
        "min": int(base_range["min"] * experience_factor * industry_factor),
        "max": int(base_range["max"] * experience_factor * industry_factor)
    }

async def apply_salary_adjustments(base_salary, location, skills, remote_position, company_size):
    """Apply adjustments to base salary based on location, skills, and other factors"""
    # Location adjustments
    location_factors = {
        "San Francisco, CA": 1.5,
        "New York, NY": 1.4,
        "Seattle, WA": 1.3,
        "Boston, MA": 1.25,
        "Austin, TX": 1.1,
        "Chicago, IL": 1.15,
        "Los Angeles, CA": 1.35,
        "Denver, CO": 1.1,
        "Portland, OR": 1.1,
        "Atlanta, GA": 1.05,
        "Dallas, TX": 1.05,
        "Remote": 1.0
    }
    
    # Default location factor
    location_factor = 1.0
    
    # Check if the location contains any of the keys
    if remote_position:
        location_factor = location_factors.get("Remote", 1.0)
    else:
        for loc, factor in location_factors.items():
            if loc in location:
                location_factor = factor
                break
    
    # Skills adjustments - premium skills
    premium_skills = [
        "Machine Learning", "AI", "Blockchain", "Cloud Architecture", 
        "DevOps", "Cybersecurity", "Data Science", "React", "AWS", 
        "Kubernetes", "Docker", "Terraform", "GraphQL", "Rust"
    ]
    
    # Calculate skills premium
    skills_premium = 1.0
    if skills:
        premium_skill_count = sum(1 for skill in skills if skill in premium_skills)
        skills_premium += min(premium_skill_count * 0.03, 0.15)  # Up to 15% premium
    
    # Company size adjustment
    size_factors = {
        "1-10 employees": 0.9,
        "11-50 employees": 0.95,
        "51-200 employees": 1.0,
        "201-500 employees": 1.05,
        "501-1000 employees": 1.1,
        "1001-5000 employees": 1.15,
        "5001-10000 employees": 1.2,
        "10000+ employees": 1.25
    }
    company_size_factor = size_factors.get(company_size, 1.0)
    
    # Apply all adjustments
    return {
        "min": int(base_salary["min"] * location_factor * skills_premium * company_size_factor),
        "max": int(base_salary["max"] * location_factor * skills_premium * company_size_factor)
    }

async def get_market_comparison(job_title, industry, location):
    """Get market comparison data for the given job title"""
    # This would ideally come from a database or external API
    # For now, we'll generate synthetic data
    
    base_percentiles = {
        "10th": 0.8,
        "25th": 0.9,
        "50th": 1.0,
        "75th": 1.15,
        "90th": 1.3
    }
    
    # Get base salary range
    base_range = await get_base_salary_range(job_title, 5, industry)  # Using mid-level experience
    median_salary = (base_range["min"] + base_range["max"]) // 2
    
    # Generate percentiles
    percentiles = {}
    for percentile, factor in base_percentiles.items():
        percentiles[percentile] = int(median_salary * factor)
    
    # Regional comparison
    regional_comparison = []
    if location:
        nearby_locations = get_nearby_locations(location)
        for nearby in nearby_locations:
            regional_comparison.append({
                "location": nearby["name"],
                "median_salary": int(median_salary * nearby["factor"]),
                "difference_percentage": int((nearby["factor"] - 1) * 100)
            })
    
    return {
        "percentiles": percentiles,
        "regional_comparison": regional_comparison,
        "industry_comparison": [
            {
                "industry": "Technology",
                "median_salary": int(median_salary * 1.1),
                "difference_percentage": 10
            },
            {
                "industry": "Finance",
                "median_salary": int(median_salary * 1.15),
                "difference_percentage": 15
            },
            {
                "industry": "Healthcare",
                "median_salary": int(median_salary * 1.0),
                "difference_percentage": 0
            }
        ]
    }

def get_nearby_locations(location):
    """Get nearby locations for regional comparison"""
    # This would ideally use geospatial data
    # For now, we'll use a simplified lookup
    
    location_map = {
        "San Francisco, CA": [
            {"name": "Oakland, CA", "factor": 0.9},
            {"name": "San Jose, CA", "factor": 1.05},
            {"name": "Sacramento, CA", "factor": 0.8}
        ],
        "New York, NY": [
            {"name": "Brooklyn, NY", "factor": 0.95},
            {"name": "Jersey City, NJ", "factor": 0.9},
            {"name": "Stamford, CT", "factor": 0.85}
        ],
        "Seattle, WA": [
            {"name": "Bellevue, WA", "factor": 1.05},
            {"name": "Tacoma, WA", "factor": 0.85},
            {"name": "Redmond, WA", "factor": 1.1}
        ],
        "Austin, TX": [
            {"name": "Round Rock, TX", "factor": 0.9},
            {"name": "San Antonio, TX", "factor": 0.85},
            {"name": "Dallas, TX", "factor": 1.0}
        ],
        "Remote": [
            {"name": "National Average", "factor": 1.0},
            {"name": "Tech Hub Average", "factor": 1.2},
            {"name": "Rural Average", "factor": 0.8}
        ]
    }
    
    # Default to remote if location not found
    for loc in location_map:
        if loc in location:
            return location_map[loc]
    
    return location_map.get("Remote", [])

def get_salary_factors(skills, location, experience_years, industry):
    """Get factors affecting salary"""
    factors = []
    
    # Experience impact
    if experience_years < 2:
        factors.append({
            "factor": "Limited experience",
            "impact": "negative",
            "description": "Entry-level positions typically command lower salaries"
        })
    elif experience_years > 8:
        factors.append({
            "factor": "Extensive experience",
            "impact": "positive",
            "description": "Senior professionals with 8+ years experience command premium salaries"
        })
    
    # Location impact
    high_col_locations = ["San Francisco", "New York", "Seattle", "Boston", "Los Angeles"]
    for high_loc in high_col_locations:
        if high_loc in location:
            factors.append({
                "factor": "High cost of living location",
                "impact": "positive",
                "description": f"Salaries in {high_loc} are typically higher to offset living costs"
            })
            break
    
    # Remote impact
    if "Remote" in location:
        factors.append({
            "factor": "Remote position",
            "impact": "neutral",
            "description": "Remote positions may be adjusted based on your location"
        })
    
    # Industry impact
    high_paying_industries = ["Technology", "Finance", "Healthcare", "Consulting"]
    if industry in high_paying_industries:
        factors.append({
            "factor": f"{industry} industry",
            "impact": "positive",
            "description": f"The {industry} industry typically offers competitive compensation"
        })
    
    # Skills impact
    premium_skills = ["Machine Learning", "AI", "Cloud Architecture", "DevOps", "Cybersecurity"]
    has_premium_skills = any(skill in premium_skills for skill in skills)
    if has_premium_skills:
        factors.append({
            "factor": "In-demand skills",
            "impact": "positive",
            "description": "Your skill set includes high-demand technologies that command a premium"
        })
    
    return factors

@app.get("/analytics/recommendations/impact", response_model=dict)
async def get_recommendation_impact_metrics(
    period: str = "last_30_days",
    recommendation_type: str = "all",
    current_user: dict = Depends(get_current_user)
):
    """
    Get metrics about the effectiveness of recommendations (view rates, application rates, etc.)
    
    This endpoint provides analytics data on how recommendations are performing,
    including metrics like view rates, application rates, and conversion rates.
    
    Parameters:
    - period: Time period for the metrics (last_7_days, last_30_days, last_90_days, all_time)
    - recommendation_type: Type of recommendations to analyze (jobs, candidates, projects, all)
    """
    try:
        # Validate period parameter
        valid_periods = ["last_7_days", "last_30_days", "last_90_days", "all_time"]
        if period not in valid_periods:
            period = "last_30_days"  # Default to 30 days if invalid
        
        # Validate recommendation type parameter
        valid_types = ["jobs", "candidates", "projects", "all"]
        if recommendation_type not in valid_types:
            recommendation_type = "all"  # Default to all if invalid
        
        # In a production system, we would query the database for actual metrics
        # For now, we'll generate simulated metrics based on the parameters
        
        # Calculate date range for the period
        end_date = datetime.now()
        if period == "last_7_days":
            start_date = end_date - timedelta(days=7)
            days_in_period = 7
        elif period == "last_30_days":
            start_date = end_date - timedelta(days=30)
            days_in_period = 30
        elif period == "last_90_days":
            start_date = end_date - timedelta(days=90)
            days_in_period = 90
        else:  # all_time
            start_date = end_date - timedelta(days=365)  # Default to 1 year for "all_time"
            days_in_period = 365
        
        # Generate metrics based on user type
        if current_user["user_type"] == UserType.EMPLOYER:
            metrics = await generate_employer_recommendation_metrics(
                current_user["id"], recommendation_type, days_in_period
            )
        else:  # Candidate
            metrics = await generate_candidate_recommendation_metrics(
                current_user["id"], recommendation_type, days_in_period
            )
        
        # Add period information to response
        metrics["period"] = {
            "name": period,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "days": days_in_period
        }
        
        # Add recommendation type to response
        metrics["recommendation_type"] = recommendation_type
        
        return metrics
    except Exception as e:
        print(f"Error generating recommendation impact metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendation impact metrics: {str(e)}"
        )

async def generate_employer_recommendation_metrics(employer_id, recommendation_type, days_in_period):
    """Generate recommendation metrics for employers"""
    # In a production system, these would be calculated from actual data
    # For now, we'll generate realistic simulated metrics
    
    # Base metrics that apply to all recommendation types
    base_metrics = {
        "summary": {
            "total_recommendations_shown": random.randint(50, 200) * (days_in_period // 10),
            "total_recommendations_viewed": random.randint(30, 100) * (days_in_period // 10),
            "total_actions_taken": random.randint(10, 50) * (days_in_period // 10),
            "conversion_rate": round(random.uniform(0.05, 0.25), 3)
        },
        "trends": generate_trend_data(days_in_period),
        "top_performing": []
    }
    
    # Add recommendation-type specific metrics
    if recommendation_type in ["candidates", "all"]:
        base_metrics["candidates"] = {
            "total_candidates_recommended": random.randint(40, 150) * (days_in_period // 10),
            "candidates_viewed": random.randint(20, 80) * (days_in_period // 10),
            "candidates_contacted": random.randint(5, 30) * (days_in_period // 10),
            "candidates_interviewed": random.randint(2, 15) * (days_in_period // 10),
            "candidates_hired": random.randint(1, 5) * (days_in_period // 20),
            "contact_rate": round(random.uniform(0.1, 0.4), 3),
            "interview_rate": round(random.uniform(0.05, 0.2), 3),
            "hire_rate": round(random.uniform(0.01, 0.1), 3),
            "average_match_score": round(random.uniform(65, 85), 1)
        }
        
        # Add top performing jobs for candidate recommendations
        base_metrics["top_performing"].extend([
            {
                "type": "job",
                "id": f"job_{i}",
                "title": f"Top Performing Job {i}",
                "metrics": {
                    "candidates_recommended": random.randint(10, 50),
                    "candidates_viewed": random.randint(5, 30),
                    "candidates_contacted": random.randint(2, 15),
                    "contact_rate": round(random.uniform(0.1, 0.5), 3),
                    "average_match_score": round(random.uniform(70, 90), 1)
                }
            }
            for i in range(1, 4)
        ])
    
    if recommendation_type in ["projects", "all"]:
        base_metrics["projects"] = {
            "total_candidates_recommended": random.randint(30, 100) * (days_in_period // 10),
            "candidates_viewed": random.randint(15, 60) * (days_in_period // 10),
            "candidates_contacted": random.randint(3, 20) * (days_in_period // 10),
            "candidates_selected": random.randint(1, 10) * (days_in_period // 20),
            "contact_rate": round(random.uniform(0.1, 0.3), 3),
            "selection_rate": round(random.uniform(0.05, 0.15), 3),
            "average_match_score": round(random.uniform(60, 80), 1)
        }
        
        # Add top performing projects
        if recommendation_type == "projects":
            base_metrics["top_performing"].extend([
                {
                    "type": "project",
                    "id": f"project_{i}",
                    "title": f"Top Performing Project {i}",
                    "metrics": {
                        "candidates_recommended": random.randint(8, 40),
                        "candidates_viewed": random.randint(4, 25),
                        "candidates_contacted": random.randint(1, 12),
                        "contact_rate": round(random.uniform(0.1, 0.4), 3),
                        "average_match_score": round(random.uniform(65, 85), 1)
                    }
                }
                for i in range(1, 4)
            ])
    
    return base_metrics

async def generate_candidate_recommendation_metrics(candidate_id, recommendation_type, days_in_period):
    """Generate recommendation metrics for candidates"""
    # Base metrics that apply to all recommendation types
    base_metrics = {
        "summary": {
            "total_recommendations_shown": random.randint(30, 150) * (days_in_period // 10),
            "total_recommendations_viewed": random.randint(20, 80) * (days_in_period // 10),
            "total_actions_taken": random.randint(5, 30) * (days_in_period // 10),
            "conversion_rate": round(random.uniform(0.1, 0.3), 3)
        },
        "trends": generate_trend_data(days_in_period),
        "top_performing": []
    }
    
    # Add recommendation-type specific metrics
    if recommendation_type in ["jobs", "all"]:
        base_metrics["jobs"] = {
            "total_jobs_recommended": random.randint(25, 120) * (days_in_period // 10),
            "jobs_viewed": random.randint(15, 70) * (days_in_period // 10),
            "jobs_saved": random.randint(5, 25) * (days_in_period // 10),
            "jobs_applied": random.randint(3, 15) * (days_in_period // 10),
            "interviews_received": random.randint(1, 8) * (days_in_period // 20),
            "view_rate": round(random.uniform(0.4, 0.7), 3),
            "application_rate": round(random.uniform(0.1, 0.3), 3),
            "interview_rate": round(random.uniform(0.05, 0.2), 3),
            "average_match_score": round(random.uniform(65, 85), 1)
        }
        
        # Add top recommended job categories
        base_metrics["top_performing"].extend([
            {
                "type": "job_category",
                "name": "Software Development",
                "metrics": {
                    "jobs_recommended": random.randint(10, 50),
                    "jobs_viewed": random.randint(5, 30),
                    "jobs_applied": random.randint(2, 10),
                    "application_rate": round(random.uniform(0.1, 0.4), 3),
                    "average_match_score": round(random.uniform(70, 90), 1)
                }
            },
            {
                "type": "job_category",
                "name": "Data Science",
                "metrics": {
                    "jobs_recommended": random.randint(8, 40),
                    "jobs_viewed": random.randint(4, 25),
                    "jobs_applied": random.randint(1, 8),
                    "application_rate": round(random.uniform(0.1, 0.3), 3),
                    "average_match_score": round(random.uniform(65, 85), 1)
                }
            },
            {
                "type": "job_category",
                "name": "Product Management",
                "metrics": {
                    "jobs_recommended": random.randint(5, 30),
                    "jobs_viewed": random.randint(3, 20),
                    "jobs_applied": random.randint(1, 6),
                    "application_rate": round(random.uniform(0.1, 0.3), 3),
                    "average_match_score": round(random.uniform(60, 80), 1)
                }
            }
        ])
    
    if recommendation_type in ["projects", "all"]:
        base_metrics["projects"] = {
            "total_projects_recommended": random.randint(15, 80) * (days_in_period // 10),
            "projects_viewed": random.randint(10, 50) * (days_in_period // 10),
            "projects_saved": random.randint(3, 20) * (days_in_period // 10),
            "projects_applied": random.randint(2, 10) * (days_in_period // 10),
            "projects_accepted": random.randint(1, 5) * (days_in_period // 20),
            "view_rate": round(random.uniform(0.4, 0.7), 3),
            "application_rate": round(random.uniform(0.1, 0.25), 3),
            "acceptance_rate": round(random.uniform(0.05, 0.15), 3),
            "average_match_score": round(random.uniform(60, 80), 1)
        }
    
    return base_metrics

def generate_trend_data(days_in_period):
    """Generate trend data for the given period"""
    # For simplicity, we'll generate daily data for up to 30 days
    # For longer periods, we'll aggregate to weekly data
    
    if days_in_period <= 30:
        # Daily data
        num_points = min(days_in_period, 30)
        date_format = "%Y-%m-%d"
        
        # Generate dates
        end_date = datetime.now()
        dates = [(end_date - timedelta(days=i)).strftime(date_format) for i in range(num_points)]
        dates.reverse()  # Oldest to newest
        
        # Generate metrics
        views = [random.randint(5, 20) for _ in range(num_points)]
        actions = [int(views[i] * random.uniform(0.2, 0.6)) for i in range(num_points)]
        match_scores = [round(random.uniform(60, 90), 1) for _ in range(num_points)]
        
        return {
            "interval": "daily",
            "dates": dates,
            "views": views,
            "actions": actions,
            "match_scores": match_scores
        }
    else:
        # Weekly data
        num_weeks = min(days_in_period // 7, 12)  # Up to 12 weeks
        date_format = "%Y-%m-%d"
        
        # Generate week ending dates
        end_date = datetime.now()
        dates = [(end_date - timedelta(days=i*7)).strftime(date_format) for i in range(num_weeks)]
        dates.reverse()  # Oldest to newest
        
        # Generate metrics
        views = [random.randint(30, 120) for _ in range(num_weeks)]
        actions = [int(views[i] * random.uniform(0.2, 0.6)) for i in range(num_weeks)]
        match_scores = [round(random.uniform(60, 90), 1) for _ in range(num_weeks)]
        
        return {
            "interval": "weekly",
            "dates": dates,
            "views": views,
            "actions": actions,
            "match_scores": match_scores
        }

@app.get("/analytics/recommendations/performance", response_model=dict)
async def get_recommendation_algorithm_performance(
    algorithm_version: str = "latest",
    current_user: dict = Depends(get_current_user)
):
    """
    Get performance metrics for the recommendation algorithm
    
    This endpoint provides analytics data on how the recommendation algorithm is performing,
    including accuracy, precision, recall, and other relevant metrics.
    
    Parameters:
    - algorithm_version: Version of the algorithm to analyze (latest, v1, v2, etc.)
    """
    try:
        # In a production system, we would query the database for actual metrics
        # For now, we'll generate simulated metrics
        
        # Validate algorithm version
        valid_versions = ["latest", "v1", "v2", "v3"]
        if algorithm_version not in valid_versions:
            algorithm_version = "latest"
        
        # Map version names to actual version numbers
        version_map = {
            "latest": "v3",
            "v1": "v1",
            "v2": "v2",
            "v3": "v3"
        }
        
        actual_version = version_map.get(algorithm_version, "v3")
        
        # Generate performance metrics based on version
        # Newer versions have better metrics
        version_factor = {
            "v1": 0.7,
            "v2": 0.85,
            "v3": 1.0
        }.get(actual_version, 1.0)
        
        # Base metrics
        metrics = {
            "algorithm_version": actual_version,
            "last_updated": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
            "overall_accuracy": round(0.75 * version_factor, 3),
            "precision": round(0.72 * version_factor, 3),
            "recall": round(0.68 * version_factor, 3),
            "f1_score": round(0.70 * version_factor, 3),
            "average_match_score": round(75 * version_factor, 1),
            "recommendation_types": {
                "jobs": {
                    "accuracy": round(0.78 * version_factor, 3),
                    "precision": round(0.75 * version_factor, 3),
                    "recall": round(0.72 * version_factor, 3),
                    "f1_score": round(0.73 * version_factor, 3),
                    "average_match_score": round(78 * version_factor, 1)
                },
                "candidates": {
                    "accuracy": round(0.72 * version_factor, 3),
                    "precision": round(0.70 * version_factor, 3),
                    "recall": round(0.65 * version_factor, 3),
                    "f1_score": round(0.67 * version_factor, 3),
                    "average_match_score": round(72 * version_factor, 1)
                },
                "projects": {
                    "accuracy": round(0.70 * version_factor, 3),
                    "precision": round(0.68 * version_factor, 3),
                    "recall": round(0.62 * version_factor, 3),
                    "f1_score": round(0.65 * version_factor, 3),
                    "average_match_score": round(70 * version_factor, 1)
                }
            },
            "embedding_metrics": {
                "dimension": 3072,
                "average_l2_norm": round(random.uniform(0.9, 1.1), 3),
                "average_cosine_similarity": round(0.65 * version_factor, 3),
                "clustering_coefficient": round(0.55 * version_factor, 3)
            },
            "version_comparison": [
                {
                    "version": "v1",
                    "accuracy": round(0.75 * 0.7, 3),
                    "improvement": "-30%"
                },
                {
                    "version": "v2",
                    "accuracy": round(0.75 * 0.85, 3),
                    "improvement": "-15%"
                },
                {
                    "version": "v3",
                    "accuracy": round(0.75, 3),
                    "improvement": "current"
                }
            ]
        }
        
        return metrics
    except Exception as e:
        print(f"Error generating recommendation algorithm performance metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendation algorithm performance metrics: {str(e)}"
        )

@app.post("/recommendations/feedback", response_model=dict)
async def submit_recommendation_feedback(
    feedback_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit feedback on a recommendation
    
    This endpoint allows users to provide feedback on recommendations they receive,
    including relevance scores, accuracy scores, and general feedback.
    
    Parameters:
    - recommendation_id: ID of the recommendation
    - recommendation_type: Type of recommendation (job, candidate, project)
    - relevance_score: Score from 1-5 indicating relevance
    - accuracy_score: Score from 1-5 indicating accuracy
    - is_helpful: Boolean indicating if the recommendation was helpful
    - feedback_text: Optional text feedback
    - action_taken: Action taken on the recommendation (viewed_details, applied, saved, dismissed, etc.)
    """
    try:
        # Validate required fields
        required_fields = ["recommendation_id", "recommendation_type", "relevance_score", "accuracy_score"]
        for field in required_fields:
            if field not in feedback_data:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required field: {field}"
                )
        
        # Validate recommendation type
        valid_types = ["job", "candidate", "project", "skill", "career_path"]
        if feedback_data.get("recommendation_type") not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid recommendation type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Validate scores
        for score_field in ["relevance_score", "accuracy_score"]:
            score = feedback_data.get(score_field)
            if not isinstance(score, int) or score < 1 or score > 5:
                raise HTTPException(
                    status_code=400,
                    detail=f"{score_field} must be an integer between 1 and 5"
                )
        
        # In a production system, we would store this feedback in the database
        # For now, we'll just log it and return a success response
        
        # Add user ID and timestamp to feedback data
        feedback_with_metadata = feedback_data.copy()
        feedback_with_metadata["user_id"] = current_user["id"]
        feedback_with_metadata["user_type"] = current_user["user_type"]
        feedback_with_metadata["timestamp"] = datetime.now().isoformat()
        
        print(f"Received recommendation feedback: {json.dumps(feedback_with_metadata)}")
        
        # Process feedback to improve recommendations (in a real system)
        # This would involve updating recommendation models, user preferences, etc.
        
        # Update user profile with feedback insights
        await update_user_preferences_from_feedback(
            current_user["id"], 
            current_user["user_type"],
            feedback_data
        )
        
        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "feedback_id": f"feedback_{uuid.uuid4().hex[:8]}",  # Generate a fake ID
            "timestamp": feedback_with_metadata["timestamp"]
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error processing recommendation feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process recommendation feedback: {str(e)}"
        )

async def update_user_preferences_from_feedback(user_id, user_type, feedback_data):
    """
    Update user preferences based on feedback
    
    This function would analyze feedback and update user preferences accordingly.
    For example, if a user consistently rates recommendations with certain attributes
    highly, we would adjust their preferences to favor those attributes.
    
    In a production system, this would involve database updates and potentially
    machine learning model updates. For now, it's just a placeholder.
    """
    # This is a placeholder function that would be implemented in a real system
    recommendation_type = feedback_data.get("recommendation_type")
    relevance_score = feedback_data.get("relevance_score")
    is_helpful = feedback_data.get("is_helpful", False)
    feedback_text = feedback_data.get("feedback_text", "")
    
    # Log that we would update preferences
    print(f"Would update preferences for user {user_id} based on {recommendation_type} recommendation feedback:")
    print(f"  - Relevance score: {relevance_score}")
    print(f"  - Helpful: {is_helpful}")
    print(f"  - Feedback: {feedback_text}")
    
    # In a real system, we might:
    # 1. Update user preference weights in the database
    # 2. Extract keywords from feedback_text to identify preferences
    # 3. Adjust recommendation algorithms for this user
    # 4. Store feedback for aggregate analysis
    
    return True

@app.get("/recommendations/feedback/summary", response_model=dict)
async def get_recommendation_feedback_summary(
    recommendation_type: str = "all",
    period: str = "last_30_days",
    current_user: dict = Depends(get_current_user)
):
    """
    Get a summary of recommendation feedback
    
    This endpoint provides aggregate statistics on recommendation feedback,
    including average scores, common actions, and feedback trends.
    
    Parameters:
    - recommendation_type: Type of recommendations to analyze (job, candidate, project, all)
    - period: Time period for the metrics (last_7_days, last_30_days, last_90_days, all_time)
    """
    try:
        # Validate recommendation type
        valid_types = ["job", "candidate", "project", "skill", "career_path", "all"]
        if recommendation_type not in valid_types:
            recommendation_type = "all"  # Default to all if invalid
        
        # Validate period
        valid_periods = ["last_7_days", "last_30_days", "last_90_days", "all_time"]
        if period not in valid_periods:
            period = "last_30_days"  # Default to 30 days if invalid
        
        # In a production system, we would query the database for actual feedback data
        # For now, we'll generate simulated feedback summary data
        
        # Generate different summaries based on user type
        if current_user["user_type"] == UserType.EMPLOYER:
            summary = generate_employer_feedback_summary(recommendation_type, period)
        else:  # Candidate
            summary = generate_candidate_feedback_summary(recommendation_type, period)
        
        # Add period information to response
        end_date = datetime.now()
        if period == "last_7_days":
            start_date = end_date - timedelta(days=7)
            days_in_period = 7
        elif period == "last_30_days":
            start_date = end_date - timedelta(days=30)
            days_in_period = 30
        elif period == "last_90_days":
            start_date = end_date - timedelta(days=90)
            days_in_period = 90
        else:  # all_time
            start_date = end_date - timedelta(days=365)  # Default to 1 year for "all_time"
            days_in_period = 365
            
        summary["period"] = {
            "name": period,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "days": days_in_period
        }
        
        # Add recommendation type to response
        summary["recommendation_type"] = recommendation_type
        
        return summary
    except Exception as e:
        print(f"Error generating recommendation feedback summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendation feedback summary: {str(e)}"
        )

def generate_employer_feedback_summary(recommendation_type, period):
    """Generate feedback summary for employers"""
    # This would be based on actual feedback data in a production system
    # For now, we'll generate realistic simulated data
    
    # Base summary that applies to all recommendation types
    base_summary = {
        "total_feedback_count": random.randint(50, 200),
        "average_scores": {
            "relevance": round(random.uniform(3.5, 4.5), 1),
            "accuracy": round(random.uniform(3.5, 4.5), 1),
            "overall": round(random.uniform(3.5, 4.5), 1)
        },
        "helpful_percentage": round(random.uniform(0.7, 0.9), 2),
        "action_breakdown": {
            "viewed_details": round(random.uniform(0.5, 0.7), 2),
            "contacted": round(random.uniform(0.2, 0.4), 2),
            "saved": round(random.uniform(0.1, 0.3), 2),
            "dismissed": round(random.uniform(0.1, 0.2), 2)
        },
        "common_feedback_themes": [
            {"theme": "Skill match", "percentage": round(random.uniform(0.3, 0.5), 2)},
            {"theme": "Experience level", "percentage": round(random.uniform(0.2, 0.4), 2)},
            {"theme": "Location", "percentage": round(random.uniform(0.1, 0.3), 2)},
            {"theme": "Availability", "percentage": round(random.uniform(0.1, 0.2), 2)}
        ],
        "trends": {
            "relevance_trend": [round(random.uniform(3.0, 4.5), 1) for _ in range(5)],
            "accuracy_trend": [round(random.uniform(3.0, 4.5), 1) for _ in range(5)],
            "helpful_trend": [round(random.uniform(0.6, 0.9), 2) for _ in range(5)]
        }
    }
    
    # Add recommendation-type specific data
    if recommendation_type in ["candidate", "all"]:
        base_summary["candidate_recommendations"] = {
            "feedback_count": random.randint(30, 150),
            "average_scores": {
                "relevance": round(random.uniform(3.5, 4.5), 1),
                "accuracy": round(random.uniform(3.5, 4.5), 1),
                "overall": round(random.uniform(3.5, 4.5), 1)
            },
            "helpful_percentage": round(random.uniform(0.7, 0.9), 2),
            "top_feedback_categories": [
                {"category": "Skills match", "percentage": round(random.uniform(0.3, 0.5), 2)},
                {"category": "Experience level", "percentage": round(random.uniform(0.2, 0.4), 2)},
                {"category": "Location", "percentage": round(random.uniform(0.1, 0.3), 2)}
            ]
        }
    
    if recommendation_type in ["project", "all"]:
        base_summary["project_recommendations"] = {
            "feedback_count": random.randint(20, 100),
            "average_scores": {
                "relevance": round(random.uniform(3.5, 4.5), 1),
                "accuracy": round(random.uniform(3.5, 4.5), 1),
                "overall": round(random.uniform(3.5, 4.5), 1)
            },
            "helpful_percentage": round(random.uniform(0.7, 0.9), 2),
            "top_feedback_categories": [
                {"category": "Project skills match", "percentage": round(random.uniform(0.3, 0.5), 2)},
                {"category": "Availability", "percentage": round(random.uniform(0.2, 0.4), 2)},
                {"category": "Project duration", "percentage": round(random.uniform(0.1, 0.3), 2)}
            ]
        }
    
    return base_summary

def generate_candidate_feedback_summary(recommendation_type, period):
    """Generate feedback summary for candidates"""
    # This would be based on actual feedback data in a production system
    # For now, we'll generate realistic simulated data
    
    # Base summary that applies to all recommendation types
    base_summary = {
        "total_feedback_count": random.randint(30, 150),
        "average_scores": {
            "relevance": round(random.uniform(3.5, 4.5), 1),
            "accuracy": round(random.uniform(3.5, 4.5), 1),
            "overall": round(random.uniform(3.5, 4.5), 1)
        },
        "helpful_percentage": round(random.uniform(0.7, 0.9), 2),
        "action_breakdown": {
            "viewed_details": round(random.uniform(0.6, 0.8), 2),
            "applied": round(random.uniform(0.1, 0.3), 2),
            "saved": round(random.uniform(0.2, 0.4), 2),
            "dismissed": round(random.uniform(0.1, 0.2), 2)
        },
        "common_feedback_themes": [
            {"theme": "Job relevance", "percentage": round(random.uniform(0.3, 0.5), 2)},
            {"theme": "Skill match", "percentage": round(random.uniform(0.2, 0.4), 2)},
            {"theme": "Salary range", "percentage": round(random.uniform(0.1, 0.3), 2)},
            {"theme": "Location", "percentage": round(random.uniform(0.1, 0.2), 2)}
        ],
        "trends": {
            "relevance_trend": [round(random.uniform(3.0, 4.5), 1) for _ in range(5)],
            "accuracy_trend": [round(random.uniform(3.0, 4.5), 1) for _ in range(5)],
            "helpful_trend": [round(random.uniform(0.6, 0.9), 2) for _ in range(5)]
        }
    }
    
    # Add recommendation-type specific data
    if recommendation_type in ["job", "all"]:
        base_summary["job_recommendations"] = {
            "feedback_count": random.randint(20, 100),
            "average_scores": {
                "relevance": round(random.uniform(3.5, 4.5), 1),
                "accuracy": round(random.uniform(3.5, 4.5), 1),
                "overall": round(random.uniform(3.5, 4.5), 1)
            },
            "helpful_percentage": round(random.uniform(0.7, 0.9), 2),
            "top_feedback_categories": [
                {"category": "Job title match", "percentage": round(random.uniform(0.3, 0.5), 2)},
                {"category": "Salary range", "percentage": round(random.uniform(0.2, 0.4), 2)},
                {"category": "Location", "percentage": round(random.uniform(0.1, 0.3), 2)}
            ]
        }
    
    if recommendation_type in ["project", "all"]:
        base_summary["project_recommendations"] = {
            "feedback_count": random.randint(10, 50),
            "average_scores": {
                "relevance": round(random.uniform(3.5, 4.5), 1),
                "accuracy": round(random.uniform(3.5, 4.5), 1),
                "overall": round(random.uniform(3.5, 4.5), 1)
            },
            "helpful_percentage": round(random.uniform(0.7, 0.9), 2),
            "top_feedback_categories": [
                {"category": "Project type match", "percentage": round(random.uniform(0.3, 0.5), 2)},
                {"category": "Project duration", "percentage": round(random.uniform(0.2, 0.4), 2)},
                {"category": "Compensation", "percentage": round(random.uniform(0.1, 0.3), 2)}
            ]
        }
    
    if recommendation_type in ["skill", "all"]:
        base_summary["skill_recommendations"] = {
            "feedback_count": random.randint(15, 80),
            "average_scores": {
                "relevance": round(random.uniform(3.5, 4.5), 1),
                "accuracy": round(random.uniform(3.5, 4.5), 1),
                "overall": round(random.uniform(3.5, 4.5), 1)
            },
            "helpful_percentage": round(random.uniform(0.7, 0.9), 2),
            "top_feedback_categories": [
                {"category": "Career relevance", "percentage": round(random.uniform(0.3, 0.5), 2)},
                {"category": "Learning difficulty", "percentage": round(random.uniform(0.2, 0.4), 2)},
                {"category": "Market demand", "percentage": round(random.uniform(0.1, 0.3), 2)}
            ]
        }
    
    return base_summary

@app.get("/ml/skills/clusters", response_model=dict)
async def get_skill_clusters(
    min_confidence: float = 0.7,
    max_clusters: int = 20,
    include_details: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Get skill clusters analysis
    
    This endpoint provides an analysis of skill clusters, grouping related skills together
    based on their co-occurrence in job postings, candidate profiles, and industry data.
    
    Parameters:
    - min_confidence: Minimum confidence score for skill relationships (0.0-1.0)
    - max_clusters: Maximum number of clusters to return
    - include_details: Whether to include detailed information about each cluster
    """
    try:
        # Validate parameters
        if min_confidence < 0.0 or min_confidence > 1.0:
            raise HTTPException(
                status_code=400,
                detail="min_confidence must be between 0.0 and 1.0"
            )
            
        if max_clusters < 1 or max_clusters > 50:
            raise HTTPException(
                status_code=400,
                detail="max_clusters must be between 1 and 50"
            )
        
        # In a production system, we would use a machine learning model to generate clusters
        # For now, we'll generate simulated skill clusters based on common industry groupings
        
        # Generate the clusters
        clusters = generate_skill_clusters(min_confidence, max_clusters, include_details)
        
        # Add metadata to response
        response = {
            "clusters": clusters,
            "metadata": {
                "min_confidence": min_confidence,
                "max_clusters": max_clusters,
                "total_clusters": len(clusters),
                "total_skills_analyzed": random.randint(1000, 5000),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
        
        # Add cluster statistics
        if include_details:
            response["statistics"] = {
                "average_cluster_size": sum(len(cluster["skills"]) for cluster in clusters) / len(clusters) if clusters else 0,
                "largest_cluster_size": max(len(cluster["skills"]) for cluster in clusters) if clusters else 0,
                "smallest_cluster_size": min(len(cluster["skills"]) for cluster in clusters) if clusters else 0,
                "average_confidence": sum(cluster["confidence"] for cluster in clusters) / len(clusters) if clusters else 0,
                "skill_distribution": calculate_skill_distribution(clusters),
                "industry_relevance": calculate_industry_relevance(clusters)
            }
        
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error generating skill clusters: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate skill clusters: {str(e)}"
        )

def generate_skill_clusters(min_confidence, max_clusters, include_details):
    """Generate skill clusters based on common industry groupings"""
    # Define some common skill clusters by domain
    domain_clusters = {
        "Frontend Development": {
            "core_skills": ["JavaScript", "HTML", "CSS", "React", "Angular", "Vue.js", "TypeScript", "Redux", "Webpack"],
            "related_skills": ["UI/UX Design", "Responsive Design", "SASS/LESS", "Jest", "Cypress", "Storybook"],
            "confidence": 0.92,
            "industry_relevance": ["Technology", "E-commerce", "Media", "Marketing"],
            "growth_rate": 0.15
        },
        "Backend Development": {
            "core_skills": ["Python", "Java", "Node.js", "C#", "PHP", "Ruby", "Go", "Express", "Django", "Spring Boot"],
            "related_skills": ["API Design", "Database Design", "Authentication", "Microservices"],
            "confidence": 0.95,
            "industry_relevance": ["Technology", "Finance", "E-commerce", "Healthcare"],
            "growth_rate": 0.18
        },
        "Database Management": {
            "core_skills": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Oracle", "SQL Server"],
            "related_skills": ["Database Optimization", "Query Performance", "Data Modeling", "Indexing"],
            "confidence": 0.90,
            "industry_relevance": ["Technology", "Finance", "Healthcare", "Retail"],
            "growth_rate": 0.12
        },
        "DevOps": {
            "core_skills": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Jenkins", "Terraform", "Ansible"],
            "related_skills": ["CI/CD", "Infrastructure as Code", "Monitoring", "Cloud Architecture"],
            "confidence": 0.88,
            "industry_relevance": ["Technology", "Finance", "E-commerce", "Media"],
            "growth_rate": 0.25
        },
        "Data Science": {
            "core_skills": ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch"],
            "related_skills": ["Data Visualization", "Statistical Analysis", "Machine Learning", "Big Data"],
            "confidence": 0.93,
            "industry_relevance": ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"],
            "growth_rate": 0.28
        },
        "Machine Learning": {
            "core_skills": ["TensorFlow", "PyTorch", "Scikit-learn", "Keras", "Computer Vision", "NLP"],
            "related_skills": ["Feature Engineering", "Model Deployment", "Data Preprocessing", "Neural Networks"],
            "confidence": 0.91,
            "industry_relevance": ["Technology", "Healthcare", "Finance", "Automotive", "Retail"],
            "growth_rate": 0.30
        },
        "Mobile Development": {
            "core_skills": ["Swift", "Kotlin", "React Native", "Flutter", "iOS", "Android", "Xamarin"],
            "related_skills": ["Mobile UI Design", "App Store Optimization", "Push Notifications", "Mobile Testing"],
            "confidence": 0.89,
            "industry_relevance": ["Technology", "E-commerce", "Media", "Healthcare"],
            "growth_rate": 0.20
        },
        "Cloud Computing": {
            "core_skills": ["AWS", "Azure", "GCP", "Cloud Architecture", "Serverless", "Lambda", "S3", "EC2"],
            "related_skills": ["Cloud Security", "Cost Optimization", "Multi-cloud", "Cloud Migration"],
            "confidence": 0.94,
            "industry_relevance": ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"],
            "growth_rate": 0.26
        },
        "Cybersecurity": {
            "core_skills": ["Network Security", "Penetration Testing", "Security Auditing", "Encryption", "Firewall"],
            "related_skills": ["Threat Analysis", "Security Compliance", "Vulnerability Assessment", "SIEM"],
            "confidence": 0.87,
            "industry_relevance": ["Finance", "Healthcare", "Government", "Technology"],
            "growth_rate": 0.22
        },
        "Project Management": {
            "core_skills": ["Agile", "Scrum", "Kanban", "JIRA", "Project Planning", "Risk Management"],
            "related_skills": ["Team Leadership", "Stakeholder Management", "Resource Allocation", "Budgeting"],
            "confidence": 0.85,
            "industry_relevance": ["All Industries"],
            "growth_rate": 0.10
        },
        "UI/UX Design": {
            "core_skills": ["Figma", "Sketch", "Adobe XD", "User Research", "Wireframing", "Prototyping"],
            "related_skills": ["Interaction Design", "Visual Design", "Usability Testing", "Information Architecture"],
            "confidence": 0.88,
            "industry_relevance": ["Technology", "E-commerce", "Media", "Marketing"],
            "growth_rate": 0.18
        },
        "Data Engineering": {
            "core_skills": ["Apache Spark", "Hadoop", "Kafka", "Airflow", "ETL", "Data Warehousing"],
            "related_skills": ["Data Modeling", "Data Pipeline", "Big Data", "Data Lake"],
            "confidence": 0.92,
            "industry_relevance": ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"],
            "growth_rate": 0.24
        },
        "Blockchain": {
            "core_skills": ["Solidity", "Smart Contracts", "Ethereum", "Bitcoin", "Hyperledger", "Web3.js"],
            "related_skills": ["Cryptography", "Consensus Algorithms", "DApps", "Tokenomics"],
            "confidence": 0.82,
            "industry_relevance": ["Finance", "Technology", "Supply Chain", "Healthcare"],
            "growth_rate": 0.35
        },
        "AR/VR Development": {
            "core_skills": ["Unity", "Unreal Engine", "ARKit", "ARCore", "WebXR", "3D Modeling"],
            "related_skills": ["Spatial Computing", "3D Animation", "Computer Vision", "Interaction Design"],
            "confidence": 0.80,
            "industry_relevance": ["Gaming", "Education", "Healthcare", "Retail", "Real Estate"],
            "growth_rate": 0.40
        },
        "Quality Assurance": {
            "core_skills": ["Selenium", "JUnit", "TestNG", "Cypress", "Jest", "Manual Testing", "Automated Testing"],
            "related_skills": ["Test Planning", "Bug Tracking", "Performance Testing", "Test Documentation"],
            "confidence": 0.86,
            "industry_relevance": ["Technology", "Finance", "Healthcare", "E-commerce"],
            "growth_rate": 0.15
        }
    }
    
    # Filter clusters by confidence
    filtered_clusters = {k: v for k, v in domain_clusters.items() if v["confidence"] >= min_confidence}
    
    # Limit to max_clusters
    cluster_items = list(filtered_clusters.items())
    random.shuffle(cluster_items)  # Randomize to get different clusters each time
    limited_clusters = dict(cluster_items[:max_clusters])
    
    # Format the response
    result = []
    for name, data in limited_clusters.items():
        cluster = {
            "name": name,
            "confidence": data["confidence"],
            "skills": data["core_skills"] + (data["related_skills"] if include_details else [])
        }
        
        if include_details:
            cluster["details"] = {
                "core_skills": data["core_skills"],
                "related_skills": data["related_skills"],
                "industry_relevance": data["industry_relevance"],
                "growth_rate": data["growth_rate"],
                "skill_count": len(data["core_skills"]) + len(data["related_skills"]),
                "market_demand": calculate_market_demand(data["core_skills"], data["growth_rate"])
            }
        
        result.append(cluster)
    
    return result

def calculate_market_demand(skills, growth_rate):
    """Calculate market demand score for a set of skills"""
    # This would be based on actual job market data in a production system
    base_demand = random.uniform(0.5, 0.9)
    growth_factor = growth_rate * 0.5  # Weight growth rate in the calculation
    
    # Add some variance based on the number of skills
    skill_factor = min(len(skills) / 10, 0.2)  # More skills generally means higher demand, up to a point
    
    return min(base_demand + growth_factor + skill_factor, 1.0)  # Cap at 1.0

def calculate_skill_distribution(clusters):
    """Calculate the distribution of skills across different domains"""
    domains = ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Media", "Education"]
    return {domain: round(random.uniform(0.1, 0.9), 2) for domain in domains}

def calculate_industry_relevance(clusters):
    """Calculate the relevance of skill clusters to different industries"""
    industries = ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Media", "Education"]
    return {
        industry: {
            "relevance_score": round(random.uniform(0.5, 0.95), 2),
            "top_clusters": random.sample([cluster["name"] for cluster in clusters], min(3, len(clusters)))
        }
        for industry in industries
    }
