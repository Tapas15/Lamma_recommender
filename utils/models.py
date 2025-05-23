from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class UserType(str, Enum):
    CANDIDATE = "candidate"
    EMPLOYER = "employer"

class UserBase(BaseModel):
    email: EmailStr
    user_type: UserType
    full_name: str

class User(UserBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Links(BaseModel):
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    resume: Optional[str] = None

class Skills(BaseModel):
    languages_frameworks: List[str] = []
    ai_ml_data: List[str] = []
    tools_platforms: List[str] = []
    soft_skills: List[str] = []

class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    duration: str
    responsibilities: List[str] = []

class Education(BaseModel):
    degree: str
    institution: str
    duration: str

class JobSearchStatus(BaseModel):
    currently_looking: bool = True
    available_from: Optional[str] = None
    desired_job_titles: List[str] = []
    preferred_employment_type: List[str] = []
    salary_expectation_usd: Optional[Dict[str, int]] = None
    notice_period_days: Optional[int] = None
    relocation_willingness: bool = False
    additional_notes: Optional[str] = None

class Candidate(UserBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    phone: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[str] = None
    education_summary: Optional[str] = None
    bio: Optional[str] = None
    about: Optional[str] = None
    links: Optional[Links] = None
    skills: Optional[Skills] = None
    experience: Optional[List[Experience]] = []
    education: Optional[List[Education]] = []
    certifications: List[str] = []
    preferred_job_locations: List[str] = []
    job_search_status: Optional[JobSearchStatus] = None

class CandidateCreate(UserBase):
    user_type: UserType = UserType.CANDIDATE
    password: str
    phone: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[str] = None
    education_summary: Optional[str] = None
    bio: Optional[str] = None
    about: Optional[str] = None
    links: Optional[Dict[str, str]] = None
    skills: Optional[Dict[str, List[str]]] = None
    experience: Optional[List[Dict[str, Any]]] = []
    education: Optional[List[Dict[str, str]]] = []
    certifications: Optional[List[str]] = []
    preferred_job_locations: Optional[List[str]] = []
    job_search_status: Optional[Dict[str, Any]] = None

class Employer(UserBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    company_name: str
    company_description: str
    company_website: str
    company_location: str
    company_size: str
    industry: str
    contact_email: str
    contact_phone: str
    location: str
    bio: str
    profile_completed: bool = True
    is_active: bool = True
    last_active: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False
    total_jobs_posted: int = 0
    total_active_jobs: int = 0
    account_type: str = "standard"
    profile_views: int = 0
    rating: Optional[float] = None
    social_links: dict = Field(default_factory=lambda: {"linkedin": "", "twitter": "", "website": ""})
    posted_jobs: Optional[List[dict]] = []

class EmployerCreate(UserBase):
    user_type: UserType = UserType.EMPLOYER
    password: str
    company_name: str
    company_description: Optional[str] = None
    company_website: Optional[str] = None
    company_location: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None

class JobBase(BaseModel):
    title: str
    company: str
    description: str
    requirements: List[str]
    location: str
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    industry: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    preferred_qualifications: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    remote_option: Optional[bool] = None
    work_mode: Optional[List[str]] = None
    salary_range: Optional[str] = None
    benefits: Optional[List[str]] = None
    application_deadline: Optional[str] = None
    posted_date: Optional[str] = None
    contact_email: Optional[str] = None

class JobCreate(JobBase):
    employer_id: str

class Job(JobBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    employer_id: str
    is_active: bool = True

class ProjectBase(BaseModel):
    title: str
    company: str
    description: str
    requirements: List[str]
    budget_range: Optional[str] = None
    duration: Optional[str] = None
    location: Optional[str] = None
    project_type: str
    skills_required: List[str]
    deadline: Optional[str] = None
    employment_type: Optional[str] = None
    objectives: Optional[List[str]] = None
    preferred_qualifications: Optional[List[str]] = None
    experience: Optional[Dict[str, Any]] = None
    tools_technologies: Optional[List[str]] = None
    timeline: Optional[Dict[str, str]] = None
    contact_email: Optional[str] = None

class ProjectCreate(ProjectBase):
    employer_id: Optional[str] = None

class Project(ProjectBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    employer_id: str
    is_active: bool = True
    status: str = "open"  # open, in_progress, completed, cancelled

class JobApplication(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    employer_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "applied"  # applied, reviewed, interview, rejected, accepted
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    notes: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    job_details: Optional[Dict[str, Any]] = None

class JobApplicationCreate(BaseModel):
    job_id: str
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    notes: Optional[str] = None

class SavedJob(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    employer_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    job_details: Optional[Dict[str, Any]] = None
    
class SavedJobCreate(BaseModel):
    job_id: str
    notes: Optional[str] = None

class SavedProject(BaseModel):
    id: str
    candidate_id: str
    project_id: str
    employer_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    project_details: Optional[Dict[str, Any]] = None
    
class SavedProjectCreate(BaseModel):
    project_id: str
    notes: Optional[str] = None

class Recommendation(BaseModel):
    id: str
    user_id: str
    job_id: Optional[str] = None
    candidate_id: Optional[str] = None
    match_score: float
    explanation: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_type: Optional[UserType] = None

class ProjectApplication(BaseModel):
    id: str
    candidate_id: str
    project_id: str
    employer_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "applied"  # applied, reviewed, interview, rejected, accepted
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    notes: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    project_details: Optional[Dict[str, Any]] = None

class ProjectApplicationCreate(BaseModel):
    project_id: str
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    notes: Optional[str] = None 