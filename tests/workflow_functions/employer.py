"""
Employer Workflow Functions

This module contains functions for the employer workflow in the visual workflow test.
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
    filename = f"{screenshots_dir}/employer_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
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

def register_employer(driver, slow_mode=True):
    """Automate the employer registration process with visual elements"""
    try:
        print("\n🔵 Demonstrating Employer Registration...")
        
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
        
        # Set registration type to employer
        try:
            registration_type = wait_and_highlight(driver, By.XPATH, 
                                              "//div[contains(@data-testid, 'stSelectbox')]")
            registration_type.click()
            time.sleep(1)
            
            employer_option = wait_and_highlight(driver, By.XPATH, 
                                           "//div[contains(@role, 'option') and contains(text(), 'employer')]")
            employer_option.click()
            
            if slow_mode:
                time.sleep(1)
                
        except TimeoutException:
            print("⚠️ Failed to find employer option in the standard way, trying alternative method")
            try:
                # Try clicking the selectbox again
                registration_type = driver.find_element(By.XPATH, "//div[contains(@data-testid, 'stSelectbox')]")
                scroll_to_element(driver, registration_type)
                registration_type.click()
                time.sleep(1)
                
                # Use JavaScript to select the employer option
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
        
        # Take screenshot after selecting employer type
        take_screenshot(driver, "registration_type_selected")
        
        # Fill in registration form
        email = f"employer_{random.randint(1000, 9999)}@example.com"
        password = "Test123!"
        company_name = f"TechCorp {random.randint(100, 999)}"
        
        # Fill in form fields
        fields = {
            "emp_email": email,
            "emp_password": password,
            "Full Name": f"Test Employer {random.randint(100, 999)}",
            "Position": "HR Manager",
            "Professional Bio": "HR professional with experience in technical recruiting."
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
            "Company Name*": company_name,
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
        
        # Take screenshot of filled form
        take_screenshot(driver, "registration_form_filled")
        
        # Click Register button
        try:
            register_button = driver.find_element(By.XPATH, "//button[text()='Register Employer']")
            scroll_to_element(driver, register_button)
            highlight_element(driver, register_button, 2)
            register_button.click()
        except NoSuchElementException:
            # Try a more general selector if the specific text is not found
            buttons = driver.find_elements(By.XPATH, "//button")
            for button in buttons:
                if "register" in button.text.lower() and "employer" in button.text.lower():
                    scroll_to_element(driver, button)
                    highlight_element(driver, button, 2)
                    button.click()
                    break
            else:
                print("⚠️ Could not find employer registration button")
        
        # Wait for success message
        try:
            success_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Registration successful')]"))
            )
            highlight_element(driver, success_message, 2)
            
            # Take screenshot of success message
            take_screenshot(driver, "registration_success")
            
            print(f"✅ Employer Registration successful: {email} / {password}")
            
            if slow_mode:
                time.sleep(3)  # Let user see the success message
            
            return email, password
            
        except TimeoutException:
            print("❌ Employer Registration failed - no success message appeared")
            
            # Take screenshot of error state
            take_screenshot(driver, "registration_error")
            
            return None, None
            
    except Exception as e:
        print(f"❌ Error during employer registration: {e}")
        # Take screenshot of error state
        take_screenshot(driver, "registration_error")
        return None, None

def login_employer(driver, email, password, slow_mode=True):
    """Login as an employer with visual highlighting"""
    try:
        print(f"\n🔵 Logging in as employer: {email}")
        
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
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Employer Dashboard')]"))
                )
                highlight_element(driver, dashboard_element, 2)
                
                # Take screenshot of dashboard
                take_screenshot(driver, "employer_dashboard")
                
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

def post_job(driver, slow_mode=True):
    """Post a new job as an employer with visual elements"""
    try:
        print("\n🔵 Creating a new job posting...")
        
        # Find and click the Post Job link
        nav_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a"))
        )
        
        post_job_link = None
        for link in nav_links:
            if "post" in link.text.lower() and "job" in link.text.lower():
                post_job_link = link
                break
        
        if not post_job_link:
            print("❌ Could not find Post Job link")
            return False, None, None
        
        highlight_element(driver, post_job_link, 2)
        post_job_link.click()
        
        if slow_mode:
            time.sleep(2)
        
        # Generate job details
        job_title = f"Software Engineer {random.randint(100, 999)}"
        
        # Take screenshot of job form
        take_screenshot(driver, "job_form")
        
        # Fill in job details
        fields = {
            "Job Title*": job_title,
            "Job Description*": "We are looking for a skilled software engineer to join our team. The ideal candidate will have experience with Python, JavaScript, and cloud technologies.",
            "Requirements*": "- 3+ years of software development experience\n- Proficiency in Python and JavaScript\n- Experience with cloud platforms (AWS, Azure, GCP)\n- Strong problem-solving skills",
            "Responsibilities*": "- Develop and maintain web applications\n- Collaborate with cross-functional teams\n- Write clean, maintainable code\n- Participate in code reviews",
            "Location*": "San Francisco, CA (Remote Available)",
            "Salary Range": "$120,000 - $160,000"
        }
        
        for label, value in fields.items():
            try:
                input_elem = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//input")
            except NoSuchElementException:
                try:
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
        
        # Take screenshot of filled form
        take_screenshot(driver, "job_form_filled")
        
        # Find and click the Post Job button
        post_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Post Job')]"))
        )
        
        scroll_to_element(driver, post_button)
        highlight_element(driver, post_button, 2)
        post_button.click()
        
        # Wait for confirmation
        try:
            success_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Job posted successfully')]"))
            )
            highlight_element(driver, success_message, 2)
            
            # Take screenshot of success message
            take_screenshot(driver, "job_post_success")
            
            # Try to get job ID from URL or page content (implementation depends on the actual app)
            job_id = f"job_{random.randint(1000, 9999)}"  # Placeholder
            
            print(f"✅ Job posted successfully: {job_title}")
            
            if slow_mode:
                time.sleep(3)
            
            return True, job_title, job_id
            
        except TimeoutException:
            print("❌ Job posting failed - no success message appeared")
            
            # Take screenshot of error state
            take_screenshot(driver, "job_post_error")
            
            return False, None, None
        
    except Exception as e:
        print(f"❌ Error posting job: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "job_post_error")
        
        return False, None, None

def post_project(driver, slow_mode=True):
    """Post a new project as an employer with visual elements"""
    try:
        print("\n🔵 Creating a new project posting...")
        
        # Find and click the Post Project link
        nav_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a"))
        )
        
        post_project_link = None
        for link in nav_links:
            if "post" in link.text.lower() and "project" in link.text.lower():
                post_project_link = link
                break
        
        if not post_project_link:
            print("❌ Could not find Post Project link")
            return False, None, None
        
        highlight_element(driver, post_project_link, 2)
        post_project_link.click()
        
        if slow_mode:
            time.sleep(2)
        
        # Generate project details
        project_title = f"Web Application Development {random.randint(100, 999)}"
        
        # Take screenshot of project form
        take_screenshot(driver, "project_form")
        
        # Fill in project details
        fields = {
            "Project Title*": project_title,
            "Project Description*": "We need a skilled developer to build a responsive web application with modern technologies. The project involves frontend and backend development.",
            "Requirements*": "- Experience with React.js and Node.js\n- Knowledge of database design\n- Strong UX/UI skills\n- Ability to meet deadlines",
            "Budget*": "$5,000 - $10,000",
            "Duration*": "2-3 months",
            "Location": "Remote"
        }
        
        for label, value in fields.items():
            try:
                input_elem = driver.find_element(By.XPATH, f"//label[text()='{label}']/..//input")
            except NoSuchElementException:
                try:
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
        
        # Take screenshot of filled form
        take_screenshot(driver, "project_form_filled")
        
        # Find and click the Post Project button
        post_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Post Project')]"))
        )
        
        scroll_to_element(driver, post_button)
        highlight_element(driver, post_button, 2)
        post_button.click()
        
        # Wait for confirmation
        try:
            success_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Project posted successfully')]"))
            )
            highlight_element(driver, success_message, 2)
            
            # Take screenshot of success message
            take_screenshot(driver, "project_post_success")
            
            # Try to get project ID from URL or page content (implementation depends on the actual app)
            project_id = f"project_{random.randint(1000, 9999)}"  # Placeholder
            
            print(f"✅ Project posted successfully: {project_title}")
            
            if slow_mode:
                time.sleep(3)
            
            return True, project_title, project_id
            
        except TimeoutException:
            print("❌ Project posting failed - no success message appeared")
            
            # Take screenshot of error state
            take_screenshot(driver, "project_post_error")
            
            return False, None, None
        
    except Exception as e:
        print(f"❌ Error posting project: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "project_post_error")
        
        return False, None, None

def view_candidates(driver, slow_mode=True):
    """View list of candidates as an employer with visual elements"""
    try:
        print("\n🔵 Viewing candidate listings...")
        
        # Find and click the Candidates link
        nav_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a"))
        )
        
        candidates_link = None
        for link in nav_links:
            if "candidate" in link.text.lower():
                candidates_link = link
                break
        
        if not candidates_link:
            print("❌ Could not find Candidates link")
            return False
        
        highlight_element(driver, candidates_link, 2)
        candidates_link.click()
        
        if slow_mode:
            time.sleep(2)
        
        # Take screenshot of candidates list
        take_screenshot(driver, "candidates_list")
        
        # Try to view a specific candidate's details if available
        try:
            candidate_items = driver.find_elements(By.XPATH, "//div[contains(@class, 'candidate-item')]")
            if candidate_items and len(candidate_items) > 0:
                highlight_element(driver, candidate_items[0], 2)
                candidate_items[0].click()
                
                if slow_mode:
                    time.sleep(2)
                
                # Take screenshot of candidate details
                take_screenshot(driver, "candidate_details")
                
                # Go back to the list
                driver.back()
                
                if slow_mode:
                    time.sleep(2)
        except:
            print("⚠️ Could not view individual candidate details")
        
        print("✅ Viewed candidates successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error viewing candidates: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "candidates_view_error")
        
        return False

def view_candidate_recommendations(driver, job_id, slow_mode=True):
    """View candidate recommendations for a job with visual elements"""
    try:
        print("\n🔵 Viewing candidate recommendations...")
        
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
        take_screenshot(driver, "recommendations_page")
        
        # Interact with any job selector if present
        try:
            job_selector = driver.find_element(By.XPATH, "//select[contains(@class, 'job-selector')]")
            highlight_element(driver, job_selector, 2)
            job_selector.click()
            
            if slow_mode:
                time.sleep(1)
            
            # Select first option
            options = job_selector.find_elements(By.TAG_NAME, "option")
            if options and len(options) > 0:
                highlight_element(driver, options[0], 1)
                options[0].click()
                
                if slow_mode:
                    time.sleep(1)
        except:
            print("⚠️ Could not find job selector")
        
        # Take screenshot of candidate recommendations
        take_screenshot(driver, "candidate_recommendations")
        
        print("✅ Viewed candidate recommendations successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error viewing candidate recommendations: {e}")
        
        # Take screenshot of error state
        take_screenshot(driver, "recommendations_error")
        
        return False 