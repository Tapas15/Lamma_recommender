#!/usr/bin/env python
"""
Visual Demonstration Script for Job Recommender Platform

This script uses Selenium to automate browser interactions with the Job Recommender 
frontend application, demonstrating registration and login flows for both 
employers and candidates.

Requirements:
- Selenium
- Chrome WebDriver
- The Job Recommender backend and frontend must be running

To run:
python tests/visual_demo.py
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
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager

# Configuration
FRONTEND_URL = "http://localhost:8501"
BACKEND_URL = "http://localhost:8000"
WAIT_TIME = 10  # seconds

# Process tracking
processes = []

def generate_random_string(length=8):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def random_email():
    """Generate a random email address"""
    return f"test_{generate_random_string()}@example.com"

def scroll_to_element(driver, element):
    """Scroll to the element to make it visible"""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    # Add a small offset to ensure element is not hidden behind fixed headers
    driver.execute_script("window.scrollBy(0, -100);")
    time.sleep(0.5)

def highlight_element(driver, element, duration=1):
    """Temporarily highlight an element by changing its background"""
    original_style = element.get_attribute("style")
    driver.execute_script(
        "arguments[0].setAttribute('style', arguments[1]);", 
        element, 
        "background-color: yellow; border: 2px solid red;"
    )
    time.sleep(duration)
    driver.execute_script(
        "arguments[0].setAttribute('style', arguments[1]);", 
        element, 
        original_style
    )

def start_services():
    """Start the backend and frontend services if they're not already running"""
    try:
        # Check if services are already running
        try:
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
        except:
            # If we can't check, assume they're not running
            pass
        
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
    """Clean up processes on exit"""
    for process in processes:
        try:
            process.terminate()
        except:
            pass

def init_driver():
    """Initialize the Selenium WebDriver"""
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

def register_candidate(driver, slow_mode=True):
    """Automate the candidate registration process"""
    try:
        print("\n🔵 Demonstrating Candidate Registration...")
        
        # Go to the frontend URL
        driver.get(FRONTEND_URL)
        
        if slow_mode:
            time.sleep(2)
        
        # Click on Register tab in sidebar
        wait = WebDriverWait(driver, WAIT_TIME)
        tabs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".stTabs [role='tab']")))
        tabs[1].click()  # Register tab
        
        if slow_mode:
            time.sleep(1)
        
        # Fill in registration form
        email = random_email()
        password = "Test123!"
        full_name = f"Test Candidate {generate_random_string(4)}"
        
        # Set registration type to candidate
        registration_type = driver.find_element(By.XPATH, "//div[contains(@data-testid, 'stSelectbox')]")
        scroll_to_element(driver, registration_type)
        highlight_element(driver, registration_type)
        registration_type.click()
        time.sleep(0.5)
        
        candidate_option = wait.until(EC.presence_of_element_located((By.XPATH, "//div[text()='candidate']")))
        highlight_element(driver, candidate_option)
        candidate_option.click()
        
        if slow_mode:
            time.sleep(1)
        
        # Fill in form fields
        fields = {
            "reg_email": email,
            "reg_password": password,
            "Full Name": full_name,
            "Location": "San Francisco, CA",
            "Experience (Years)": "5",
            "Education Summary": "Computer Science Degree",
            "Professional Bio": "Experienced software developer with focus on backend technologies."
        }
        
        for label, value in fields.items():
            # Handle special cases for number input
            if label == "Experience (Years)":
                # Find number input and clear it
                num_input = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//input")
                scroll_to_element(driver, num_input)
                highlight_element(driver, num_input)
                num_input.clear()
                num_input.send_keys(value)
                continue
                
            # Regular text inputs
            try:
                # Try first by looking for key attribute
                input_elem = driver.find_element(By.CSS_SELECTOR, f"input[aria-label='{label}']")
            except NoSuchElementException:
                try:
                    # Then try by looking for label text
                    input_elem = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//input")
                except NoSuchElementException:
                    # Finally try for textarea
                    input_elem = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//textarea")
            
            scroll_to_element(driver, input_elem)
            highlight_element(driver, input_elem)
            input_elem.clear()
            input_elem.send_keys(value)
            if slow_mode:
                time.sleep(0.5)
        
        # Fill in Skills information
        skills_input = driver.find_element(By.XPATH, "//label[text()='Technical Skills (comma separated)']/..//textarea")
        scroll_to_element(driver, skills_input)
        highlight_element(driver, skills_input)
        skills_input.send_keys("Python, JavaScript, SQL, Docker, AWS")
        
        if slow_mode:
            time.sleep(0.5)
            
        soft_skills = driver.find_element(By.XPATH, "//label[text()='Soft Skills (comma separated)']/..//textarea")
        scroll_to_element(driver, soft_skills)
        highlight_element(driver, soft_skills)
        soft_skills.send_keys("Communication, Teamwork, Problem Solving")
        
        if slow_mode:
            time.sleep(0.5)
        
        # Select job types
        job_types_dropdown = driver.find_element(By.XPATH, "//label[text()='Preferred Job Types']/../div")
        scroll_to_element(driver, job_types_dropdown)
        highlight_element(driver, job_types_dropdown)
        job_types_dropdown.click()
        time.sleep(0.5)
        
        for job_type in ["Full-time", "Remote"]:
            try:
                option = driver.find_element(By.XPATH, f"//div[text()='{job_type}']")
                highlight_element(driver, option)
                option.click()
                time.sleep(0.2)
            except:
                pass
        
        # Click outside to close dropdown
        driver.find_element(By.TAG_NAME, "body").click()
        
        if slow_mode:
            time.sleep(0.5)
        
        # Fill preferred locations
        locations = driver.find_element(By.XPATH, "//label[text()='Preferred Locations (comma separated)']/..//textarea")
        scroll_to_element(driver, locations)
        highlight_element(driver, locations)
        locations.send_keys("San Francisco, New York, Remote")
        
        if slow_mode:
            time.sleep(1)
        
        # Click Register button
        register_button = driver.find_element(By.XPATH, "//button[text()='Register Candidate']")
        scroll_to_element(driver, register_button)
        highlight_element(driver, register_button)
        register_button.click()
        
        # Wait for success message
        try:
            success_message = WebDriverWait(driver, WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Registration successful')]"))
            )
            highlight_element(driver, success_message, 2)
            print(f"✅ Candidate Registration successful: {email} / {password}")
            
            if slow_mode:
                time.sleep(3)  # Let user see the success message
            
            return email, password
            
        except TimeoutException:
            print("❌ Candidate Registration failed - no success message appeared")
            # Check for error messages
            try:
                error_msg = driver.find_element(By.XPATH, "//div[contains(@class, 'stAlert')]").text
                print(f"Error: {error_msg}")
            except:
                pass
            return None, None
            
    except Exception as e:
        print(f"❌ Error during candidate registration: {e}")
        return None, None

