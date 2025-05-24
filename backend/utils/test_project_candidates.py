#!/usr/bin/env python
"""
Test script for the enhanced project candidate recommendations API endpoint.
This script will:
1. Login as an employer
2. Get a project ID from the employer's posted projects
3. Test the project candidate recommendations endpoint with various filter combinations
4. Display the results

Usage:
    python test_project_candidates.py
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
        "password": PASSWORD,
    }
    
    try:
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Error during login: {str(e)}")
        sys.exit(1)

def get_employer_projects(access_token):
    """Get projects created by the employer"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/employer-projects", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            if projects:
                return projects
            else:
                print("No projects found for this employer")
                return None
        else:
            print(f"Failed to get projects: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting projects: {str(e)}")
        return None

def test_project_candidates(access_token, project_id, query_params=None):
    """Test the project candidate recommendations endpoint with given parameters"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/recommendations/candidates-for-project/{project_id}"
    if query_params:
        url += f"?{urlencode(query_params)}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Project candidates request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during project candidates request: {str(e)}")
        return None

def display_results(results, test_name):
    """Display project candidate recommendations results in a formatted table"""
    if not results:
        print(f"\n{test_name}: No results or error occurred")
        return
    
    candidates = results.get("candidates", [])
    total_count = results.get("total_count", 0)
    
    print(f"\n{test_name}")
    print(f"Total candidates found: {total_count}")
    
    if total_count == 0:
        print("No matching candidates found.")
        return
    
    # Display metadata
    metadata = results.get("metadata", {})
    project_title = metadata.get("project_title", "Unknown Project")
    print(f"Project: {project_title}")
    
    filters = metadata.get("filters_applied", {})
    print("\nFilters applied:")
    for key, value in filters.items():
        if value is not None and value != "" and value != 0 and value != False:
            print(f"  {key}: {value}")
    
    # Prepare table data
    table_data = []
    for candidate in candidates:
        candidate_id = candidate.get("candidate_id", "N/A")
        match_score = candidate.get("match_score", 0)
        skills_match = candidate.get("match_factors", {}).get("skills_match", 0)
        experience_match = candidate.get("match_factors", {}).get("experience_match", 0)
        
        # Get candidate details if available
        details = candidate.get("candidate_details", {})
        name = details.get("full_name", "N/A")
        experience = details.get("experience_years", "N/A")
        availability_hours = details.get("availability_hours", "N/A")
        location = details.get("location", "N/A")
        remote = "Yes" if details.get("remote_availability", False) else "No"
        
        table_data.append([
            name,
            match_score,
            skills_match,
            experience_match,
            experience,
            availability_hours,
            location,
            remote
        ])
    
    # Display table
    headers = ["Name", "Match Score", "Skills Match", "Exp Match", "Experience", "Avail. Hours", "Location", "Remote"]
    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

def main():
    """Main test function"""
    print("Project Candidate Recommendations API Test")
    print("=========================================\n")
    
    # Login
    access_token = login()
    if not access_token:
        return
    
    print("Successfully logged in")
    
    # Get employer projects
    projects = get_employer_projects(access_token)
    if not projects:
        return
    
    # Select first project for testing
    project_id = projects[0]["id"]
    project_title = projects[0]["title"]
    print(f"Using project: {project_title} (ID: {project_id})")
    
    # Test 1: Basic request with no filters
    test1_results = test_project_candidates(access_token, project_id)
    display_results(test1_results, "Test 1: Basic Request (No Filters)")
    
    # Test 2: Filter by minimum match score and limit
    test2_params = {
        "min_match_score": 70,
        "limit": 5
    }
    test2_results = test_project_candidates(access_token, project_id, test2_params)
    display_results(test2_results, "Test 2: Minimum Match Score (70%) and Limit (5)")
    
    # Test 3: Filter by experience range
    test3_params = {
        "experience_min": 3,
        "experience_max": 8,
        "sort_by": "experience_years"
    }
    test3_results = test_project_candidates(access_token, project_id, test3_params)
    display_results(test3_results, "Test 3: Experience Range (3-8 years)")
    
    # Test 4: Filter by availability and remote work
    test4_params = {
        "availability_min_hours": 20,
        "remote_only": True,
        "sort_by": "availability_hours"
    }
    test4_results = test_project_candidates(access_token, project_id, test4_params)
    display_results(test4_results, "Test 4: Availability (20+ hours) and Remote Only")
    
    # Test 5: Filter by education level and additional skills
    test5_params = {
        "education_level": "Bachelors,Masters",
        "skills_required": "Python,React",
        "include_details": True
    }
    test5_results = test_project_candidates(access_token, project_id, test5_params)
    display_results(test5_results, "Test 5: Education Level and Additional Skills")
    
    # Test 6: Combined filters
    test6_params = {
        "min_match_score": 80,
        "experience_min": 2,
        "availability_min_hours": 15,
        "remote_only": True,
        "limit": 10,
        "sort_by": "match_score"
    }
    test6_results = test_project_candidates(access_token, project_id, test6_params)
    display_results(test6_results, "Test 6: Combined Filters")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 