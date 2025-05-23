import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state variables
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_type" not in st.session_state:
    st.session_state.user_type = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Set page config
st.set_page_config(
    page_title="Job Recommender API Tester",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper functions
def make_api_request(endpoint, method="GET", data=None, params=None, auth=True):
    """Make API request with proper headers and authentication"""
    headers = {
        "Content-Type": "application/json"
    }
    
    if auth and st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    url = f"{API_BASE_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.content else {"message": "Success"}
        else:
            try:
                error_data = response.json() if response.content else {"detail": "Unknown error"}
                
                # Handle different error formats
                if isinstance(error_data, dict):
                    if "detail" in error_data:
                        # Regular FastAPI error format
                        detail = error_data["detail"]
                        if isinstance(detail, list):
                            # Validation errors list
                            return {"error": f"Validation errors (Status {response.status_code})", "detail": detail}
                        else:
                            # Simple string error
                            return {"error": detail, "detail": error_data}
                    else:
                        # Unknown format
                        return {"error": f"Status {response.status_code}", "detail": error_data}
                else:
                    # Other error format
                    return {"error": f"Status {response.status_code}", "detail": error_data}
            except Exception as json_error:
                return {"error": f"Status {response.status_code}", "detail": {"message": "Failed to parse error response"}}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}", "detail": {"message": str(e)}}

def login(email, password):
    """Login and get access token"""
    # Validate required fields
    if not email or not password:
        st.error("Email and password are required.")
        return False
        
    data = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/token", 
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.access_token = token_data.get("access_token")
            st.session_state.authenticated = True
            
            # Get user profile to determine user type
            profile = make_api_request("profile")
            if "error" not in profile:
                st.session_state.user_type = profile.get("user_type", "unknown")
            
            return True
        else:
            error_detail = "Invalid credentials"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except:
                pass
                
            st.error(f"Login failed: {error_detail}")
            return False
    except Exception as e:
        st.error(f"Error connecting to server: {str(e)}")
        return False

def register_user(data, user_type):
    """Register a new user (candidate or employer)"""
    endpoint = f"register/{user_type}"
    return make_api_request(endpoint, method="POST", data=data, auth=False)

