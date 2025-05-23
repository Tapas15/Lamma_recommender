#!/usr/bin/env python
"""
Visual Workflow Test for Job Recommender Platform

This script provides a visual demonstration of the complete workflow for both
employer and candidate users, including registration, login, job/project posting,
applications, and recommendations.

Requirements:
- Selenium
- Chrome WebDriver
- The Job Recommender backend and frontend must be running
"""

import os
import sys
import time
import random
import string
import json
from datetime import datetime
import subprocess
import threading
import argparse
import signal

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("Selenium is not installed. Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "selenium", "webdriver-manager"])
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from webdriver_manager.chrome import ChromeDriverManager

# Configuration
FRONTEND_URL = "http://localhost:8501"
BACKEND_URL = "http://localhost:8000"
WAIT_TIME = 10  # seconds
SLOW_MODE = True  # Set to False for faster execution
SCREENSHOTS_DIR = "screenshots"

# Process tracking
processes = []

# Test data storage
test_data = {
    "candidate": {
        "email": None,
        "password": None
    },
    "employer": {
        "email": None,
        "password": None
    },
    "job": {
        "id": None,
        "title": None
    },
    "project": {
        "id": None,
        "title": None
    }
}

# Helper functions
def generate_random_string(length=8):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def random_email():
    """Generate a random email address"""
    return f"test_{generate_random_string()}@example.com"

def take_screenshot(driver, name):
    """Take a screenshot and save it to the screenshots directory"""
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)
    filename = f"{SCREENSHOTS_DIR}/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    driver.save_screenshot(filename)
    print(f"📸 Screenshot saved: {filename}")
    return filename

def scroll_to_element(driver, element):
    """Scroll element into view with a smooth scrolling effect"""
    driver.execute_script("""
        arguments[0].scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    """, element)
    time.sleep(0.5)

def highlight_element(driver, element, duration=1):
    """Highlight element to make it visible in the UI"""
    original_style = element.get_attribute("style")
    driver.execute_script(
        "arguments[0].setAttribute('style', arguments[1]);", 
        element, 
        "background-color: yellow; border: 2px solid red; transition: all 0.3s ease;"
    )
    time.sleep(duration)
    driver.execute_script(
        "arguments[0].setAttribute('style', arguments[1]);", 
        element, 
        original_style
    )

def wait_and_highlight(driver, locator_type, locator_value, duration=1):
    """Wait for element to be present, then highlight it"""
    wait = WebDriverWait(driver, WAIT_TIME)
    element = wait.until(EC.presence_of_element_located((locator_type, locator_value)))
    scroll_to_element(driver, element)
    highlight_element(driver, element, duration)
    return element

def click_with_retry(driver, element, max_retries=3):
    """Click element with retry logic in case of StaleElementReferenceException"""
    retries = 0
    while retries < max_retries:
        try:
            scroll_to_element(driver, element)
            highlight_element(driver, element, 0.5)
            element.click()
            return True
        except Exception as e:
            print(f"Click failed, retrying... ({retries+1}/{max_retries})")
            retries += 1
            time.sleep(1)
            if retries == max_retries:
                print(f"Failed to click element after {max_retries} attempts: {e}")
                return False

def start_services():
    """Start backend and frontend services if not already running"""
    try:
        # Check if services are already running
        import requests
        frontend_running = False
        backend_running = False
        
        try:
            response = requests.get(FRONTEND_URL, timeout=2)
            frontend_running = response.status_code == 200
        except:
            pass
            
        try:
            response = requests.get(f"{BACKEND_URL}/docs", timeout=2)
            backend_running = response.status_code == 200
        except:
            pass
        
        if frontend_running and backend_running:
            print("✅ Both services are already running!")
            return True
        
        print("Starting services...")
        
        # Start the backend
        if not backend_running:
            backend_process = subprocess.Popen([sys.executable, "run_backend.py"])
            processes.append(backend_process)
            print("Started backend service")
        
        # Start the frontend
        if not frontend_running:
            frontend_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
            processes.append(frontend_process)
            print("Started frontend service")
        
        # Give services time to start
        print("Waiting for services to start up...")
        time.sleep(10)
        return True
    
    except Exception as e:
        print(f"Error starting services: {e}")
        return False

