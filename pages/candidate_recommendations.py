import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.content else {"message": "Success"}
        else:
            error_msg = response.json() if response.content else {"detail": "Unknown error"}
            return {"error": f"Status {response.status_code}", "detail": error_msg}
    except Exception as e:
        return {"error": str(e)}

# Helper function for validation
def validate_weights(skills_w, exp_w, edu_w, loc_w):
    """Validate that weights sum to 1.0 and are valid"""
    weights = [skills_w, exp_w, edu_w, loc_w]
    if not all(0 <= w <= 1 for w in weights):
        return False, "All weights must be between 0 and 1"
    total = sum(weights)
    if not 0.99 <= total <= 1.01:  # Allow small floating point differences
        return False, f"Weights must sum to 1.0 (current sum: {total:.2f})"
    return True, ""

# Page title
st.title("Candidate Recommendations")

# Explanation
st.write("""
Our advanced AI matching system analyzes candidate profiles and recommends the best 
matches for your job postings based on skills, experience, and preferences.
""")

# Initialize session state variables
if "selected_job" not in st.session_state:
    st.session_state.selected_job = None
if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = None
if "recommendation_threshold" not in st.session_state:
    st.session_state.recommendation_threshold = 70  # Default minimum match score

# Add form validation state to session
if "form_validation_error" not in st.session_state:
    st.session_state.form_validation_error = None

# Get employer's active job postings for the dropdown
with st.spinner("Loading job postings..."):
    jobs_response = make_api_request("jobs", params={"employer_id": "current", "status": "Active"})

    if "error" in jobs_response:
        st.error(f"Failed to load job postings: {jobs_response.get('error')}")
        st.stop()

    # Extract jobs from the response
    if isinstance(jobs_response, list):
        jobs = jobs_response
    else:
        jobs = jobs_response.get("items", [])

if not jobs:
    st.warning("You don't have any active job postings. Create a job posting to get candidate recommendations.")
    
    # Show a button to create a new job posting
    if st.button("Create Job Posting"):
        # Redirect logic would go here
        st.info("Redirecting to job creation page...")
    
    st.stop()

# Create a job selector dropdown
job_options = {f"{job.get('title')} ({job.get('id')})": job.get('id') for job in jobs}
selected_job_title = st.selectbox(
    "Select a job posting to view candidate recommendations:",
    options=list(job_options.keys())
)

# Set the selected job ID
selected_job_id = job_options[selected_job_title]
st.session_state.selected_job = selected_job_id

# Get selected job details
selected_job = next((job for job in jobs if job.get('id') == selected_job_id), None)

# Create two columns layout
col1, col2 = st.columns([1, 3])

