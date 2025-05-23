import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px

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

# Initialize session state for search parameters
if "last_search_params" not in st.session_state:
    st.session_state.last_search_params = {}
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = None
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Helper functions for validation
def validate_weights(*weights):
    """Validate that weights sum to 1.0 and are valid"""
    if not all(0 <= w <= 1 for w in weights):
        return False, "All weights must be between 0 and 1"
    total = sum(weights)
    if not 0.99 <= total <= 1.01:  # Allow small floating point differences
        return False, f"Weights must sum to 1.0 (current sum: {total:.2f})"
    return True, ""

def validate_skills(skills_text):
    """Validate skills input"""
    if not skills_text.strip():
        return False, "At least one skill is required"
    skills = [s.strip() for s in skills_text.split(",")]
    if any(len(s) < 2 for s in skills):
        return False, "Each skill must be at least 2 characters long"
    return True, skills

# Add validation state to session
if "form_validation_error" not in st.session_state:
    st.session_state.form_validation_error = None

# Page title
st.title("Talent Search")

# Explanation
st.write("""
Find qualified candidates for your job openings. Use advanced filters to narrow down 
candidates based on skills, experience, location, and more.
""")

# Create two columns layout
search_col, results_col = st.columns([1, 2])

with search_col:
    # Search form
    with st.form("talent_search_form"):
        st.subheader("Search Parameters")
        
        # Skills search (most important)
        skills_input = st.text_area(
            "Skills (comma separated)", 
            placeholder="Python, React, Machine Learning, etc.",
            help="Enter skills separated by commas. At least one skill is required."
        )
        
        # Experience level
        experience_levels = st.multiselect(
            "Experience Level",
            options=["Entry-level", "Mid-level", "Senior", "Manager", "Executive"],
            default=[],
            help="Select one or more experience levels"
        )
        
        # Experience years
        min_experience = st.number_input(
            "Minimum Experience (Years)", 
            min_value=0, 
            max_value=40, 
            value=0,
            help="Minimum years of experience required"
        )
        
        # Location
        location = st.text_input(
            "Location",
            help="Enter city, state, or country. Leave blank for any location."
        )
        remote_only = st.checkbox(
            "Remote Only",
            help="Only show candidates open to remote work"
        )
        
        # Education
        education_levels = st.multiselect(
            "Education Level",
            options=["High School", "Associate's", "Bachelor's", "Master's", "PhD"],
            default=[],
            help="Select one or more education levels"
        )
        
        # Job type
        job_types = st.multiselect(
            "Preferred Job Types",
            options=["Full-time", "Part-time", "Contract", "Remote", "Hybrid"],
            default=[]
        )
        
        # Industry
        industries = st.multiselect(
            "Industries",
            options=["Technology", "Finance", "Healthcare", "Education", "E-commerce", 
                     "Manufacturing", "Retail", "Media", "Consulting", "Other"],
            default=[]
        )
        
        # Availability
        availability = st.selectbox(
            "Availability",
            options=["Any", "Immediately", "1-2 weeks", "1 month", "3+ months"],
            index=0
        )
        
        # Advanced search options
        with st.expander("Advanced Search Options"):
            # Weights for search criteria
            st.subheader("Search Weights")
            st.write("Adjust importance of each criterion in search results (must sum to 1.0)")
            
            col1, col2 = st.columns(2)
            with col1:
                skills_weight = st.slider("Skills Weight", 0.0, 1.0, 0.8, 0.1)
                experience_weight = st.slider("Experience Weight", 0.0, 1.0, 0.6, 0.1)
            with col2:
                location_weight = st.slider("Location Weight", 0.0, 1.0, 0.4, 0.1)
                education_weight = st.slider("Education Weight", 0.0, 1.0, 0.3, 0.1)
            
            # Show current total
            total_weight = skills_weight + experience_weight + location_weight + education_weight
            st.write(f"Total weight: {total_weight:.2f}")
            if not 0.99 <= total_weight <= 1.01:
                st.warning("Weights must sum to 1.0")
            
            # Exclude candidates
            exclude_applied = st.checkbox(
                "Exclude candidates who already applied to your jobs",
                value=True,
                help="Filter out candidates who have already applied to your positions"
            )
            exclude_contacted = st.checkbox(
                "Exclude candidates you've already contacted",
                value=True,
                help="Filter out candidates you've already reached out to"
            )
        
        # Search button
        search_button = st.form_submit_button("Search Candidates")
        
        # Validate form on submission
        if search_button:
            # Validate skills
            skills_valid, skills_result = validate_skills(skills_input)
            if not skills_valid:
                st.error(skills_result)
                st.stop()
            
            # Validate weights
            weights_valid, weights_error = validate_weights(
                skills_weight, experience_weight, 
                location_weight, education_weight
            )
            if not weights_valid:
                st.error(weights_error)
                st.stop()
            
            # Store validated skills
            skills_list = skills_result
            
            # Build search parameters
            search_params = {
                "skills": skills_list,
                "min_experience": min_experience
            }
            
            if experience_levels:
                search_params["experience_levels"] = experience_levels
            if location:
                search_params["location"] = location.strip()
            if remote_only:
                search_params["remote_only"] = remote_only
            if education_levels:
                search_params["education_levels"] = education_levels
            if job_types:
                search_params["job_types"] = job_types
            if industries:
                search_params["industries"] = industries
            if availability != "Any":
                search_params["availability"] = availability
            
            # Add weights
            search_params["weights"] = {
                "skills": skills_weight,
                "experience": experience_weight,
                "location": location_weight,
                "education": education_weight
            }
            
            # Add exclusions
            if exclude_applied:
                search_params["exclude_applied"] = True
            if exclude_contacted:
                search_params["exclude_contacted"] = True
            
            # Store search parameters
            st.session_state.last_search_params = search_params
            
            # Make API request
            with st.spinner("Searching for candidates..."):
                try:
                    results = make_api_request("candidates/search", method="POST", data=search_params)
                    
                    if "error" in results:
                        st.error(f"Search failed: {results.get('error')}")
                        if st.button("Retry Search"):
                            st.rerun()
                    else:
                        st.session_state.search_results = results
                        st.success(f"Found {len(results.get('candidates', []))} matching candidates")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    if st.button("Retry Search"):
                        st.rerun()

    # Saved searches
    st.subheader("Saved Searches")
    if st.session_state.search_history:
        for i, search in enumerate(st.session_state.search_history):
            search_name = search.get("name", f"Search {i+1}")
            if st.button(search_name, key=f"saved_search_{i}"):
                # Load saved search parameters
                st.session_state.last_search_params = search.get("params", {})
                st.rerun()
    else:
        st.info("No saved searches yet. Save your searches for quick access later.")
    
    # Save current search with validation
    if search_button or st.session_state.last_search_params:
        with st.expander("Save Current Search"):
            with st.form("save_search_form"):
                search_name = st.text_input(
                    "Search Name",
                    help="Enter a name to identify this search"
                )
                save_search = st.form_submit_button("Save Search")
                
                if save_search:
                    if not search_name.strip():
                        st.error("Please enter a name for the search")
                    elif any(s["name"] == search_name for s in st.session_state.search_history):
                        st.error("A search with this name already exists")
                    else:
                        current_params = st.session_state.last_search_params
                        st.session_state.search_history.append({
                            "name": search_name,
                            "params": current_params,
                            "created_at": pd.Timestamp.now().isoformat()
                        })
                        st.success(f"Search '{search_name}' saved!")
                        st.rerun()

