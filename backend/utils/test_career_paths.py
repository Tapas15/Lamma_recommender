#!/usr/bin/env python
"""
Test script for the career paths endpoint.
This script will:
1. Login as a candidate
2. Call the career paths endpoint with different parameters
3. Display the results

Usage:
    python test_career_paths.py
"""

import requests
import json
import sys
from tabulate import tabulate

# API configuration
BASE_URL = "http://localhost:8000"
EMAIL = "testcandidate@example.com"
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

def test_career_paths(token, current_role="Software Engineer", industry="Technology", 
                     timeframe_years=5, include_skill_requirements=True, include_salary_data=True):
    """Test the career paths endpoint with different parameters"""
    if not token:
        print("❌ No authentication token available")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting career paths for {current_role} in {industry} industry (timeframe: {timeframe_years} years)...")
    
    try:
        url = f"{BASE_URL}/recommendations/career-paths"
        params = {
            "current_role": current_role,
            "industry": industry,
            "timeframe_years": timeframe_years,
            "include_skill_requirements": str(include_skill_requirements).lower(),
            "include_salary_data": str(include_salary_data).lower()
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            paths = result.get("paths", [])
            
            if not paths:
                print("No career paths found for the given parameters.")
                return
            
            print(f"Found {len(paths)} career paths:")
            
            for i, path in enumerate(paths):
                print(f"\n{'-' * 80}")
                print(f"Path {i+1}: {path.get('name')}")
                print(f"{'-' * 80}")
                
                print(f"Description: {path.get('description')}")
                print(f"Average Time: {path.get('average_time_years')} years")
                print(f"Salary Growth: {path.get('salary_growth_percentage')}%")
                print(f"Difficulty: {path.get('difficulty')}/10")
                
                steps = path.get("steps", [])
                print(f"\nCareer Steps ({len(steps)}):")
                
                for j, step in enumerate(steps):
                    print(f"\n  Step {j+1}: {step.get('role')}")
                    print(f"  Timeline: {step.get('timeline')}")
                    print(f"  Description: {step.get('description')}")
                    
                    if "skills" in step:
                        print(f"  Skills: {', '.join(step.get('skills', []))}")
                    
                    if include_skill_requirements and "skill_requirements" in step:
                        print("\n  Skill Requirements:")
                        skill_reqs = step.get("skill_requirements", {})
                        
                        for category, skills in skill_reqs.items():
                            print(f"    {category.title()}: {', '.join(skills)}")
                    
                    if "responsibilities" in step:
                        print(f"\n  Responsibilities: {', '.join(step.get('responsibilities', []))}")
                    
                    if include_salary_data and "salary_data" in step:
                        salary_data = step.get("salary_data", {})
                        median = salary_data.get("median", "N/A")
                        salary_range = salary_data.get("range", {})
                        min_salary = salary_range.get("min", "N/A")
                        max_salary = salary_range.get("max", "N/A")
                        currency = salary_data.get("currency", "USD")
                        
                        print(f"\n  Salary: {median} {currency} (Range: {min_salary}-{max_salary} {currency})")
            
            return True
        else:
            print(f"❌ Failed to get career paths: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error testing career paths: {str(e)}")
        return False

def main():
    """Main function"""
    print("=" * 80)
    print("TESTING CAREER PATHS ENDPOINT")
    print("=" * 80)
    
    # Login
    token = login()
    if not token:
        print("❌ Failed to login, exiting...")
        sys.exit(1)
    
    # Test different combinations
    test_cases = [
        {
            "current_role": "Software Engineer",
            "industry": "Technology",
            "timeframe_years": 5,
            "include_skill_requirements": True,
            "include_salary_data": True
        },
        {
            "current_role": "Software Engineer",
            "industry": "Finance",
            "timeframe_years": 3,
            "include_skill_requirements": True,
            "include_salary_data": False
        },
        {
            "current_role": "Data Scientist",
            "industry": "Technology",
            "timeframe_years": 4,
            "include_skill_requirements": False,
            "include_salary_data": True
        }
    ]
    
    for test_case in test_cases:
        test_career_paths(token, **test_case)
        print("\n" + "=" * 80)

if __name__ == "__main__":
    main() 