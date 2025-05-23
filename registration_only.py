#!/usr/bin/env python
"""
Candidate Registration Script for Job Recommender Platform

This script focuses solely on the candidate registration process,
with enhanced debugging and more robust element finding.

Usage:
python registration_only.py
"""

import os
import sys
import time
import traceback
import random
import string
import argparse
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException, 
        NoSuchElementException,
        ElementClickInterceptedException,
        StaleElementReferenceException
    )
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "selenium", "webdriver-manager"])
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException, 
        NoSuchElementException,
        ElementClickInterceptedException,
        StaleElementReferenceException
    )
    from webdriver_manager.chrome import ChromeDriverManager

# Configuration
FRONTEND_URL = "http://localhost:8501"
WAIT_TIME = 15  # seconds - increased for better reliability
SCREENSHOTS_DIR = "registration_screenshots"

def ensure_screenshots_dir():
    """Ensure screenshots directory exists"""
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)
    return SCREENSHOTS_DIR

def generate_random_string(length=8):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def random_email():
    """Generate a random email address"""
    return f"candidate_{random.randint(1000, 9999)}@example.com"

def take_screenshot(driver, name):
    """Take a screenshot with timestamp"""
    screenshots_dir = ensure_screenshots_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{screenshots_dir}/{name}_{timestamp}.png"
    try:
        driver.save_screenshot(filename)
        print(f"📸 Screenshot saved: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Failed to save screenshot: {e}")
        return None

def scroll_to_element(driver, element, center=True):
    """Scroll to the element to make it visible"""
    try:
        if center:
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", 
                element
            )
        else:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});", element)
        
        # Add a small offset to ensure element is not hidden behind fixed headers
        driver.execute_script("window.scrollBy(0, -100);")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"⚠️ Error scrolling to element: {e}")
        return False

def highlight_element(driver, element, duration=1):
    """Temporarily highlight an element by changing its background"""
    try:
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
        return True
    except Exception as e:
        print(f"⚠️ Error highlighting element: {e}")
        return False

def wait_for_element(driver, by, selector, timeout=WAIT_TIME, visible=True):
    """Wait for an element to be present and optionally visible"""
    try:
        wait = WebDriverWait(driver, timeout)
        if visible:
            return wait.until(EC.visibility_of_element_located((by, selector)))
        else:
            return wait.until(EC.presence_of_element_located((by, selector)))
    except Exception as e:
        print(f"⚠️ Timeout waiting for element: {by}='{selector}'")
        take_screenshot(driver, f"element_not_found_{selector.replace('/', '_')}")
        return None

def init_driver():
    """Initialize the Selenium WebDriver with enhanced options"""
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        
        # Initialize Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set window size to standard desktop size
        driver.set_window_size(1366, 768)
        
        return driver
    except Exception as e:
        print(f"❌ Failed to initialize WebDriver: {e}")
        return None

def click_with_retry(driver, element, retries=3, delay=1):
    """Click element with multiple retry attempts and methods"""
    for attempt in range(retries):
        try:
            # Scroll into view first
            scroll_to_element(driver, element)
            
            # Highlight to show what we're clicking
            highlight_element(driver, element, 0.5)
            
            # Try regular click
            element.click()
            print(f"✅ Successfully clicked element (attempt {attempt+1})")
            return True
        except StaleElementReferenceException:
            print(f"⚠️ Element is stale, retrying... (attempt {attempt+1})")
            if attempt < retries - 1:
                time.sleep(delay)
        except ElementClickInterceptedException:
            print(f"⚠️ Click intercepted, trying JavaScript click... (attempt {attempt+1})")
            try:
                driver.execute_script("arguments[0].click();", element)
                print(f"✅ Successfully clicked element with JavaScript (attempt {attempt+1})")
                return True
            except:
                if attempt < retries - 1:
                    time.sleep(delay)
        except Exception as e:
            print(f"⚠️ Click failed: {e}, retrying... (attempt {attempt+1})")
            if attempt < retries - 1:
                time.sleep(delay)
    
    # All retries failed, try Action Chains as a last resort
    try:
        print("⚠️ Trying click with Action Chains...")
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()
        print("✅ Successfully clicked element with Action Chains")
        return True
    except Exception as e:
        print(f"❌ All click attempts failed: {e}")
        take_screenshot(driver, "click_failed")
        return False

def fill_input(driver, element, value, click_first=True, clear_first=True):
    """Fill an input field with better error handling"""
    try:
        if click_first:
            try:
                element.click()
            except:
                driver.execute_script("arguments[0].click();", element)
        
        if clear_first:
            try:
                element.clear()
            except:
                # Alternative clear methods
                element.send_keys(Keys.CONTROL + "a")
                element.send_keys(Keys.DELETE)
        
        # Type the value
        element.send_keys(value)
        return True
    except Exception as e:
        print(f"⚠️ Error filling input: {e}")
        try:
            # Try JavaScript as a fallback
            driver.execute_script(f"arguments[0].value = '{value}';", element)
            return True
        except:
            return False

