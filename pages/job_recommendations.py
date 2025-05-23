import streamlit as st
import requests
import json
import pandas as pd
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

# Initialize session state for filters
if "job_filters" not in st.session_state:
    st.session_state.job_filters = {
        "job_types": [],
        "industries": [],
        "location": "",
        "experience_level": [],
        "min_match_score": 50
    }

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
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.content else {"message": "Success"}
        else:
            error_msg = response.json() if response.content else {"detail": "Unknown error"}
            return {"error": f"Status {response.status_code}", "detail": error_msg}
    except Exception as e:
        return {"error": str(e)}

def validate_application(cover_letter, resume):
    """Validate job application inputs"""
    if not cover_letter.strip():
        return False, "Cover letter is required"
    if len(cover_letter.strip()) < 100:
        return False, "Cover letter should be at least 100 characters"
    if resume is None:
        return False, "Resume is required"
    if resume.size > 5 * 1024 * 1024:  # 5MB limit
        return False, "Resume file size should be less than 5MB"
    allowed_types = ['.pdf', '.doc', '.docx']
    if not any(resume.name.lower().endswith(ext) for ext in allowed_types):
        return False, "Resume must be in PDF, DOC, or DOCX format"
    return True, ""

# Page title
st.title("Job Recommendations")

# Filters sidebar
with st.sidebar:
    st.header("Filter Recommendations")
    
    with st.form("filter_form"):
        # Job type filter
        job_types = st.multiselect(
            "Job Types",
            options=["Full-time", "Part-time", "Contract", "Remote", "Hybrid"],
            default=st.session_state.job_filters["job_types"],
            help="Select one or more job types"
        )
        
        # Industry filter
        industries = st.multiselect(
            "Industries",
            options=["Technology", "Finance", "Healthcare", "Education", "E-commerce", 
                    "Manufacturing", "Retail", "Media", "Consulting", "Other"],
            default=st.session_state.job_filters["industries"],
            help="Select one or more industries"
        )
        
        # Location filter
        location = st.text_input(
            "Location",
            value=st.session_state.job_filters["location"],
            help="Enter city, state, or country (optional)"
        )
        
        # Experience level filter
        experience_level = st.multiselect(
            "Experience Level",
            options=["Entry-level", "Mid-level", "Senior", "Manager", "Executive"],
            default=st.session_state.job_filters["experience_level"],
            help="Select one or more experience levels"
        )
        
        # Minimum match score
        min_match_score = st.slider(
            "Minimum Match Score (%)",
            min_value=0,
            max_value=100,
            value=st.session_state.job_filters["min_match_score"],
            help="Only show jobs with match scores above this threshold"
        )
        
        # Apply filters button
        filter_button = st.form_submit_button("Apply Filters")
        
    # Reset filters button outside form
    if st.button("Reset Filters"):
        st.session_state.job_filters = {
            "job_types": [],
            "industries": [],
            "location": "",
            "experience_level": [],
            "min_match_score": 50
        }
        st.rerun()

# Update session state if filters are applied
if filter_button:
    st.session_state.job_filters = {
        "job_types": job_types,
        "industries": industries,
        "location": location,
        "experience_level": experience_level,
        "min_match_score": min_match_score
    }

# Job recommendation settings
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Personalized Job Recommendations")
    st.write("Jobs that match your skills, experience, and preferences.")
with col2:
    recommendation_count = st.selectbox(
        "Show",
        [10, 20, 50, 100],
        index=0,
        help="Number of recommendations to display per page"
    )

# Define params for API request based on filters
params = {"limit": recommendation_count}

# Add active filters to params
filters = st.session_state.job_filters
if filters["job_types"]:
    params["job_types"] = json.dumps(filters["job_types"])
if filters["industries"]:
    params["industries"] = json.dumps(filters["industries"])
if filters["location"]:
    params["location"] = filters["location"].strip()
if filters["experience_level"]:
    params["experience_level"] = json.dumps(filters["experience_level"])
