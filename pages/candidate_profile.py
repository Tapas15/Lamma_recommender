import streamlit as st
import requests
import json
import pandas as pd
import re
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login to access this page")
    st.stop()

if st.session_state.user_type != "candidate":
    st.warning("This page is only available for candidates")
    st.stop()

# Initialize session state for profile data
if "profile_data" not in st.session_state:
    st.session_state.profile_data = None

# Helper function for validation
def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_url(url):
    """Validate URL format"""
    pattern = r"^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
    return bool(re.match(pattern, url)) if url else True

# Helper function
def make_api_request(endpoint, method="GET", data=None, params=None):
    """Make API request with proper headers and authentication"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.session_state.access_token}"
    }
    
    url = f"{API_BASE_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.content else {"message": "Success"}
        else:
            error_msg = response.json() if response.content else {"detail": "Unknown error"}
            return {"error": f"Status {response.status_code}", "detail": error_msg}
    except Exception as e:
        return {"error": str(e)}

# Function to fetch profile data
def fetch_profile_data():
    try:
        response = requests.get(
            "http://localhost:8000/profile",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch profile data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching profile data: {str(e)}")
        return None

# Fetch profile data if not in session state
if not st.session_state.profile_data:
    st.session_state.profile_data = fetch_profile_data()

# Get profile data from session state
profile_data = st.session_state.profile_data

# Page title and description
st.title("Candidate Profile")
st.write("Complete your profile to improve job recommendations and help employers find you.")

# Show error and retry button if profile data is None
if profile_data is None:
    st.error("Failed to load profile data. Please try again.")
    if st.button("Retry Loading Profile"):
        st.session_state.profile_data = fetch_profile_data()
        st.rerun()
    st.stop()

# Create tabs for different sections of the profile
tabs = st.tabs(["Basic Information", "Skills & Experience", "Education", "Job Preferences", "Settings"])

# Basic Information Tab
with tabs[0]:
    with st.form("basic_info_form"):
        st.subheader("Personal Information")
        
        # Get profile data safely
        profile_data = st.session_state.profile_data or {}
        
        # Required fields
        full_name = st.text_input(
            "Full Name*", 
            value=profile_data.get("full_name", ""),
            help="Your full professional name"
        )
        
        email = st.text_input(
            "Email*", 
            value=profile_data.get("email", ""), 
            disabled=True,
            help="Your email is your unique identifier and cannot be changed"
        )
        
        phone = st.text_input(
            "Phone Number",
            value=profile_data.get("phone", ""),
            help="Format: +1-123-456-7890"
        )
        
        location = st.text_input(
            "Location*", 
            value=profile_data.get("location", ""),
            help="City, State, Country"
        )
        
        # Convert experience_years to int if it's a string
        experience_value = profile_data.get("experience_years", "0")
        try:
            experience_value = int(experience_value) if isinstance(experience_value, str) else experience_value
        except (ValueError, TypeError):
            experience_value = 0
        
        experience_years = st.number_input(
            "Experience (Years)*", 
            min_value=0, 
            max_value=50, 
            value=experience_value,
            help="Total professional experience in years"
        )
        
        # Professional summary
        st.subheader("Professional Summary")
        
        bio = st.text_area(
            "Professional Bio*", 
            value=profile_data.get("bio", ""),
            help="A brief summary of your professional background (100-500 characters)",
            height=150
        )
        
        about = st.text_area(
            "About Me", 
            value=profile_data.get("about", ""),
            help="More detailed information about your professional journey",
            height=200
        )
        
        # Profile links
        st.subheader("Professional Links")
        
        # Get links safely
        links = profile_data.get("links") or {}
        
        linkedin = st.text_input(
            "LinkedIn URL", 
            value=links.get("linkedin", ""),
            help="Your LinkedIn profile URL"
        )
        
        github = st.text_input(
            "GitHub URL", 
            value=links.get("github", ""),
            help="Your GitHub profile URL"
        )
        
        portfolio = st.text_input(
            "Portfolio URL", 
            value=links.get("portfolio", ""),
            help="Your personal website or portfolio URL"
        )
        
        # Submit button
        basic_info_submit = st.form_submit_button("Update Basic Information")
    
    # Handle form submission
    if basic_info_submit:
        # Validation
        validation_errors = []
        
        if not full_name:
            validation_errors.append("Full Name is required")
        
        if not location:
            validation_errors.append("Location is required")
        
        if not bio:
            validation_errors.append("Professional Bio is required")
        elif len(bio) < 100:
            validation_errors.append("Professional Bio must be at least 100 characters")
        
        if linkedin and not validate_url(linkedin):
            validation_errors.append("LinkedIn URL is not valid")
        
        if github and not validate_url(github):
            validation_errors.append("GitHub URL is not valid")
        
        if portfolio and not validate_url(portfolio):
            validation_errors.append("Portfolio URL is not valid")
        
        if validation_errors:
            for error in validation_errors:
                st.error(error)
        else:
            # Build updated profile data
            updated_profile = {
                "full_name": full_name,
                "phone": phone,
                "location": location,
                "experience_years": experience_years,
                "bio": bio,
                "about": about,
                "links": {
                    "linkedin": linkedin,
                    "github": github,
                    "portfolio": portfolio
                }
            }
            
            # Send update request
            with st.spinner("Updating profile..."):
                result = make_api_request("profile", method="PUT", data=updated_profile)
            
            if "error" in result:
                st.error(f"Failed to update profile: {result.get('error')}")
                if "detail" in result:
                    st.json(result.get("detail"))
            else:
                st.success("Basic information updated successfully!")
                st.balloons()

# Skills & Experience Tab
with tabs[1]:
    st.subheader("Skills")
    
    with st.form("skills_form"):
        # Get skills safely
        skills = profile_data.get("skills") or {}
        
        # Technical skills section
        st.write("**Technical Skills**")
        
        languages_frameworks = skills.get("languages_frameworks") or []
        languages_frameworks_input = st.text_area(
            "Programming Languages & Frameworks*",
            value=", ".join(languages_frameworks),
            help="Separate with commas (e.g., Python, JavaScript, React)"
        )
        
        tools_platforms = skills.get("tools_platforms") or []
        tools_platforms_input = st.text_area(
            "Tools & Platforms",
            value=", ".join(tools_platforms),
            help="Separate with commas (e.g., Git, Docker, AWS, Jira)"
        )
        
        ai_ml_data = skills.get("ai_ml_data") or []
        ai_ml_input = st.text_area(
            "AI, ML & Data Skills",
            value=", ".join(ai_ml_data),
            help="Separate with commas (e.g., TensorFlow, PyTorch, SQL, Pandas)"
        )
        
        # Soft skills section
        st.write("**Soft Skills**")
        
        soft_skills = skills.get("soft_skills") or []
        soft_skills_input = st.text_area(
            "Soft Skills",
            value=", ".join(soft_skills),
            help="Separate with commas (e.g., Communication, Leadership, Problem-solving)"
        )
        
        # Submit button
        skills_submit = st.form_submit_button("Update Skills")

# Education & Certifications Tab
with tabs[2]:
    st.subheader("Education")
    
    with st.form("education_form"):
        # Get education data safely
        education_data = profile_data.get("education") or []
        
        # Education summary
        education_summary = st.text_area(
            "Education Summary*",
            value=profile_data.get("education_summary", ""),
            help="Brief overview of your educational background",
            height=100
        )
        
        # Detailed education entries
        st.write("**Education History**")
        education_entries = []
        
        # Display existing education entries and allow editing
        for i, edu in enumerate(education_data):
            st.write(f"Education Entry #{i+1}")
            
            # Get education entry safely
            edu = edu or {}
            
            degree = st.text_input(
                "Degree/Certificate*", 
                value=edu.get("degree", ""),
                key=f"degree_{i}"
            )
            
            institution = st.text_input(
                "Institution*", 
                value=edu.get("institution", ""),
                key=f"institution_{i}"
            )
            
            field = st.text_input(
                "Field of Study*", 
                value=edu.get("field", ""),
                key=f"field_{i}"
            )
            
            # Handle date safely
            try:
                start_date = datetime.strptime(edu.get("start_date", "2000-01-01"), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                start_date = datetime.strptime("2000-01-01", "%Y-%m-%d").date()
                
            try:
                end_date = datetime.strptime(edu.get("end_date", "2000-01-01"), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                end_date = datetime.strptime("2000-01-01", "%Y-%m-%d").date()
            
            start_date_input = st.date_input(
                "Start Date*",
                value=start_date,
                key=f"start_date_{i}"
            )
            
            end_date_input = st.date_input(
                "End Date*",
                value=end_date,
                key=f"end_date_{i}"
            )
            
            gpa = st.text_input(
                "GPA", 
                value=edu.get("gpa", ""),
                key=f"gpa_{i}"
            )
            
            education_entries.append({
                "degree": degree,
                "institution": institution,
                "field": field,
                "start_date": start_date_input.strftime("%Y-%m-%d"),
                "end_date": end_date_input.strftime("%Y-%m-%d"),
                "gpa": gpa
            })
        
        # Certifications section
        st.subheader("Certifications")
        certifications = profile_data.get("certifications") or []
        cert_entries = []
        
        for i, cert in enumerate(certifications):
            st.write(f"Certification #{i+1}")
            
            # Get certification safely
            cert = cert or {}
            
            name = st.text_input(
                "Certification Name*", 
                value=cert.get("name", ""),
                key=f"cert_name_{i}"
            )
            
            issuer = st.text_input(
                "Issuing Organization*", 
                value=cert.get("issuer", ""),
                key=f"cert_issuer_{i}"
            )
            
            # Handle dates safely
            try:
                issue_date = datetime.strptime(cert.get("issue_date", "2000-01-01"), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                issue_date = datetime.strptime("2000-01-01", "%Y-%m-%d").date()
                
            try:
                expiry_date = datetime.strptime(cert.get("expiry_date", "2000-01-01"), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                expiry_date = datetime.strptime("2000-01-01", "%Y-%m-%d").date()
            
            issue_date_input = st.date_input(
                "Issue Date*",
                value=issue_date,
                key=f"cert_date_{i}"
            )
            
            expiry_date_input = st.date_input(
                "Expiry Date (if applicable)",
                value=expiry_date,
                key=f"cert_expiry_{i}"
            )
            
            credential_id = st.text_input(
                "Credential ID", 
                value=cert.get("credential_id", ""),
                key=f"cert_id_{i}"
            )
            
            cert_url = st.text_input(
                "Credential URL", 
                value=cert.get("url", ""),
                key=f"cert_url_{i}"
            )
            
            cert_entries.append({
                "name": name,
                "issuer": issuer,
                "issue_date": issue_date_input.strftime("%Y-%m-%d"),
                "expiry_date": expiry_date_input.strftime("%Y-%m-%d"),
                "credential_id": credential_id,
                "url": cert_url
            })
        
        education_submit = st.form_submit_button("Update Education & Certifications")

# Job Preferences Tab
with tabs[3]:
    st.subheader("Job Preferences")
    
    with st.form("preferences_form"):
        # Get preferences safely
        preferences = profile_data.get("job_preferences") or {}
        
        # Job types
        job_types = preferences.get("job_types") or []
        job_types_options = st.multiselect(
            "Preferred Job Types*",
            options=["Full-time", "Part-time", "Contract", "Remote", "Hybrid", "On-site"],
            default=job_types,
            help="Select all that apply"
        )
        
        # Work locations
        locations = preferences.get("locations") or []
        locations_input = st.text_area(
            "Preferred Work Locations*",
            value=", ".join(locations),
            help="Separate with commas (e.g., New York, London, Remote)"
        )
        
        # Industries
        industries = preferences.get("industries") or []
        industries_input = st.text_area(
            "Preferred Industries",
            value=", ".join(industries),
            help="Separate with commas (e.g., Technology, Finance, Healthcare)"
        )
        
        # Salary expectations
        salary_range = preferences.get("salary_range") or {}
        col1, col2 = st.columns(2)
        with col1:
            min_salary = st.number_input(
                "Minimum Expected Salary (USD)",
                min_value=0,
                value=int(salary_range.get("min", 0))
            )
        with col2:
            max_salary = st.number_input(
                "Maximum Expected Salary (USD)",
                min_value=0,
                value=int(salary_range.get("max", 0))
            )
        
        # Notice period
        notice_period = st.number_input(
            "Notice Period (days)",
            min_value=0,
            value=preferences.get("notice_period", 0),
            help="Number of days needed before starting a new position"
        )
        
        # Relocation preference
        willing_to_relocate = st.checkbox(
            "Willing to Relocate",
            value=preferences.get("willing_to_relocate", False),
            help="Are you open to relocating for the right opportunity?"
        )
        
        # Travel preference
        travel_preference = st.slider(
            "Travel Preference (%)",
            min_value=0,
            max_value=100,
            value=preferences.get("travel_percentage", 0),
            help="What percentage of travel are you comfortable with?"
        )
        
        preferences_submit = st.form_submit_button("Update Job Preferences")

# Handle form submissions
if "basic_info_submit" in locals() and basic_info_submit:
    # Prepare basic info data
    basic_data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "location": location,
        "experience_years": str(experience_years),
        "bio": bio,
        "about": about,
        "links": {
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio
        }
    }
    
    try:
        response = requests.patch(
            "http://localhost:8000/profile",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            json=basic_data
        )
        if response.status_code == 200:
            st.success("Basic information updated successfully!")
            st.session_state.profile_data = None  # Force refresh
            st.rerun()
        else:
            st.error(f"Failed to update basic information: {response.status_code}")
    except Exception as e:
        st.error(f"Error updating basic information: {str(e)}")

# Handle skills form submission
if "skills_submit" in locals() and skills_submit:
    # Process skills data
    skills_data = {
        "skills": {
            "languages_frameworks": [s.strip() for s in languages_frameworks_input.split(",") if s.strip()],
            "tools_platforms": [s.strip() for s in tools_platforms_input.split(",") if s.strip()],
            "ai_ml_data": [s.strip() for s in ai_ml_input.split(",") if s.strip()],
            "soft_skills": [s.strip() for s in soft_skills_input.split(",") if s.strip()]
        }
    }
    
    try:
        response = requests.patch(
            "http://localhost:8000/profile",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            json=skills_data
        )
        if response.status_code == 200:
            st.success("Skills updated successfully!")
            st.session_state.profile_data = None  # Force refresh
            st.rerun()
        else:
            st.error(f"Failed to update skills: {response.status_code}")
    except Exception as e:
        st.error(f"Error updating skills: {str(e)}")

# Handle education form submission
if "education_submit" in locals() and education_submit:
    education_data = {
        "education_summary": education_summary,
        "education": education_entries,
        "certifications": cert_entries
    }
    
    try:
        response = requests.patch(
            "http://localhost:8000/profile",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            json=education_data
        )
        if response.status_code == 200:
            st.success("Education and certifications updated successfully!")
            st.session_state.profile_data = None  # Force refresh
            st.rerun()
        else:
            st.error(f"Failed to update education: {response.status_code}")
    except Exception as e:
        st.error(f"Error updating education: {str(e)}")

# Handle preferences form submission
if "preferences_submit" in locals() and preferences_submit:
    preferences_data = {
        "job_preferences": {
            "job_types": job_types_options,
            "locations": [loc.strip() for loc in locations_input.split(",") if loc.strip()],
            "industries": [ind.strip() for ind in industries_input.split(",") if ind.strip()],
            "salary_range": {
                "min": min_salary,
                "max": max_salary
            },
            "notice_period": notice_period,
            "willing_to_relocate": willing_to_relocate,
            "travel_percentage": travel_preference
        }
    }
    
    try:
        response = requests.patch(
            "http://localhost:8000/profile",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            json=preferences_data
        )
        if response.status_code == 200:
            st.success("Job preferences updated successfully!")
            st.session_state.profile_data = None  # Force refresh
            st.rerun()
        else:
            st.error(f"Failed to update preferences: {response.status_code}")
    except Exception as e:
        st.error(f"Error updating preferences: {str(e)}") 