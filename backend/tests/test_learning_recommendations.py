import requests
import json
import sys
import os
from tabulate import tabulate
from dotenv import load_dotenv
import time

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_CANDIDATE_EMAIL = os.getenv("TEST_CANDIDATE_EMAIL", "test@example.com")
TEST_CANDIDATE_PASSWORD = os.getenv("TEST_CANDIDATE_PASSWORD", "password")
TEST_EMPLOYER_EMAIL = os.getenv("TEST_EMPLOYER_EMAIL", "employer@example.com")
TEST_EMPLOYER_PASSWORD = os.getenv("TEST_EMPLOYER_PASSWORD", "password")

def get_token():
    """Get authentication token"""
    login_data = {
        "username": TEST_CANDIDATE_EMAIL,
        "password": TEST_CANDIDATE_PASSWORD
    }
    
    response = requests.post(f"{API_BASE_URL}/token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get token: {response.status_code} - {response.text}")
        return None

def test_basic_learning_recommendations(token):
    """Test basic learning recommendations functionality"""
    print("\n===== Testing Basic Learning Recommendations =====")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Use some sample skills to test
    test_skills = ["Python", "React", "Machine Learning"]
    skills_param = json.dumps(test_skills)
    
    # Make request
    start_time = time.time()
    response = requests.get(
        f"{API_BASE_URL}/recommendations/learning?skills={skills_param}",
        headers=headers
    )
    end_time = time.time()
    
    # Print response time
    print(f"\nResponse time: {(end_time - start_time):.2f} seconds")
    
    # Check response status
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    
    # Parse response
    result = response.json()
    
    # Print basic information
    print("\n===== Learning Recommendations =====")
    print(f"Timeframe: {result.get('timeframe')}")
    print(f"Timeframe Months: {result.get('timeframe_months')}")
    
    # Print resources
    resources = result.get("resources", [])
    if resources:
        print(f"\nFound {len(resources)} skill resources")
        
        for resource_group in resources:
            skill = resource_group.get("skill", "Unknown")
            skill_resources = resource_group.get("resources", [])
            
            print(f"\n--- Resources for {skill} ---")
            
            if skill_resources:
                resource_data = []
                for resource in skill_resources[:2]:  # Show top 2 resources per skill
                    resource_data.append([
                        resource.get("title", "N/A"),
                        resource.get("provider", "N/A"),
                        resource.get("duration", "N/A"),
                        resource.get("level", "N/A")
                    ])
                
                print(tabulate(
                    resource_data,
                    headers=["Title", "Provider", "Duration", "Level"],
                    tablefmt="grid"
                ))
            else:
                print("No resources found for this skill")
    
    # Return the result for further processing if needed
    return result

def test_career_goal_recommendations(token):
    """Test learning recommendations with career goal"""
    print("\n===== Testing Career Goal Learning Recommendations =====")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Career goal parameters
    career_goal = "Senior Software Engineer"
    timeframe = "6_months"
    
    # Make request
    start_time = time.time()
    response = requests.get(
        f"{API_BASE_URL}/recommendations/learning?career_goal={career_goal}&timeframe={timeframe}",
        headers=headers
    )
    end_time = time.time()
    
    # Print response time
    print(f"\nResponse time: {(end_time - start_time):.2f} seconds")
    
    # Check response status
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    
    # Parse response
    result = response.json()
    
    # Print basic information
    print("\n===== Career Goal Learning Recommendations =====")
    print(f"Career Goal: {result.get('career_goal')}")
    print(f"Timeframe: {result.get('timeframe')}")
    print(f"Timeframe Months: {result.get('timeframe_months')}")
    
    # Print learning path if available
    learning_path = result.get("learning_path", {})
    if learning_path:
        print("\n===== Learning Path =====")
        
        phases = learning_path.get("phases", [])
        for i, phase in enumerate(phases):
            print(f"\n--- {phase.get('name')} ---")
            print(f"Duration: {phase.get('duration_months')} months")
            
            resources = phase.get("resources", [])
            if resources:
                resource_data = []
                for resource in resources:
                    resource_data.append([
                        resource.get("skill", "N/A"),
                        resource.get("title", "N/A"),
                        resource.get("provider", "N/A"),
                        resource.get("duration", "N/A")
                    ])
                
                print(tabulate(
                    resource_data,
                    headers=["Skill", "Title", "Provider", "Duration"],
                    tablefmt="grid"
                ))
    
    # Print resources
    resources = result.get("resources", [])
    if resources:
        print(f"\nFound {len(resources)} skill resources")
        
        # Count career goal skills
        career_goal_skills = [r for r in resources if r.get("from_career_goal", False)]
        print(f"Career goal skills: {len(career_goal_skills)}")
        
        # Show one example resource for each career goal skill
        if career_goal_skills:
            print("\n===== Career Goal Skills =====")
            for resource_group in career_goal_skills[:3]:  # Show top 3 career goal skills
                skill = resource_group.get("skill", "Unknown")
                skill_resources = resource_group.get("resources", [])
                
                if skill_resources:
                    print(f"\n--- {skill} ---")
                    resource = skill_resources[0]  # Show first resource
                    print(f"Title: {resource.get('title', 'N/A')}")
                    print(f"Provider: {resource.get('provider', 'N/A')}")
                    print(f"Duration: {resource.get('duration', 'N/A')}")
                    print(f"Level: {resource.get('level', 'N/A')}")
    
    # Return the result for further processing if needed
    return result

def test_different_timeframes(token):
    """Test learning recommendations with different timeframes"""
    print("\n===== Testing Different Timeframes =====")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Career goal parameters
    career_goal = "Senior Software Engineer"
    timeframes = ["3_months", "6_months", "1_year", "2_years"]
    
    for timeframe in timeframes:
        print(f"\n----- Testing Timeframe: {timeframe} -----")
        
        # Make request
        response = requests.get(
            f"{API_BASE_URL}/recommendations/learning?career_goal={career_goal}&timeframe={timeframe}",
            headers=headers
        )
        
        # Check response status
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            continue
        
        # Parse response
        result = response.json()
        
        # Print basic information
        print(f"Timeframe: {result.get('timeframe')}")
        print(f"Timeframe Months: {result.get('timeframe_months')}")
        
        # Count resources
        resources = result.get("resources", [])
        total_resources = sum(len(r.get("resources", [])) for r in resources)
        print(f"Total resources: {total_resources}")
        
        # Print learning path summary if available
        learning_path = result.get("learning_path", {})
        if learning_path:
            phases = learning_path.get("phases", [])
            print(f"Learning path phases: {len(phases)}")
            
            # Count resources in each phase
            for i, phase in enumerate(phases):
                resources = phase.get("resources", [])
                print(f"Phase {i+1} resources: {len(resources)}")

def run_tests():
    """Run all tests"""
    # Get authentication token
    token = get_token()
    if not token:
        print("Failed to get authentication token. Exiting.")
        return
    
    # Run basic test
    test_basic_learning_recommendations(token)
    
    # Test with career goal
    test_career_goal_recommendations(token)
    
    # Test with different timeframes
    test_different_timeframes(token)
    
    print("\n===== All tests completed =====")

if __name__ == "__main__":
    run_tests() 