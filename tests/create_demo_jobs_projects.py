#!/usr/bin/env python
"""
Test script to create demo jobs and projects for testing purposes.
This script will create a specified number of jobs and projects using employer accounts.
If the employer login fails, it will register a new employer account.

Usage:
    python create_demo_jobs_projects.py [--jobs N] [--projects M]
    
    --jobs N: Number of job postings to create (default: 10)
    --projects M: Number of project postings to create (default: 10)
"""

import os
import sys
import json
import random
import argparse
import requests
from datetime import datetime, timedelta
from faker import Faker

# Add the parent directory to the path so we can import from utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
API_BASE_URL = "http://localhost:8000"
fake = Faker()

# Try to load existing employers from the demo file
EMPLOYERS = []
try:
    with open("tests/demo_employers.json", "r") as f:
        EMPLOYERS = json.load(f)
except Exception:
    print("No existing demo employers found. Will create new employers as needed.")

# Job and project data
JOB_TITLES = [
    "Senior Software Engineer", "Full Stack Developer", "Frontend Developer",
    "Backend Developer", "DevOps Engineer", "Data Scientist", "Machine Learning Engineer",
    "AI Researcher", "Mobile Developer", "iOS Developer", "Android Developer",
    "UI/UX Designer", "Product Manager", "Project Manager", "QA Engineer",
    "Database Administrator", "Cloud Architect", "Security Engineer",
    "Technical Writer", "Site Reliability Engineer", "Systems Architect"
]

PROJECT_TITLES = [
    "E-commerce Website Development", "Mobile App Development", 
    "Machine Learning Recommendation System", "Data Visualization Dashboard",
    "API Integration", "Cloud Migration", "DevOps Pipeline Setup",
    "Security Assessment", "UI/UX Redesign", "Database Optimization",
    "Blockchain Implementation", "IoT System Development", "AI Chatbot",
    "Content Management System", "Payment Gateway Integration",
    "Social Media Platform", "Video Streaming Service", "Real-time Analytics Platform",
    "Customer Portal Development", "Enterprise Resource Planning System"
]

PROJECT_TYPES = [
    "Web Application", "Mobile Application", "API Development",
    "Data Science", "Machine Learning", "DevOps", "Cloud Infrastructure",
    "UI/UX Design", "Database Design", "Security Implementation",
    "Blockchain", "IoT", "AI/ML", "Content Management", "E-commerce"
]

TECH_STACK = [
    "Python", "JavaScript", "TypeScript", "Java", "C#", "Go", "Rust",
    "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot",
    "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch",
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform"
]

EXPERIENCE_LEVELS = [
    "Entry-level", "Junior", "Mid-level", "Senior", "Lead", "Manager", "Director"
]

INDUSTRIES = [
    "Technology", "Finance", "Healthcare", "Education", "E-commerce", 
    "Manufacturing", "Retail", "Media", "Consulting", "Telecommunications"
]

EMPLOYMENT_TYPES = [
    "Full-time", "Part-time", "Contract", "Freelance", "Internship"
]

WORK_MODES = [
    "On-site", "Remote", "Hybrid"
]

LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Boston, MA",
    "Austin, TX", "Chicago, IL", "Los Angeles, CA", "Denver, CO",
    "Portland, OR", "Atlanta, GA", "Toronto, Canada", "Vancouver, Canada",
    "London, UK", "Berlin, Germany", "Paris, France", "Amsterdam, Netherlands",
    "Sydney, Australia", "Singapore", "Tokyo, Japan", "Remote"
]

BENEFITS = [
    "Health insurance", "Dental insurance", "Vision insurance",
    "401(k) matching", "Unlimited PTO", "Flexible work hours",
    "Remote work options", "Professional development budget",
    "Home office stipend", "Gym membership", "Mental health benefits",
    "Parental leave", "Stock options", "Performance bonuses",
    "Company retreats", "Free lunch", "Transit benefits"
]