# Sidebar for authentication
with st.sidebar:
    st.title("Job Recommender API")
    
    if not st.session_state.authenticated:
        st.subheader("Authentication")
        auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])
        
        with auth_tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                if login(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Login failed. Please check your credentials.")
        
        with auth_tab2:
            user_type = st.selectbox("Registration Type", ["candidate", "employer"])
            
            if user_type == "candidate":
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                full_name = st.text_input("Full Name")
                location = st.text_input("Location")
                experience_years_num = st.number_input("Experience (Years)", min_value=0, max_value=50)
                experience_years = str(experience_years_num)  # Convert to string for API compatibility
                education = st.text_input("Education Summary")
                bio = st.text_area("Professional Bio")
                
                st.subheader("Skills Information")
                skills_input = st.text_area("Technical Skills (comma separated)", 
                                          help="Languages, frameworks, and tools you know")
                soft_skills_input = st.text_area("Soft Skills (comma separated)",
                                               help="Communication, teamwork, etc.")
                
                st.subheader("Job Preferences")
                job_types = st.multiselect("Preferred Job Types", 
                                         ["Full-time", "Part-time", "Contract", "Remote", "Hybrid"])
                preferred_locations = st.text_area("Preferred Locations (comma separated)",
                                                help="Cities or countries where you'd like to work")
                
                if st.button("Register Candidate"):
                    # Validate required fields
                    if not reg_email or not reg_password or not full_name:
                        st.error("Email, password, and full name are required.")
                    else:
                        skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]
                        soft_skills_list = [s.strip() for s in soft_skills_input.split(",") if s.strip()]
                        locations_list = [s.strip() for s in preferred_locations.split(",") if s.strip()]
                        
                        # Clean empty fields to avoid validation errors
                        data = {
                            "email": reg_email,
                            "password": reg_password,
                            "full_name": full_name,
                            "user_type": "candidate",
                            "skills": {
                                "languages_frameworks": skills_list,
                                "soft_skills": soft_skills_list
                            }
                        }
                        
                        # Add optional fields only if they have values
                        if location:
                            data["location"] = location
                        if experience_years and experience_years != "0":
                            data["experience_years"] = experience_years
                        if education:
                            data["education_summary"] = education
                        if bio:
                            data["bio"] = bio
                        if locations_list:
                            data["preferred_job_locations"] = locations_list
                        if job_types:
                            data["preferred_job_types"] = job_types
                        
                        result = register_user(data, "candidate")
                        if "error" not in result:
                            st.success("Registration successful! Please login.")
                        else:
                            error_msg = result.get('detail')
                            st.error(f"Registration failed: {error_msg or result.get('error', 'Unknown error')}")
                            # Show detailed validation errors if available
                            if isinstance(error_msg, list):
                                for err in error_msg:
                                    field = '.'.join(err.get('loc', [])[1:]) if 'loc' in err else 'unknown'
                                    msg = err.get('msg', 'invalid value')
                                    st.error(f"Field '{field}': {msg}")
            
            else:  # employer
                reg_email = st.text_input("Email", key="emp_email")
                reg_password = st.text_input("Password", type="password", key="emp_password")
                full_name = st.text_input("Full Name")
                position = st.text_input("Position")
                bio = st.text_area("Professional Bio", placeholder="Brief description of your role and experience")
                
                st.subheader("Company Details")
                company_name = st.text_input("Company Name*", help="Required field")
                industry = st.selectbox(
                    "Industry*", 
                    ["Technology", "Finance", "Healthcare", "Education", "E-commerce", 
                     "Manufacturing", "Retail", "Media", "Consulting", "Other"],
                    help="Required field"
                )
                company_description = st.text_area("Company Description")
                company_size = st.selectbox("Company Size", ["1-10 employees", "11-50 employees", "51-200 employees", "201-500 employees", "501+ employees"])
                company_location = st.text_input("Company Location")
                company_website = st.text_input("Company Website")
                founded_year_num = st.number_input("Founded Year", min_value=1900, max_value=2023, value=2000)
                founded_year = int(founded_year_num)  # Ensure it's an integer for the API
                
                st.subheader("Hiring Information")
                hiring_needs = st.text_area("Hiring Needs (comma separated)")
                
                if st.button("Register Employer"):
                    # Check required fields
                    if not reg_email or not reg_password or not full_name:
                        st.error("Email, password, and full name are required.")
                    elif not company_name or not industry:
                        st.error("Company name and industry are required fields.")
                    else:
                        hiring_list = [s.strip() for s in hiring_needs.split(",") if s.strip()]
                        
                        # Clean empty fields to avoid validation errors
                        data = {
                            "email": reg_email,
                            "password": reg_password,
                            "full_name": full_name,
                            "user_type": "employer",
                            "company_details": {
                                "company_name": company_name,
                                "industry": industry
                            }
                        }
                        
                        # Add optional fields only if they have values
                        if position:
                            data["position"] = position
                        if bio:
                            data["bio"] = bio
                            
                        # Add optional company details if they have values
                        if company_description:
                            data["company_details"]["company_description"] = company_description
                        if company_website:
                            data["company_details"]["company_website"] = company_website
                        if company_size:
                            data["company_details"]["company_size"] = company_size
                        if company_location:
                            data["company_details"]["company_location"] = company_location
                        if founded_year:
                            data["company_details"]["founded_year"] = founded_year
                            
                        # Add hiring preferences if values exist
                        if hiring_list:
                            data["hiring_preferences"] = {
                                "job_roles_hiring": hiring_list
                            }
                        
                        result = register_user(data, "employer")
                        if "error" not in result:
                            st.success("Registration successful! Please login.")
                        else:
                            error_msg = result.get('detail')
                            st.error(f"Registration failed: {error_msg or result.get('error', 'Unknown error')}")
                            # Show detailed validation errors if available
                            if isinstance(error_msg, list):
                                for err in error_msg:
                                    field = '.'.join(err.get('loc', [])[1:]) if 'loc' in err else 'unknown'
                                    msg = err.get('msg', 'invalid value')
                                    st.error(f"Field '{field}': {msg}")
    
    else:
        st.success(f"Logged in as {st.session_state.user_type}")
        
        if st.button("Logout"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
        
        # Navigation for authenticated users
        st.subheader("Navigation")
        
        # Show different options based on user type
        if st.session_state.user_type == "candidate":
            st.page_link("streamlit_app.py", label="Dashboard", icon="🏠")
            st.page_link("pages/candidate_profile.py", label="Profile", icon="👤")
            st.page_link("pages/job_recommendations.py", label="Job Recommendations", icon="💼")
            st.page_link("pages/project_recommendations.py", label="Project Recommendations", icon="📋")
            st.page_link("pages/skill_gap.py", label="Skill Gap Analysis", icon="📊")
            st.page_link("pages/career_paths.py", label="Career Paths", icon="📈")
        else:  # employer
            st.page_link("streamlit_app.py", label="Dashboard", icon="🏠")
            st.page_link("pages/employer_profile.py", label="Company Profile", icon="🏢")
            st.page_link("pages/manage_jobs.py", label="Manage Jobs", icon="💼")
            st.page_link("pages/talent_search.py", label="Talent Search", icon="🔍")
            st.page_link("pages/candidate_recommendations.py", label="Candidate Recommendations", icon="👥")

# Main content area
if not st.session_state.authenticated:
    st.title("Welcome to Job Recommender API Tester")
    st.write("Please login or register to access the features.")
    
    st.markdown("""
    ## Features
    
    ### For Candidates:
    - Get personalized job and project recommendations
    - Analyze your skill gaps for target roles
    - Explore career path options
    - Receive learning recommendations
    
    ### For Employers:
    - Find qualified candidates for your job postings
    - Get salary recommendations for roles
    - Use advanced talent search with weighted criteria
    - Access recommendation performance analytics
    """)
    
else:
    # Dashboard for authenticated users
    if st.session_state.user_type == "candidate":
        st.title("Candidate Dashboard")
        
        # Profile summary
        profile = make_api_request("profile")
        if "error" in profile:
            st.error(f"Failed to load profile: {profile.get('error', 'Unknown error')}")
            if st.button("Retry Loading Profile"):
                st.rerun()
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Your Profile")
                st.write(f"**Name:** {profile.get('full_name', 'N/A')}")
                st.write(f"**Experience:** {profile.get('experience_years', 'N/A')} years")
                st.write(f"**Location:** {profile.get('location', 'N/A')}")
                
                skills = profile.get('skills', {})
                if skills:
                    languages_frameworks = skills.get('languages_frameworks', [])
                    if languages_frameworks:
                        st.write("**Skills:**")
                        st.write(", ".join(languages_frameworks))
                    else:
                        st.info("No skills added yet. Update your profile to add skills.")
                else:
                    st.info("No skills added yet. Update your profile to add skills.")
            
            with col2:
                st.subheader("Quick Actions")
                st.button("Update Profile", key="goto_profile")
                st.button("View Job Recommendations", key="goto_jobs")
                st.button("Check Skill Gap Analysis", key="goto_skills")
        
        # Job recommendation preview
        st.subheader("Latest Job Recommendations")
        job_recs = make_api_request("recommendations/jobs", params={"limit": 3})
        if "error" not in job_recs:
            # Handle both list and dictionary responses from the API
            if isinstance(job_recs, list):
                jobs = job_recs
            else:
                # Handle response as dictionary with 'items' field
                jobs = job_recs.get("items", [])
                
            if jobs:
                for idx, job in enumerate(jobs):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### {job.get('title', 'Job Title')}")
                            st.write(f"**Company:** {job.get('company', 'N/A')}")
                            st.write(f"**Location:** {job.get('location', 'N/A')}")
                            st.write(f"**Match Score:** {job.get('match_score', 'N/A')}%")
                        with col2:
                            # Use index as fallback when id is None
                            job_id = job.get('id')
                            button_key = f"view_job_{job_id if job_id is not None else f'idx_{idx}'}"
                            st.button("View Details", key=button_key)
                        st.divider()
            else:
                st.info("No job recommendations found. Update your profile to get personalized recommendations.")
                
        # Skill gap summary
        st.subheader("Skill Gap Summary")
        skill_gap = make_api_request("recommendations/skill-gap", params={"target_role": "Software Engineer"})
        if "error" not in skill_gap:
            missing_skills = skill_gap.get("missing_skills", [])
            if missing_skills:
                st.write("Top skills to develop:")
                for skill in missing_skills[:3]:
                    st.write(f"- {skill}")
            else:
                st.info("No skill gap analysis available.")
    
    else:  # employer
        st.title("Employer Dashboard")
        
        # Company profile summary
        profile = make_api_request("profile")
        if "error" not in profile:
            col1, col2 = st.columns(2)
            with col1:
                company_details = profile.get('company_details', {})
                st.subheader("Company Profile")
                st.write(f"**Company:** {company_details.get('company_name', 'N/A')}")
                st.write(f"**Industry:** {company_details.get('industry', 'N/A')}")
                st.write(f"**Size:** {company_details.get('company_size', 'N/A')}")
                st.write(f"**Location:** {company_details.get('company_location', 'N/A')}")
            
            with col2:
                st.subheader("Quick Actions")
                st.button("Update Company Profile", key="goto_company")
                st.button("Post a New Job", key="goto_new_job")
                st.button("Search Talent", key="goto_talent")
        
        # Recent job postings
        st.subheader("Your Recent Job Postings")
        jobs = make_api_request("jobs", params={"employer_id": "current", "limit": 3})
        if "error" not in jobs:
            # Handle both list and dictionary responses from the API
            if isinstance(jobs, list):
                job_list = jobs
            else:
                # Handle response as dictionary with 'items' field
                job_list = jobs.get("items", [])
                
            if job_list:
                for job in job_list:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"### {job.get('title', 'Job Title')}")
                            st.write(f"**Posted:** {job.get('created_at', 'N/A')}")
                            applications_count = job.get('applications_count', 0)
                            st.write(f"**Applications:** {applications_count}")
                        with col2:
                            st.button("View Candidates", key=f"candidates_{job.get('id')}")
                        with col3:
                            st.button("Edit Job", key=f"edit_job_{job.get('id')}")
                        st.divider()
            else:
                st.info("No job postings found. Create your first job posting to start receiving applications.")
        
        # Candidate recommendation preview
        st.subheader("Talent Matches")
        st.info("Post jobs to see candidate recommendations matched to your requirements.") 