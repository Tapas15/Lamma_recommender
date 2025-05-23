import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

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

# Page title
st.title("Skill Gap Analysis")

# Explanation
st.write("""
Identify the skills you need to develop to qualify for your target jobs. This analysis 
compares your current skills with the skills required for specific job roles.
""")

# Target role selection
col1, col2 = st.columns([3, 1])
with col1:
    # Get common job roles from API
    job_roles = make_api_request("job-roles")
    if "error" not in job_roles:
        # Handle both list and dictionary responses
        if isinstance(job_roles, list):
            role_options = [role.get("title") for role in job_roles]
        else:
            role_options = [role.get("title") for role in job_roles.get("items", [])]
        
        target_role = st.selectbox(
            "Select a target job role:",
            options=role_options
        )
    else:
        # Fallback if API fails
        target_role = st.selectbox(
            "Select a target job role:",
            options=[
                "Software Engineer", 
                "Data Scientist", 
                "Frontend Developer", 
                "Backend Developer",
                "Full Stack Developer", 
                "DevOps Engineer", 
                "Product Manager", 
                "UX/UI Designer"
            ]
        )

with col2:
    experience_level = st.selectbox(
        "Experience Level",
        options=["Entry-level", "Mid-level", "Senior", "Lead"]
    )

# Perform skill gap analysis
with st.spinner("Analyzing skill gap..."):
    skill_gap = make_api_request(
        "recommendations/skill-gap", 
        params={"target_role": target_role, "experience_level": experience_level}
    )

if "error" in skill_gap:
    error_message = skill_gap.get('error', '')
    if "404" in error_message:
        # API endpoint doesn't exist yet, use mock data
        st.info("Skill gap analysis is currently being developed. Showing sample data for demonstration purposes.")
        
        # Sample mock skill gap data
        skill_gap = {
            "match_score": 65,  # Example match score
            "your_skills": [
                {"name": "Python", "proficiency": 8},
                {"name": "JavaScript", "proficiency": 7},
                {"name": "React", "proficiency": 6},
                {"name": "SQL", "proficiency": 7},
                {"name": "Git", "proficiency": 8},
                {"name": "Docker", "proficiency": 5},
            ],
            "required_skills": [
                {"name": "Python", "importance": 9},
                {"name": "JavaScript", "importance": 7},
                {"name": "React", "importance": 8},
                {"name": "SQL", "importance": 6},
                {"name": "Git", "importance": 7},
                {"name": "Docker", "importance": 7},
                {"name": "Kubernetes", "importance": 8},
                {"name": "AWS", "importance": 9},
                {"name": "System Design", "importance": 8},
            ],
            "missing_skills": [
                {"name": "Kubernetes", "importance": 8},
                {"name": "AWS", "importance": 9},
                {"name": "System Design", "importance": 8},
            ]
        }
    else:
        st.error(f"Failed to analyze skill gap: {error_message}")
