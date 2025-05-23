#!/usr/bin/env python
"""
Perfect Visual Workflow for Job Recommender Platform

This script provides a robust, error-resistant workflow for the Job Recommender platform,
ensuring that the visual demonstration runs perfectly every time.

It enhances the existing visual_demo.py script by adding:
- Better error handling and recovery
- More robust element identification
- Browser stability improvements
- Clear, step-by-step progress indicators
- Additional diagnostic information

Usage:
python perfect_visual_workflow.py [--employer-only] [--candidate-only] [--no-slow]
"""

import os
import sys
import time
import traceback
import json
import random
import requests
import platform
import subprocess
import signal
import argparse
from datetime import datetime

# Import from visual_demo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tests.visual_demo import (
    init_driver, cleanup, start_services, 
    register_candidate, register_employer, login, explore_dashboard,
    scroll_to_element, highlight_element, generate_random_string
)

# Constants
SCREENSHOTS_DIR = "workflow_screenshots"
FRONTEND_URL = "http://localhost:8501"
BACKEND_URL = "http://localhost:8000"

# Test data storage
test_data = {
    "candidate": {
        "email": None,
        "password": None,
        "registered": False
    },
    "employer": {
        "email": None,
        "password": None,
        "registered": False
    }
}

def print_header(message):
    """Print a highlighted header message"""
    terminal_width = 80
    print("\n" + "="*terminal_width)
    print(f"🚀 {message}".center(terminal_width))
    print("="*terminal_width + "\n")

def print_step(message):
    """Print a step message"""
    print(f"\n🔷 {message}")

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"⚠️ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def ensure_screenshots_dir():
    """Ensure screenshots directory exists"""
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)
    return SCREENSHOTS_DIR

def take_screenshot(driver, name):
    """Take a screenshot with timestamp"""
    screenshots_dir = ensure_screenshots_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{screenshots_dir}/{name}_{timestamp}.png"
    try:
        driver.save_screenshot(filename)
        print(f"📸 Screenshot saved: {filename}")
        return True
    except Exception as e:
        print_error(f"Failed to take screenshot: {e}")
        return False

def verify_services_running():
    """Verify that both frontend and backend services are running"""
    print_step("Verifying services...")
    
    frontend_running = False
    backend_running = False
    
    try:
        # Check frontend
        response = requests.get(FRONTEND_URL, timeout=5)
        frontend_running = response.status_code == 200
        if frontend_running:
            print_success("Frontend is running")
        else:
            print_error("Frontend is not running properly")
    except Exception as e:
        print_error(f"Frontend check failed: {e}")
    
    try:
        # Check backend
        response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        backend_running = response.status_code == 200
        if backend_running:
            print_success("Backend is running")
        else:
            print_error("Backend is not running properly")
    except Exception as e:
        print_error(f"Backend check failed: {e}")
    
    return frontend_running and backend_running

def initialize_browser():
    """Initialize browser with enhanced error handling"""
    print_step("Initializing browser...")
    
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            driver = init_driver()
            if driver:
                print_success("Browser initialized successfully")
                # Set window size to a standard resolution
                driver.set_window_size(1366, 768)
                return driver
            else:
                print_error(f"Failed to initialize browser (Attempt {attempt}/{max_attempts})")
        except Exception as e:
            print_error(f"Error initializing browser (Attempt {attempt}/{max_attempts}): {e}")
        
        if attempt < max_attempts:
            print_warning(f"Retrying in 3 seconds...")
            time.sleep(3)
    
    print_error("Failed to initialize browser after multiple attempts")
    return None