def register_employer(driver, slow_mode=True):
    """Automate the employer registration process"""
    try:
        print("\n🔵 Demonstrating Employer Registration...")
        
        # Go to the frontend URL
        driver.get(FRONTEND_URL)
        
        if slow_mode:
            time.sleep(2)
        
        # Click on Register tab in sidebar
        wait = WebDriverWait(driver, WAIT_TIME)
        tabs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".stTabs [role='tab']")))
        tabs[1].click()  # Register tab
        
        if slow_mode:
            time.sleep(1)
        
        # Set registration type to employer
        # Using a more robust approach to find and interact with the selectbox
        try:
            # First try to find the selectbox
            registration_type = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@data-testid, 'stSelectbox')]")
            ))
            scroll_to_element(driver, registration_type)
            highlight_element(driver, registration_type)
            registration_type.click()
            time.sleep(1)
            
            # Now try to find and click the 'employer' option
            # Using a more generic approach to find select options
            employer_option = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@role, 'option') and contains(text(), 'employer')]")
            ))
            highlight_element(driver, employer_option)
            employer_option.click()
            
            if slow_mode:
                time.sleep(1)
                
        except TimeoutException:
            print("⚠️ Failed to find employer option in the standard way, trying alternative method")
            # Try clicking the selectbox again and using arrow keys
            try:
                # Click the selectbox again
                registration_type = driver.find_element(By.XPATH, "//div[contains(@data-testid, 'stSelectbox')]")
                scroll_to_element(driver, registration_type)
                registration_type.click()
                time.sleep(1)
                
                # Use JavaScript to select the employer option directly
                driver.execute_script("""
                    var options = document.querySelectorAll('[role="option"]');
                    for (var i = 0; i < options.length; i++) {
                        if (options[i].textContent.includes('employer')) {
                            options[i].click();
                            break;
                        }
                    }
                """)
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Alternative method also failed: {e}")
                # As a last resort, try to click the first option and then next option
                try:
                    registration_type.click()
                    time.sleep(0.5)
                    # Press down arrow and enter to select the second option
                    from selenium.webdriver.common.keys import Keys
                    registration_type.send_keys(Keys.ARROW_DOWN)
                    time.sleep(0.5)
                    registration_type.send_keys(Keys.ENTER)
                    time.sleep(0.5)
                except Exception as inner_e:
                    print(f"⚠️ Final attempt failed: {inner_e}")
        
        # Fill in registration form
        email = random_email()
        password = "Test123!"
        full_name = f"Test Employer {generate_random_string(4)}"
        
        # Fill in form fields
        fields = {
            "emp_email": email,
            "emp_password": password,
            "Full Name": full_name,
            "Position": "HR Manager",
            "Professional Bio": "HR professional with 10+ years of recruiting experience."
        }
        
        for label, value in fields.items():
            try:
                # Try first by looking for key attribute
                input_elem = driver.find_element(By.CSS_SELECTOR, f"input[aria-label='{label}']")
            except NoSuchElementException:
                try:
                    # Then try by looking for label text
                    input_elem = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//input")
                except NoSuchElementException:
                    # Finally try for textarea
                    input_elem = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//textarea")
            
            scroll_to_element(driver, input_elem)
            highlight_element(driver, input_elem)
            input_elem.clear()
            input_elem.send_keys(value)
            if slow_mode:
                time.sleep(0.5)
        
        # Fill company details
        company_fields = {
            "Company Name*": "TechCorp Solutions",
            "Company Description": "Leading provider of innovative software solutions.",
            "Company Location": "San Francisco, CA",
            "Company Website": "https://example.com",
        }
        
        for label, value in company_fields.items():
            try:
                input_elem = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//input")
            except NoSuchElementException:
                input_elem = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//textarea")
            
            scroll_to_element(driver, input_elem)
            highlight_element(driver, input_elem)
            input_elem.clear()
            input_elem.send_keys(value)
            if slow_mode:
                time.sleep(0.5)
        
        # Select industry - using more robust selectors
        try:
            industry_dropdown = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[contains(text(), 'Industry')]/..//div[contains(@data-testid, 'stSelectbox')]")
            ))
            scroll_to_element(driver, industry_dropdown)
            highlight_element(driver, industry_dropdown)
            industry_dropdown.click()
            time.sleep(1)
            
            industry_option = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@role, 'option') and contains(text(), 'Technology')]")
            ))
            highlight_element(driver, industry_option)
            industry_option.click()
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ Failed to select industry: {e}")
            
        # Select company size - using more robust selectors
        try:
            size_dropdown = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[contains(text(), 'Company Size')]/..//div[contains(@data-testid, 'stSelectbox')]")
            ))
            scroll_to_element(driver, size_dropdown)
            highlight_element(driver, size_dropdown)
            size_dropdown.click()
            time.sleep(1)
            
            size_option = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@role, 'option') and contains(text(), '51-200')]")
            ))
            highlight_element(driver, size_option)
            size_option.click()
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ Failed to select company size: {e}")
        
        if slow_mode:
            time.sleep(0.5)
        
        # Fill in hiring needs
        try:
            hiring_needs = driver.find_element(By.XPATH, "//label[text()='Hiring Needs (comma separated)']/..//textarea")
            scroll_to_element(driver, hiring_needs)
            highlight_element(driver, hiring_needs)
            hiring_needs.send_keys("Software Engineers, Data Scientists, Product Managers")
        except NoSuchElementException:
            print("⚠️ Could not find hiring needs field")
        
        if slow_mode:
            time.sleep(1)
        
        # Take a screenshot of the completed form
        try:
            screenshot_path = os.path.join(os.getcwd(), 'employer_registration.png')
            driver.save_screenshot(screenshot_path)
            print(f"📸 Saved screenshot to {screenshot_path}")
        except Exception as e:
            print(f"⚠️ Failed to save screenshot: {e}")
        
        # Click Register button
        try:
            register_button = driver.find_element(By.XPATH, "//button[text()='Register Employer']")
            scroll_to_element(driver, register_button)
            highlight_element(driver, register_button)
            register_button.click()
        except NoSuchElementException:
            # Try a more general selector if the specific text is not found
            buttons = driver.find_elements(By.XPATH, "//button")
            for button in buttons:
                if "register" in button.text.lower() and "employer" in button.text.lower():
                    scroll_to_element(driver, button)
                    highlight_element(driver, button)
                    button.click()
                    break
            else:
                print("⚠️ Could not find employer registration button")
        
        # Wait for success message
        try:
            success_message = WebDriverWait(driver, WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Registration successful')]"))
            )
            highlight_element(driver, success_message, 2)
            print(f"✅ Employer Registration successful: {email} / {password}")
            
            if slow_mode:
                time.sleep(3)  # Let user see the success message
            
            return email, password
            
        except TimeoutException:
            print("❌ Employer Registration failed - no success message appeared")
            # Check for error messages
            try:
                error_msg = driver.find_element(By.XPATH, "//div[contains(@class, 'stAlert')]").text
                print(f"Error: {error_msg}")
            except:
                pass
            
            # Take a screenshot of the error state
            try:
                screenshot_path = os.path.join(os.getcwd(), 'employer_registration_error.png')
                driver.save_screenshot(screenshot_path)
                print(f"📸 Saved error screenshot to {screenshot_path}")
            except Exception as e:
                print(f"⚠️ Failed to save error screenshot: {e}")
                
            return None, None
            
    except Exception as e:
        print(f"❌ Error during employer registration: {e}")
        return None, None