# Display search results
with results_col:
    if st.session_state.selected_candidate:
        # Back button
        if st.button("Back to Results"):
            st.session_state.selected_candidate = None
            st.rerun()
        
        # Get candidate details
        candidate_id = st.session_state.selected_candidate
        candidate_details = make_api_request(f"candidates/{candidate_id}")
        
        if "error" in candidate_details:
            st.error(f"Failed to load candidate details: {candidate_details.get('error')}")
        else:
            # Display candidate profile
            st.subheader(candidate_details.get("full_name", "Candidate"))
            
            # Summary card
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Experience:** {candidate_details.get('experience_years', 'N/A')} years")
                st.markdown(f"**Location:** {candidate_details.get('location', 'N/A')}")
                
                # Match score if available
                match_score = candidate_details.get("match_score", 0)
                st.progress(match_score / 100)
                st.markdown(f"**Match Score:** {match_score}%")
            
            with col2:
                # Contact actions
                st.button("Contact Candidate", key="contact_button")
                st.button("Save to Talent Pool", key="save_button")
                st.button("Send Job Offer", key="job_offer_button")
            
            # Tabs for different sections of the profile
            profile_tabs = st.tabs(["Skills & Experience", "Education", "Projects", "Resume"])
            
            with profile_tabs[0]:
                # Skills section
                st.subheader("Skills")
                skills = candidate_details.get("skills", {})
                
                # Technical skills
                tech_skills = skills.get("languages_frameworks", [])
                if tech_skills:
                    st.markdown("**Technical Skills:**")
                    st.write(", ".join(tech_skills))
                
                # Tools
                tools = skills.get("tools", [])
                if tools:
                    st.markdown("**Tools & Technologies:**")
                    st.write(", ".join(tools))
                
                # Soft skills
                soft_skills = skills.get("soft_skills", [])
                if soft_skills:
                    st.markdown("**Soft Skills:**")
                    st.write(", ".join(soft_skills))
                
                # Experience
                st.subheader("Experience")
                experience = candidate_details.get("experience", [])
                for job in experience:
                    st.markdown(f"**{job.get('title')} at {job.get('company')}**")
                    st.markdown(f"_{job.get('start_date')} to {job.get('end_date', 'Present')}_")
                    st.markdown(job.get("description", ""))
                    st.divider()
            
            with profile_tabs[1]:
                # Education section
                st.subheader("Education")
                education = candidate_details.get("education", [])
                for edu in education:
                    st.markdown(f"**{edu.get('degree')} in {edu.get('field')}**")
                    st.markdown(f"_{edu.get('institution')}, {edu.get('graduation_year')}_")
                    st.markdown(edu.get("description", ""))
                    st.divider()
            
            with profile_tabs[2]:
                # Projects section
                st.subheader("Projects")
                projects = candidate_details.get("projects", [])
                for project in projects:
                    st.markdown(f"**{project.get('title')}**")
                    st.markdown(f"_{project.get('date')}_")
                    st.markdown(project.get("description", ""))
                    
                    # Project skills
                    skills = project.get("skills", [])
                    if skills:
                        st.markdown("**Skills Used:**")
                        st.write(", ".join(skills))
                    
                    # Project link
                    link = project.get("link")
                    if link:
                        st.markdown(f"[View Project]({link})")
                    
                    st.divider()
            
            with profile_tabs[3]:
                # Resume section
                st.subheader("Resume")
                # This would typically be a download link to the candidate's resume
                st.info("Resume download functionality would be implemented with file storage API")
                st.button("Download Resume", key="download_resume")
                
                # Preview placeholder
                st.markdown("**Resume Preview:**")
                st.text("Resume content would be displayed here...")
    
    elif st.session_state.search_results:
        # Display results
        results = st.session_state.search_results
        candidates = results.get("candidates", [])
        total_candidates = results.get("total_count", 0)
        
        # Results header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Search Results")
            st.write(f"Found {total_candidates} matching candidates")
        with col2:
            result_sort = st.selectbox(
                "Sort By", 
                options=["Match Score", "Experience", "Recent Activity", "Location"]
            )
        
        # Display matching candidates
        if not candidates:
            st.info("No candidates found matching your criteria. Try adjusting your search parameters.")
        else:
            for candidate in candidates:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        name = candidate.get("full_name", "Candidate")
                        headline = candidate.get("headline", "")
                        st.subheader(name)
                        if headline:
                            st.write(headline)
                        
                        # Basic info
                        experience = candidate.get("experience_years", "N/A")
                        location = candidate.get("location", "N/A")
                        st.markdown(f"**Experience:** {experience} years | **Location:** {location}")
                        
                        # Top skills
                        skills = candidate.get("skills", {}).get("languages_frameworks", [])
                        if skills:
                            st.markdown("**Skills:** " + ", ".join(skills[:5]) + 
                                        ("..." if len(skills) > 5 else ""))
                        
                        # Match score
                        match_score = candidate.get("match_score", 0)
                        st.progress(match_score / 100)
                        st.markdown(f"**Match Score:** {match_score}%")
                        
                        # Match factors
                        match_factors = candidate.get("match_factors", {})
                        if match_factors:
                            factors_text = []
                            for factor, value in match_factors.items():
                                factors_text.append(f"{factor.replace('_', ' ').title()}: {value}")
                            st.markdown("**Match Factors:** " + " | ".join(factors_text))
                    
                    with col2:
                        # Action buttons
                        view_button = st.button("View Profile", key=f"view_{candidate.get('id')}")
                        if view_button:
                            st.session_state.selected_candidate = candidate.get("id")
                            st.rerun()
                        
                        st.button("Contact", key=f"contact_{candidate.get('id')}")
                        st.button("Save", key=f"save_{candidate.get('id')}")
                    
                    st.divider()
            
            # Pagination
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                if total_candidates > len(candidates):
                    st.markdown("### Pages")
                    page_count = (total_candidates + 9) // 10  # Assuming 10 candidates per page
                    page_nums = list(range(1, page_count + 1))
                    selected_page = st.select_slider("", options=page_nums, value=1)
    
    else:
        # Initial state - no search yet
        st.info("""
        Use the search form to find candidates for your job openings.
        
        Start with the most important skills you're looking for, then refine 
        your search using additional criteria like experience level and location.
        """)
        
        # Show candidate distribution chart as a helper
        st.subheader("Available Candidate Pool")
        with st.expander("View Candidate Distribution"):
            # This would normally be fetched from an API
            st.write("Overview of candidate distribution in the talent pool")
            
            # Mock skills distribution data
            skills_data = {
                "Skill": ["JavaScript", "Python", "React", "Java", "SQL", "AWS", "Machine Learning", "Node.js", "DevOps", "UX Design"],
                "Count": [135, 120, 95, 85, 80, 75, 60, 55, 45, 40]
            }
            skills_df = pd.DataFrame(skills_data)
            
            # Create chart
            fig = px.bar(
                skills_df, 
                x="Skill", 
                y="Count", 
                title="Top Skills in Candidate Pool",
                color="Count",
                color_continuous_scale="blues"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Industry distribution
            industry_data = {
                "Industry": ["Technology", "Finance", "Healthcare", "Retail", "Education", "Manufacturing"],
                "Percentage": [45, 20, 15, 10, 7, 3]
            }
            industry_df = pd.DataFrame(industry_data)
            
            fig = px.pie(
                industry_df,
                values="Percentage",
                names="Industry",
                title="Candidates by Industry",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

# Sidebar for search history and quick actions
with st.sidebar:
    # Search history
    st.subheader("Recent Searches")
    
    # This would typically be stored in the user's profile
    recent_searches = [
        "Python developers in Boston",
        "React developers with 3+ years",
        "Data Scientists with ML experience",
        "Remote UX Designers"
    ]
    
    for search in recent_searches:
        st.button(search, key=f"recent_{search}")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    st.button("View Talent Pool", key="view_talent_pool")
    st.button("View Contacted Candidates", key="view_contacted")
    st.button("Export Search Results", key="export_results")
    
    st.markdown("---")
    
    # Search tips
    with st.expander("Search Tips", expanded=False):
        st.markdown("""
        * Start with the most important skills for the role
        * Be specific with technical skills (e.g., "React.js" instead of just "JavaScript")
        * Use location filters for in-office roles
        * Adjust search weights to prioritize what matters most
        * Save searches you use frequently
        """) 