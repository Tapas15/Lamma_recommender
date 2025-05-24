#!/usr/bin/env python
"""
Script to create test data for the job recommendation system.
This script will:
1. Create a test candidate user
2. Create a test employer user
3. Create test jobs

Usage:
    python create_test_data.py
"""

import requests
import json
import sys
import os
import time

# API configuration
BASE_URL = "http://localhost:8000"

# Test candidate
CANDIDATE_EMAIL = "testcandidate@example.com"
CANDIDATE_PASSWORD = "password123"
CANDIDATE_NAME = "Test Candidate"

# Test employer
EMPLOYER_EMAIL = "testemployer@example.com"
EMPLOYER_PASSWORD = "password123"
EMPLOYER_NAME = "Test Employer"

def create_candidate():
    """Create a test candidate user"""
    print("Creating test candidate...")
    
    candidate_data = {
        "email": CANDIDATE_EMAIL,
        "password": CANDIDATE_PASSWORD,
        "full_name": CANDIDATE_NAME,
        "skills": {
            "languages_frameworks": ["Python", "JavaScript", "React", "Node.js"],
            "tools_platforms": ["Git", "Docker", "AWS", "Linux"],
            "ai_ml_data": ["TensorFlow", "PyTorch", "Pandas"],
            "soft_skills": ["Communication", "Teamwork", "Problem Solving"]
        },
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Company",
                "duration": "3 years",
                "description": "Developed web applications and APIs"
            },
            {
                "title": "Software Developer",
                "company": "Startup Inc",
                "duration": "2 years",
                "description": "Full-stack development"
            }
        ],
        "education": [
            {
                "degree": "Master's in Computer Science",
                "institution": "Tech University",
                "year": "2020"
            }
        ],
        "location": "San Francisco, CA",
        "bio": "Experienced software engineer with a passion for AI and machine learning"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/candidate", json=candidate_data)
        
        if response.status_code == 200:
            print("✅ Candidate created successfully")
            return response.json()
        elif response.status_code == 400 and "Email already registered" in response.text:
            print("✅ Candidate already exists")
            return {"email": CANDIDATE_EMAIL, "password": CANDIDATE_PASSWORD}
        else:
            print(f"❌ Failed to create candidate: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error creating candidate: {str(e)}")
        return None

