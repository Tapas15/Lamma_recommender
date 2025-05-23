#!/usr/bin/env python
"""
Service starter script for the Job Recommender application.
Starts both backend and frontend services.
"""

import subprocess
import sys
import time
import webbrowser
import requests
import platform
import os

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

def check_if_port_in_use(port):
    """Check if a port is already in use"""
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(
                f"netstat -ano | findstr :{port}", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0 and result.stdout.strip() != ""
        else:
            result = subprocess.run(
                f"lsof -i :{port}", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0 and result.stdout.strip() != ""
    except Exception as e:
        print(f"Error checking port {port}: {e}")
        return False

def check_service(url, timeout=3):
    """Check if a service is responding at the given URL"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code < 400
    except requests.RequestException:
        return False

def start_services():
    """Start both backend and frontend services"""
    print("===== Starting Job Recommender System Services =====")
    
    # Check if services are already running
    backend_running = check_service(f"{BACKEND_URL}/docs")
    frontend_running = check_service(FRONTEND_URL)
    
    if backend_running and frontend_running:
        print("✅ Both services are already running!")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Docs:    {BACKEND_URL}/docs")
        print(f"Frontend:    {FRONTEND_URL}")
        return True
    
    # Check ports
    backend_port_used = check_if_port_in_use(8000)
    frontend_port_used = check_if_port_in_use(8501)
    
    if backend_port_used and not backend_running:
        print("⚠️ Backend port 8000 is in use but service is not responding.")
        print("   You may need to kill the process using this port.")
        print("   Use 'python diagnostics/service_check.py' to get more information.")
        return False
    
    if frontend_port_used and not frontend_running:
        print("⚠️ Frontend port 8501 is in use but service is not responding.")
        print("   You may need to kill the process using this port.")
        print("   Use 'python diagnostics/service_check.py' to get more information.")
        return False
    
    # Start services
    try:
        print("\nStarting Job Recommender services...")
        
        # Use run_app.py to start both services
        subprocess.Popen(["python", "run_app.py", "--no-browser"])
        
        # Wait for services to start
        max_wait = 30  # seconds
        start_time = time.time()
        backend_started = False
        frontend_started = False
        
        print("\nWaiting for services to start...")
        while time.time() - start_time < max_wait:
            if not backend_started:
                backend_started = check_service(f"{BACKEND_URL}/docs")
                if backend_started:
                    print("✅ Backend started successfully!")
            
            if not frontend_started:
                frontend_started = check_service(FRONTEND_URL)
                if frontend_started:
                    print("✅ Frontend started successfully!")
            
            if backend_started and frontend_started:
                break
                
            time.sleep(1)
        
        # Final status
        if backend_started and frontend_started:
            print("\n🎉 All services started successfully!")
            print(f"Backend URL: {BACKEND_URL}")
            print(f"API Docs:    {BACKEND_URL}/docs")
            print(f"Frontend:    {FRONTEND_URL}")
            
            # Ask if user wants to open in browser
            open_browser = input("\nOpen in browser? (y/n): ")
            if open_browser.lower() == 'y':
                webbrowser.open(FRONTEND_URL)
                webbrowser.open(f"{BACKEND_URL}/docs")
            
            return True
        else:
            print("\n❌ Failed to start all services.")
            
            if not backend_started:
                print("   - Backend failed to start")
            
            if not frontend_started:
                print("   - Frontend failed to start")
                
            print("\nTry running 'python diagnostics/service_check.py' for more details.")
            return False
            
    except Exception as e:
        print(f"Error starting services: {e}")
        return False

if __name__ == "__main__":
    start_services() 