def login_employer(email, password):
    """Login as an employer and get access token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={
                "username": email,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Login failed for {email}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error logging in as {email}: {str(e)}")
        return None

def generate_job_data(employer_id=None):
    """Generate realistic job posting data"""
    title = random.choice(JOB_TITLES)
    company = fake.company()
    
    # Select job details
    experience_level = random.choice(EXPERIENCE_LEVELS)
    industry = random.choice(INDUSTRIES)
    location = random.choice(LOCATIONS)
    employment_type = random.choice(EMPLOYMENT_TYPES)
    remote_option = random.choice([True, False])
    work_mode = random.sample(WORK_MODES, random.randint(1, len(WORK_MODES)))
    
    # Select technical requirements
    requirements = random.sample(TECH_STACK, random.randint(3, 8))
    
    # Generate salary range based on experience level
    if experience_level in ["Entry-level", "Junior"]:
        salary_min = random.randint(50000, 80000)
        salary_max = salary_min + random.randint(10000, 30000)
    elif experience_level in ["Mid-level"]:
        salary_min = random.randint(80000, 110000)
        salary_max = salary_min + random.randint(20000, 40000)
    else:  # Senior, Lead, Manager, Director
        salary_min = random.randint(120000, 160000)
        salary_max = salary_min + random.randint(30000, 80000)
    
    # Generate dates
    today = datetime.now()
    posted_date = today.strftime("%Y-%m-%d")
    deadline = (today + timedelta(days=random.randint(14, 90))).strftime("%Y-%m-%d")
    
    # Generate responsibilities and qualifications
    responsibilities = [fake.sentence() for _ in range(random.randint(4, 8))]
    preferred_qualifications = [fake.sentence() for _ in range(random.randint(3, 6))]
    
    # Generate benefits
    job_benefits = random.sample(BENEFITS, random.randint(4, 10))
    
    # Generate job data
    job_data = {
        "title": title,
        "company": company,
        "description": fake.paragraph(nb_sentences=5),
        "requirements": requirements,
        "location": location,
        "employment_type": employment_type,
        "experience_level": experience_level,
        "industry": industry,
        "responsibilities": responsibilities,
        "preferred_qualifications": preferred_qualifications,
        "tech_stack": requirements,
        "remote_option": remote_option,
        "work_mode": work_mode,
        "salary_range": {
            "min": salary_min,
            "max": salary_max,
            "currency": "USD"
        },
        "benefits": job_benefits,
        "application_deadline": deadline,
        "posted_date": posted_date,
        "contact_email": fake.email()
    }
    
    # Add employer ID if provided
    if employer_id:
        job_data["employer_id"] = employer_id
    
    return job_data

def generate_project_data(employer_id=None):
    """Generate realistic project posting data"""
    title = random.choice(PROJECT_TITLES)
    company = fake.company()
    project_type = random.choice(PROJECT_TYPES)
    
    # Select project details
    location = random.choice(LOCATIONS)
    requirements = random.sample(TECH_STACK, random.randint(3, 8))
    skills_required = random.sample(TECH_STACK, random.randint(3, 8))
    
    # Generate budget range
    budget_min = random.choice([5000, 10000, 15000, 20000, 25000, 30000, 40000, 50000])
    budget_max = budget_min + random.choice([5000, 10000, 15000, 20000, 30000, 50000])
    
    # Generate duration
    duration_months = random.randint(1, 12)
    estimated_hours = duration_months * random.randint(40, 160)
    
    # Generate tools and technologies
    tools_technologies = random.sample(TECH_STACK, random.randint(3, 8))
    
    # Generate objectives and qualifications
    objectives = [fake.sentence() for _ in range(random.randint(3, 6))]
    preferred_qualifications = [fake.sentence() for _ in range(random.randint(3, 5))]
    
    # Generate dates for timeline
    today = datetime.now()
    start_date = (today + timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=30*duration_months + random.randint(0, 30))).strftime("%Y-%m-%d")
    
    # Generate milestones
    num_milestones = random.randint(2, 5)
    milestones = []
    for i in range(num_milestones):
        milestone_date = (today + timedelta(days=30*(i+1))).strftime("%Y-%m-%d")
        milestones.append({
            "name": f"Milestone {i+1}: {fake.bs()}",
            "deadline": milestone_date
        })
    
    # Generate deliverables
    deliverables = [fake.sentence() for _ in range(random.randint(3, 6))]
    
    # Generate project data
    project_data = {
        "title": title,
        "company": company,
        "description": fake.paragraph(nb_sentences=4),
        "project_type": project_type,
        "requirements": requirements,
        "skills_required": skills_required,
        "location": location,
        "budget_range": {
            "min": budget_min,
            "max": budget_max,
            "currency": "USD"
        },
        "duration": {
            "time_frame": f"{duration_months} months",
            "estimated_hours": estimated_hours
        },
        "tools_technologies": tools_technologies,
        "objectives": objectives,
        "preferred_qualifications": preferred_qualifications,
        "timeline": {
            "start_date": start_date,
            "end_date": end_date,
            "milestones": milestones
        },
        "experience": {
            "level": random.choice(["Beginner", "Intermediate", "Advanced", "Expert"]),
            "domain": random.choice(PROJECT_TYPES),
            "years": f"{random.randint(1, 10)}+ years",
            "project_examples": [fake.bs() for _ in range(random.randint(1, 3))]
        },
        "deliverables": deliverables
    }
    
    # Add employer ID if provided
    if employer_id:
        project_data["employer_id"] = employer_id
    
    return project_data

def create_job(token, job_data):
    """Create a job posting using the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/jobs",
            json=job_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Created job: {job_data['title']} at {job_data['company']}")
            return response.json()
        else:
            print(f"❌ Failed to create job {job_data['title']}: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating job {job_data['title']}: {str(e)}")
        return None