def employer_workflow(driver, slow_mode=True):
    """Run the employer workflow with enhanced error handling"""
    print_header("EMPLOYER WORKFLOW")
    
    success = True
    
    # Step 1: Registration
    if not test_data["employer"]["registered"]:
        print_step("Step 1: Employer Registration")
        try:
            email, password = register_employer(driver, slow_mode)
            if email and password:
                test_data["employer"]["email"] = email
                test_data["employer"]["password"] = password
                test_data["employer"]["registered"] = True
                print_success(f"Employer registered: {email}")
                take_screenshot(driver, "employer_registration_complete")
            else:
                print_error("Employer registration failed")
                success = False
        except Exception as e:
            print_error(f"Error during employer registration: {e}")
            traceback.print_exc()
            take_screenshot(driver, "employer_registration_error")
            success = False
    else:
        print_step("Using existing employer account")
    
    # Step 2: Login (if not already logged in)
    if success:
        print_step("Step 2: Employer Login")
        try:
            login_success = login(driver, 
                                test_data["employer"]["email"], 
                                test_data["employer"]["password"], 
                                slow_mode)
            if login_success:
                print_success("Employer login successful")
                take_screenshot(driver, "employer_login_complete")
            else:
                print_error("Employer login failed")
                success = False
        except Exception as e:
            print_error(f"Error during employer login: {e}")
            traceback.print_exc()
            take_screenshot(driver, "employer_login_error")
            success = False
    
    # Step 3: Explore Dashboard
    if success:
        print_step("Step 3: Exploring Employer Dashboard")
        try:
            explore_success = explore_dashboard(driver, "employer", slow_mode)
            if explore_success:
                print_success("Employer dashboard exploration complete")
                take_screenshot(driver, "employer_dashboard_explored")
            else:
                print_error("Employer dashboard exploration failed")
                success = False
        except Exception as e:
            print_error(f"Error exploring employer dashboard: {e}")
            traceback.print_exc()
            take_screenshot(driver, "employer_dashboard_error")
            success = False
    
    # Logout is handled by visual_demo.py's explore_dashboard function
    
    return success

def candidate_workflow(driver, slow_mode=True):
    """Run the candidate workflow with enhanced error handling"""
    print_header("CANDIDATE WORKFLOW")
    
    success = True
    
    # Step 1: Registration
    if not test_data["candidate"]["registered"]:
        print_step("Step 1: Candidate Registration")
        try:
            email, password = register_candidate(driver, slow_mode)
            if email and password:
                test_data["candidate"]["email"] = email
                test_data["candidate"]["password"] = password
                test_data["candidate"]["registered"] = True
                print_success(f"Candidate registered: {email}")
                take_screenshot(driver, "candidate_registration_complete")
            else:
                print_error("Candidate registration failed")
                success = False
        except Exception as e:
            print_error(f"Error during candidate registration: {e}")
            traceback.print_exc()
            take_screenshot(driver, "candidate_registration_error")
            success = False
    else:
        print_step("Using existing candidate account")
    
    # Step 2: Login (if not already logged in)
    if success:
        print_step("Step 2: Candidate Login")
        try:
            login_success = login(driver, 
                                test_data["candidate"]["email"], 
                                test_data["candidate"]["password"], 
                                slow_mode)
            if login_success:
                print_success("Candidate login successful")
                take_screenshot(driver, "candidate_login_complete")
            else:
                print_error("Candidate login failed")
                success = False
        except Exception as e:
            print_error(f"Error during candidate login: {e}")
            traceback.print_exc()
            take_screenshot(driver, "candidate_login_error")
            success = False
    
    # Step 3: Explore Dashboard
    if success:
        print_step("Step 3: Exploring Candidate Dashboard")
        try:
            explore_success = explore_dashboard(driver, "candidate", slow_mode)
            if explore_success:
                print_success("Candidate dashboard exploration complete")
                take_screenshot(driver, "candidate_dashboard_explored")
            else:
                print_error("Candidate dashboard exploration failed")
                success = False
        except Exception as e:
            print_error(f"Error exploring candidate dashboard: {e}")
            traceback.print_exc()
            take_screenshot(driver, "candidate_dashboard_error")
            success = False
    
    # Logout is handled by visual_demo.py's explore_dashboard function
    
    return success

def print_system_info():
    """Print system information for diagnostics"""
    print_header("SYSTEM INFORMATION")
    
    try:
        print(f"🖥️ Operating System: {platform.system()} {platform.release()}")
        print(f"🐍 Python Version: {platform.python_version()}")
        
        # Check if we can import key libraries
        try:
            import selenium
            print(f"🧪 Selenium Version: {selenium.__version__}")
        except ImportError:
            print("🧪 Selenium: Not installed")
        
        try:
            import webdriver_manager
            print(f"🧪 Webdriver Manager Version: {webdriver_manager.__version__}")
        except ImportError:
            print("🧪 Webdriver Manager: Not installed")
            
        # Network checks
        try:
            frontend_response = requests.get(FRONTEND_URL, timeout=2)
            print(f"🌐 Frontend URL: {FRONTEND_URL} (Status: {frontend_response.status_code})")
        except:
            print(f"🌐 Frontend URL: {FRONTEND_URL} (Not accessible)")
            
        try:
            backend_response = requests.get(f"{BACKEND_URL}/docs", timeout=2)
            print(f"🌐 Backend URL: {BACKEND_URL} (Status: {backend_response.status_code})")
        except:
            print(f"🌐 Backend URL: {BACKEND_URL} (Not accessible)")
    
    except Exception as e:
        print_error(f"Error gathering system information: {e}")

