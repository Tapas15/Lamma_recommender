from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Link models for candidate profiles
class Links(BaseModel):
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    resume: Optional[str] = None

# Skills models for detailed candidate profiles
class Skills(BaseModel):
    languages_frameworks: Optional[List[str]] = []
    ai_ml_data: Optional[List[str]] = []
    tools_platforms: Optional[List[str]] = []
    soft_skills: Optional[List[str]] = []

# Experience model for candidate profiles
class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    duration: str
    responsibilities: Optional[List[str]] = []

# Education model for candidate profiles
class Education(BaseModel):
    degree: str
    institution: str
    duration: Optional[str] = None

# Job search status model for candidate profiles
class JobSearchStatus(BaseModel):
    currently_looking: bool = True
    available_from: Optional[str] = None
    desired_job_titles: Optional[List[str]] = []
    preferred_employment_type: Optional[List[str]] = []
    salary_expectation_usd: Optional[Dict[str, int]] = None
    notice_period_days: Optional[int] = None
    relocation_willingness: bool = False
    additional_notes: Optional[str] = None

# Extended candidate model for detailed profiles
class ExtendedCandidate(BaseModel):
    email: EmailStr
    full_name: str
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

# Extended candidate registration model
class ExtendedCandidateCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
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

# Company Socials model for employer profiles
class CompanySocials(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    glassdoor: Optional[str] = None

# Company Details model for employer profiles
class CompanyDetails(BaseModel):
    company_name: str
    company_description: Optional[str] = None
    company_website: Optional[str] = None
    company_location: Optional[str] = None
    company_size: Optional[str] = None
    industry: str
    founded_year: Optional[int] = None
    company_logo: Optional[str] = None
    company_socials: Optional[CompanySocials] = None
    values: Optional[List[str]] = []
    mission: Optional[str] = None
    vision: Optional[str] = None

# Hiring Preferences model for employer profiles
class HiringPreferences(BaseModel):
    job_roles_hiring: Optional[List[str]] = []
    employment_types: Optional[List[str]] = []
    locations_hiring: Optional[List[str]] = []
    salary_range_usd: Optional[Dict[str, int]] = None
    remote_friendly: bool = False
    tech_stack: Optional[List[str]] = []

# Extended Employer model
class ExtendedEmployer(BaseModel):
    email: EmailStr
    full_name: str
    user_type: str = "employer"
    position: Optional[str] = None
    bio: Optional[str] = None
    about: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    location: Optional[str] = None
    company_details: CompanyDetails
    hiring_preferences: Optional[HiringPreferences] = None
    
# Extended Employer Create model
class ExtendedEmployerCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    user_type: str = "employer"
    position: Optional[str] = None
    bio: Optional[str] = None
    about: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    location: Optional[str] = None
    company_details: Dict[str, Any]
    hiring_preferences: Optional[Dict[str, Any]] = None 