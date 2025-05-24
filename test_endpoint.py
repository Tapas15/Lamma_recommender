import requests
import json
import sys

# API configuration
API_BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzE2MzIzMjAwfQ.zB7zCxnxS7Vk5aIVBmtWLFjMUCLvL22Cj4mQpCJlg8A"

def test_endpoint(endpoint):
    """Test an endpoint with authentication"""
    print(f"Testing endpoint: {endpoint}")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test the health endpoint first
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Health endpoint status: {response.status_code}")
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    # Test the ML learning recommendations endpoint
    endpoint = "/ml/learning-recommendations?career_goal=Senior%20Software%20Engineer&timeframe=6_months"

    test_endpoint(endpoint)
    
    # Also test the original learning recommendations endpoint for comparison
    endpoint = "/recommendations/learning?career_goal=Senior%20Software%20Engineer&timeframe=6_months"
    test_endpoint(endpoint) 
    test_endpoint(endpoint) 