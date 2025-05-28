#!/usr/bin/env python3
"""
Script to run the working backend and test endpoints
"""
import subprocess
import time
import requests
import sys
import os

def test_endpoint(url, description):
    """Test an endpoint and print results"""
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ {description}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   📊 Returned {len(data)} items")
            else:
                print(f"   📄 Response: {data}")
        else:
            print(f"   ❌ Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ {description}: Failed - {str(e)}")
        return False

def main():
    print("🚀 Starting Working Backend Server...")
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    os.chdir(backend_dir)
    
    # Start the server
    try:
        # Kill any existing Python processes
        try:
            subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                         capture_output=True, check=False)
            time.sleep(2)
        except:
            pass
        
        print("Starting uvicorn server...")
        process = subprocess.Popen([
            "python", "-m", "uvicorn", "working_app:app", 
            "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(8)
        
        # Test endpoints
        print("\n🧪 Testing Endpoints...")
        
        success_count = 0
        total_tests = 4
        
        if test_endpoint("http://localhost:8000/", "Root endpoint"):
            success_count += 1
            
        if test_endpoint("http://localhost:8000/health", "Health check"):
            success_count += 1
            
        if test_endpoint("http://localhost:8000/candidates/public", "Candidates endpoint"):
            success_count += 1
            
        if test_endpoint("http://localhost:8000/jobs/public", "Jobs endpoint"):
            success_count += 1
        
        print(f"\n📊 Test Results: {success_count}/{total_tests} endpoints working")
        
        if success_count == total_tests:
            print("🎉 All endpoints are working! Backend is ready.")
            print("🌐 Frontend can now connect to: http://localhost:8000")
            print("📚 API docs available at: http://localhost:8000/docs")
        else:
            print("⚠️  Some endpoints failed. Check the logs above.")
        
        # Keep server running
        print("\n⏳ Server is running. Press Ctrl+C to stop...")
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()
            
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 