else:
    # Display overall match score
    match_score = skill_gap.get("match_score", 0)
    st.subheader("Overall Skill Match")
    
    # Create a gauge chart for match score
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = match_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Match Score"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "royalblue"},
            'steps': [
                {'range': [0, 40], 'color': "lightgray"},
                {'range': [40, 70], 'color': "gray"},
                {'range': [70, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add context about the score
    if match_score >= 80:
        st.success("You're highly qualified for this role!")
    elif match_score >= 60:
        st.info("You have many of the required skills, but could strengthen some areas.")
    else:
        st.warning("You may need to develop more skills before applying for this role.")
    
    # Skills comparison section
    st.subheader("Skills Comparison")
    
    # Get skills data
    your_skills = skill_gap.get("your_skills", [])
    required_skills = skill_gap.get("required_skills", [])
    missing_skills = skill_gap.get("missing_skills", [])
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Required vs. Your Skills", "Missing Skills", "Recommendations"])
    
    with tab1:
        # Create dataframe for comparison chart
        skill_comparison = []
        
        # Combine all skills
        all_skills = set()
        for skill in your_skills:
            all_skills.add(skill.get("name"))
        for skill in required_skills:
            all_skills.add(skill.get("name"))
        
        # Prepare data for chart
        for skill_name in all_skills:
            # Find skill in your skills
            your_skill_value = 0
            for skill in your_skills:
                if skill.get("name") == skill_name:
                    your_skill_value = skill.get("proficiency", 0)
                    break
                    
            # Find skill in required skills
            required_skill_value = 0
            for skill in required_skills:
                if skill.get("name") == skill_name:
                    required_skill_value = skill.get("importance", 0)
                    break
            
            # Add to comparison data
            skill_comparison.append({
                "Skill": skill_name,
                "Your Proficiency": your_skill_value,
                "Required Level": required_skill_value,
                "Gap": required_skill_value - your_skill_value
            })
        
        # Create bubble chart
        if skill_comparison:
            df = pd.DataFrame(skill_comparison)
            
            # Create bubble chart
            fig_bubble = px.scatter(
                df,
                x="Required Level",
                y="Your Proficiency",
                size="Gap",
                color="Gap",
                hover_name="Skill",
                color_continuous_scale="RdYlBu_r",
                title="Skill Proficiency vs Required Level",
                labels={
                    "Required Level": "Required Skill Level",
                    "Your Proficiency": "Your Skill Level",
                    "Gap": "Skill Gap"
                }
            )
            
            # Add diagonal line for reference
            fig_bubble.add_trace(
                go.Scatter(
                    x=[0, 10],
                    y=[0, 10],
                    mode='lines',
                    line=dict(dash='dash', color='gray'),
                    name='Perfect Match'
                )
            )
            
            st.plotly_chart(fig_bubble, use_container_width=True)
        else:
            st.info("No skill comparison data available.")
    
    with tab2:
        # Display missing skills with importance
        if missing_skills:
            st.write("These are the skills you should develop for this role:")
            
            # Create a bar chart of missing skills by importance
            missing_df = pd.DataFrame([
                {"Skill": skill.get("name"), "Importance": skill.get("importance", 0)}
                for skill in missing_skills
            ])
            
            # Sort by importance
            missing_df = missing_df.sort_values("Importance", ascending=False)
            
            # Create bar chart
            fig = px.bar(
                missing_df,
                x="Skill",
                y="Importance",
                color="Importance",
                color_continuous_scale="Reds",
                title=f"Missing Skills for {target_role}",
                labels={"Importance": "Importance (0-10)"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display as list with importance
            for skill in missing_skills:
                importance = skill.get("importance", 0)
                name = skill.get("name", "")
                
                # Create a colored badge based on importance
                if importance >= 8:
                    badge = "🔴 High Priority"
                elif importance >= 5:
                    badge = "🟠 Medium Priority"
                else:
                    badge = "🟡 Low Priority"
                
                st.markdown(f"**{name}** - {badge} (Importance: {importance}/10)")
        else:
            st.success("Great! You have all the required skills for this role.")
    
    with tab3:
        # Learning recommendations
        st.subheader("Learning Recommendations")
        if missing_skills:
            # Get learning resources from API
            learning_recs = make_api_request(
                "recommendations/learning", 
                params={"skills": json.dumps([s.get("name") for s in missing_skills[:3]])}
            )
            
            if "error" not in learning_recs:
                resources = learning_recs.get("resources", [])
                if resources:
                    for i, resource in enumerate(resources):
                        skill = resource.get("skill")
                        res_list = resource.get("resources", [])
                        
                        st.markdown(f"### {skill}")
                        for res in res_list:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"**{res.get('title')}**")
                                st.markdown(f"_{res.get('provider')}_")
                                st.markdown(f"{res.get('description')}")
                            with col2:
                                st.link_button("View", res.get("url"), use_container_width=True)
                            st.divider()
                else:
                    st.info("No specific learning resources found.")
            else:
                error_message = learning_recs.get('error', '')
                if "404" in error_message:
                    # API endpoint doesn't exist yet, use mock data
                    st.info("Learning recommendations are currently being developed. Showing sample data for demonstration purposes.")
                    
                    # Sample mock learning resources
                    missing_skill_names = [s.get("name") for s in missing_skills[:3]]
                    resources = []
                    
                    for skill in missing_skill_names:
                        skill_resources = {
                            "skill": skill,
                            "resources": [
                                {
                                    "title": f"{skill} Fundamentals",
                                    "provider": "Coursera",
                                    "description": f"Learn the basics of {skill} and how to apply it in real-world scenarios.",
                                    "url": "https://coursera.org"
                                },
                                {
                                    "title": f"Advanced {skill} Techniques",
                                    "provider": "Udemy",
                                    "description": f"Master advanced concepts and best practices for {skill}.",
                                    "url": "https://udemy.com"
                                },
                                {
                                    "title": f"Hands-on {skill} Projects",
                                    "provider": "Pluralsight",
                                    "description": f"Build practical projects to solidify your {skill} knowledge.",
                                    "url": "https://pluralsight.com"
                                }
                            ]
                        }
                        resources.append(skill_resources)
                    
                    # Display mock resources
                    for i, resource in enumerate(resources):
                        skill = resource.get("skill")
                        res_list = resource.get("resources", [])
                        
                        st.markdown(f"### {skill}")
                        for res in res_list:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"**{res.get('title')}**")
                                st.markdown(f"_{res.get('provider')}_")
                                st.markdown(f"{res.get('description')}")
                            with col2:
                                st.link_button("View", res.get("url"), use_container_width=True)
                            st.divider()
                else:
                    # Fallback recommendations
                    st.info("""
                    To improve your skills, consider:
                    1. Online courses on platforms like Coursera, Udemy, or edX
                    2. Hands-on projects to build your portfolio
                    3. Open source contributions
                    4. Coding challenges and hackathons
                    """)
        else:
            st.success("You have all the required skills! Consider learning advanced topics to stand out.")
    
    # Career path section
    st.subheader("Career Path Analysis")
    
    # Get career path data
    career_path = make_api_request(
        "recommendations/career-path",
        params={"current_role": target_role}
    )
    
    if "error" not in career_path:
        paths = career_path.get("paths", [])
        if paths:
            st.write("Potential career paths based on your target role:")
            
            # Create timeline chart
            timeline_data = []
            for i, path in enumerate(paths):
                roles = path.get("roles", [])
                base_date = datetime.now()
                
                for j, role in enumerate(roles):
                    timeline_data.append({
                        "Path": f"Path {i+1}",
                        "Role": role.get("title", ""),
                        "Start": base_date + timedelta(years=j*2),
                        "End": base_date + timedelta(years=(j+1)*2),
                        "Level": role.get("level", ""),
                        "Salary": role.get("salary", {}).get("median", 0)
                    })
            
            if timeline_data:
                df_timeline = pd.DataFrame(timeline_data)
                
                fig_timeline = px.timeline(
                    df_timeline, 
                    x_start="Start",
                    x_end="End",
                    y="Path",
                    color="Level",
                    hover_data=["Role", "Salary"],
                    title="Career Progression Timeline"
                )
                
                fig_timeline.update_layout(
                    xaxis_title="Time",
                    yaxis_title="Career Path",
                    showlegend=True
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No career path data available for this role.")
    else:
        error_message = career_path.get('error', '')
        if "404" in error_message:
            # API endpoint doesn't exist yet, use mock data
            st.info("Career path analysis is currently being developed. Showing sample data for demonstration purposes.")
            
            # Sample career path data
            st.write("Potential career paths based on your target role:")
            
            # Create a mock career path
            path = {
                "name": f"From {target_role} to Senior Roles",
                "description": "A typical progression path for your role",
                "steps": [
                    {
                        "role": target_role,
                        "timeline": "Current",
                        "description": "Build foundational skills and experience",
                        "salary": {"amount": 85000, "currency": "USD"}
                    },
                    {
                        "role": f"Senior {target_role}",
                        "timeline": "2-3 years",
                        "description": "Lead complex projects and mentor junior team members",
                        "salary": {"amount": 120000, "currency": "USD"}
                    },
                    {
                        "role": f"Lead {target_role}",
                        "timeline": "4-6 years",
                        "description": "Set technical direction and manage large initiatives",
                        "salary": {"amount": 150000, "currency": "USD"}
                    }
                ]
            }
            
            # Display mock path
            for i, step in enumerate(path.get("steps", [])):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Step {i+1}: {step.get('role')}**")
                    st.markdown(f"_Typical Timeline: {step.get('timeline')}_")
                    st.markdown(step.get("description", ""))
                with col2:
                    # Show averages
                    salary = step.get("salary", {})
                    if salary:
                        amount = salary.get("amount", 0)
                        currency = salary.get("currency", "USD")
                        st.metric("Avg. Salary", f"{amount:,} {currency}")
                
                if i < len(path.get("steps", [])) - 1:
                    st.markdown("↓")
        else:
            st.error("Failed to load career path data.") 