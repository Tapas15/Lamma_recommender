#!/usr/bin/env python
"""
Test script to create demo job postings for testing purposes.
This script will create a specified number of jobs using employer accounts.
If the employer login fails, it will register a new employer account.

Usage:
    python create_demo_jobs.py [--count N]
    
    --count N: Number of job postings to create (default: 10)
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

# Job data
JOB_TITLES = [
    "Senior Software Engineer", "Full Stack Developer", "Frontend Developer",
    "Backend Developer", "DevOps Engineer", "Data Scientist", "Machine Learning Engineer",
    "AI Researcher", "Mobile Developer", "iOS Developer", "Android Developer",
    "UI/UX Designer", "Product Manager", "Project Manager", "QA Engineer",
    "Database Administrator", "Cloud Architect", "Security Engineer",
    "Technical Writer", "Site Reliability Engineer", "Systems Architect"
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
            
            # Get employer ID from API
            try:
                response = requests.get(
                    f"{API_BASE_URL}/profile",
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )
                
                if response.status_code == 200:
                    employer_id = response.json().get("id")
                    if employer_id:
                        print(f"Retrieved employer ID: {employer_id}")
                        return token, employer_id
                    else:
                        print("Error: No employer ID found in profile response.")
                else:
                    print(f"Error getting profile: {response.status_code}")
            except Exception as e:
                print(f"Error retrieving employer profile: {str(e)}")
            
            return token, None
    
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
            
            # Get employer ID from API
            try:
                response = requests.get(
                    f"{API_BASE_URL}/profile",
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )
                
                if response.status_code == 200:
                    employer_id = response.json().get("id")
                    if employer_id:
                        print(f"Retrieved employer ID: {employer_id}")
                        return token, employer_id
                    else:
                        print("Error: No employer ID found in profile response.")
                else:
                    print(f"Error getting profile: {response.status_code}")
            except Exception as e:
                print(f"Error retrieving employer profile: {str(e)}")
    
    print("❌ Failed to get an employer token. Cannot create jobs.")
    return None, None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Create demo job postings")
    parser.add_argument("--count", type=int, default=10, help="Number of jobs to create")
    args = parser.parse_args()
    
    # Get employer token
    token, employer_id = get_employer_token()
    if not token:
        print("Exiting due to authentication failure.")
        return
    
    if not employer_id:
        print("Error: No employer ID available. Cannot create jobs.")
        return
        
    # Create jobs
    print(f"\nCreating {args.count} demo job postings...")
    created_jobs = []
    for i in range(args.count):
        job_data = generate_job_data(employer_id)
        result = create_job(token, job_data)
        if result:
            created_jobs.append(result)
    
    print(f"\nSuccessfully created {len(created_jobs)} out of {args.count} job postings.")
    
    # Save created jobs to a JSON file for reference
    with open("tests/demo_jobs.json", "w") as f:
        json.dump(created_jobs, f, indent=2)
    print(f"Job data saved to tests/demo_jobs.json")

if __name__ == "__main__":
    main() 