def cleanup():
    """Clean up resources at exit"""
    for process in processes:
        try:
            process.terminate()
        except:
            pass

def init_driver():
    """Initialize Chrome WebDriver with visual enhancements"""
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # Initialize Chrome WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                options=chrome_options)
        return driver
    except Exception as e:
        print(f"Failed to initialize WebDriver: {e}")
        return None

# Import workflow functions from separate modules
# These will be implemented in separate files to keep code organized
from workflow_functions.employer import (
    register_employer, 
    login_employer, 
    post_job, 
    post_project, 
    view_candidates,
    view_candidate_recommendations
)

from workflow_functions.candidate import (
    register_candidate, 
    login_candidate, 
    browse_jobs,
    apply_for_job,
    view_job_recommendations,
    browse_projects,
    view_project_recommendations
)

def employer_visual_workflow(driver):
    """Run through the complete employer workflow with visual elements"""
    print("\n========== EMPLOYER VISUAL WORKFLOW ==========")
    
    try:
        # Register if needed
        if not test_data["employer"]["email"]:
            print("\n🔵 STEP 1: Employer Registration")
            test_data["employer"]["email"], test_data["employer"]["password"] = register_employer(driver, SLOW_MODE)
            
            if SLOW_MODE:
                time.sleep(2)
        
        # Login
        print("\n🔵 STEP 2: Employer Login")
        login_success = login_employer(driver, 
                                     test_data["employer"]["email"], 
                                     test_data["employer"]["password"], 
                                     SLOW_MODE)
        
        if not login_success:
            print("❌ Employer login failed, cannot continue workflow")
            return False
        
        if SLOW_MODE:
            time.sleep(2)
        
        # Post a job
        print("\n🔵 STEP 3: Posting a New Job")
        job_success, job_title, job_id = post_job(driver, SLOW_MODE)
        if job_success:
            test_data["job"]["id"] = job_id
            test_data["job"]["title"] = job_title
            print(f"✅ Successfully posted job: {job_title}")
        
        if SLOW_MODE:
            time.sleep(2)
        
        # Post a project
        print("\n🔵 STEP 4: Posting a New Project")
        project_success, project_title, project_id = post_project(driver, SLOW_MODE)
        if project_success:
            test_data["project"]["id"] = project_id
            test_data["project"]["title"] = project_title
            print(f"✅ Successfully posted project: {project_title}")
        
        if SLOW_MODE:
            time.sleep(2)
        
        # View candidate list
        print("\n🔵 STEP 5: Viewing Candidates")
        view_candidates(driver, SLOW_MODE)
        
        if SLOW_MODE:
            time.sleep(2)
        
        # View candidate recommendations for job
        if test_data["job"]["id"]:
            print("\n🔵 STEP 6: Viewing Candidate Recommendations")
            view_candidate_recommendations(driver, test_data["job"]["id"], SLOW_MODE)
        
        # Take final screenshot of employer dashboard
        take_screenshot(driver, "employer_workflow_complete")
        
        print("\n✅ Employer workflow completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during employer workflow: {e}")
        # Take screenshot of error state
        take_screenshot(driver, "employer_workflow_error")
        return False

