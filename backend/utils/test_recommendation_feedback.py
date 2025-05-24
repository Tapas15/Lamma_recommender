#!/usr/bin/env python
"""
Test script for the recommendation feedback API endpoints.
This script will:
1. Login as a user
2. Test the recommendation feedback submission endpoint
3. Test the recommendation feedback summary endpoint
4. Display the results

Usage:
    python test_recommendation_feedback.py
"""

import requests
import json
import time
import random
from datetime import datetime
import sys

# API configuration
BASE_URL = "http://localhost:8000"
EMAIL = "johndoe@example.com"  # Can be either employer or candidate
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
            # Try employer login if candidate login fails
            login_data["username"] = "techcorp@example.com"
            response = requests.post(f"{BASE_URL}/token", data=login_data)
            if response.status_code == 200:
                token_data = response.json()
                return token_data["access_token"]
            else:
                print(f"Employer login also failed: {response.status_code} - {response.text}")
                sys.exit(1)
    except Exception as e:
        print(f"Error during login: {str(e)}")
        sys.exit(1)

def test_submit_feedback(access_token):
    """Test submitting recommendation feedback"""
    url = f"{BASE_URL}/recommendations/feedback"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test with job recommendation feedback
    job_feedback = {
        "recommendation_id": f"job_rec_{random.randint(1000, 9999)}",
        "recommendation_type": "job",
        "relevance_score": random.randint(3, 5),
        "accuracy_score": random.randint(3, 5),
        "is_helpful": random.choice([True, False]),
        "feedback_text": "This job recommendation matched my skills well, but the location wasn't ideal.",
        "action_taken": random.choice(["viewed_details", "applied", "saved", "dismissed"])
    }
    
    print("\nTesting Job Recommendation Feedback Submission")
    print(json.dumps(job_feedback, indent=2))
    
    response = requests.post(url, json=job_feedback, headers=headers)
    
    if response.status_code == 200:
        print("✅ Job feedback submission successful")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Job feedback submission failed: {response.status_code}")
        print(response.text)
    
    # Test with candidate recommendation feedback
    candidate_feedback = {
        "recommendation_id": f"candidate_rec_{random.randint(1000, 9999)}",
        "recommendation_type": "candidate",
        "relevance_score": random.randint(3, 5),
        "accuracy_score": random.randint(3, 5),
        "is_helpful": random.choice([True, False]),
        "feedback_text": "Good candidate match for technical skills, but experience level was too junior.",
        "action_taken": random.choice(["viewed_details", "contacted", "saved", "dismissed"])
    }
    
    print("\nTesting Candidate Recommendation Feedback Submission")
    print(json.dumps(candidate_feedback, indent=2))
    
    response = requests.post(url, json=candidate_feedback, headers=headers)
    
    if response.status_code == 200:
        print("✅ Candidate feedback submission successful")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Candidate feedback submission failed: {response.status_code}")
        print(response.text)
    
    # Test with invalid feedback (missing required field)
    invalid_feedback = {
        "recommendation_id": f"job_rec_{random.randint(1000, 9999)}",
        # Missing recommendation_type
        "relevance_score": 4,
        "accuracy_score": 5
    }
    
    print("\nTesting Invalid Feedback Submission (Missing Field)")
    print(json.dumps(invalid_feedback, indent=2))
    
    response = requests.post(url, json=invalid_feedback, headers=headers)
    
    if response.status_code == 400:
        print("✅ Invalid feedback validation working correctly")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Invalid feedback validation failed: {response.status_code}")
        print(response.text)
    
    # Test with invalid score value
    invalid_score_feedback = {
        "recommendation_id": f"job_rec_{random.randint(1000, 9999)}",
        "recommendation_type": "job",
        "relevance_score": 10,  # Invalid score (should be 1-5)
        "accuracy_score": 5
    }
    
    print("\nTesting Invalid Feedback Submission (Invalid Score)")
    print(json.dumps(invalid_score_feedback, indent=2))
    
    response = requests.post(url, json=invalid_score_feedback, headers=headers)
    
    if response.status_code == 400:
        print("✅ Invalid score validation working correctly")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Invalid score validation failed: {response.status_code}")
        print(response.text)

def test_feedback_summary(access_token):
    """Test getting recommendation feedback summary"""
    url = f"{BASE_URL}/recommendations/feedback/summary"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Test with default parameters
    print("\nTesting Feedback Summary (Default Parameters)")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Feedback summary retrieval successful")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Feedback summary retrieval failed: {response.status_code}")
        print(response.text)
    
    # Test with specific recommendation type
    print("\nTesting Feedback Summary (Job Recommendations)")
    
    params = {"recommendation_type": "job"}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        print("✅ Job feedback summary retrieval successful")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Job feedback summary retrieval failed: {response.status_code}")
        print(response.text)
    
    # Test with specific period
    print("\nTesting Feedback Summary (Last 7 Days)")
    
    params = {"period": "last_7_days"}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        print("✅ 7-day feedback summary retrieval successful")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ 7-day feedback summary retrieval failed: {response.status_code}")
        print(response.text)

def main():
    """Main function to run tests"""
    print("RECOMMENDATION FEEDBACK API TESTS")
    print("================================\n")
    
    try:
        # Login
        access_token = login()
        print("✅ Login successful")
        
        # Test feedback submission
        test_submit_feedback(access_token)
        
        # Test feedback summary
        test_feedback_summary(access_token)
        
        print("\nALL TESTS COMPLETED")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 