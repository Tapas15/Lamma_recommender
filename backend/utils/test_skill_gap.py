#!/usr/bin/env python
"""
Test script for the improved skill gap endpoint.
This script will:
1. Login as a candidate
2. Call the skill gap endpoint with different parameters
3. Display the results

Usage:
    python test_skill_gap.py
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

def test_skill_gap(token, target_role="Software Engineer", industry="Technology", include_learning_resources=True):
    """Test the skill gap endpoint with different parameters"""
    if not token:
        print("❌ No authentication token available")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting skill gap analysis for {target_role} in {industry} industry...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/recommendations/skill-gap?target_role={target_role}&industry={industry}&include_learning_resources={str(include_learning_resources).lower()}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Print match score
            match_score = result.get("match_score", 0)
            print(f"Match Score: {match_score}%")
            
            # Print your skills
            your_skills = result.get("your_skills", [])
            if your_skills:
                print("\nYour Skills:")
                skill_data = [[s.get("name"), s.get("proficiency")] for s in your_skills[:10]]
                print(tabulate(skill_data, headers=["Skill", "Proficiency"], tablefmt="grid"))
            
            # Print required skills
            required_skills = result.get("required_skills", [])
            if required_skills:
                print("\nRequired Skills:")
                skill_data = [[s.get("name"), s.get("importance")] for s in required_skills[:10]]
                print(tabulate(skill_data, headers=["Skill", "Importance"], tablefmt="grid"))
            
            # Print missing skills
            missing_skills = result.get("missing_skills", [])
            if missing_skills:
                print("\nMissing Skills:")
                skill_data = [[s.get("name"), s.get("importance")] for s in missing_skills[:10]]
                print(tabulate(skill_data, headers=["Skill", "Importance"], tablefmt="grid"))
            
            # Print categorized missing skills
            categorized_missing_skills = result.get("categorized_missing_skills", {})
            if categorized_missing_skills:
                print("\nCategorized Missing Skills:")
                for category, skills in categorized_missing_skills.items():
                    print(f"\n{category.title()}:")
                    skill_data = [[s.get("name"), s.get("importance")] for s in skills[:5]]
                    print(tabulate(skill_data, headers=["Skill", "Importance"], tablefmt="grid"))
            
            # Print industry-specific requirements
            industry_specific = result.get("industry_specific_requirements", [])
            if industry_specific:
                print("\nIndustry-Specific Requirements:")
                skill_data = [[s.get("name"), s.get("importance")] for s in industry_specific]
                print(tabulate(skill_data, headers=["Skill", "Importance"], tablefmt="grid"))
            
            # Print market demand
            market_demand = result.get("market_demand")
            if market_demand:
                print("\nMarket Demand:")
                demand_data = [
                    ["Demand Score", market_demand.get("demand_score", "N/A")],
                    ["Growth Rate", f"{market_demand.get('growth_rate', 'N/A')}%"],
                    ["Average Salary", market_demand.get("avg_salary", "N/A")]
                ]
                print(tabulate(demand_data, tablefmt="grid"))
            
            # Print learning resources
            if include_learning_resources:
                learning_resources = result.get("learning_resources", {}).get("resources", [])
                if learning_resources:
                    print("\nLearning Resources:")
                    for resource in learning_resources:
                        skill = resource.get("skill")
                        resources = resource.get("resources", [])
                        print(f"\n{skill}:")
                        for r in resources[:2]:  # Show only first 2 resources per skill
                            print(f"  - {r.get('title')} ({r.get('provider')})")
                            print(f"    {r.get('description')}")
            
            return True
        else:
            print(f"❌ Failed to get skill gap analysis: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error testing skill gap analysis: {str(e)}")
        return False

def main():
    """Main function"""
    print("=" * 80)
    print("TESTING IMPROVED SKILL GAP ENDPOINT")
    print("=" * 80)
    
    # Login
    token = login()
    if not token:
        print("❌ Failed to login, exiting...")
        sys.exit(1)
    
    # Test different combinations
    test_cases = [
        {"target_role": "Software Engineer", "industry": "Technology"},
        {"target_role": "Data Scientist", "industry": "Finance"},
        {"target_role": "Senior Software Engineer", "industry": "Healthcare"}
    ]
    
    for test_case in test_cases:
        test_skill_gap(token, **test_case)
        print("\n" + "-" * 80)

if __name__ == "__main__":
    main() 