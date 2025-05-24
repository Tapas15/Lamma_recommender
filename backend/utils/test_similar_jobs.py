#!/usr/bin/env python
"""
Test script for the similar jobs recommendation endpoint.
This script will:
1. Register a test candidate if needed
2. Login to get an access token
3. Get a job ID to use for testing
4. Call the similar jobs endpoint
5. Display the results

Usage:
    python test_similar_jobs.py
"""

import requests
import json
import sys
import os
from tabulate import tabulate

# API configuration
BASE_URL = "http://localhost:8000"
EMAIL = "testcandidate@example.com"
PASSWORD = "password123"
NAME = "Test Candidate"

def register_candidate():
    """Register a test candidate if they don't exist"""
    print("Registering test candidate...")
    
    candidate_data = {
        "email": EMAIL,
        "password": PASSWORD,
        "full_name": NAME,
        "skills": {
            "languages_frameworks": ["Python", "FastAPI", "MongoDB", "React"],
            "tools_platforms": ["Git", "Docker", "AWS"],
            "soft_skills": ["Communication", "Teamwork"]
        },
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Company",
                "duration": "3 years",
                "description": "Developed web applications"
            }
        ],
        "education": [
            {
                "degree": "Bachelor's in Computer Science",
                "institution": "Tech University",
                "year": "2020"
            }
        ],
        "location": "Remote"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/candidate", json=candidate_data)
        
        if response.status_code == 200:
            print("✅ Candidate registered successfully")
            return True
        elif response.status_code == 400 and "Email already registered" in response.text:
            print("✅ Candidate already exists")
            return True
        else:
            print(f"❌ Failed to register candidate: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error registering candidate: {str(e)}")
        return False

def login():
    """Login and get access token"""
    print("Logging in...")
    
    login_data = {
        "username": EMAIL,
        "password": PASSWORD
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

def get_job_id(token):
    """Get a job ID to use for testing"""
    print("Getting a job ID for testing...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/jobs", headers=headers)
        
        if response.status_code == 200:
            jobs = response.json()
            if jobs and len(jobs) > 0:
                job_id = jobs[0].get("id")
                print(f"✅ Got job ID: {job_id}")
                return job_id
            else:
                print("❌ No jobs found")
                return None
        else:
            print(f"❌ Failed to get jobs: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error getting jobs: {str(e)}")
        return None

def get_similar_jobs(token, job_id, limit=5, exclude_applied=True, exclude_company=False):
    """Test the similar jobs endpoint"""
    print(f"Testing similar jobs endpoint for job ID: {job_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/recommendations/similar-jobs/{job_id}?limit={limit}&exclude_applied={str(exclude_applied).lower()}&exclude_company={str(exclude_company).lower()}"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            similar_jobs = response.json()
            print(f"✅ Found {len(similar_jobs)} similar jobs")
            return similar_jobs
        else:
            print(f"❌ Failed to get similar jobs: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error getting similar jobs: {str(e)}")
        return None

def display_similar_jobs(similar_jobs):
    """Display the similar jobs in a table format"""
    if not similar_jobs:
        print("No similar jobs found")
        return
    
    print("\n" + "="*80)
    print("SIMILAR JOBS RECOMMENDATIONS")
    print("="*80 + "\n")
    
    table_data = []
    for i, job in enumerate(similar_jobs, 1):
        job_details = job.get("job_details", {})
        
        table_data.append([
            i,
            job_details.get("title", "N/A"),
            job_details.get("company", "N/A"),
            job_details.get("location", "N/A"),
            f"{job.get('similarity_score', 0):.2f}%",
            ", ".join(job_details.get("required_skills", []))[:50] + ("..." if len(", ".join(job_details.get("required_skills", []))) > 50 else "")
        ])
    
    headers = ["#", "Title", "Company", "Location", "Similarity", "Required Skills"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def main():
    """Main function"""
    print("\n" + "="*80)
    print("SIMILAR JOBS RECOMMENDATION TEST")
    print("="*80 + "\n")
    
    # Register candidate if needed
    if not register_candidate():
        return
    
    # Login
    token = login()
    if not token:
        return
    
    # Get a job ID
    job_id = get_job_id(token)
    if not job_id:
        return
    
    # Get similar jobs
    similar_jobs = get_similar_jobs(token, job_id, limit=10)
    if not similar_jobs:
        return
    
    # Display results
    display_similar_jobs(similar_jobs)
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main() 