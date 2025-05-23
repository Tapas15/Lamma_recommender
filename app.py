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
    recommendations = await get_candidate_job_matches(candidate, jobs)
    
    # Save recommendations with score > 70 to recommendations collection
    for rec in recommendations:
        if rec["match_score"] >= 70:
            # Create recommendation document
            recommendation_doc = {
                "id": str(ObjectId()),
                "candidate_id": candidate["id"],
                "job_id": rec["job_id"],
                "match_score": rec["match_score"],
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
                "job_id": rec["job_id"],
                    "type": "job_recommendation",
                }
            )
            
            # If it doesn't exist or score has changed, save/update it
            if not existing_rec:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).insert_one(
                    recommendation_doc
                )
                print(
                    f"Saved job recommendation with score {rec['match_score']} for candidate {candidate['id']}"
                )
            elif existing_rec["match_score"] != rec["match_score"]:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).update_one(
                    {"id": existing_rec["id"]},
                    {
                        "$set": {
                            "match_score": rec["match_score"],
                            "timestamp": datetime.utcnow(),
                        }
                    },
                )
                print(
                    f"Updated job recommendation score to {rec['match_score']} for candidate {candidate['id']}"
                )
    
    return recommendations


@app.get("/recommendations/candidates/{job_id}", response_model=List[dict])
async def get_candidate_recommendations(
    job_id: str, current_user: dict = Depends(get_current_user)
):
    if current_user["user_type"] != UserType.EMPLOYER:
        raise HTTPException(
            status_code=403, detail="Only employers can get candidate recommendations"
        )
    
    job = await Database.get_collection(JOBS_COLLECTION).find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Make sure to only get active candidates with complete profiles
    candidates = (
        await Database.get_collection(CANDIDATES_COLLECTION)
        .find({"is_active": True, "profile_completed": True})
        .to_list(length=None)
    )
    
    if not candidates:
        print(f"No active candidates found for job {job_id}")
        return []
    
    recommendations = await get_job_candidate_matches(job, candidates)
    
    # Save high-scoring recommendations to the recommendations collection
    for rec in recommendations:
        if rec["match_score"] >= 70:
            # Create recommendation document
            recommendation_doc = {
                "id": str(ObjectId()),
                "candidate_id": rec["candidate_id"],
                "job_id": job_id,
                "employer_id": current_user["id"],
                "match_score": rec["match_score"],
                "type": "candidate_recommendation",
                "timestamp": datetime.utcnow(),
                "viewed": False,
            }
            
            # Check if this recommendation already exists
            existing_rec = await Database.get_collection(
                RECOMMENDATIONS_COLLECTION
            ).find_one(
                {
                "candidate_id": rec["candidate_id"],
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
                    f"Saved candidate recommendation with score {rec['match_score']} for job {job_id}"
                )
            elif existing_rec["match_score"] != rec["match_score"]:
                await Database.get_collection(RECOMMENDATIONS_COLLECTION).update_one(
                    {"id": existing_rec["id"]},
                    {
                        "$set": {
                            "match_score": rec["match_score"],
                            "timestamp": datetime.utcnow(),
                        }
                    },
                )
                print(
                    f"Updated candidate recommendation score to {rec['match_score']} for job {job_id}"
                )
    
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
    
    return detailed_recommendations


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
    "/recommendations/candidates-for-project/{project_id}", response_model=List[dict]
)
async def get_candidate_recommendations_for_project(
    project_id: str, current_user: dict = Depends(get_current_user)
):
    """Get candidate recommendations for a specific project"""
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
    
    # Get active candidates with complete profiles
    candidates = (
        await Database.get_collection(CANDIDATES_COLLECTION)
        .find({"is_active": True, "profile_completed": True})
        .to_list(length=None)
    )
    
    if not candidates:
        return []
    
    recommendations = []
    for candidate in candidates:
        # Convert project format to job-like format for the recommender
        project_job_format = {
            "title": project.get("title", ""),
            "required_skills": project.get("skills_required", []),
            "description": project.get("description", ""),
        }
        
        # Use the same matching algorithm
        score, explanation = await get_match_score(project_job_format, candidate)
        
        candidate_id = candidate.get("id")
        recommendation = {
            "candidate_id": candidate_id,
            "match_score": score,
            "explanation": explanation,
            "candidate": {
                "full_name": candidate.get("full_name", ""),
                "skills": candidate.get("skills", []),
                "location": candidate.get("location", ""),
                "experience": candidate.get("experience", ""),
            },
        }
        
        recommendations.append(recommendation)
        
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
    
    # Sort by match score
    recommendations = sorted(
        recommendations, key=lambda x: x["match_score"], reverse=True
    )
    return recommendations


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