def find_element_with_multiple_strategies(driver, strategies, timeout=WAIT_TIME):
    """Try multiple strategies to find an element"""
    for by, selector in strategies:
        try:
            element = wait_for_element(driver, by, selector, timeout=timeout/len(strategies))
            if element:
                print(f"✅ Found element using: {by}='{selector}'")
                return element
        except:
            continue
    
    print("❌ Element not found with any strategy")
    take_screenshot(driver, "element_not_found_multiple_strategies")
    return None

def register_candidate(driver, debug_mode=False):
    """Automate the candidate registration process with enhanced debugging"""
    email = random_email()
    password = "Test123!"
    full_name = f"Test Candidate {generate_random_string(4)}"
    
    print(f"\n🔵 Starting Candidate Registration Process (email: {email})")
    take_screenshot(driver, "registration_start")
    
    try:
        # Go to the frontend URL
        driver.get(FRONTEND_URL)
        print("✅ Navigated to frontend URL")
        time.sleep(3)  # Give frontend time to load completely
        take_screenshot(driver, "frontend_loaded")
        
        # Find and click the Register tab
        print("🔍 Looking for Register tab...")
        
        # Multiple strategies to find the tabs
        tab_strategies = [
            (By.CSS_SELECTOR, ".stTabs [role='tab']"),
            (By.XPATH, "//div[contains(@data-baseweb, 'tab-list')]/div[2]"),
            (By.XPATH, "//div[contains(text(), 'Register')]"),
            (By.CSS_SELECTOR, "button.stTabs"),
        ]
        
        tabs = driver.find_elements(By.CSS_SELECTOR, ".stTabs [role='tab']")
        if len(tabs) >= 2:
            print(f"✅ Found {len(tabs)} tabs")
            register_tab = tabs[1]  # Second tab should be Register
            print("🖱️ Clicking on Register tab...")
            click_with_retry(driver, register_tab)
        else:
            print("⚠️ Could not find tabs with main strategy, trying alternatives...")
            register_tab = find_element_with_multiple_strategies(driver, [
                (By.XPATH, "//div[contains(text(), 'Register')]"),
                (By.XPATH, "//button[contains(text(), 'Register')]"),
                (By.XPATH, "//div[@role='tab'][contains(., 'Register')]")
            ])
            
            if register_tab:
                print("🖱️ Clicking on Register tab (alternative)...")
                click_with_retry(driver, register_tab)
            else:
                print("❌ Could not find Register tab")
                return None, None
        
        time.sleep(2)  # Wait for register form to load
        take_screenshot(driver, "register_tab_clicked")
        
        # Set registration type to candidate
        print("🔍 Looking for registration type dropdown...")
        
        # Multiple strategies to find the dropdown
        dropdown_strategies = [
            (By.XPATH, "//div[contains(@data-testid, 'stSelectbox')]"),
            (By.XPATH, "//label[contains(text(), 'Register as')]/following-sibling::div"),
            (By.CSS_SELECTOR, "div.stSelectbox"),
        ]
        
        registration_type = find_element_with_multiple_strategies(driver, dropdown_strategies)
        
        if registration_type:
            print("🖱️ Clicking on registration type dropdown...")
            click_with_retry(driver, registration_type)
            time.sleep(1)
            
            print("🔍 Looking for 'candidate' option...")
            
            # Multiple strategies to find the candidate option
            candidate_option_strategies = [
                (By.XPATH, "//div[text()='candidate']"),
                (By.XPATH, "//div[@role='option' and contains(text(), 'candidate')]"),
                (By.XPATH, "//div[contains(@class, 'options') or contains(@class, 'menu')]//div[contains(text(), 'candidate')]"),
            ]
            
            candidate_option = find_element_with_multiple_strategies(driver, candidate_option_strategies)
            
            if candidate_option:
                print("🖱️ Clicking on 'candidate' option...")
                click_with_retry(driver, candidate_option)
                time.sleep(1)
            else:
                print("❌ Could not find 'candidate' option")
                return None, None
            
            take_screenshot(driver, "candidate_selected")
        else:
            print("❌ Could not find registration type dropdown")
            return None, None
            
        # Fill in form fields
        print("\n🖊️ Filling out registration form...")
        fields = {
            "reg_email": email,
            "reg_password": password,
            "Full Name": full_name,
            "Location": "San Francisco, CA",
            "Experience (Years)": "5",
            "Education Summary": "Computer Science Degree",
            "Professional Bio": "Experienced software developer with focus on backend technologies."
        }
        
        # Handle each field with multiple strategies
        for label, value in fields.items():
            print(f"🔍 Looking for field: {label}")
            
            # Special handling for Experience field (number input)
            if label == "Experience (Years)":
                exp_strategies = [
                    (By.XPATH, f"//label[text()='{label}']/..//input"),
                    (By.XPATH, f"//label[contains(text(), '{label}')]/..//input"),
                    (By.XPATH, f"//div[contains(text(), '{label}')]/following-sibling::input"),
                ]
                
                exp_input = find_element_with_multiple_strategies(driver, exp_strategies)
                
                if exp_input:
                    print(f"🖊️ Filling field: {label} = {value}")
                    scroll_to_element(driver, exp_input)
                    highlight_element(driver, exp_input)
                    fill_input(driver, exp_input, value)
                    time.sleep(0.5)
                else:
                    print(f"⚠️ Could not find field: {label}")
                
                continue
            
            # Standard strategies for other fields
            field_strategies = [
                (By.CSS_SELECTOR, f"input[aria-label='{label}']"),
                (By.XPATH, f"//label[text()='{label}']/..//input"),
                (By.XPATH, f"//label[text()='{label}']/..//textarea"),
                (By.XPATH, f"//label[contains(text(), '{label}')]/..//input"),
                (By.XPATH, f"//label[contains(text(), '{label}')]/..//textarea"),
            ]
            
            input_elem = find_element_with_multiple_strategies(driver, field_strategies)
            
            if input_elem:
                print(f"🖊️ Filling field: {label} = {value}")
                scroll_to_element(driver, input_elem)
                highlight_element(driver, input_elem)
                fill_input(driver, input_elem, value)
                time.sleep(0.5)
            else:
                print(f"⚠️ Could not find field: {label}")
        
        # Fill in Skills information
        print("\n🖊️ Filling skills information...")
        
        skills_strategies = [
            (By.XPATH, "//label[text()='Technical Skills (comma separated)']/..//textarea"),
            (By.XPATH, "//label[contains(text(), 'Technical Skills')]/..//textarea"),
            (By.CSS_SELECTOR, "textarea[placeholder*='skills' i]"),
        ]
        
        skills_input = find_element_with_multiple_strategies(driver, skills_strategies)
            
        if skills_input:
            print("🖊️ Filling technical skills")
            scroll_to_element(driver, skills_input)
            highlight_element(driver, skills_input)
            fill_input(driver, skills_input, "Python, JavaScript, SQL, Docker, AWS")
            time.sleep(0.5)
        else:
            print("⚠️ Could not find technical skills field")
        
        soft_skills_strategies = [
            (By.XPATH, "//label[text()='Soft Skills (comma separated)']/..//textarea"),
            (By.XPATH, "//label[contains(text(), 'Soft Skills')]/..//textarea"),
        ]
        
        soft_skills = find_element_with_multiple_strategies(driver, soft_skills_strategies)
            
        if soft_skills:
            print("🖊️ Filling soft skills")
            scroll_to_element(driver, soft_skills)
            highlight_element(driver, soft_skills)
            fill_input(driver, soft_skills, "Communication, Teamwork, Problem Solving")
            time.sleep(0.5)
        else:
            print("⚠️ Could not find soft skills field")
        
        # Handle job types dropdown
        print("\n🖊️ Selecting job types...")
        
        job_types_strategies = [
            (By.XPATH, "//label[text()='Preferred Job Types']/../div"),
            (By.XPATH, "//label[contains(text(), 'Preferred Job Types')]/../div"),
            (By.XPATH, "//div[contains(@data-baseweb, 'select')]"),
        ]
        
        job_types_dropdown = find_element_with_multiple_strategies(driver, job_types_strategies)
            
        if job_types_dropdown:
            print("🖱️ Clicking job types dropdown")
            scroll_to_element(driver, job_types_dropdown)
            highlight_element(driver, job_types_dropdown)
            click_with_retry(driver, job_types_dropdown)
            time.sleep(1)
            
            for job_type in ["Full-time", "Remote"]:
                print(f"🔍 Looking for job type: {job_type}")
                job_option_strategies = [
                    (By.XPATH, f"//div[text()='{job_type}']"),
                    (By.XPATH, f"//div[@role='option' and contains(text(), '{job_type}')]"),
                ]
                
                option = find_element_with_multiple_strategies(driver, job_option_strategies)
                
                if option:
                    print(f"🖱️ Selecting job type: {job_type}")
                    highlight_element(driver, option)
                    click_with_retry(driver, option)
                    time.sleep(0.5)
                else:
                    print(f"⚠️ Could not find job type: {job_type}")
            
            # Click outside to close dropdown
            try:
                driver.find_element(By.TAG_NAME, "body").click()
                time.sleep(0.5)
            except:
                pass
        else:
            print("⚠️ Could not find job types dropdown")
        
        # Fill preferred locations
        print("\n🖊️ Filling preferred locations...")
        
        locations_strategies = [
            (By.XPATH, "//label[text()='Preferred Locations (comma separated)']/..//textarea"),
            (By.XPATH, "//label[contains(text(), 'Preferred Locations')]/..//textarea"),
            (By.XPATH, "//textarea[contains(@placeholder, 'location')]"),
        ]
        
        locations = find_element_with_multiple_strategies(driver, locations_strategies)
            
        if locations:
            print("🖊️ Filling preferred locations")
            scroll_to_element(driver, locations)
            highlight_element(driver, locations)
            fill_input(driver, locations, "San Francisco, New York, Remote")
            time.sleep(0.5)
        else:
            print("⚠️ Could not find preferred locations field")
        
        # Take screenshot of filled form
        take_screenshot(driver, "form_filled")
        
        # Click Register button
        print("\n🖱️ Submitting registration form...")
        
        register_button_strategies = [
            (By.XPATH, "//button[text()='Register Candidate']"),
            (By.XPATH, "//button[contains(text(), 'Register') and contains(text(), 'Candidate')]"),
            (By.XPATH, "//div[contains(@class, 'stButton')]//button"),
            (By.CSS_SELECTOR, "button.stButton"),
        ]
        
        register_button = find_element_with_multiple_strategies(driver, register_button_strategies)
            
        if register_button:
            print("🖱️ Clicking register button")
            scroll_to_element(driver, register_button)
            highlight_element(driver, register_button, 2)
            click_with_retry(driver, register_button)
        else:
            print("❌ Could not find register button")
            return None, None
        
        # Wait for success message with increased timeout
        print("\n🔍 Waiting for registration result...")
        
        try:
            success_strategies = [
                (By.XPATH, "//div[contains(text(), 'Registration successful')]"),
                (By.XPATH, "//div[contains(@class, 'stAlert') and contains(text(), 'success')]"),
                (By.XPATH, "//div[contains(text(), 'success')]"),
            ]
            
            for by, selector in success_strategies:
                try:
                    success_message = WebDriverWait(driver, WAIT_TIME).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    
                    highlight_element(driver, success_message, 2)
                    take_screenshot(driver, "registration_success")
                    
                    print(f"\n✅ Candidate Registration successful: {email} / {password}")
                    time.sleep(3)  # Let user see the success message
                    
                    return email, password
                except TimeoutException:
                    continue
            
            # If we get here, success message wasn't found
            print("❌ Registration failed - no success message appeared")
            
            # Check for error messages
            error_strategies = [
                (By.XPATH, "//div[contains(@class, 'stAlert')]"),
                (By.XPATH, "//div[contains(@class, 'error')]"),
                (By.XPATH, "//div[contains(text(), 'error')]"),
            ]
            
            for by, selector in error_strategies:
                try:
                    error_msg = driver.find_element(by, selector).text
                    print(f"⚠️ Error message: {error_msg}")
                    take_screenshot(driver, "registration_error")
                    break
                except:
                    pass
            
            return None, None
            
        except Exception as e:
            print(f"❌ Error checking registration result: {e}")
            take_screenshot(driver, "registration_check_error")
            return None, None
            
    except Exception as e:
        print(f"❌ Error during candidate registration: {e}")
        print("Detailed error:")
        traceback.print_exc()
        take_screenshot(driver, "registration_exception")
        return None, None

def main():
    """Main function to run the focused registration test"""
    parser = argparse.ArgumentParser(description="Candidate Registration Test")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with additional output")
    args = parser.parse_args()
    
    debug_mode = args.debug
    
    print("="*80)
    print(" CANDIDATE REGISTRATION TEST ".center(80, "="))
    print("="*80)
    
    driver = None
    
    try:
        # Initialize the WebDriver
        driver = init_driver()
        if not driver:
            print("❌ Failed to initialize WebDriver, exiting.")
            return
        
        # Run the registration process
        email, password = register_candidate(driver, debug_mode)
        
        if email and password:
            print("\n🎉 Registration Test Successful!")
            print(f"Created candidate account: {email} / {password}")
        else:
            print("\n❌ Registration Test Failed!")
        
        # Keep the browser open for 10 seconds to review the final state
        print("\nClosing browser in 10 seconds...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Unhandled error: {e}")
        print("Detailed error:")
        traceback.print_exc()
        
        if driver:
            take_screenshot(driver, "unhandled_error")
    finally:
        # Close the browser
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main() 