import streamlit as st
import requests
import json
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login to access this page")
    st.stop()

if st.session_state.user_type != "candidate":
    st.warning("This page is only available for candidates")
    st.stop()

# Helper function
def make_api_request(endpoint, method="GET", data=None, params=None):
    """Make API request with proper headers and authentication"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.session_state.access_token}"
    }
    
    url = f"{API_BASE_URL}/{endpoint}"
    logger.info(f"Making {method} request to {url}")
    if params:
        logger.info(f"With params: {params}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        
        logger.info(f"Response status code: {response.status_code}")
        
        # Log response content for debugging
        try:
            content = response.json() if response.content else None
            logger.info(f"Response content: {content}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {str(e)}")
            logger.error(f"Raw response content: {response.content}")
            return {"error": "Invalid JSON response from server", "detail": str(e)}
        
        if response.status_code in [200, 201, 204]:
            if not response.content:
                return {"items": [], "total_count": 0}
            return content
        else:
            error_msg = content if content else {"detail": "Unknown error"}
            return {"error": f"Status {response.status_code}", "detail": error_msg}
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while connecting to {url}")
        return {"error": "Failed to connect to the server. Please ensure the backend is running."}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": str(e)}

# Page title
st.title("Project Recommendations")

# Explanation
st.write("""
Projects are opportunities to build your portfolio, gain practical experience, 
and develop skills that employers are looking for. These recommendations are 
based on your profile and career goals.
""")

# Filters in sidebar
with st.sidebar:
    st.header("Filter Projects")
    
    # Project type filter
    project_types = st.multiselect(
        "Project Types",
        options=["Open Source", "Personal", "Freelance", "Collaboration", "Learning"],
        default=[]
    )
    
    # Technology filter
    tech_stack = st.multiselect(
        "Technology Stack",
        options=["JavaScript", "Python", "Java", "C#", "Ruby", "Go", "Swift", 
                "React", "Angular", "Vue", "Django", "Flask", "Spring", "Node.js"],
        default=[]
    )
    
    # Difficulty level
    difficulty = st.multiselect(
        "Difficulty Level",
        options=["Beginner", "Intermediate", "Advanced", "Expert"],
        default=[]
    )
    
    # Estimated time
    time_commitment = st.multiselect(
        "Time Commitment",
        options=["Less than 1 week", "1-2 weeks", "2-4 weeks", "1-3 months", "3+ months"],
        default=[]
    )
    
    # Apply filters button
    filter_button = st.button("Apply Filters")
    
    # Reset filters button
    reset_button = st.button("Reset Filters")

# Project recommendation settings
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Recommended Projects")
with col2:
    recommendation_count = st.selectbox("Show", [10, 20, 50], index=0)

# Define params for API request based on filters
params = {"limit": recommendation_count}

if filter_button:
    if project_types:
        params["project_types"] = json.dumps(project_types)
    if tech_stack:
        params["tech_stack"] = json.dumps(tech_stack)
    if difficulty:
        params["difficulty"] = json.dumps(difficulty)
    if time_commitment:
        params["time_commitment"] = json.dumps(time_commitment)

# Get project recommendations
with st.spinner("Loading project recommendations..."):
    project_recs = make_api_request("recommendations/projects", params=params)

if "error" in project_recs:
    error_msg = project_recs.get("error", "Unknown error")
    detail = project_recs.get("detail", "")
    st.error(f"Failed to load project recommendations: {error_msg}")
    if detail:
        st.error(f"Details: {detail}")
    
    # Show retry button
    if st.button("Retry Loading Projects"):
        st.experimental_rerun()
else:
    # Handle both list and dictionary responses
    if isinstance(project_recs, list):
        projects = project_recs
        total_count = len(projects)
    else:
        projects = project_recs.get("items", [])
        total_count = project_recs.get("total_count", 0)
    
    # Show recommendation stats
    if total_count > 0:
        st.write(f"Found {total_count} project recommendations")
    else:
        st.info("No project recommendations found. This could be because:")
        st.markdown("""
        - Your profile needs more information
        - The filters are too restrictive
        - You haven't set your career goals
        
        Try adjusting your filters or updating your profile with more details.
        """)
    
    # Display project recommendations in cards
    projects_per_row = 2
    for i in range(0, len(projects), projects_per_row):
        cols = st.columns(projects_per_row)
        for j in range(projects_per_row):
            if i + j < len(projects):
                project = projects[i + j]
                with cols[j]:
                    with st.container():
                        st.markdown(f"### {project.get('title', 'Project Title')}")
                        
                        # Project type and difficulty
                        st.markdown(f"**Type:** {project.get('project_type', 'N/A')} | **Difficulty:** {project.get('difficulty', 'N/A')}")
                        
                        # Match score
                        match_score = project.get('match_score', 0)
                        st.progress(match_score / 100)
                        st.markdown(f"**Match Score:** {match_score}%")
                        
                        # Tech stack
                        tech = project.get('tech_stack', [])
                        if tech:
                            st.markdown("**Tech Stack:**")
                            st.markdown(", ".join(tech))
                        
                        # Description
                        description = project.get('description', '')
                        if len(description) > 150:
                            description = description[:150] + "..."
                        st.markdown(description)
                        
                        # Time commitment
                        st.markdown(f"**Time:** {project.get('time_commitment', 'N/A')}")
                        
                        # Skills to gain
                        skills_to_gain = project.get('skills_to_gain', [])
                        if skills_to_gain:
                            st.markdown("**Skills to Gain:**")
                            st.markdown(", ".join(skills_to_gain[:3]) + ("..." if len(skills_to_gain) > 3 else ""))
                        
                        # View details button
                        st.button("View Details", key=f"view_project_{project.get('id')}")
    
    # Pagination 
    if total_count > recommendation_count:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            page_count = (total_count + recommendation_count - 1) // recommendation_count
            pages = st.select_slider("Page", options=list(range(1, page_count + 1)), value=1)

# Project details modal (displayed when a project is selected)
if "selected_project" in st.session_state:
    project_id = st.session_state.selected_project
    with st.expander("Project Details", expanded=True):
        # Get project details from API
        project_details = make_api_request(f"projects/{project_id}")
        
        if "error" not in project_details:
            st.subheader(project_details.get("title", "Project Details"))
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Description:** {project_details.get('description', 'N/A')}")
                st.markdown(f"**Project Type:** {project_details.get('project_type', 'N/A')}")
                st.markdown(f"**Difficulty:** {project_details.get('difficulty', 'N/A')}")
                st.markdown(f"**Time Commitment:** {project_details.get('time_commitment', 'N/A')}")
                
                # Tech stack
                tech = project_details.get('tech_stack', [])
                if tech:
                    st.markdown("**Tech Stack:**")
                    st.markdown(", ".join(tech))
                
                # Skills to gain
                skills_to_gain = project_details.get('skills_to_gain', [])
                if skills_to_gain:
                    st.markdown("**Skills to Gain:**")
                    st.markdown(", ".join(skills_to_gain))
                
                # Learning resources
                resources = project_details.get('learning_resources', [])
                if resources:
                    st.markdown("**Learning Resources:**")
                    for resource in resources:
                        st.markdown(f"- [{resource.get('title')}]({resource.get('url')})")
            
            with col2:
                st.button("Start Project")
                st.button("Save for Later")
                st.button("Close", on_click=lambda: st.session_state.pop("selected_project", None))

# Skills development section
st.subheader("Skills Development")
st.write("""
These projects will help you develop the following skills that are in demand for your target roles:
""")

with st.spinner("Loading skill recommendations..."):
    skill_recs = make_api_request("recommendations/skill-development")

if "error" in skill_recs:
    error_msg = skill_recs.get("error", "Unknown error")
    detail = skill_recs.get("detail", "")
    st.error(f"Failed to load skill development recommendations: {error_msg}")
    if detail:
        st.error(f"Details: {detail}")
    
    # Show retry button
    if st.button("Retry Loading Skills", key="retry_skills"):
        st.experimental_rerun()
else:
    skills = skill_recs.get("recommended_skills", [])
    if skills:
        cols = st.columns(3)
        for i, skill in enumerate(skills[:6]):
            with cols[i % 3]:
                name = skill.get("name", "Unknown Skill")
                demand_score = skill.get("demand_score", 0)
                growth_trend = skill.get("growth_trend", 0)
                
                # Add color coding based on demand score
                if demand_score >= 8:
                    name = f"🔥 {name}"  # High demand
                elif demand_score >= 6:
                    name = f"📈 {name}"  # Growing demand
                
                st.metric(
                    label=name,
                    value=f"{demand_score}/10",
                    delta=f"{growth_trend:+.1f}%" if growth_trend else None,
                    delta_color="normal" if growth_trend >= 0 else "inverse"
                )
                
                # Add skill details in an expander
                with st.expander("Details"):
                    st.write(f"**Current Demand:** {demand_score}/10")
                    st.write(f"**Growth Trend:** {growth_trend:+.1f}%")
                    if skill.get("description"):
                        st.write(skill["description"])
                    if skill.get("learning_resources"):
                        st.write("**Learning Resources:**")
                        for resource in skill["learning_resources"]:
                            st.markdown(f"- [{resource['title']}]({resource['url']})")
    else:
        st.info("""
        No skill development recommendations available. This could be because:
        - Your profile needs more information about your current skills
        - You haven't set your career goals
        - The system needs more data about your interests
        
        Try updating your profile with more details about your skills and career goals.
        """) 