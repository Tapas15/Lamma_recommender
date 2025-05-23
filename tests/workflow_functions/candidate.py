"""
Candidate Workflow Functions

This module contains functions for the candidate workflow in the visual workflow test.
"""

import os
import time
import random
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# Helper functions
def take_screenshot(driver, name):
    """Take a screenshot and save it to the screenshots directory"""
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    filename = f"{screenshots_dir}/candidate_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
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

def wait_and_highlight(driver, locator_type, locator_value, duration=1, wait_time=10):
    """Wait for element to be present, then highlight it"""
    wait = WebDriverWait(driver, wait_time)
    element = wait.until(EC.presence_of_element_located((locator_type, locator_value)))
    scroll_to_element(driver, element)
    highlight_element(driver, element, duration)
    return element

def register_candidate(driver, slow_mode=True):
    """Automate the candidate registration process with visual elements"""
    try:
        print("\n🔵 Demonstrating Candidate Registration...")
        
        # Go to the frontend URL
        driver.get("http://localhost:8501")
        
        if slow_mode:
            time.sleep(2)
        
        # Take screenshot of the landing page
        take_screenshot(driver, "registration_start")
        
        # Click on Register tab in sidebar
        wait = WebDriverWait(driver, 10)
        tabs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".stTabs [role='tab']")))
        tabs[1].click()  # Register tab
        
        if slow_mode:
            time.sleep(1)
        
        # Set registration type to candidate
        try:
            registration_type = wait_and_highlight(driver, By.XPATH, 
                                              "//div[contains(@data-testid, 'stSelectbox')]")
            registration_type.click()
            time.sleep(1)
            
            candidate_option = wait_and_highlight(driver, By.XPATH, 
                                           "//div[contains(@role, 'option') and contains(text(), 'candidate')]")
            candidate_option.click()
            
            if slow_mode:
                time.sleep(1)
        except Exception as e:
            print(f"⚠️ Failed to select candidate option: {e}")
        
        # Take screenshot after selecting candidate type
        take_screenshot(driver, "registration_type_selected")
        
        # Fill in registration form
        email = f"candidate_{random.randint(1000, 9999)}@example.com"
        password = "Test123!"
        full_name = f"Test Candidate {random.randint(100, 999)}"
        
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
                try:
                    # Find number input and clear it
                    num_input = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//input")
                    scroll_to_element(driver, num_input)
                    highlight_element(driver, num_input)
                    num_input.clear()
                    num_input.send_keys(value)
                    continue
                except:
                    pass
                    
            # Regular text inputs
            try:
                # Try first by looking for key attribute
                input_elem = driver.find_element(By.CSS_SELECTOR, f"input[aria-label='{label}']")
            except NoSuchElementException:
                try:
                    # Then try by looking for label text
                    input_elem = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//input")
                except NoSuchElementException:
                    try:
                        # Finally try for textarea
                        input_elem = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//textarea")
                    except:
                        print(f"⚠️ Could not find input field for {label}")
                        continue
            
            scroll_to_element(driver, input_elem)
            highlight_element(driver, input_elem)
            input_elem.clear()
            input_elem.send_keys(value)
            if slow_mode:
                time.sleep(0.5)
        
        # Fill in Skills information
        try:
            skills_input = driver.find_element(By.XPATH, "//label[text()='Technical Skills (comma separated)']/..//textarea")
            scroll_to_element(driver, skills_input)
            highlight_element(driver, skills_input)
            skills_input.send_keys("Python, JavaScript, SQL, Docker, AWS")
            
            if slow_mode:
                time.sleep(0.5)
        except:
            print("⚠️ Could not find technical skills field")
            
        try:
            soft_skills = driver.find_element(By.XPATH, "//label[text()='Soft Skills (comma separated)']/..//textarea")
            scroll_to_element(driver, soft_skills)
            highlight_element(driver, soft_skills)
            soft_skills.send_keys("Communication, Teamwork, Problem Solving")
            
            if slow_mode:
                time.sleep(0.5)
        except:
            print("⚠️ Could not find soft skills field")
        
        # Take screenshot of filled form
        take_screenshot(driver, "registration_form_filled")
        
        # Select job types if present
        try:
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
        except:
            print("⚠️ Could not find job types dropdown")
        
        # Fill preferred locations if present
        try:
            locations = driver.find_element(By.XPATH, "//label[text()='Preferred Locations (comma separated)']/..//textarea")
            scroll_to_element(driver, locations)
            highlight_element(driver, locations)
            locations.send_keys("San Francisco, New York, Remote")
            
            if slow_mode:
                time.sleep(1)
        except:
            print("⚠️ Could not find preferred locations field")
        
        # Click Register button
        try:
            register_button = driver.find_element(By.XPATH, "//button[text()='Register Candidate']")
            scroll_to_element(driver, register_button)
            highlight_element(driver, register_button, 2)
            register_button.click()
        except NoSuchElementException:
            # Try a more general selector if the specific text is not found
            buttons = driver.find_elements(By.XPATH, "//button")
            for button in buttons:
                if "register" in button.text.lower() and "candidate" in button.text.lower():
                    scroll_to_element(driver, button)
                    highlight_element(driver, button, 2)
                    button.click()
                    break
            else:
                print("⚠️ Could not find candidate registration button")
        
        # Wait for success message
        try:
            success_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Registration successful')]"))
            )
            highlight_element(driver, success_message, 2)
            
            # Take screenshot of success message
            take_screenshot(driver, "registration_success")
            
            print(f"✅ Candidate Registration successful: {email} / {password}")
            
            if slow_mode:
                time.sleep(3)  # Let user see the success message
            
            return email, password
            
        except TimeoutException:
            print("❌ Candidate Registration failed - no success message appeared")
            
            # Take screenshot of error state
            take_screenshot(driver, "registration_error")
            
            # Check for error messages
            try:
                error_msg = driver.find_element(By.XPATH, "//div[contains(@class, 'stAlert')]").text
                print(f"Error: {error_msg}")
            except:
                pass
                
            return None, None
            
    except Exception as e:
        print(f"❌ Error during candidate registration: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "registration_error")
        
        return None, None

def login_candidate(driver, email, password, slow_mode=True):
    """Login as a candidate with visual highlighting"""
    try:
        print(f"\n🔵 Logging in as candidate: {email}")
        
        # Go to the frontend URL
        driver.get("http://localhost:8501")
        
        if slow_mode:
            time.sleep(2)
        
        # Click on Login tab in sidebar
        wait = WebDriverWait(driver, 10)
        tabs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".stTabs [role='tab']")))
        tabs[0].click()  # Login tab
        
        if slow_mode:
            time.sleep(1)
        
        # Take screenshot of login form
        take_screenshot(driver, "login_form")
        
        # Fill in login form
        email_input = wait_and_highlight(driver, By.CSS_SELECTOR, "input[aria-label='login_email']")
        email_input.clear()
        email_input.send_keys(email)
        
        if slow_mode:
            time.sleep(0.5)
        
        password_input = wait_and_highlight(driver, By.CSS_SELECTOR, "input[aria-label='login_password']")
        password_input.clear()
        password_input.send_keys(password)
        
        if slow_mode:
            time.sleep(1)
        
        # Take screenshot of filled login form
        take_screenshot(driver, "login_form_filled")
        
        # Click Login button
        login_button = wait_and_highlight(driver, By.XPATH, "//button[text()='Login']", 2)
        login_button.click()
        
        # Wait for successful login
        try:
            # Look for welcome message or dashboard content
            success_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Login successful')]"))
            )
            highlight_element(driver, success_element, 2)
            
            # Take screenshot of success message
            take_screenshot(driver, "login_success")
            
            print(f"✅ Login successful for {email}")
            
            if slow_mode:
                time.sleep(3)  # Let user see the success message
            
            return True
            
        except TimeoutException:
            # Alternative check: look for elements that appear after successful login
            try:
                dashboard_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Candidate Dashboard')]"))
                )
                highlight_element(driver, dashboard_element, 2)
                
                # Take screenshot of dashboard
                take_screenshot(driver, "candidate_dashboard")
                
                print(f"✅ Login successful for {email}")
                
                if slow_mode:
                    time.sleep(3)
                
                return True
            except TimeoutException:
                print(f"❌ Login failed for {email}")
                
                # Take screenshot of error state
                take_screenshot(driver, "login_error")
                
                return False
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "login_error")
        
        return False

