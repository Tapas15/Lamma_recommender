#!/usr/bin/env python
"""
Login Script for Job Recommender Platform

This script focuses solely on the login process,
with enhanced debugging and more robust element finding.

Usage:
python login_only.py --email example@email.com --password yourpassword
"""

import os
import sys
import time
import traceback
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
SCREENSHOTS_DIR = "login_screenshots"

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

def login(driver, email, password, debug_mode=False):
    """Automate the login process with enhanced debugging"""
    print(f"\n🔵 Starting Login Process (email: {email})")
    take_screenshot(driver, "login_start")
    
    try:
        # Go to the frontend URL
        driver.get(FRONTEND_URL)
        print("✅ Navigated to frontend URL")
        time.sleep(3)  # Give frontend time to load completely
        take_screenshot(driver, "frontend_loaded")
        
        # Find and ensure we're on the Login tab
        print("🔍 Looking for Login tab...")
        
        # Multiple strategies to find the Login tab
        login_tab_strategies = [
            (By.CSS_SELECTOR, ".stTabs [role='tab']"),
            (By.XPATH, "//div[contains(@data-baseweb, 'tab-list')]/div[1]"),  # First tab
            (By.XPATH, "//div[contains(text(), 'Login')]"),
            (By.CSS_SELECTOR, "button.stTabs"),
        ]
        
        tabs = driver.find_elements(By.CSS_SELECTOR, ".stTabs [role='tab']")
        if len(tabs) >= 1:
            print(f"✅ Found {len(tabs)} tabs")
            login_tab = tabs[0]  # First tab should be Login
            print("🖱️ Clicking on Login tab...")
            click_with_retry(driver, login_tab)
        else:
            print("⚠️ Could not find tabs with main strategy, trying alternatives...")
            login_tab = find_element_with_multiple_strategies(driver, [
                (By.XPATH, "//div[contains(text(), 'Login')]"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//div[@role='tab'][contains(., 'Login')]")
            ])
            
            if login_tab:
                print("🖱️ Clicking on Login tab (alternative)...")
                click_with_retry(driver, login_tab)
            else:
                print("⚠️ Could not find Login tab, but the app may already be on the login page")
        
        time.sleep(2)  # Wait for login form to load/become active
        take_screenshot(driver, "login_tab_active")
        
        # Fill in login form
        print("\n🖊️ Filling login form...")
        
        # Email field
        print("🔍 Looking for email field...")
        email_field_strategies = [
            (By.CSS_SELECTOR, "input[aria-label='login_email']"),
            (By.XPATH, "//input[@type='email']"),
            (By.XPATH, "//label[contains(text(), 'Email')]/..//input"),
            (By.XPATH, "//input[contains(@placeholder, 'email')]"),
        ]
        
        email_field = find_element_with_multiple_strategies(driver, email_field_strategies)
        
        if email_field:
            print(f"🖊️ Filling email: {email}")
            scroll_to_element(driver, email_field)
            highlight_element(driver, email_field)
            fill_input(driver, email_field, email)
            time.sleep(0.5)
        else:
            print("❌ Could not find email field")
            return False
        
        # Password field
        print("🔍 Looking for password field...")
        password_field_strategies = [
            (By.CSS_SELECTOR, "input[aria-label='login_password']"),
            (By.XPATH, "//input[@type='password']"),
            (By.XPATH, "//label[contains(text(), 'Password')]/..//input"),
            (By.XPATH, "//input[contains(@placeholder, 'password')]"),
        ]
        
        password_field = find_element_with_multiple_strategies(driver, password_field_strategies)
        
        if password_field:
            print("🖊️ Filling password")
            scroll_to_element(driver, password_field)
            highlight_element(driver, password_field)
            fill_input(driver, password_field, password)
            time.sleep(0.5)
        else:
            print("❌ Could not find password field")
            return False
        
        # Take screenshot of filled form
        take_screenshot(driver, "login_form_filled")
        
        # Click Login button
        print("\n🖱️ Submitting login form...")
        
        login_button_strategies = [
            (By.XPATH, "//button[text()='Login']"),
            (By.XPATH, "//button[contains(text(), 'Login')]"),
            (By.XPATH, "//div[contains(@class, 'stButton')]//button"),
            (By.CSS_SELECTOR, "button.stButton"),
        ]
        
        login_button = find_element_with_multiple_strategies(driver, login_button_strategies)
            
        if login_button:
            print("🖱️ Clicking login button")
            scroll_to_element(driver, login_button)
            highlight_element(driver, login_button, 2)
            click_with_retry(driver, login_button)
        else:
            print("❌ Could not find login button")
            return False
        
        # Wait for login result with increased timeout
        print("\n🔍 Waiting for login result...")
        
        try:
            # Check for successful login indicators
            success_strategies = [
                (By.XPATH, "//div[contains(text(), 'Login successful')]"),
                (By.XPATH, "//div[contains(@class, 'stAlert') and contains(text(), 'success')]"),
                (By.XPATH, "//div[contains(text(), 'Welcome')]"),
                (By.XPATH, "//div[contains(text(), 'Logout')]"),  # Logout option appears after login
                (By.XPATH, "//div[contains(text(), 'Dashboard')]"),  # Dashboard heading
            ]
            
            for by, selector in success_strategies:
                try:
                    success_element = WebDriverWait(driver, WAIT_TIME).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    
                    highlight_element(driver, success_element, 2)
                    take_screenshot(driver, "login_success")
                    
                    print("\n✅ Login successful!")
                    time.sleep(2)  # Let user see the success message/dashboard
                    
                    # Take a screenshot of the dashboard area
                    take_screenshot(driver, "dashboard_after_login")
                    
                    return True
                except TimeoutException:
                    continue
            
            # If we get here, success indicators weren't found
            print("❌ Login failed - no success indicators found")
            
            # Check for error messages
            error_strategies = [
                (By.XPATH, "//div[contains(@class, 'stAlert')]"),
                (By.XPATH, "//div[contains(@class, 'error')]"),
                (By.XPATH, "//div[contains(text(), 'error')]"),
                (By.XPATH, "//div[contains(text(), 'Invalid')]"),
                (By.XPATH, "//div[contains(text(), 'incorrect')]"),
            ]
            
            for by, selector in error_strategies:
                try:
                    error_msg = driver.find_element(by, selector).text
                    print(f"⚠️ Error message: {error_msg}")
                    take_screenshot(driver, "login_error")
                    break
                except:
                    pass
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking login result: {e}")
            take_screenshot(driver, "login_check_error")
            return False
            
    except Exception as e:
        print(f"❌ Error during login process: {e}")
        print("Detailed error:")
        traceback.print_exc()
        take_screenshot(driver, "login_exception")
        return False

def main():
    """Main function to run the focused login test"""
    parser = argparse.ArgumentParser(description="Login Test")
    parser.add_argument("--email", type=str, help="Email address to use for login")
    parser.add_argument("--password", type=str, help="Password to use for login")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with additional output")
    args = parser.parse_args()
    
    # Default test credentials if not provided
    email = args.email or "test@example.com"
    password = args.password or "Test123!"
    debug_mode = args.debug
    
    print("="*80)
    print(" LOGIN TEST ".center(80, "="))
    print("="*80)
    print(f"Using email: {email}")
    
    driver = None
    
    try:
        # Initialize the WebDriver
        driver = init_driver()
        if not driver:
            print("❌ Failed to initialize WebDriver, exiting.")
            return
        
        # Run the login process
        success = login(driver, email, password, debug_mode)
        
        if success:
            print("\n🎉 Login Test Successful!")
        else:
            print("\n❌ Login Test Failed!")
        
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