#!/usr/bin/env python
"""
Test script for the enhanced candidate recommendations API endpoint.
This script will:
1. Login as an employer
2. Get a job ID from the employer's posted jobs
3. Test the candidate recommendations endpoint with various filter combinations
4. Display the results

Usage:
    python test_candidate_recommendations.py
"""

import requests
import json
import sys
from tabulate import tabulate
from urllib.parse import urlencode

# API configuration
BASE_URL = "http://localhost:8000"
EMAIL = "testemployer@example.com"
PASSWORD = "password123"

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
        print(f"❌ Error during login: {str(e)}")
        return None

def get_employer_jobs(token):
    """Get jobs posted by the employer"""
    if not token:
        print("❌ No authentication token available")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        
        if response.status_code == 200:
            profile = response.json()
            jobs = profile.get("posted_jobs", [])
            
            if not jobs:
                print("❌ No jobs found for this employer")
                return None
            
            print(f"✅ Found {len(jobs)} jobs")
            return jobs
        else:
            print(f"❌ Failed to get employer profile: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error getting employer jobs: {str(e)}")
        return None

def test_candidate_recommendations(token, job_id, params=None):
    """Test the candidate recommendations endpoint with the given parameters"""
    if not token:
        print("❌ No authentication token available")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/recommendations/candidates/{job_id}"
    if params:
        url += "?" + urlencode(params)
    
    param_str = ", ".join([f"{k}={v}" for k, v in (params or {}).items()])
    print(f"\nTesting candidate recommendations for job {job_id} with parameters: {param_str}")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            candidates = result.get("candidates", [])
            total_count = result.get("total_count", 0)
            filters_applied = result.get("filters_applied", {})
            
            print(f"✅ Found {total_count} matching candidates")
            print(f"Filters applied: {json.dumps(filters_applied, indent=2)}")
            
            if candidates:
                # Prepare table data
                table_data = []
                for i, candidate in enumerate(candidates):
                    details = candidate.get("candidate_details", {})
                    row = [
                        i + 1,
                        details.get("full_name", "Unknown"),
                        f"{candidate.get('match_score', 0):.1f}",
                        details.get("experience_years", "N/A"),
                        details.get("location", "N/A"),
                        details.get("education_summary", "N/A")
                    ]
                    table_data.append(row)
                
                # Print table
                headers = ["#", "Name", "Score", "Experience", "Location", "Education"]
                print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
                
                # Print first candidate's explanation
                if candidates:
                    print(f"\nSample explanation: {candidates[0].get('explanation', 'No explanation')}")
            else:
                print("No candidates found matching the criteria")
            
            return result
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error in API request: {str(e)}")
        return None

def main():
    """Main function"""
    print("=" * 80)
    print("TESTING CANDIDATE RECOMMENDATIONS API")
    print("=" * 80)
    
    # Login
    token = login()
    if not token:
        print("❌ Failed to login, exiting...")
        sys.exit(1)
    
    # Get employer jobs
    jobs = get_employer_jobs(token)
    if not jobs or len(jobs) == 0:
        print("❌ No jobs found, exiting...")
        sys.exit(1)
    
    # Use the first job for testing
    job_id = jobs[0].get("id")
    job_title = jobs[0].get("title", "Unknown")
    print(f"Using job: {job_title} (ID: {job_id})")
    
    # Test cases
    test_cases = [
        {
            "name": "Default parameters",
            "params": {}
        },
        {
            "name": "High match score",
            "params": {
                "min_match_score": 70
            }
        },
        {
            "name": "Experience filter",
            "params": {
                "experience_min": 3,
                "experience_max": 8
            }
        },
        {
            "name": "Education filter",
            "params": {
                "education_level": "Bachelors,Masters"
            }
        },
        {
            "name": "Location and remote",
            "params": {
                "location_radius": 50,
                "include_remote": True
            }
        },
        {
            "name": "Availability filter",
            "params": {
                "availability": "Immediate,2 weeks"
            }
        },
        {
            "name": "Sort by experience",
            "params": {
                "sort_by": "experience_years"
            }
        },
        {
            "name": "Combined filters",
            "params": {
                "min_match_score": 60,
                "experience_min": 2,
                "education_level": "Bachelors,Masters",
                "include_remote": True,
                "sort_by": "match_score",
                "limit": 5
            }
        }
    ]
    
    # Run test cases
    for test_case in test_cases:
        print("\n" + "=" * 80)
        print(f"TEST CASE: {test_case['name']}")
        print("=" * 80)
        
        result = test_candidate_recommendations(token, job_id, test_case["params"])
        
        if result:
            print(f"✅ Test case completed successfully")
        else:
            print(f"❌ Test case failed")

if __name__ == "__main__":
    main() 