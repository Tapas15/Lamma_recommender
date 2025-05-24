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

# Target role and industry selection
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
                "Senior Software Engineer",
                "Product Manager", 
                "UX/UI Designer"
            ]
        )

with col2:
    experience_level = st.selectbox(
        "Experience Level",
        options=["Entry-level", "Mid-level", "Senior", "Lead"]
    )

# Add industry selection
industry_options = [
    "Technology", 
    "Finance", 
    "Healthcare", 
    "Education", 
    "E-commerce", 
    "Manufacturing", 
    "Retail", 
    "Media", 
    "Consulting"
]
industry = st.selectbox("Industry", options=industry_options)

# Add option to include learning resources
include_learning_resources = st.checkbox("Include learning resources", value=True)

# Perform skill gap analysis
with st.spinner("Analyzing skill gap..."):
    skill_gap = make_api_request(
        "recommendations/skill-gap", 
        params={
            "target_role": target_role, 
            "industry": industry,
            "experience_level": experience_level,
            "include_learning_resources": str(include_learning_resources).lower()
        }
    )

if "error" not in skill_gap:
    # Match score
    match_score = skill_gap.get("match_score", 0)
    
    # Create columns for match score and market demand
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric("Match Score", f"{match_score}%")
        
        # Create gauge chart for match score
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = match_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Match Score"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, 33], 'color': "#ffcccb"},
                    {'range': [33, 66], 'color': "#ffffcc"},
                    {'range': [66, 100], 'color': "#ccffcc"}
                ]
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Market demand data
        market_demand = skill_gap.get("market_demand", {})
        if market_demand:
            st.subheader("Market Demand")
            
            demand_score = market_demand.get("demand_score", 0)
            growth_rate = market_demand.get("growth_rate", 0)
            avg_salary = market_demand.get("avg_salary", "N/A")
            
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            metrics_col1.metric("Demand Score", demand_score)
            metrics_col2.metric("Growth Rate", f"{growth_rate}%")
            metrics_col3.metric("Avg. Salary", avg_salary)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Skills Comparison", "Missing Skills", "Learning Resources", "Industry Requirements"])
    
    # Your skills and required skills
    your_skills = skill_gap.get("your_skills", [])
    required_skills = skill_gap.get("required_skills", [])
    missing_skills = skill_gap.get("missing_skills", [])
    
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
        
        # Convert to dataframe and sort
        if skill_comparison:
            df = pd.DataFrame(skill_comparison)
            df = df.sort_values(by="Gap", ascending=False)
            
            # Create bar chart
            fig = px.bar(
                df, 
                x="Skill", 
                y=["Your Proficiency", "Required Level"],
                barmode="group",
                title="Skills Comparison",
                labels={"value": "Level (0-10)", "variable": ""},
                color_discrete_map={
                    "Your Proficiency": "#1f77b4",
                    "Required Level": "#ff7f0e"
                }
            )
            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
            
            # Create table view
            st.subheader("Skills Details")
            st.dataframe(
                df.style.background_gradient(subset=["Gap"], cmap="RdYlGn_r"),
                use_container_width=True,
                hide_index=True
            )
    
    with tab2:
        # Missing skills by category
        categorized_missing_skills = skill_gap.get("categorized_missing_skills", {})
        
        if categorized_missing_skills:
            st.subheader("Missing Skills by Category")
            
            # Create pie chart for categories
            categories = list(categorized_missing_skills.keys())
            category_counts = [len(skills) for skills in categorized_missing_skills.values()]
            
            if sum(category_counts) > 0:
                fig = px.pie(
                    values=category_counts,
                    names=categories,
                    title="Missing Skills Distribution",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            
            # Display categorized skills
            for category, skills in categorized_missing_skills.items():
                if skills:
                    with st.expander(f"{category.title()} Skills ({len(skills)})", expanded=True):
                        # Create a dataframe for the skills
                        skill_data = []
                        for skill in skills:
                            skill_data.append({
                                "Skill": skill.get("name"),
                                "Importance": skill.get("importance")
                            })
                        
                        if skill_data:
                            df = pd.DataFrame(skill_data)
                            df = df.sort_values(by="Importance", ascending=False)
                            
                            # Display as a bar chart
                            fig = px.bar(
                                df,
                                x="Skill",
                                y="Importance",
                                title=f"{category.title()} Skills",
                                color="Importance",
                                color_continuous_scale="Viridis"
                            )
                            st.plotly_chart(fig, use_container_width=True)
        else:
            # Display missing skills as before
            if missing_skills:
                st.subheader("Missing Skills")
                
                # Create a dataframe for missing skills
                missing_skill_data = []
                for skill in missing_skills:
                    missing_skill_data.append({
                        "Skill": skill.get("name"),
                        "Importance": skill.get("importance")
                    })
                
                if missing_skill_data:
                    df = pd.DataFrame(missing_skill_data)
                    df = df.sort_values(by="Importance", ascending=False)
                    
                    # Display as a bar chart
                    fig = px.bar(
                        df,
                        x="Skill",
                        y="Importance",
                        title="Missing Skills",
                        color="Importance",
                        color_continuous_scale="Viridis"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display as a table
                    st.dataframe(
                        df.style.background_gradient(subset=["Importance"], cmap="Viridis"),
                        use_container_width=True,
                        hide_index=True
                    )
            else:
                st.success("You have all the required skills!")
    
    with tab3:
        # Learning recommendations
        st.subheader("Learning Resources")
        if include_learning_resources:
            learning_resources = skill_gap.get("learning_resources", {}).get("resources", [])
            
            if learning_resources:
                for resource in learning_resources:
                    skill = resource.get("skill")
                    resources_list = resource.get("resources", [])
                    
                    st.markdown(f"### {skill}")
                    for res in resources_list:
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
            st.info("Enable 'Include learning resources' option to see personalized learning recommendations.")
    
    with tab4:
        # Industry-specific requirements
        st.subheader(f"Industry-Specific Requirements for {industry}")
        industry_specific = skill_gap.get("industry_specific_requirements", [])
        
        if industry_specific:
            # Create a dataframe for industry-specific skills
            industry_skill_data = []
            for skill in industry_specific:
                industry_skill_data.append({
                    "Skill": skill.get("name"),
                    "Importance": skill.get("importance")
                })
            
            if industry_skill_data:
                df = pd.DataFrame(industry_skill_data)
                df = df.sort_values(by="Importance", ascending=False)
                
                # Display as a bar chart
                fig = px.bar(
                    df,
                    x="Skill",
                    y="Importance",
                    title=f"{industry} Industry Skills for {target_role}",
                    color="Importance",
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display as a table
                st.dataframe(
                    df.style.background_gradient(subset=["Importance"], cmap="Viridis"),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Check if you have these skills
                your_skill_names = [s.get("name") for s in your_skills]
                industry_skill_names = [s.get("name") for s in industry_specific]
                
                missing_industry_skills = [s for s in industry_skill_names if s not in your_skill_names]
                
                if missing_industry_skills:
                    st.warning(f"You're missing {len(missing_industry_skills)} out of {len(industry_skill_names)} industry-specific skills.")
                else:
                    st.success("You have all the industry-specific skills!")
        else:
            st.info(f"No specific skill requirements found for {target_role} in the {industry} industry.")
else:
    error_message = skill_gap.get('error', '')
    st.error(f"Failed to analyze skill gap: {error_message}")

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