def browse_jobs(driver, slow_mode=True):
    """Browse available jobs with visual elements"""
    try:
        print("\n🔵 Browsing available jobs...")
        
        # Find and click the Jobs link
        nav_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a"))
        )
        
        jobs_link = None
        for link in nav_links:
            if "job" in link.text.lower() and not "post" in link.text.lower():
                jobs_link = link
                break
        
        if not jobs_link:
            print("❌ Could not find Jobs link")
            return None
        
        highlight_element(driver, jobs_link, 2)
        jobs_link.click()
        
        if slow_mode:
            time.sleep(2)
        
        # Take screenshot of jobs list
        take_screenshot(driver, "jobs_list")
        
        # Try to interact with search/filter if available
        try:
            search_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Search')]")
            scroll_to_element(driver, search_input)
            highlight_element(driver, search_input, 1)
            search_input.clear()
            search_input.send_keys("developer")
            
            if slow_mode:
                time.sleep(1)
                
            # Try to click search button if present
            search_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Search')]")
            highlight_element(driver, search_button, 1)
            search_button.click()
            
            if slow_mode:
                time.sleep(2)
                
            # Take screenshot of search results
            take_screenshot(driver, "jobs_search_results")
        except:
            print("⚠️ Could not find or interact with search functionality")
        
        # Try to view a specific job's details if available
        job_id = None
        try:
            job_items = driver.find_elements(By.XPATH, "//div[contains(@class, 'job-item')]")
            if not job_items or len(job_items) == 0:
                # Try alternative selector
                job_items = driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'stExpander')]")
            
            if job_items and len(job_items) > 0:
                highlight_element(driver, job_items[0], 2)
                job_items[0].click()
                
                # Extract job ID if possible
                job_id = f"job_{random.randint(1000, 9999)}"  # Placeholder
                
                if slow_mode:
                    time.sleep(2)
                
                # Take screenshot of job details
                take_screenshot(driver, "job_details")
        except Exception as e:
            print(f"⚠️ Could not view individual job details: {e}")
        
        print("✅ Browsed jobs successfully")
        return job_id
        
    except Exception as e:
        print(f"❌ Error browsing jobs: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "browse_jobs_error")
        
        return None

def apply_for_job(driver, job_id, slow_mode=True):
    """Apply for a job with visual elements"""
    try:
        print(f"\n🔵 Applying for job: {job_id}...")
        
        # Find and click Apply button
        apply_button = None
        try:
            # Try different possible selectors for Apply button
            for selector in [
                "//button[contains(text(), 'Apply')]",
                "//a[contains(text(), 'Apply')]",
                "//div[contains(text(), 'Apply')]"
            ]:
                try:
                    apply_button = driver.find_element(By.XPATH, selector)
                    break
                except:
                    pass
            
            if not apply_button:
                print("❌ Could not find Apply button")
                return False
            
            scroll_to_element(driver, apply_button)
            highlight_element(driver, apply_button, 2)
            apply_button.click()
            
            if slow_mode:
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error finding or clicking Apply button: {e}")
            return False
        
        # Take screenshot of application form
        take_screenshot(driver, "application_form")
        
        # Fill in application details
        try:
            # Cover letter
            try:
                cover_letter = driver.find_element(By.XPATH, "//label[contains(text(), 'Cover Letter')]/..//textarea")
                scroll_to_element(driver, cover_letter)
                highlight_element(driver, cover_letter, 1)
                cover_letter.clear()
                cover_letter.send_keys(
                    "I am excited to apply for this position as I believe my skills and experience align well with your requirements. "
                    "I have worked on similar projects and am confident I can contribute effectively to your team."
                )
                
                if slow_mode:
                    time.sleep(1)
            except:
                print("⚠️ Could not find cover letter field")
            
            # Additional fields that might be present
            additional_fields = {
                "Expected Salary": "$120,000",
                "Availability": "Immediately",
                "Additional Information": "I am willing to relocate if necessary and am available for interviews at your convenience."
            }
            
            for label, value in additional_fields.items():
                try:
                    field = driver.find_element(By.XPATH, f"//label[contains(text(), '{label}')]/..//input")
                    scroll_to_element(driver, field)
                    highlight_element(driver, field, 1)
                    field.clear()
                    field.send_keys(value)
                    
                    if slow_mode:
                        time.sleep(0.5)
                except:
                    try:
                        # Try textarea
                        field = driver.find_element(By.XPATH, f"//label[contains(text(), '{label}')]/..//textarea")
                        scroll_to_element(driver, field)
                        highlight_element(driver, field, 1)
                        field.clear()
                        field.send_keys(value)
                        
                        if slow_mode:
                            time.sleep(0.5)
                    except:
                        print(f"⚠️ Could not find field for {label}")
        except Exception as e:
            print(f"⚠️ Error filling application form: {e}")
        
        # Take screenshot of filled application form
        take_screenshot(driver, "application_form_filled")
        
        # Submit application
        try:
            submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit Application')]")
            scroll_to_element(driver, submit_button)
            highlight_element(driver, submit_button, 2)
            submit_button.click()
            
            # Wait for confirmation
            success_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Application submitted successfully')]"))
            )
            highlight_element(driver, success_message, 2)
            
            # Take screenshot of success message
            take_screenshot(driver, "application_success")
            
            print("✅ Application submitted successfully")
            
            if slow_mode:
                time.sleep(3)
                
            return True
            
        except Exception as e:
            print(f"❌ Error submitting application: {e}")
            
            # Take screenshot of error state
            take_screenshot(driver, "application_error")
            
            return False
        
    except Exception as e:
        print(f"❌ Error during job application: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "application_error")
        
        return False

def view_job_recommendations(driver, slow_mode=True):
    """View job recommendations with visual elements"""
    try:
        print("\n🔵 Viewing job recommendations...")
        
        # Find and click the Recommendations link
        nav_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a"))
        )
        
        recommendations_link = None
        for link in nav_links:
            if "recommend" in link.text.lower():
                recommendations_link = link
                break
        
        if not recommendations_link:
            print("❌ Could not find Recommendations link")
            return False
        
        highlight_element(driver, recommendations_link, 2)
        recommendations_link.click()
        
        if slow_mode:
            time.sleep(2)
        
        # Take screenshot of recommendations page
        take_screenshot(driver, "job_recommendations")
        
        # Try to interact with recommendation settings if available
        try:
            settings_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Settings')]")
            scroll_to_element(driver, settings_button)
            highlight_element(driver, settings_button, 1)
            settings_button.click()
            
            if slow_mode:
                time.sleep(1)
                
            # Take screenshot of settings
            take_screenshot(driver, "recommendation_settings")
            
            # Close settings
            close_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Close')]")
            highlight_element(driver, close_button, 1)
            close_button.click()
            
            if slow_mode:
                time.sleep(1)
        except:
            print("⚠️ Could not find or interact with recommendation settings")
        
        # Try to view a specific job recommendation if available
        try:
            job_items = driver.find_elements(By.XPATH, "//div[contains(@class, 'job-recommendation')]")
            if not job_items or len(job_items) == 0:
                # Try alternative selector
                job_items = driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'stExpander')]")
            
            if job_items and len(job_items) > 0:
                scroll_to_element(driver, job_items[0])
                highlight_element(driver, job_items[0], 2)
                job_items[0].click()
                
                if slow_mode:
                    time.sleep(2)
                
                # Take screenshot of job details
                take_screenshot(driver, "recommended_job_details")
        except:
            print("⚠️ Could not view individual job recommendation details")
        
        print("✅ Viewed job recommendations successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error viewing job recommendations: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "recommendations_error")
        
        return False

def browse_projects(driver, slow_mode=True):
    """Browse available projects with visual elements"""
    try:
        print("\n🔵 Browsing available projects...")
        
        # Find and click the Projects link
        nav_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a"))
        )
        
        projects_link = None
        for link in nav_links:
            if "project" in link.text.lower() and not "post" in link.text.lower():
                projects_link = link
                break
        
        if not projects_link:
            print("❌ Could not find Projects link")
            return False
        
        highlight_element(driver, projects_link, 2)
        projects_link.click()
        
        if slow_mode:
            time.sleep(2)
        
        # Take screenshot of projects list
        take_screenshot(driver, "projects_list")
        
        # Try to view a specific project's details if available
        try:
            project_items = driver.find_elements(By.XPATH, "//div[contains(@class, 'project-item')]")
            if not project_items or len(project_items) == 0:
                # Try alternative selector
                project_items = driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'stExpander')]")
            
            if project_items and len(project_items) > 0:
                scroll_to_element(driver, project_items[0])
                highlight_element(driver, project_items[0], 2)
                project_items[0].click()
                
                if slow_mode:
                    time.sleep(2)
                
                # Take screenshot of project details
                take_screenshot(driver, "project_details")
        except:
            print("⚠️ Could not view individual project details")
        
        print("✅ Browsed projects successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error browsing projects: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "browse_projects_error")
        
        return False

def view_project_recommendations(driver, slow_mode=True):
    """View project recommendations with visual elements"""
    try:
        print("\n🔵 Viewing project recommendations...")
        
        # Find and click the Project Recommendations link
        nav_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a"))
        )
        
        recommendations_link = None
        for link in nav_links:
            if "recommend" in link.text.lower() and "project" in link.text.lower():
                recommendations_link = link
                break
        
        # If we can't find a specific project recommendations link, try the general recommendations link
        if not recommendations_link:
            for link in nav_links:
                if "recommend" in link.text.lower():
                    recommendations_link = link
                    break
        
        if not recommendations_link:
            print("❌ Could not find Project Recommendations link")
            return False
        
        highlight_element(driver, recommendations_link, 2)
        recommendations_link.click()
        
        if slow_mode:
            time.sleep(2)
        
        # Take screenshot of recommendations page
        take_screenshot(driver, "project_recommendations")
        
        # Try to view a specific project recommendation if available
        try:
            project_items = driver.find_elements(By.XPATH, "//div[contains(@class, 'project-recommendation')]")
            if not project_items or len(project_items) == 0:
                # Try alternative selector
                project_items = driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'stExpander')]")
            
            if project_items and len(project_items) > 0:
                scroll_to_element(driver, project_items[0])
                highlight_element(driver, project_items[0], 2)
                project_items[0].click()
                
                if slow_mode:
                    time.sleep(2)
                
                # Take screenshot of project details
                take_screenshot(driver, "recommended_project_details")
        except:
            print("⚠️ Could not view individual project recommendation details")
        
        print("✅ Viewed project recommendations successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error viewing project recommendations: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "project_recommendations_error")
        
        return False 