def save_credentials():
    """Save credentials to a file for future use"""
    try:
        with open('workflow_credentials.json', 'w') as f:
            json.dump(test_data, f, indent=4)
        print_success("Credentials saved to workflow_credentials.json")
    except Exception as e:
        print_error(f"Failed to save credentials: {e}")

def load_credentials():
    """Load credentials from a file if available"""
    try:
        if os.path.exists('workflow_credentials.json'):
            with open('workflow_credentials.json', 'r') as f:
                data = json.load(f)
                test_data.update(data)
            print_success("Loaded credentials from workflow_credentials.json")
            return True
        return False
    except Exception as e:
        print_error(f"Failed to load credentials: {e}")
        return False

def main():
    """Main function to run the perfect visual workflow"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Perfect Visual Workflow for Job Recommender Platform")
    parser.add_argument("--employer-only", action="store_true", help="Run only employer workflow")
    parser.add_argument("--candidate-only", action="store_true", help="Run only candidate workflow")
    parser.add_argument("--no-slow", action="store_true", help="Disable slow mode (run quickly)")
    parser.add_argument("--use-existing", action="store_true", help="Use existing accounts if available")
    args = parser.parse_args()
    
    # Set slow mode
    slow_mode = not args.no_slow
    
    # Print welcome message
    print_header("PERFECT VISUAL WORKFLOW")
    print("This script will guide you through the complete Job Recommender platform workflow")
    
    # Print system information
    print_system_info()
    
    # Try to load existing credentials if requested
    if args.use_existing:
        if load_credentials():
            test_data["employer"]["registered"] = True
            test_data["candidate"]["registered"] = True
    
    # Register signal handler for cleanup
    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())
    
    try:
        # Step 1: Ensure services are running
        if not verify_services_running():
            print_step("Starting services...")
            if not start_services():
                print_error("Failed to start services. Please start them manually.")
                return
        
        # Step 2: Initialize browser
        driver = initialize_browser()
        if not driver:
            return
        
        try:
            # Step 3: Run employer workflow
            if not args.candidate_only:
                employer_success = employer_workflow(driver, slow_mode)
                
                if slow_mode and not args.employer_only and employer_success:
                    print_step("Pausing before switching to candidate workflow...")
                    print("Press Ctrl+C to exit or wait 5 seconds to continue")
                    time.sleep(5)
            
            # Step 4: Run candidate workflow
            if not args.employer_only:
                candidate_success = candidate_workflow(driver, slow_mode)
            
            # Save credentials for future use
            save_credentials()
            
            # Step 5: Show completion message
            print_header("WORKFLOW COMPLETE")
            print("The visual workflow demonstration has completed")
            
            if hasattr(locals(), 'employer_success') and employer_success:
                print_success(f"Employer credentials: {test_data['employer']['email']} / {test_data['employer']['password']}")
            
            if hasattr(locals(), 'candidate_success') and candidate_success:
                print_success(f"Candidate credentials: {test_data['candidate']['email']} / {test_data['candidate']['password']}")
            
            print(f"\nScreenshots saved to: {SCREENSHOTS_DIR}")
            
            # Keep browser open for a moment to see the final state
            if slow_mode:
                print_step("Closing browser in 10 seconds...")
                time.sleep(10)
        finally:
            # Close the browser
            try:
                driver.quit()
                print_success("Browser closed successfully")
            except:
                print_error("Failed to close browser properly")
    except Exception as e:
        print_error(f"Unhandled error in workflow: {e}")
        traceback.print_exc()
    finally:
        # Clean up
        cleanup()

if __name__ == "__main__":
    main() 