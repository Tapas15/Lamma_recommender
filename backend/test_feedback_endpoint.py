import requests
import json

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
                return None
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None

def test_feedback_endpoint(access_token):
    """Test the recommendation feedback endpoint"""
    if not access_token:
        print("No access token available. Cannot test endpoint.")
        return
    
    url = f"{BASE_URL}/recommendations/feedback"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test payload
    feedback_data = {
        "recommendation_id": "job_rec_1234",
        "recommendation_type": "job",
        "relevance_score": 4,
        "accuracy_score": 5,
        "is_helpful": True,
        "feedback_text": "This job recommendation matched my skills well, but the location wasn't ideal.",
        "action_taken": "viewed_details"
    }
    
    print("\nTesting Recommendation Feedback Endpoint")
    print(json.dumps(feedback_data, indent=2))
    
    try:
        response = requests.post(url, json=feedback_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Feedback submission successful")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Feedback submission failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error testing feedback endpoint: {str(e)}")

def main():
    """Main function"""
    print("RECOMMENDATION FEEDBACK API TEST")
    print("===============================\n")
    
    # Login
    access_token = login()
    if access_token:
        print("✅ Login successful")
        
        # Test feedback endpoint
        test_feedback_endpoint(access_token)
    else:
        print("❌ Login failed. Cannot proceed with tests.")

if __name__ == "__main__":
    main() 