def create_project(token, project_data):
    """Create a project posting using the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/projects",
            json=project_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Created project: {project_data['title']} at {project_data['company']}")
            return response.json()
        else:
            print(f"❌ Failed to create project {project_data['title']}: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating project {project_data['title']}: {str(e)}")
        return None

def get_employer_token():
    """Get an employer token, either by logging in or creating a new account"""
    # Try to login with existing employers
    for employer in EMPLOYERS:
        email = employer.get("email")
        if not email:
            continue
            
        token = login_employer(email, "Password123!")
        if token:
            print(f"✅ Logged in as existing employer: {email}")
            return token, employer.get("id")
    
    # If no existing employers or login failed, create a new one
    print("Creating a new employer account...")
    from create_demo_employers import generate_employer_data, create_employer
    
    employer_data = generate_employer_data()
    new_employer = create_employer(employer_data)
    
    if new_employer:
        # Try to login with the new employer
        token = login_employer(employer_data["email"], "Password123!")
        if token:
            print(f"✅ Logged in as new employer: {employer_data['email']}")
            return token, new_employer.get("id")
    
    print("❌ Failed to get an employer token. Cannot create jobs/projects.")
    return None, None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Create demo jobs and projects")
    parser.add_argument("--jobs", type=int, default=10, help="Number of jobs to create")
    parser.add_argument("--projects", type=int, default=10, help="Number of projects to create")
    args = parser.parse_args()
    
    # Get employer token
    token, employer_id = get_employer_token()
    if not token:
        print("Exiting due to authentication failure.")
        return
    
    # Create jobs
    print(f"\nCreating {args.jobs} demo job postings...")
    created_jobs = []
    for i in range(args.jobs):
        job_data = generate_job_data(employer_id)
        result = create_job(token, job_data)
        if result:
            created_jobs.append(result)
    
    print(f"\nSuccessfully created {len(created_jobs)} out of {args.jobs} job postings.")
    
    # Save created jobs to a JSON file for reference
    with open("tests/demo_jobs.json", "w") as f:
        json.dump(created_jobs, f, indent=2)
    print(f"Job data saved to tests/demo_jobs.json")
    
    # Create projects
    print(f"\nCreating {args.projects} demo project postings...")
    created_projects = []
    for i in range(args.projects):
        project_data = generate_project_data(employer_id)
        result = create_project(token, project_data)
        if result:
            created_projects.append(result)
    
    print(f"\nSuccessfully created {len(created_projects)} out of {args.projects} project postings.")
    
    # Save created projects to a JSON file for reference
    with open("tests/demo_projects.json", "w") as f:
        json.dump(created_projects, f, indent=2)
    print(f"Project data saved to tests/demo_projects.json")

if __name__ == "__main__":
    main() 