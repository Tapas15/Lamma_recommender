#!/usr/bin/env python
"""
Test script for the enhanced talent search API endpoint.
This script will:
1. Login as an employer
2. Test the talent search endpoint with various filter combinations
3. Display the results

Usage:
    python test_talent_search.py
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

def test_talent_search(access_token, search_params, query_params=None):
    """Test the talent search endpoint with given parameters"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/recommendations/talent-search"
    if query_params:
        url += f"?{urlencode(query_params)}"
    
    try:
        # Ensure location is a string if provided
        if "location" in search_params and search_params["location"] is not None:
            search_params["location"] = str(search_params["location"])
            
        response = requests.post(url, headers=headers, json=search_params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Talent search failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during talent search: {str(e)}")
        return None

def display_results(results, test_name):
    """Display talent search results in a formatted table"""
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
        location = details.get("location", "N/A")
        availability = details.get("availability", "N/A")
        
        table_data.append([
            name,
            match_score,
            skills_match,
            experience_match,
            experience,
            location,
            availability
        ])
    
    # Display table
    headers = ["Name", "Match Score", "Skills Match", "Exp Match", "Experience", "Location", "Availability"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Display metadata
    metadata = results.get("metadata", {})
    filters = metadata.get("filters_applied", {})
    print("\nFilters applied:")
    for key, value in filters.items():
        if value is not None:
            print(f"  {key}: {value}")

def main():
    """Main test function"""
    print("Talent Search API Test")
    print("=====================\n")
    
    # Login
    access_token = login()
    if not access_token:
        return
    
    print("Successfully logged in")
    
    # Test 1: Basic search with skills only
    test1_params = {
        "skills": ["Python", "JavaScript", "React"]
    }
    test1_results = test_talent_search(access_token, test1_params)
    display_results(test1_results, "Test 1: Basic Skills Search")
    
    # Test 2: Search with experience filters
    test2_params = {
        "skills": ["Python", "JavaScript", "React"],
        "job_title": "Full Stack Developer"
    }
    test2_query = {
        "experience_min": 3,
        "experience_max": 10,
        "sort_by": "experience_years"
    }
    test2_results = test_talent_search(access_token, test2_params, test2_query)
    display_results(test2_results, "Test 2: Experience-Filtered Search")
    
    # Test 3: Search with education and availability filters
    test3_params = {
        "skills": ["Python", "Data Science", "Machine Learning"],
        "job_title": "Data Scientist",
        "industry": "Technology"
    }
    test3_query = {
        "education_level": "Masters,PhD",
        "availability": "Immediate,2 weeks",
        "min_match_score": 70
    }
    test3_results = test_talent_search(access_token, test3_params, test3_query)
    display_results(test3_results, "Test 3: Education and Availability Filtered Search")
    
    # Test 4: Location-based search with remote option
    test4_params = {
        "skills": ["Java", "Spring", "Microservices"],
        "location": "New York, NY"  # Ensure location is a string
    }
    test4_query = {
        "include_remote": True,
        "sort_by": "match_score",
        "limit": 5
    }
    test4_results = test_talent_search(access_token, test4_params, test4_query)
    display_results(test4_results, "Test 4: Location-Based Search with Remote Option")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 