if filters["min_match_score"]:
    params["min_match_score"] = filters["min_match_score"]

# Get job recommendations
with st.spinner("Loading job recommendations..."):
    try:
        job_recs = make_api_request("recommendations/jobs", params=params)

        if "error" in job_recs:
            st.error(f"Failed to load job recommendations: {job_recs.get('error')}")
            if st.button("Retry"):
                st.rerun()
        else:
            # Handle both list and dictionary responses from the API
            if isinstance(job_recs, list):
                jobs = job_recs
                total_count = len(jobs)
            else:
                jobs = job_recs.get("items", [])
                total_count = job_recs.get("total_count", 0)
            
            # Show recommendation stats
            st.write(f"Found {total_count} matching job recommendations")
            
            if not jobs:
                st.info("""
                No job recommendations found with the current filters. Try:
                - Lowering the minimum match score
                - Removing some filters
                - Updating your profile with more skills
                """)
            
            # Display job recommendations
            for idx, job in enumerate(jobs):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {job.get('title', 'Untitled Position')}")
                        st.write(f"**Company:** {job.get('company', 'N/A')}")
                        st.write(f"**Location:** {job.get('location', 'N/A')}")
                        st.write(f"**Match Score:** {job.get('match_score', 'N/A')}%")
                        
                        # Display skills match
                        skills_match = job.get('skills_match', [])
                        if skills_match:
                            st.write("**Matching Skills:**")
                            st.write(", ".join(skills_match))
                        
                        # Display description preview
                        description = job.get('description', '')
                        if description:
                            st.write("**Description Preview:**")
                            preview = description[:200] + "..." if len(description) > 200 else description
                            st.write(preview)
                    
                    with col2:
                        # Use index as fallback for unique keys
                        job_id = job.get('id')
                        view_key = f"view_{job_id if job_id is not None else f'idx_{idx}'}"
                        apply_key = f"apply_{job_id if job_id is not None else f'idx_{idx}'}"
                        save_key = f"save_{job_id if job_id is not None else f'idx_{idx}'}"
                        
                        st.button("View Details", key=view_key)
                        st.button("Apply Now", key=apply_key)
                        st.button("Save Job", key=save_key)
                    
                    # Add metrics if available
                    if job.get('salary_range'):
                        salary = job['salary_range']
                        st.write(f"**Salary Range:** ${salary.get('min', 'N/A')} - ${salary.get('max', 'N/A')}")
                    
                    if job.get('required_experience'):
                        st.write(f"**Required Experience:** {job['required_experience']} years")
                    
                    st.divider()

            # Pagination with validation
            if total_count > recommendation_count:
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    page_count = (total_count + recommendation_count - 1) // recommendation_count
                    current_page = st.session_state.get("current_page", 1)
                    pages = st.select_slider(
                        "Page",
                        options=list(range(1, page_count + 1)),
                        value=current_page,
                        help=f"Page {current_page} of {page_count}"
                    )
                    if pages != current_page:
                        st.session_state.current_page = pages
                        st.rerun()

    except Exception as e:
        st.error(f"An error occurred while loading recommendations: {str(e)}")
        if st.button("Retry"):
            st.rerun()

# Job application modal with validation
if "show_application_modal" in st.session_state and st.session_state.show_application_modal:
    with st.form("application_form"):
        st.subheader("Apply for Job")
        
        cover_letter = st.text_area(
            "Cover Letter",
            height=200,
            help="Write a personalized cover letter (minimum 100 characters)"
        )
        
        resume = st.file_uploader(
            "Resume",
            type=['pdf', 'doc', 'docx'],
            help="Upload your resume (PDF, DOC, or DOCX, max 5MB)"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Submit Application")
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_application_modal = False
                st.rerun()
        
        if submit:
            is_valid, error_msg = validate_application(cover_letter, resume)
            if not is_valid:
                st.error(error_msg)
            else:
                try:
                    # Add API call to submit application
                    st.success("Application submitted successfully!")
                    st.session_state.show_application_modal = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to submit application: {str(e)}") 