def login(driver, email, password, slow_mode=True):
    """Automate the login process"""
    try:
        print(f"\n🔵 Demonstrating Login for {email}...")
        
        # Go to the frontend URL
        driver.get(FRONTEND_URL)
        
        if slow_mode:
            time.sleep(2)
        
        # Click on Login tab in sidebar
        wait = WebDriverWait(driver, WAIT_TIME)
        tabs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".stTabs [role='tab']")))
        tabs[0].click()  # Login tab
        
        if slow_mode:
            time.sleep(1)
        
        # Fill in login form
        email_input = driver.find_element(By.CSS_SELECTOR, "input[aria-label='login_email']")
        scroll_to_element(driver, email_input)
        highlight_element(driver, email_input)
        email_input.clear()
        email_input.send_keys(email)
        
        if slow_mode:
            time.sleep(0.5)
        
        password_input = driver.find_element(By.CSS_SELECTOR, "input[aria-label='login_password']")
        scroll_to_element(driver, password_input)
        highlight_element(driver, password_input)
        password_input.clear()
        password_input.send_keys(password)
        
        if slow_mode:
            time.sleep(1)
        
        # Click Login button
        login_button = driver.find_element(By.XPATH, "//button[text()='Login']")
        scroll_to_element(driver, login_button)
        highlight_element(driver, login_button)
        login_button.click()
        
        # Wait for successful login
        try:
            # Look for welcome message or main app content
            success_element = WebDriverWait(driver, WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Login successful')]"))
            )
            highlight_element(driver, success_element, 2)
            print(f"✅ Login successful for {email}")
            
            if slow_mode:
                time.sleep(3)  # Let user see the success message
            
            return True
            
        except TimeoutException:
            # Alternative check: look for elements that appear after successful login
            try:
                logout_element = WebDriverWait(driver, WAIT_TIME).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Logout')]"))
                )
                highlight_element(driver, logout_element)
                print(f"✅ Login successful for {email}")
                
                if slow_mode:
                    time.sleep(3)
                
                return True
            except TimeoutException:
                print(f"❌ Login failed for {email}")
                try:
                    error_msg = driver.find_element(By.XPATH, "//div[contains(@class, 'stAlert')]").text
                    print(f"Error: {error_msg}")
                except:
                    pass
                return False
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False

