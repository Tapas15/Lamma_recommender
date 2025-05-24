#!/usr/bin/env python
"""
Simple test script for the similar jobs recommendation endpoint.
This script assumes you already have a user and some jobs in the database.

Usage:
    python test_similar_jobs_simple.py <email> <password> <job_id>
"""

import requests
import json
import sys
from tabulate import tabulate

# API configuration
BASE_URL = "http://localhost:8000"

def login(email, password):
    """Login and get access token"""
    print("Logging in...")
    
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
    
    # Check command line arguments
    if len(sys.argv) < 4:
        print("Usage: python test_similar_jobs_simple.py <email> <password> <job_id>")
        return
    
    email = sys.argv[1]
    password = sys.argv[2]
    job_id = sys.argv[3]
    
    # Login
    token = login(email, password)
    if not token:
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