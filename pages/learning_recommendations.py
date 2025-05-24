import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Configuration
API_BASE_URL = "http://localhost:8000"

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login to access this page")
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
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.content else {"message": "Success"}
        else:
            error_msg = response.json() if response.content else {"detail": "Unknown error"}
            return {"error": f"Status {response.status_code}", "detail": error_msg}
    except Exception as e:
        return {"error": str(e)}

# Page title
st.title("Learning Recommendations")
st.write("""
Get personalized learning recommendations based on your career goals and timeframe.
These recommendations will help you develop the skills needed to advance in your career.
""")

# Sidebar for filters
with st.sidebar:
    st.header("Recommendation Settings")
    
    # Career goal selection
    career_goals = [
        "Software Engineer",
        "Data Scientist",
        "Machine Learning Engineer",
        "Full Stack Developer",
        "DevOps Engineer",
        "UX/UI Designer",
        "Product Manager",
        "Project Manager",
        "Business Analyst",
        "Cloud Architect",
        "Cybersecurity Specialist",
        "Mobile Developer",
        "Frontend Developer",
        "Backend Developer",
        "Database Administrator",
        "Data Engineer",
        "AI Researcher",
        "Game Developer",
        "QA Engineer",
        "Technical Writer"
    ]
    
    career_goal = st.selectbox(
        "Career Goal",
        options=career_goals,
        index=0,
        help="Select your target career path"
    )
    
    # Timeframe selection
    timeframe_options = {
        "3_months": "3 Months",
        "6_months": "6 Months",
        "1_year": "1 Year",
        "2_years": "2 Years",
        "5_years": "5 Years"
    }
    
    timeframe = st.selectbox(
        "Learning Timeframe",
        options=list(timeframe_options.keys()),
        format_func=lambda x: timeframe_options[x],
        index=1,  # Default to 6 months
        help="Select your learning timeframe"
    )
    
    # Current skills
    current_skills = st.text_area(
        "Your Current Skills (optional)",
        placeholder="Enter your skills, separated by commas",
        help="List your current skills to get more tailored recommendations"
    )
    
    # Display preferences
    st.subheader("Display Preferences")
    show_difficulty = st.checkbox("Show Difficulty Levels", value=True)
    show_prerequisites = st.checkbox("Show Prerequisites", value=True)
    show_time_commitment = st.checkbox("Show Time Commitment", value=True)

# Prepare parameters
params = {
    "career_goal": career_goal,
    "timeframe": timeframe
}

if current_skills:
    skills_list = [skill.strip() for skill in current_skills.split(",") if skill.strip()]
    if skills_list:
        params["skills"] = json.dumps(skills_list)

