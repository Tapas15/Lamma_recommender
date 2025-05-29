#!/usr/bin/env python
"""
Diagnostic and Fix Script for API Errors
This script identifies and fixes the ApiError issues in professional, jobs, and projects sections.
"""
import requests
import json
import time
import subprocess
import sys
import os
from pathlib import Path

def test_backend_endpoint(url, description=""):
    """Test a backend endpoint and return status"""
    try:
        print(f"Testing {description}: {url}")
        response = requests.get(url, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Response: Success (returned {len(data) if isinstance(data, list) else 'object'})")
                return True
            except:
                print(f"  Response: Success (non-JSON)")
                return True
        else:
            print(f"  Error: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  Error: Connection refused - Backend not running")
        return False
    except Exception as e:
        print(f"  Error: {str(e)}")
        return False

def check_backend_health():
    """Check if backend is running and healthy"""
    print("=" * 50)
    print("BACKEND HEALTH CHECK")
    print("=" * 50)
    
    backend_base = "http://localhost:8000"
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/docs", "API documentation"),
        ("/jobs/public", "Public jobs"),
        ("/projects/public", "Public projects"),
        ("/candidates/public", "Public candidates"),
    ]
    
    backend_running = False
    for endpoint, description in endpoints:
        if test_backend_endpoint(f"{backend_base}{endpoint}", description):
            backend_running = True
            break
    
    return backend_running

def check_frontend_proxy():
    """Check if frontend proxy is working"""
    print("\n" + "=" * 50)
    print("FRONTEND PROXY CHECK")
    print("=" * 50)
    
    frontend_base = "http://localhost:3000"
    endpoints = [
        ("/health", "Health check via proxy"),
        ("/candidates/public", "Candidates via proxy"),
        ("/jobs/public", "Jobs via proxy"),
        ("/projects/public", "Projects via proxy"),
    ]
    
    proxy_working = False
    for endpoint, description in endpoints:
        if test_backend_endpoint(f"{frontend_base}{endpoint}", description):
            proxy_working = True
    
    return proxy_working

def start_backend():
    """Start the backend server"""
    print("\n" + "=" * 50)
    print("STARTING BACKEND")
    print("=" * 50)
    
    try:
        # Check if already running
        if test_backend_endpoint("http://localhost:8000/health", "Health check"):
            print("Backend is already running!")
            return True
            
        print("Starting backend server...")
        # Use subprocess to start backend
        subprocess.Popen([
            sys.executable, "run_cors_backend.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for backend to start
        for i in range(10):
            time.sleep(2)
            print(f"Waiting for backend... ({i+1}/10)")
            if test_backend_endpoint("http://localhost:8000/health", "Health check"):
                print("✅ Backend started successfully!")
                return True
        
        print("❌ Backend failed to start")
        return False
        
    except Exception as e:
        print(f"❌ Error starting backend: {str(e)}")
        return False

def start_frontend():
    """Start the frontend server"""
    print("\n" + "=" * 50)
    print("STARTING FRONTEND")
    print("=" * 50)
    
    try:
        # Check if already running
        if test_backend_endpoint("http://localhost:3000", "Frontend check"):
            print("Frontend is already running!")
            return True
            
        print("Starting frontend server...")
        frontend_dir = Path("frontend/lnd-nexus")
        if frontend_dir.exists():
            os.chdir(frontend_dir)
            subprocess.Popen([
                "npm", "run", "dev"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.chdir("../..")
            
            # Wait for frontend to start
            for i in range(15):
                time.sleep(2)
                print(f"Waiting for frontend... ({i+1}/15)")
                if test_backend_endpoint("http://localhost:3000", "Frontend check"):
                    print("✅ Frontend started successfully!")
                    return True
            
        print("❌ Frontend failed to start")
        return False
        
    except Exception as e:
        print(f"❌ Error starting frontend: {str(e)}")
        return False

def diagnose_api_errors():
    """Main diagnostic function"""
    print("🔍 DIAGNOSING API ERRORS")
    print("=" * 60)
    print("This script will identify and fix ApiError issues in:")
    print("- Professional section")
    print("- Jobs section") 
    print("- Projects section")
    print("=" * 60)
    
    # Step 1: Check backend
    backend_healthy = check_backend_health()
    if not backend_healthy:
        print("\n🚨 ISSUE FOUND: Backend not running or unhealthy")
        if input("Start backend automatically? (y/n): ").lower() == 'y':
            backend_healthy = start_backend()
    
    if not backend_healthy:
        print("\n❌ CRITICAL: Cannot proceed without healthy backend")
        return False
    
    # Step 2: Check frontend proxy
    frontend_healthy = check_frontend_proxy()
    if not frontend_healthy:
        print("\n🚨 ISSUE FOUND: Frontend proxy not working")
        if input("Start frontend automatically? (y/n): ").lower() == 'y':
            frontend_healthy = start_frontend()
            if frontend_healthy:
                time.sleep(5)  # Give proxy time to initialize
                frontend_healthy = check_frontend_proxy()
    
    # Step 3: Provide solutions
    print("\n" + "=" * 50)
    print("DIAGNOSIS RESULTS")
    print("=" * 50)
    
    if backend_healthy and frontend_healthy:
        print("✅ All systems healthy! API errors should be resolved.")
        print("\n🌐 Access your application at:")
        print("   http://localhost:3000")
        print("\n📚 Test these endpoints:")
        print("   http://localhost:3000/candidates/public")
        print("   http://localhost:3000/jobs/public")
        print("   http://localhost:3000/projects/public")
        print("   http://localhost:3000/health")
        return True
    else:
        print("❌ Issues remain. Manual intervention required.")
        print("\n📋 Manual Steps:")
        
        if not backend_healthy:
            print("1. Start backend: python run_cors_backend.py")
            
        if not frontend_healthy:
            print("2. Start frontend: cd frontend/lnd-nexus && npm run dev")
            
        print("3. Check proxy configuration in frontend/lnd-nexus/next.config.ts")
        print("4. Verify API_BASE_URL in frontend/lnd-nexus/app/services/api.ts")
        
        return False

if __name__ == "__main__":
    try:
        success = diagnose_api_errors()
        if success:
            print("\n🎉 API errors should now be resolved!")
        else:
            print("\n⚠️  Manual intervention required.")
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnostic cancelled by user")
    except Exception as e:
        print(f"\n💥 Diagnostic error: {str(e)}")
        import traceback
        traceback.print_exc() 