def create_employer():
    """Create a test employer user"""
    print("Creating test employer...")
    
    employer_data = {
        "email": EMPLOYER_EMAIL,
        "password": EMPLOYER_PASSWORD,
        "full_name": EMPLOYER_NAME,
        "position": "HR Manager",
        "company_details": {
            "company_name": "Tech Solutions Inc",
            "company_description": "We provide innovative tech solutions",
            "company_website": "https://techsolutions.example.com",
            "company_location": "San Francisco, CA",
            "company_size": "50-200",
            "industry": "Information Technology"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/employer", json=employer_data)
        
        if response.status_code == 200:
            print("✅ Employer created successfully")
            return response.json()
        elif response.status_code == 400 and "Email already registered" in response.text:
            print("✅ Employer already exists")
            return {"email": EMPLOYER_EMAIL, "password": EMPLOYER_PASSWORD}
        else:
            print(f"❌ Failed to create employer: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error creating employer: {str(e)}")
        return None

def login(email, password):
    """Login and get access token"""
    print(f"Logging in as {email}...")
    
    login_data = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error logging in: {str(e)}")
        return None

def create_job(token, job_data):
    """Create a test job"""
    print(f"Creating job: {job_data['title']}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/jobs", json=job_data, headers=headers)
        
        if response.status_code == 200:
            job = response.json()
            print(f"✅ Job created successfully: {job['id']}")
            return job
        else:
            print(f"❌ Failed to create job: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error creating job: {str(e)}")
        return None

def main():
    """Main function"""
    print("\n" + "="*80)
    print("CREATING TEST DATA FOR JOB RECOMMENDATION SYSTEM")
    print("="*80 + "\n")
    
    # Create test candidate
    candidate = create_candidate()
    if not candidate:
        print("Failed to create test candidate")
    
    # Create test employer
    employer = create_employer()
    if not employer:
        print("Failed to create test employer")
        return
    
    # Print employer details to debug
    print("\nEmployer details:")
    print(json.dumps(employer, indent=2))
    
    # Get employer ID
    employer_id = employer.get("id")
    if not employer_id:
        print("❌ Failed to get employer ID")
        return
        
    print(f"Using employer ID: {employer_id}")
    
    # Login as employer
    token = login(EMPLOYER_EMAIL, EMPLOYER_PASSWORD)
    if not token:
        print("Failed to login as employer")
        return
    
    # Create test jobs
    jobs = [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Solutions Inc",
            "description": "We are looking for a Senior Software Engineer to join our team. You will be responsible for designing, developing, and maintaining our core products.",
            "requirements": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
            "location": "San Francisco, CA",
            "employment_type": "Full-time",
            "experience_level": "Senior",
            "industry": "Information Technology",
            "responsibilities": ["Design and develop software", "Lead technical projects", "Mentor junior developers"],
            "preferred_qualifications": ["Master's degree", "5+ years of experience", "Experience with cloud technologies"],
            "tech_stack": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
            "remote_option": True,
            "work_mode": ["Remote", "Hybrid"],
            "salary_range": "120000-150000 USD",
            "benefits": ["Health insurance", "401(k)", "Flexible hours"],
            "contact_email": EMPLOYER_EMAIL,
            "employer_id": employer_id
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Innovations",
            "description": "Join our AI team to develop cutting-edge machine learning models for various applications.",
            "requirements": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning"],
            "location": "Remote",
            "employment_type": "Full-time",
            "experience_level": "Mid-level",
            "industry": "Artificial Intelligence",
            "responsibilities": ["Develop ML models", "Process and analyze data", "Deploy models to production"],
            "preferred_qualifications": ["PhD in Computer Science", "Experience with NLP"],
            "tech_stack": ["Python", "TensorFlow", "PyTorch", "Scikit-learn"],
            "remote_option": True,
            "work_mode": ["Remote"],
            "salary_range": "130000-160000 USD",
            "benefits": ["Health insurance", "Stock options", "Learning budget"],
            "contact_email": EMPLOYER_EMAIL,
            "employer_id": employer_id
        },
        {
            "title": "Frontend Developer",
            "company": "Web Solutions",
            "description": "Create beautiful and responsive user interfaces for our web applications.",
            "requirements": ["JavaScript", "React", "HTML", "CSS", "TypeScript"],
            "location": "New York, NY",
            "employment_type": "Full-time",
            "experience_level": "Junior",
            "industry": "Web Development",
            "responsibilities": ["Develop user interfaces", "Implement designs", "Optimize performance"],
            "preferred_qualifications": ["Experience with Redux", "UI/UX knowledge"],
            "tech_stack": ["JavaScript", "React", "HTML", "CSS", "TypeScript"],
            "remote_option": False,
            "work_mode": ["On-site"],
            "salary_range": "80000-100000 USD",
            "benefits": ["Health insurance", "Gym membership"],
            "contact_email": EMPLOYER_EMAIL,
            "employer_id": employer_id
        },
        {
            "title": "DevOps Engineer",
            "company": "Cloud Systems",
            "description": "Help us build and maintain our cloud infrastructure and CI/CD pipelines.",
            "requirements": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD"],
            "location": "Seattle, WA",
            "employment_type": "Full-time",
            "experience_level": "Senior",
            "industry": "Cloud Computing",
            "responsibilities": ["Manage cloud infrastructure", "Implement CI/CD pipelines", "Monitor systems"],
            "preferred_qualifications": ["AWS certification", "Experience with microservices"],
            "tech_stack": ["AWS", "Docker", "Kubernetes", "Terraform", "Jenkins"],
            "remote_option": True,
            "work_mode": ["Hybrid"],
            "salary_range": "130000-160000 USD",
            "benefits": ["Health insurance", "Remote work stipend"],
            "contact_email": EMPLOYER_EMAIL,
            "employer_id": employer_id
        },
        {
            "title": "Data Scientist",
            "company": "Data Insights",
            "description": "Extract insights from data to help our clients make better decisions.",
            "requirements": ["Python", "Pandas", "SQL", "Statistics", "Machine Learning"],
            "location": "Boston, MA",
            "employment_type": "Full-time",
            "experience_level": "Mid-level",
            "industry": "Data Science",
            "responsibilities": ["Analyze data", "Build predictive models", "Present findings"],
            "preferred_qualifications": ["Master's in Statistics", "Experience with big data"],
            "tech_stack": ["Python", "Pandas", "SQL", "Scikit-learn", "Tableau"],
            "remote_option": True,
            "work_mode": ["Remote", "Hybrid"],
            "salary_range": "110000-140000 USD",
            "benefits": ["Health insurance", "Flexible hours", "Learning budget"],
            "contact_email": EMPLOYER_EMAIL,
            "employer_id": employer_id
        }
    ]
    
    created_jobs = []
    for job_data in jobs:
        job = create_job(token, job_data)
        if job:
            created_jobs.append(job)
            # Add a small delay to avoid rate limiting
            time.sleep(1)
    
    print(f"\n✅ Created {len(created_jobs)} test jobs")
    
    # Print job IDs for testing
    if created_jobs:
        print("\nJob IDs for testing:")
        for job in created_jobs:
            print(f"- {job['id']} ({job['title']})")
    
    print("\nTest data creation completed!")
    print(f"\nYou can now test the similar jobs endpoint with:")
    print(f"python test_similar_jobs_simple.py {CANDIDATE_EMAIL} {CANDIDATE_PASSWORD} <job_id>")

if __name__ == "__main__":
    main() 