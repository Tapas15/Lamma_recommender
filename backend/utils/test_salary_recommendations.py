#!/usr/bin/env python
"""
Test script for the salary recommendations API endpoint.
This script will:
1. Login as a user
2. Test the salary recommendations endpoint with various parameters
3. Display the results

Usage:
    python test_salary_recommendations.py
"""

import requests
import json
import sys
from tabulate import tabulate

# API configuration
BASE_URL = "http://localhost:8000"
EMAIL = "testemployer@example.com"  # Can be either employer or candidate
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

def test_salary_recommendations(access_token, job_params):
    """Test the salary recommendations endpoint with given parameters"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/recommendations/salary"
    
    try:
        response = requests.post(url, headers=headers, json=job_params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Salary recommendations request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during salary recommendations request: {str(e)}")
        return None

def display_results(results, test_name):
    """Display salary recommendation results in a formatted way"""
    if not results:
        print(f"\n{test_name}: No results or error occurred")
        return
    
    print(f"\n{test_name}")
    print("=" * len(test_name))
    
    # Display basic info
    job_title = results.get("job_title", "N/A")
    salary_rec = results.get("salary_recommendation", {})
    salary_range = salary_rec.get("range", {})
    min_salary = salary_range.get("min", 0)
    max_salary = salary_range.get("max", 0)
    median = salary_rec.get("median", 0)
    currency = salary_rec.get("currency", "USD")
    
    print(f"Job Title: {job_title}")
    print(f"Salary Range: {currency} {min_salary:,} - {currency} {max_salary:,}")
    print(f"Median Salary: {currency} {median:,}")
    
    # Display percentiles
    market_comparison = results.get("market_comparison", {})
    percentiles = market_comparison.get("percentiles", {})
    
    if percentiles:
        print("\nSalary Percentiles:")
        percentile_data = []
        for percentile, value in percentiles.items():
            percentile_data.append([percentile, f"{currency} {value:,}"])
        print(tabulate(percentile_data, headers=["Percentile", "Salary"], tablefmt="grid"))
    
    # Display regional comparison
    regional_comparison = market_comparison.get("regional_comparison", [])
    
    if regional_comparison:
        print("\nRegional Comparison:")
        regional_data = []
        for region in regional_comparison:
            location = region.get("location", "N/A")
            median_salary = region.get("median_salary", 0)
            diff_pct = region.get("difference_percentage", 0)
            diff_str = f"{diff_pct:+d}%" if diff_pct != 0 else "0%"
            regional_data.append([location, f"{currency} {median_salary:,}", diff_str])
        print(tabulate(regional_data, headers=["Location", "Median Salary", "Difference"], tablefmt="grid"))
    
    # Display industry comparison
    industry_comparison = market_comparison.get("industry_comparison", [])
    
    if industry_comparison:
        print("\nIndustry Comparison:")
        industry_data = []
        for ind in industry_comparison:
            industry_name = ind.get("industry", "N/A")
            median_salary = ind.get("median_salary", 0)
            diff_pct = ind.get("difference_percentage", 0)
            diff_str = f"{diff_pct:+d}%" if diff_pct != 0 else "0%"
            industry_data.append([industry_name, f"{currency} {median_salary:,}", diff_str])
        print(tabulate(industry_data, headers=["Industry", "Median Salary", "Difference"], tablefmt="grid"))
    
    # Display factors affecting salary
    factors = results.get("factors", [])
    
    if factors:
        print("\nFactors Affecting Salary:")
        factor_data = []
        for factor in factors:
            factor_name = factor.get("factor", "N/A")
            impact = factor.get("impact", "N/A")
            description = factor.get("description", "N/A")
            
            # Format impact
            if impact == "positive":
                impact_str = "↑ Positive"
            elif impact == "negative":
                impact_str = "↓ Negative"
            else:
                impact_str = "↔ Neutral"
                
            factor_data.append([factor_name, impact_str, description])
        print(tabulate(factor_data, headers=["Factor", "Impact", "Description"], tablefmt="grid"))
    
    # Display metadata
    metadata = results.get("metadata", {})
    confidence = metadata.get("confidence_level", "N/A")
    data_freshness = metadata.get("data_freshness", "N/A")
    
    print(f"\nConfidence Level: {confidence}")
    print(f"Data Freshness: {data_freshness}")

def main():
    """Main test function"""
    print("Salary Recommendations API Test")
    print("==============================\n")
    
    # Login
    access_token = login()
    if not access_token:
        return
    
    print("Successfully logged in")
    
    # Test 1: Basic test with job title only
    test1_params = {
        "job_title": "Software Engineer"
    }
    test1_results = test_salary_recommendations(access_token, test1_params)
    display_results(test1_results, "Test 1: Basic Job Title Only")
    
    # Test 2: Software Engineer with experience and location
    test2_params = {
        "job_title": "Software Engineer",
        "experience_years": 3,
        "location": "San Francisco, CA",
        "industry": "Technology"
    }
    test2_results = test_salary_recommendations(access_token, test2_params)
    display_results(test2_results, "Test 2: Software Engineer in San Francisco")
    
    # Test 3: Senior role with premium skills
    test3_params = {
        "job_title": "Senior Software Engineer",
        "required_skills": ["JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes"],
        "experience_years": 7,
        "location": "New York, NY",
        "industry": "Finance",
        "company_size": "1001-5000 employees"
    }
    test3_results = test_salary_recommendations(access_token, test3_params)
    display_results(test3_results, "Test 3: Senior Engineer with Premium Skills")
    
    # Test 4: Remote position
    test4_params = {
        "job_title": "Full Stack Developer",
        "required_skills": ["Python", "Django", "JavaScript", "React"],
        "experience_years": 4,
        "remote_position": True,
        "industry": "Technology",
        "company_size": "51-200 employees"
    }
    test4_results = test_salary_recommendations(access_token, test4_params)
    display_results(test4_results, "Test 4: Remote Full Stack Developer")
    
    # Test 5: Data Scientist role
    test5_params = {
        "job_title": "Data Scientist",
        "required_skills": ["Python", "Machine Learning", "SQL", "Data Analysis"],
        "experience_years": 2,
        "location": "Austin, TX",
        "industry": "Healthcare",
        "company_size": "201-500 employees"
    }
    test5_results = test_salary_recommendations(access_token, test5_params)
    display_results(test5_results, "Test 5: Data Scientist in Healthcare")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 