def explore_dashboard(driver, user_type, slow_mode=True):
    """Browse through the dashboard to demonstrate functionality"""
    try:
        print(f"\n🔵 Exploring {user_type.capitalize()} Dashboard...")
        
        if slow_mode:
            time.sleep(2)
        
        # Take a screenshot of the dashboard
        try:
            screenshot_path = os.path.join(os.getcwd(), f'{user_type}_dashboard.png')
            driver.save_screenshot(screenshot_path)
            print(f"📸 Saved dashboard screenshot to {screenshot_path}")
        except Exception as e:
            print(f"⚠️ Failed to save dashboard screenshot: {e}")
        
        # Explore different sections based on user type
        if user_type == "candidate":
            # Check for job listings
            try:
                wait = WebDriverWait(driver, WAIT_TIME)
                
                # Look for navigation links
                nav_links = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a")))
                
                # Find and click Jobs link
                job_link = None
                for link in nav_links:
                    if "job" in link.text.lower():
                        job_link = link
                        break
                
                if job_link:
                    scroll_to_element(driver, job_link)
                    highlight_element(driver, job_link)
                    job_link.click()
                    print("✅ Browsing Jobs section")
                    
                    if slow_mode:
                        time.sleep(3)
                
                # Find and click Recommendations link
                recommendations_link = None
                nav_links = driver.find_elements(By.XPATH, "//a")
                for link in nav_links:
                    if "recommend" in link.text.lower():
                        recommendations_link = link
                        break
                
                if recommendations_link:
                    scroll_to_element(driver, recommendations_link)
                    highlight_element(driver, recommendations_link)
                    recommendations_link.click()
                    print("✅ Viewing Job Recommendations")
                    
                    if slow_mode:
                        time.sleep(3)
                    
                    # Take a screenshot of recommendations
                    try:
                        screenshot_path = os.path.join(os.getcwd(), 'candidate_recommendations.png')
                        driver.save_screenshot(screenshot_path)
                        print(f"📸 Saved recommendations screenshot to {screenshot_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to save recommendations screenshot: {e}")
                
            except Exception as e:
                print(f"Error exploring candidate dashboard: {e}")
                
        elif user_type == "employer":
            # Check for employer dashboard
            try:
                wait = WebDriverWait(driver, WAIT_TIME)
                
                # Look for navigation links
                nav_links = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a")))
                
                # Find and click Post Job link
                post_job_link = None
                for link in nav_links:
                    if "post" in link.text.lower() and "job" in link.text.lower():
                        post_job_link = link
                        break
                
                if post_job_link:
                    scroll_to_element(driver, post_job_link)
                    highlight_element(driver, post_job_link)
                    post_job_link.click()
                    print("✅ Viewing Post Job section")
                    
                    if slow_mode:
                        time.sleep(3)
                        
                    # Take a screenshot
                    try:
                        screenshot_path = os.path.join(os.getcwd(), 'employer_post_job.png')
                        driver.save_screenshot(screenshot_path)
                        print(f"📸 Saved post job screenshot to {screenshot_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to save post job screenshot: {e}")
                
                # Find and click Candidates link
                candidates_link = None
                nav_links = driver.find_elements(By.XPATH, "//a")
                for link in nav_links:
                    if "candidate" in link.text.lower():
                        candidates_link = link
                        break
                
                if candidates_link:
                    scroll_to_element(driver, candidates_link)
                    highlight_element(driver, candidates_link)
                    candidates_link.click()
                    print("✅ Viewing Candidates section")
                    
                    if slow_mode:
                        time.sleep(3)
                    
                    # Take a screenshot
                    try:
                        screenshot_path = os.path.join(os.getcwd(), 'employer_candidates.png')
                        driver.save_screenshot(screenshot_path)
                        print(f"📸 Saved candidates screenshot to {screenshot_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to save candidates screenshot: {e}")
                
            except Exception as e:
                print(f"Error exploring employer dashboard: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exploring dashboard: {e}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Visual Demonstration of Job Recommender Platform")
    parser.add_argument("--no-slow", action="store_true", help="Disable slow mode (run quickly)")
    parser.add_argument("--candidate-only", action="store_true", help="Run only candidate demo")
    parser.add_argument("--employer-only", action="store_true", help="Run only employer demo")
    parser.add_argument("--screenshots-dir", type=str, help="Directory to save screenshots", default=".")
    args = parser.parse_args()
    
    # Use slow mode by default (for better visualization)
    slow_mode = not args.no_slow
    
    # Create screenshots directory if it doesn't exist
    if not os.path.exists(args.screenshots_dir):
        os.makedirs(args.screenshots_dir)
    
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
        
        candidate_email = None
        candidate_password = None
        employer_email = None 
        employer_password = None
        
        try:
            # Candidate flow
            if not args.employer_only:
                candidate_email, candidate_password = register_candidate(driver, slow_mode)
                if candidate_email and candidate_password:
                    # Go back to login
                    if login(driver, candidate_email, candidate_password, slow_mode):
                        explore_dashboard(driver, "candidate", slow_mode)
            
            # Employer flow
            if not args.candidate_only:
                employer_email, employer_password = register_employer(driver, slow_mode)
                if employer_email and employer_password:
                    # Go back to login
                    if login(driver, employer_email, employer_password, slow_mode):
                        explore_dashboard(driver, "employer", slow_mode)
            
            # Final message with credentials
            print("\n🎉 Visual Demo Complete!")
            if candidate_email:
                print(f"Candidate Credentials: {candidate_email} / {candidate_password}")
            if employer_email:
                print(f"Employer Credentials: {employer_email} / {employer_password}")
                
            # Keep browser open for 10 seconds to see the final state
            if slow_mode:
                print("\nClosing browser in 10 seconds...")
                time.sleep(10)
                
        finally:
            # Close the browser
            driver.quit()
            
    except Exception as e:
        print(f"❌ Unhandled error in demo: {e}")
    finally:
        # Clean up
        cleanup()

if __name__ == "__main__":
    main() 