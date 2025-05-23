import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8000"

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login to access this page")
    st.stop()

if st.session_state.user_type != "employer":
    st.warning("This page is only available for employers")
    st.stop()

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

# Initialize session state for job editing
if "editing_job" not in st.session_state:
    st.session_state.editing_job = False
if "job_to_edit" not in st.session_state:
    st.session_state.job_to_edit = None
if "show_create_job" not in st.session_state:
    st.session_state.show_create_job = False

# Page title
st.title("Manage Job Postings")

# Sidebar for filters
with st.sidebar:
    st.header("Job Filters")
    
    # Status filter
    status_filter = st.multiselect(
        "Status",
        options=["Active", "Draft", "Closed", "Archived"],
        default=["Active"]
    )
    
    # Date filter
    date_filter = st.selectbox(
        "Posted Date",
        options=["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
    )
    
    # Location filter
    location_filter = st.text_input("Location")
    
    # Apply filters button
    apply_filters = st.button("Apply Filters")
    
    # Create new job button
    if st.button("Create New Job"):
        st.session_state.show_create_job = True
        st.session_state.editing_job = False
        st.session_state.job_to_edit = None

# Function to reset job editing state
def reset_job_editing():
    st.session_state.editing_job = False
    st.session_state.job_to_edit = None
    st.session_state.show_create_job = False

# Function to handle job editing
def edit_job(job_id):
    st.session_state.editing_job = True
    st.session_state.job_to_edit = job_id
    st.session_state.show_create_job = False

# Function to display job posting form
def show_job_form(job_data=None, is_edit=False):
    # Default values for form fields
    defaults = {
        "title": "",
        "description": "",
        "location": "",
        "job_type": "Full-time",
        "experience_level": "Entry-level",
        "salary_min": 0,
        "salary_max": 0,
        "salary_currency": "USD",
        "remote_option": False,
        "department": "",
        "required_skills": [],
        "preferred_skills": [],
        "education_requirement": "",
        "application_deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "status": "Draft"
    }
    
    # Use provided job data if available
    if job_data:
        for key in defaults:
            if key in job_data:
                defaults[key] = job_data[key]
        
        # Handle special cases
        if "salary_range" in job_data:
            salary_range = job_data["salary_range"]
            defaults["salary_min"] = salary_range.get("min", 0)
            defaults["salary_max"] = salary_range.get("max", 0)
            defaults["salary_currency"] = salary_range.get("currency", "USD")
        
        if "skills" in job_data:
            skills = job_data["skills"]
            defaults["required_skills"] = skills.get("required", [])
            defaults["preferred_skills"] = skills.get("preferred", [])
    
    # Create the job posting form
    with st.form("job_posting_form"):
        st.subheader("Job Details")
        
        # Basic job information
        title = st.text_input("Job Title", value=defaults["title"])
        
        col1, col2 = st.columns(2)
        with col1:
            job_type = st.selectbox(
                "Job Type",
                options=["Full-time", "Part-time", "Contract", "Internship", "Temporary"],
                index=["Full-time", "Part-time", "Contract", "Internship", "Temporary"].index(defaults["job_type"])
            )
            
            experience_level = st.selectbox(
                "Experience Level",
                options=["Entry-level", "Mid-level", "Senior", "Manager", "Executive"],
                index=["Entry-level", "Mid-level", "Senior", "Manager", "Executive"].index(defaults["experience_level"])
            )
        
        with col2:
            location = st.text_input("Location", value=defaults["location"])
            remote_option = st.checkbox("Remote Option", value=defaults["remote_option"])
            department = st.text_input("Department", value=defaults["department"])
        
        # Salary information
        st.subheader("Salary Information")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            salary_min = st.number_input("Minimum Salary", value=defaults["salary_min"])
        with col2:
            salary_max = st.number_input("Maximum Salary", value=defaults["salary_max"])
        with col3:
            salary_currency = st.selectbox(
                "Currency",
                options=["USD", "EUR", "GBP", "CAD", "AUD", "INR"],
                index=["USD", "EUR", "GBP", "CAD", "AUD", "INR"].index(defaults["salary_currency"])
            )
        
        # Job description
        st.subheader("Job Description")
        description = st.text_area("Description", value=defaults["description"], height=200)
        
        # Skills requirements
        st.subheader("Skills")
        required_skills = st.text_area(
            "Required Skills (comma separated)",
            value=", ".join(defaults["required_skills"])
        )
        
        preferred_skills = st.text_area(
            "Preferred Skills (comma separated)",
            value=", ".join(defaults["preferred_skills"])
        )
        
        # Additional requirements
        st.subheader("Additional Requirements")
        education_requirement = st.text_input("Education", value=defaults["education_requirement"])
        application_deadline = st.date_input("Application Deadline", value=datetime.strptime(defaults["application_deadline"], "%Y-%m-%d"))
        
        # Job status
        status = st.selectbox(
            "Job Status",
            options=["Draft", "Active", "Closed", "Archived"],
            index=["Draft", "Active", "Closed", "Archived"].index(defaults["status"])
        )
        
        # Submit buttons
        if is_edit:
            submit_label = "Update Job"
            cancel_button = st.form_submit_button("Cancel")
            if cancel_button:
                reset_job_editing()
                st.rerun()
        else:
            submit_label = "Create Job"
        
        submit_button = st.form_submit_button(submit_label)
    
    # Handle form submission
    if submit_button:
        # Parse comma-separated text fields into lists
        required_skills_list = [s.strip() for s in required_skills.split(",") if s.strip()]
        preferred_skills_list = [s.strip() for s in preferred_skills.split(",") if s.strip()]
        
        # Build job data
        job_post_data = {
            "title": title,
            "description": description,
            "location": location,
            "job_type": job_type,
            "experience_level": experience_level,
            "remote_option": remote_option,
            "department": department,
            "salary_range": {
                "min": salary_min,
                "max": salary_max,
                "currency": salary_currency
            },
            "skills": {
                "required": required_skills_list,
                "preferred": preferred_skills_list
            },
            "education_requirement": education_requirement,
            "application_deadline": application_deadline.strftime("%Y-%m-%d"),
            "status": status
        }
        
        # Send request to API
        if is_edit:
            endpoint = f"jobs/{st.session_state.job_to_edit}"
            result = make_api_request(endpoint, method="PUT", data=job_post_data)
            success_message = "Job posting updated successfully!"
        else:
            result = make_api_request("jobs", method="POST", data=job_post_data)
            success_message = "Job posting created successfully!"
        
        if "error" in result:
            st.error(f"Failed to save job posting: {result.get('error')}")
            if "detail" in result:
                st.json(result.get("detail"))
        else:
            st.success(success_message)
            reset_job_editing()
            st.rerun()

# Main content area
if st.session_state.editing_job and st.session_state.job_to_edit:
    # Fetch job details
    job_details = make_api_request(f"jobs/{st.session_state.job_to_edit}")
    if "error" in job_details:
        st.error(f"Failed to load job details: {job_details.get('error')}")
        reset_job_editing()
    else:
        st.subheader(f"Edit Job: {job_details.get('title', 'Job')}")
        show_job_form(job_details, is_edit=True)
elif st.session_state.show_create_job:
    st.subheader("Create New Job")
    show_job_form(is_edit=False)
else:
    # Job posting management interface
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("Your Job Postings")
    with col2:
        sort_by = st.selectbox("Sort By", ["Date (Newest)", "Date (Oldest)", "Status", "Applications"])
    with col3:
        items_per_page = st.selectbox("Show", [10, 25, 50, 100])
    
    # Define API parameters
    params = {
        "employer_id": "current",
        "limit": items_per_page
    }
    
    # Add filter parameters
    if apply_filters:
        if status_filter:
            params["status"] = json.dumps(status_filter)
        if date_filter != "All Time":
            days = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
            params["days"] = days.get(date_filter, 0)
        if location_filter:
            params["location"] = location_filter
    
    # Fetch job postings
    with st.spinner("Loading job postings..."):
        job_postings = make_api_request("jobs", params=params)
    
    if "error" in job_postings:
        st.error(f"Failed to load job postings: {job_postings.get('error')}")
    else:
        # Handle both list and dictionary responses
        if isinstance(job_postings, list):
            jobs = job_postings
            total_jobs = len(jobs)
        else:
            jobs = job_postings.get("items", [])
            total_jobs = job_postings.get("total_count", 0)
        
        # Display summary
        st.write(f"Showing {len(jobs)} of {total_jobs} job postings")
        
        if not jobs:
            st.info("No job postings found. Create your first job posting to start receiving applications!")
        else:
            # Create a table of job postings
            for job in jobs:
                with st.container():
                    cols = st.columns([3, 1, 1, 1])
                    with cols[0]:
                        st.subheader(job.get("title", "Job Title"))
                        status_color = {
                            "Active": "green",
                            "Draft": "gray",
                            "Closed": "orange",
                            "Archived": "red"
                        }.get(job.get("status", "Draft"), "gray")
                        st.markdown(f"**Status:** :{status_color}[{job.get('status', 'Draft')}]")
                        st.markdown(f"**Location:** {job.get('location', 'N/A')}")
                        st.markdown(f"**Posted:** {job.get('created_at', 'N/A')}")
                    
                    with cols[1]:
                        # Show statistics
                        views = job.get("views_count", 0)
                        applications = job.get("applications_count", 0)
                        st.metric("Views", views)
                        st.metric("Applications", applications)
                    
                    with cols[2]:
                        # Action buttons
                        st.button("Edit", key=f"edit_{job.get('id')}", on_click=edit_job, args=(job.get('id'),))
                        st.button("View Applications", key=f"view_apps_{job.get('id')}")
                    
                    with cols[3]:
                        # More actions
                        status = job.get("status", "Draft")
                        
                        if status == "Draft":
                            st.button("Publish", key=f"publish_{job.get('id')}")
                        elif status == "Active":
                            st.button("Close", key=f"close_{job.get('id')}")
                        
                        st.button("Duplicate", key=f"duplicate_{job.get('id')}")
                    
                    st.divider()
            
            # Pagination
            if total_jobs > items_per_page:
                page_count = (total_jobs + items_per_page - 1) // items_per_page
                cols = st.columns([1, 3, 1])
                with cols[1]:
                    st.markdown("### Pages")
                    page_nums = list(range(1, page_count + 1))
                    selected_page = st.select_slider("", options=page_nums, value=1)
    
    # Job posting insights
    st.subheader("Job Posting Insights")
    with st.expander("View Performance Metrics"):
        st.write("Insights to optimize your job postings and attract more qualified candidates.")
        
        # Mock metrics display
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Views", "156", "+14%")
        with col2:
            st.metric("Conversion Rate", "4.2%", "-0.8%")
        with col3:
            st.metric("Average Time to Fill", "18 days", "+2 days")
        
        st.info("""
        💡 **Tips to improve performance:**
        
        - Include clear job responsibilities and qualifications
        - Specify salary range to attract more candidates
        - Add comprehensive details about required skills
        - Highlight company culture and benefits
        """)

# Quick actions floating menu
with st.sidebar:
    st.subheader("Quick Actions")
    st.markdown("---")
    st.button("Export Job Listings")
    st.button("Import from Template")
    st.button("Job Analytics Dashboard")
    st.markdown("---")
    st.info("Need help with your job postings? Contact support for assistance.") 