# Get learning recommendations
with st.spinner("Generating learning recommendations..."):
    learning_data = make_api_request("ml/learning-recommendations", params=params)
    
    if "error" in learning_data:
        st.error(f"Failed to get learning recommendations: {learning_data.get('error')}")
        if "detail" in learning_data:
            st.error(f"Details: {learning_data['detail']}")
        if st.button("Retry"):
            st.rerun()
    else:
        # Display the learning recommendations
        learning_path = learning_data.get("learning_path", {})
        resources = learning_data.get("resources", [])
        metadata = learning_data.get("metadata", {})
        
        # Show metadata
        st.subheader("Learning Path Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Career Goal", career_goal)
        with col2:
            st.metric("Timeframe", timeframe_options.get(timeframe, timeframe))
        with col3:
            st.metric("Total Resources", len(resources))
        
        # Display learning path description
        if learning_path.get("description"):
            st.write(learning_path.get("description"))
        
        # Display learning path phases
        if learning_path.get("phases"):
            st.subheader("Learning Path Phases")
            
            # Create a timeline visualization
            phases = learning_path.get("phases", [])
            
            if phases:
                # Create a Gantt chart for phases
                phase_data = []
                start_date = pd.Timestamp.now()
                
                for i, phase in enumerate(phases):
                    # Calculate duration based on timeframe and phase weight
                    total_days = {
                        "3_months": 90,
                        "6_months": 180,
                        "1_year": 365,
                        "2_years": 730,
                        "5_years": 1825
                    }.get(timeframe, 180)
                    
                    phase_weight = phase.get("weight", 1)
                    phase_duration = int(total_days * phase_weight / sum(p.get("weight", 1) for p in phases))
                    
                    end_date = start_date + pd.Timedelta(days=phase_duration)
                    
                    phase_data.append({
                        "Task": phase.get("name", f"Phase {i+1}"),
                        "Description": phase.get("description", ""),
                        "Start": start_date,
                        "Finish": end_date,
                        "Duration": phase_duration,
                        "Priority": phase.get("priority", "Medium")
                    })
                    
                    # Update start date for next phase
                    start_date = end_date
                
                # Create DataFrame
                df = pd.DataFrame(phase_data)
                
                # Create Gantt chart
                fig = px.timeline(
                    df, 
                    x_start="Start", 
                    x_end="Finish", 
                    y="Task",
                    color="Priority",
                    hover_data=["Description", "Duration"],
                    height=300,
                    color_discrete_map={
                        "High": "red",
                        "Medium": "orange",
                        "Low": "green"
                    }
                )
                
                fig.update_layout(
                    title="Learning Path Timeline",
                    xaxis_title="Timeline",
                    yaxis_title="Learning Phases"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display phase details
                for i, phase in enumerate(phases):
                    with st.expander(f"{phase.get('name', f'Phase {i+1}')}"):
                        st.write(f"**Description:** {phase.get('description', 'No description available')}")
                        
                        if phase.get("skills_to_learn"):
                            st.write("**Skills to Learn:**")
                            for skill in phase.get("skills_to_learn", []):
                                st.write(f"- {skill}")
                        
                        if phase.get("milestones"):
                            st.write("**Milestones:**")
                            for milestone in phase.get("milestones", []):
                                st.write(f"- {milestone}")
        
        # Display learning resources
        if resources:
            st.subheader("Recommended Learning Resources")
            
            # Group resources by type
            resource_types = {}
            for resource in resources:
                res_type = resource.get("type", "Other")
                if res_type not in resource_types:
                    resource_types[res_type] = []
                resource_types[res_type].append(resource)
            
            # Create tabs for each resource type
            tabs = st.tabs(list(resource_types.keys()))
            
            for i, (res_type, res_list) in enumerate(resource_types.items()):
                with tabs[i]:
                    for j, resource in enumerate(res_list):
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                title = resource.get("title", "Untitled Resource")
                                url = resource.get("url", "#")
                                st.markdown(f"### [{title}]({url})")
                                
                                if resource.get("description"):
                                    st.write(resource.get("description"))
                                
                                # Show tags if available
                                if resource.get("tags"):
                                    tags = resource.get("tags", [])
                                    st.write(" ".join([f"`{tag}`" for tag in tags]))
                            
                            with col2:
                                # Display metrics based on preferences
                                if show_difficulty and "difficulty" in resource:
                                    difficulty = resource.get("difficulty", "Medium")
                                    st.metric("Difficulty", difficulty)
                                
                                if show_time_commitment and "time_commitment" in resource:
                                    time_commitment = resource.get("time_commitment", "Unknown")
                                    st.metric("Time", time_commitment)
                            
                            # Show prerequisites if enabled and available
                            if show_prerequisites and resource.get("prerequisites"):
                                st.write("**Prerequisites:**")
                                st.write(", ".join(resource.get("prerequisites", [])))
                            
                            st.divider()
        else:
            st.info("No learning resources found for the selected criteria.")

# Feedback section
st.subheader("Recommendation Feedback")
st.write("Help us improve our recommendations by providing feedback.")

with st.form("feedback_form"):
    relevance_score = st.slider(
        "Relevance Score",
        min_value=1,
        max_value=10,
        value=7,
        help="How relevant are these recommendations to your career goal?"
    )
    
    accuracy_score = st.slider(
        "Accuracy Score",
        min_value=1,
        max_value=10,
        value=7,
        help="How accurate are these recommendations based on your current skills?"
    )
    
    action_taken = st.selectbox(
        "Action Taken",
        options=["Viewed", "Saved", "Started Learning", "Completed", "None"],
        index=0,
        help="What action did you take on these recommendations?"
    )
    
    comments = st.text_area(
        "Comments",
        placeholder="Any additional feedback or comments?",
        help="Provide any additional feedback to help us improve"
    )
    
    submit_button = st.form_submit_button("Submit Feedback")
    
    if submit_button:
        feedback_data = {
            "recommendation_type": "learning",
            "recommendation_id": learning_data.get("id", str(hash(f"{career_goal}_{timeframe}"))),
            "relevance_score": relevance_score,
            "accuracy_score": accuracy_score,
            "action_taken": action_taken,
            "comments": comments
        }
        
        feedback_response = make_api_request("recommendations/feedback", method="POST", data=feedback_data)
        
        if "error" in feedback_response:
            st.error(f"Failed to submit feedback: {feedback_response.get('error')}")
        else:
            st.success("Feedback submitted successfully! Thank you for helping us improve.")

# Additional information section
st.subheader("About Learning Recommendations")
st.write("""
Our learning recommendations are tailored to your career goals and timeframe.
We analyze industry trends, job requirements, and skill relationships to create
a personalized learning path that will help you achieve your career objectives.
""")

# Call to action
st.subheader("Next Steps")
col1, col2 = st.columns(2)
with col1:
    if st.button("View Market Trends"):
        st.switch_page("pages/market_trends.py")
with col2:
    if st.button("Explore Skill Clusters"):
        st.switch_page("pages/skill_clusters.py") 