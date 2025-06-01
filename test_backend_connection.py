#!/usr/bin/env python3
"""
Quick test script to verify backend connectivity
"""
import requests
import time

def test_backend_connection():
    """Test if the backend is running and accessible"""
    base_url = "http://localhost:8000"
    endpoints = [
        "/health",
        "/jobs/public",
        "/docs"
    ]
    
    print("🔍 Testing Backend Connection...")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"Testing {url}...")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK (Status: {response.status_code})")
                if endpoint == "/jobs/public":
                    try:
                        data = response.json()
                        print(f"   📝 Jobs found: {len(data) if isinstance(data, list) else 'Unknown'}")
                    except:
                        print("   ⚠️  Response is not valid JSON")
            else:
                print(f"❌ {endpoint}: Error (Status: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Connection refused - Backend not running")
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint}: Timeout - Backend not responding")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {str(e)}")
        
        print()
    
    print("=" * 50)
    print("💡 If you see connection errors:")
    print("   1. Make sure to start the backend: python run_cors_backend.py")
    print("   2. Check if port 8000 is available")
    print("   3. Verify virtual environment is activated")
    print("   4. Check firewall settings")

if __name__ == "__main__":
    test_backend_connection() 