with col1:
    # Display selected job details
    st.subheader("Job Details")
    if selected_job:
        st.write(f"**Title:** {selected_job.get('title', 'N/A')}")
        st.write(f"**Location:** {selected_job.get('location', 'N/A')}")
        st.write(f"**Type:** {selected_job.get('job_type', 'N/A')}")
        st.write(f"**Experience:** {selected_job.get('experience_level', 'N/A')}")
        
        # Display skills required
        if "skills" in selected_job:
            skills = selected_job["skills"]
            
            st.write("**Required Skills:**")
            for skill in skills.get("required", []):
                st.markdown(f"- {skill}")
            
            if skills.get("preferred", []):
                st.write("**Preferred Skills:**")
                for skill in skills.get("preferred", []):
                    st.markdown(f"- {skill}")
    
    # Add a divider
    st.divider()
    
    # Recommendation settings
    st.subheader("Recommendation Settings")
    
    # Minimum match score threshold
    min_match_score = st.slider(
        "Minimum Match Score",
        min_value=0,
        max_value=100,
        value=st.session_state.recommendation_threshold,
        step=5
    )
    st.session_state.recommendation_threshold = min_match_score
    
    # Recommendation preferences
    st.subheader("Match Preferences")
    
    with st.form("match_preferences"):
        # These would typically be loaded from the employer's profile
        skills_weight = st.slider("Skills Weight", 0.0, 1.0, 0.4, 0.05,
                                help="Weight given to skills match in the overall score")
        experience_weight = st.slider("Experience Weight", 0.0, 1.0, 0.3, 0.05,
                                    help="Weight given to experience match in the overall score")
        education_weight = st.slider("Education Weight", 0.0, 1.0, 0.2, 0.05,
                                   help="Weight given to education match in the overall score")
        location_weight = st.slider("Location Weight", 0.0, 1.0, 0.1, 0.05,
                                  help="Weight given to location match in the overall score")
        
        # Add a note about weights
        st.info("Note: The sum of all weights must equal 1.0")
        
        # Show current sum of weights
        total_weight = skills_weight + experience_weight + education_weight + location_weight
        st.write(f"Current total weight: {total_weight:.2f}")
        
        # Apply settings button
        submit_settings = st.form_submit_button("Apply Settings")
        
        if submit_settings:
            # Validate weights
            is_valid, error_msg = validate_weights(
                skills_weight, experience_weight, 
                education_weight, location_weight
            )
            
            if not is_valid:
                st.error(error_msg)
                st.session_state.form_validation_error = error_msg
            else:
                st.session_state.form_validation_error = None
                # Store the weights for the API call
                st.session_state.weights = {
                    "skills": skills_weight,
                    "experience": experience_weight,
                    "education": education_weight,
                    "location": location_weight
                }
                st.success("Settings applied successfully!")

    # Talent pool insights
    st.subheader("Talent Insights")
    
    # This would typically be retrieved from the API
    with st.expander("View Talent Pool Stats"):
        # Mock data for talent pool insights
        st.metric("Total Candidates", "487")
        st.metric("Above 80% Match", "32")
        st.metric("Above 60% Match", "124")
        
        # Create a simple histogram of match scores
        match_data = {
            "Range": ["90-100%", "80-89%", "70-79%", "60-69%", "50-59%", "< 50%"],
            "Count": [8, 24, 47, 45, 62, 301]
        }
        match_df = pd.DataFrame(match_data)
        
        fig = px.bar(
            match_df,
            x="Range",
            y="Count",
            title="Candidate Match Score Distribution",
            color="Count",
            color_continuous_scale="greens"
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Get candidate recommendations
with col2:
    # Initialize search parameters
    params = {
        "job_id": selected_job_id,
        "min_match_score": min_match_score
    }
    
    # Add weights if settings were applied and valid
    if hasattr(st.session_state, 'weights') and not st.session_state.form_validation_error:
        params["weights"] = st.session_state.weights
    
    # Get candidate recommendations
    with st.spinner("Finding the best candidates for your job..."):
        try:
            recommendations = make_api_request("candidates/recommendations", params=params)
            
            if "error" in recommendations:
                st.error(f"Failed to load recommendations: {recommendations.get('error')}")
                if st.button("Retry Search"):
                    st.rerun()
            else:
                st.session_state.search_results = recommendations
                st.success(f"Found {len(recommendations.get('candidates', []))} matching candidates")
        except Exception as e:
            st.error(f"An error occurred while searching: {str(e)}")
            if st.button("Retry Search"):
                st.rerun()

    # Display results
    if st.session_state.selected_candidate:
        # Back button
        if st.button("Back to Results"):
            st.session_state.selected_candidate = None

# Add a sidebar with additional actions and information
with st.sidebar:
    st.subheader("Quick Actions")
    
    # Recommendation settings
    with st.expander("Recommendation Settings", expanded=False):
        st.write("Adjust how candidates are matched to your jobs")
        
        # These would typically be saved to the employer's profile
        auto_contact = st.toggle("Auto-contact candidates above 90% match", value=False)
        daily_digest = st.toggle("Receive daily recommendation digests", value=True)
        
        if st.button("Save Preferences"):
            st.success("Preferences saved successfully!")
    
    # Export options
    st.subheader("Export Options")
    export_format = st.selectbox("Export Format", ["CSV", "Excel", "PDF"])
    
    if st.button("Export Recommendations"):
        st.success(f"Recommendations exported as {export_format}")
    
    # Help and resources
    st.subheader("Resources")
    st.markdown("[Matching Algorithm Explanation](https://example.com)")
    st.markdown("[Best Practices for Hiring](https://example.com)")
    st.markdown("[Candidate Engagement Guide](https://example.com)")
    
    # Recommendation quality feedback with validation
    st.subheader("Feedback")
    with st.form("feedback_form"):
        recommendation_quality = st.slider(
            "Recommendation Quality", 
            1, 5, 4,
            help="Rate the quality of recommendations from 1 (poor) to 5 (excellent)"
        )
        feedback = st.text_area(
            "How can we improve recommendations?",
            help="Please provide specific feedback to help us improve"
        )
        
        submit_feedback = st.form_submit_button("Submit Feedback")
        
        if submit_feedback:
            if len(feedback.strip()) < 10:
                st.error("Please provide more detailed feedback (at least 10 characters)")
            else:
                # This would send feedback to the API
                try:
                    # Add API call here
                    st.success("Thank you for your feedback!")
                except Exception as e:
                    st.error(f"Failed to submit feedback: {str(e)}")

# Display candidate recommendations
if recommendations:
    for idx, candidate in enumerate(recommendations):
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {candidate.get('full_name', 'Anonymous Candidate')}")
                st.write(f"**Location:** {candidate.get('location', 'N/A')}")
                st.write(f"**Experience:** {candidate.get('experience_years', 'N/A')} years")
                st.write(f"**Match Score:** {candidate.get('match_score', 'N/A')}%")
                
                # Display skills match
                skills = candidate.get('skills', {})
                if skills:
                    tech_skills = skills.get('languages_frameworks', [])
                    if tech_skills:
                        st.write("**Technical Skills:**")
                        st.write(", ".join(tech_skills))
                    
                    soft_skills = skills.get('soft_skills', [])
                    if soft_skills:
                        st.write("**Soft Skills:**")
                        st.write(", ".join(soft_skills))
                
                # Display bio preview
                bio = candidate.get('bio', '')
                if bio:
                    st.write("**Professional Summary:**")
                    preview = bio[:200] + "..." if len(bio) > 200 else bio
                    st.write(preview)
            
            with col2:
                # Use index as fallback for unique keys
                candidate_id = candidate.get('id')
                view_key = f"view_{candidate_id if candidate_id is not None else f'idx_{idx}'}"
                contact_key = f"contact_{candidate_id if candidate_id is not None else f'idx_{idx}'}"
                save_key = f"save_{candidate_id if candidate_id is not None else f'idx_{idx}'}"
                
                st.button("View Profile", key=view_key)
                st.button("Contact", key=contact_key)
                st.button("Save Profile", key=save_key)
            
            # Add education if available
            education = candidate.get('education_summary')
            if education:
                st.write("**Education:**")
                st.write(education)
            
            st.divider()
else:
    st.info("No candidate recommendations found. Post a job to get matched candidates.")

# Filters sidebar
with st.sidebar:
    st.subheader("Filter Candidates")
    
    # Experience filter
    experience_range = st.slider(
        "Experience (years)",
        min_value=0,
        max_value=20,
        value=(0, 20),
        key="filter_experience"
    )
    
    # Skills filter
    required_skills = st.text_input(
        "Required Skills",
        help="Comma-separated list of required skills",
        key="filter_skills"
    )
    
    # Location filter
    location = st.text_input(
        "Location",
        help="Filter by candidate location",
        key="filter_location"
    )
    
    # Education Level filter
    education_level = st.multiselect(
        "Education Level",
        ["Bachelor's", "Master's", "PhD", "Other"],
        key="filter_education"
    )
    
    # Apply filters button
    if st.button("Apply Filters", key="apply_filters"):
        st.rerun()

# Pagination controls
if recommendations:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if page > 1:
            if st.button("Previous Page", key="prev_page"):
                st.session_state.page = page - 1
                st.rerun()
    
    with col2:
        st.write(f"Page {page} of {total_pages}")
    
    with col3:
        if page < total_pages:
            if st.button("Next Page", key="next_page"):
                st.session_state.page = page + 1
                st.rerun() 