def candidate_visual_workflow(driver):
    """Run through the complete candidate workflow with visual elements"""
    print("\n========== CANDIDATE VISUAL WORKFLOW ==========")
    
    try:
        # Register if needed
        if not test_data["candidate"]["email"]:
            print("\n🔵 STEP 1: Candidate Registration")
            test_data["candidate"]["email"], test_data["candidate"]["password"] = register_candidate(driver, SLOW_MODE)
            
            if SLOW_MODE:
                time.sleep(2)
        
        # Login
        print("\n🔵 STEP 2: Candidate Login")
        login_success = login_candidate(driver, 
                                      test_data["candidate"]["email"], 
                                      test_data["candidate"]["password"], 
                                      SLOW_MODE)
        
        if not login_success:
            print("❌ Candidate login failed, cannot continue workflow")
            return False
        
        if SLOW_MODE:
            time.sleep(2)
        
        # Browse jobs
        print("\n🔵 STEP 3: Browsing Available Jobs")
        job_id = browse_jobs(driver, SLOW_MODE)
        
        if SLOW_MODE:
            time.sleep(2)
        
        # Apply for a job
        if job_id:
            print("\n🔵 STEP 4: Applying for a Job")
            apply_for_job(driver, job_id, SLOW_MODE)
        
        if SLOW_MODE:
            time.sleep(2)
        
        # View job recommendations
        print("\n🔵 STEP 5: Viewing Job Recommendations")
        view_job_recommendations(driver, SLOW_MODE)
        
        if SLOW_MODE:
            time.sleep(2)
        
        # Browse projects
        print("\n🔵 STEP 6: Browsing Available Projects")
        browse_projects(driver, SLOW_MODE)
        
        if SLOW_MODE:
            time.sleep(2)
        
        # View project recommendations
        print("\n🔵 STEP 7: Viewing Project Recommendations")
        view_project_recommendations(driver, SLOW_MODE)
        
        # Take final screenshot of candidate dashboard
        take_screenshot(driver, "candidate_workflow_complete")
        
        print("\n✅ Candidate workflow completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during candidate workflow: {e}")
        # Take screenshot of error state
        take_screenshot(driver, "candidate_workflow_error")
        return False

def main():
    parser = argparse.ArgumentParser(description="Visual Workflow Test for Job Recommender Platform")
    parser.add_argument("--employer-only", action="store_true", help="Run only employer workflow")
    parser.add_argument("--candidate-only", action="store_true", help="Run only candidate workflow")
    parser.add_argument("--no-slow", action="store_true", help="Disable slow mode (run quickly)")
    parser.add_argument("--use-existing", action="store_true", help="Use existing accounts instead of registering new ones")
    parser.add_argument("--screenshots-dir", type=str, help="Directory to save screenshots", default="screenshots")
    args = parser.parse_args()
    
    # Set slow mode based on args
    global SLOW_MODE
    SLOW_MODE = not args.no_slow
    
    # Set screenshots directory
    global SCREENSHOTS_DIR
    SCREENSHOTS_DIR = args.screenshots_dir
    
    # Use existing accounts if specified
    if args.use_existing:
        # These would be replaced with actual test account credentials
        test_data["employer"]["email"] = "employer@example.com"
        test_data["employer"]["password"] = "password123"
        test_data["candidate"]["email"] = "candidate@example.com"
        test_data["candidate"]["password"] = "password123"
    
    # Register signal handler for cleanup
    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())
    
    try:
        # Start services if needed
        if not start_services():
            print("❌ Failed to start services. Please start them manually.")
            return
        
        # Initialize WebDriver
        driver = init_driver()
        if not driver:
            print("❌ Failed to initialize WebDriver.")
            cleanup()
            return
        
        try:
            # Run employer workflow
            if not args.candidate_only:
                employer_visual_workflow(driver)
                
                if SLOW_MODE and not args.employer_only:
                    print("\nSwitching to candidate workflow in 3 seconds...")
                    time.sleep(3)
            
            # Run candidate workflow
            if not args.employer_only:
                candidate_visual_workflow(driver)
            
            print("\n🎉 Visual Workflow Test Finished!")
            print(f"\nEmployer credentials: {test_data['employer']['email']} / {test_data['employer']['password']}")
            print(f"Candidate credentials: {test_data['candidate']['email']} / {test_data['candidate']['password']}")
            
            # Keep browser open for a moment to see the final state
            if SLOW_MODE:
                print("\nClosing browser in 10 seconds...")
                time.sleep(10)
                
        finally:
            # Close the browser
            driver.quit()
            
    except Exception as e:
        print(f"❌ Unhandled error in visual workflow test: {e}")
    finally:
        # Clean up
        cleanup()

if __name__ == "__main__":
    main() 