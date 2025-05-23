import streamlit as st
import requests
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

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

# Set page title
st.title("Career Path Explorer")

# Explanation
st.write("""
Discover possible career paths based on your current profile and interests.
Explore different roles, required skills, and typical progression timelines.
""")

# Get profile data
profile = make_api_request("profile")
if "error" in profile:
    st.error("Failed to load your profile data.")
    profile = {}

# Current role and industry selections
col1, col2 = st.columns(2)
with col1:
    # Extract current role from profile or allow selection
    default_role = profile.get("current_role", "Software Engineer")
    
    # Get job roles from API
    job_roles = make_api_request("job-roles")
    if "error" not in job_roles:
        # Handle both list and dictionary responses
        if isinstance(job_roles, list):
            role_options = [role.get("title") for role in job_roles]
        else:
            role_options = [role.get("title") for role in job_roles.get("items", [])]
            
        current_role = st.selectbox(
            "Your Current Role:",
            options=role_options,
            index=role_options.index(default_role) if default_role in role_options else 0
        )
    else:
        # Fallback if API fails
        current_role = st.selectbox(
            "Your Current Role:",
            options=[
                "Software Engineer", 
                "Data Scientist", 
                "Frontend Developer", 
                "Backend Developer",
                "Full Stack Developer", 
                "DevOps Engineer", 
                "Product Manager", 
                "UX/UI Designer"
            ],
            index=0
        )

with col2:
    # Get industries from API
    industries_data = make_api_request("industries")
    if "error" not in industries_data:
        # Handle both list and dictionary responses
        if isinstance(industries_data, list):
            industry_options = [ind.get("name") for ind in industries_data]
        else:
            industry_options = [ind.get("name") for ind in industries_data.get("items", [])]
            
        current_industry = st.selectbox(
            "Industry:",
            options=industry_options
        )
    else:
        # Fallback if API fails
        current_industry = st.selectbox(
            "Industry:",
            options=[
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
        )

# Additional preferences
career_goal = st.selectbox(
    "Career Goal:",
    options=[
        "Technical Leadership", 
        "Management", 
        "Individual Contributor", 
        "Entrepreneurship", 
        "Career Change"
    ]
)

# Load career path data
with st.spinner("Loading career paths..."):
    career_paths = make_api_request(
        "recommendations/career-path", 
        params={
            "current_role": current_role,
            "industry": current_industry,
            "career_goal": career_goal
        }
    )

if "error" in career_paths:
    error_message = career_paths.get('error', '')
    if "404" in error_message:
        # API endpoint doesn't exist yet, use mock data
        st.info("Career paths data is currently being developed. Showing sample data for demonstration purposes.")
        
        # Sample mock career path data
        career_paths = {
            "paths": [
                {
                    "name": f"From {current_role} to Technical Lead",
                    "description": "This path focuses on technical excellence and leadership within engineering teams.",
                    "average_time_years": 5,
                    "salary_growth_percentage": 40,
                    "difficulty": 7,
                    "steps": [
                        {
                            "role": current_role,
                            "timeline": "Current",
                            "description": "Your current role, focusing on building expertise.",
                            "skills": ["Python", "JavaScript", "System Design", "Problem Solving"],
                            "responsibilities": ["Develop features", "Fix bugs", "Write tests"],
                            "avg_salary": {"amount": 90000, "currency": "USD"},
                            "experience_required": 2
                        },
                        {
                            "role": f"Senior {current_role}",
                            "timeline": "2-3 years",
                            "description": "Lead technical implementation of complex features.",
                            "skills": ["Architecture", "Mentoring", "Advanced algorithms", "Performance optimization"],
                            "responsibilities": ["Design solutions", "Review code", "Mentor juniors"],
                            "avg_salary": {"amount": 120000, "currency": "USD"},
                            "experience_required": 5,
                            "transition_advice": "Focus on system design skills and take on more ownership of features"
                        },
                        {
                            "role": "Technical Lead",
                            "timeline": "2-3 years after Senior",
                            "description": "Lead a team of engineers, setting technical direction.",
                            "skills": ["Team Leadership", "Project Management", "Technical Strategy", "Cross-team collaboration"],
                            "responsibilities": ["Set technical vision", "Unblock team", "Manage project timelines"],
                            "avg_salary": {"amount": 150000, "currency": "USD"},
                            "experience_required": 8,
                            "transition_advice": "Take ownership of larger initiatives and demonstrate leadership skills",
                            "growth_opportunities": ["Principal Engineer", "Engineering Manager", "CTO"]
                        }
                    ]
                },
                {
                    "name": f"From {current_role} to Engineering Manager",
                    "description": "This path transitions from technical focus to people leadership.",
                    "average_time_years": 6,
                    "salary_growth_percentage": 45,
                    "difficulty": 8,
                    "steps": [
                        {
                            "role": current_role,
                            "timeline": "Current",
                            "description": "Your current role, focusing on building expertise.",
                            "skills": ["Python", "JavaScript", "System Design", "Problem Solving"],
                            "responsibilities": ["Develop features", "Fix bugs", "Write tests"],
                            "avg_salary": {"amount": 90000, "currency": "USD"},
                            "experience_required": 2
                        },
                        {
                            "role": f"Senior {current_role}",
                            "timeline": "2-3 years",
                            "description": "Technical leadership with mentoring responsibilities.",
                            "skills": ["Architecture", "Mentoring", "Communication", "Code Review"],
                            "responsibilities": ["Design solutions", "Review code", "Mentor juniors"],
                            "avg_salary": {"amount": 120000, "currency": "USD"},
                            "experience_required": 5,
                            "transition_advice": "Focus on mentoring and developing your communication skills"
                        },
                        {
                            "role": "Engineering Manager",
                            "timeline": "3-4 years after Senior",
                            "description": "Lead a team of engineers with focus on people management.",
                            "skills": ["People Management", "Hiring", "Performance Reviews", "Project Planning"],
                            "responsibilities": ["Grow team", "Performance management", "Resource planning"],
                            "avg_salary": {"amount": 160000, "currency": "USD"},
                            "experience_required": 8,
                            "transition_advice": "Start taking on people management responsibilities and work closely with your manager",
                            "growth_opportunities": ["Director of Engineering", "VP of Engineering", "CTO"]
                        }
                    ]
                }
            ]
        }
    else:
        st.error(f"Failed to load career paths: {error_message}")
else:
    paths = career_paths.get("paths", [])
    
    if not paths:
        st.info("No career paths found with the current selections. Try adjusting your preferences.")
    else:
        # Display career paths as tabs
        path_tabs = st.tabs([f"Path {i+1}: {path.get('name', f'Option {i+1}')}" for i, path in enumerate(paths)])
        
        for i, tab in enumerate(path_tabs):
            with tab:
                path = paths[i]
                
                # Path overview
                st.subheader(path.get("name", f"Career Path {i+1}"))
                st.write(path.get("description", ""))
                
                # Path metrics
                metrics_cols = st.columns(3)
                with metrics_cols[0]:
                    avg_time = path.get("average_time_years", "N/A")
                    st.metric("Avg. Time to Complete", f"{avg_time} years" if avg_time != "N/A" else "N/A")
                with metrics_cols[1]:
                    salary_growth = path.get("salary_growth_percentage", "N/A")
                    st.metric("Salary Growth", f"{salary_growth}%" if salary_growth != "N/A" else "N/A")
                with metrics_cols[2]:
                    difficulty = path.get("difficulty", "N/A")
                    st.metric("Difficulty", f"{difficulty}/10" if difficulty != "N/A" else "N/A")
                
                # Path steps
                st.subheader("Career Progression Steps")
                
                steps = path.get("steps", [])
                if steps:
                    # Create a simple visual representation of the path
                    if len(steps) > 1:
                        # Create a network graph of the career path
                        G = nx.DiGraph()
                        
                        # Add nodes and edges
                        for j, step in enumerate(steps):
                            G.add_node(j, role=step.get("role", f"Role {j+1}"))
                            if j > 0:
                                G.add_edge(j-1, j)
                        
                        # Create plot
                        plt.figure(figsize=(10, 4))
                        pos = {i: (i, 0) for i in range(len(steps))}  # Position nodes in a line
                        
                        # Create custom colormap for nodes based on progression
                        colors = LinearSegmentedColormap.from_list("career_progress", ["#4285F4", "#EA4335"])
                        node_colors = [colors(j/(len(steps)-1)) for j in range(len(steps))]
                        
                        # Draw the graph
                        nx.draw(
                            G, 
                            pos,
                            with_labels=True,
                            labels={j: data["role"] for j, data in G.nodes(data=True)},
                            node_color=node_colors,
                            node_size=2500,
                            font_size=10,
                            font_color="white",
                            font_weight="bold",
                            arrowsize=20,
                            edge_color="#666666",
                            width=2.0
                        )
                        
                        # Save figure to buffer and display with st.pyplot
                        buffer = plt.gcf()
                        st.pyplot(buffer)
                        plt.close()
                    
                    # Display details for each step
                    for j, step in enumerate(steps):
                        with st.expander(f"Step {j+1}: {step.get('role')}", expanded=j == 0):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**Role:** {step.get('role')}")
                                st.markdown(f"**Timeline:** {step.get('timeline', 'N/A')}")
                                st.markdown(step.get("description", ""))
                                
                                # Required skills for this step
                                skills = step.get("skills", [])
                                if skills:
                                    st.markdown("**Key Skills Required:**")
                                    for skill in skills:
                                        st.markdown(f"- {skill}")
                                
                                # Responsibilities
                                responsibilities = step.get("responsibilities", [])
                                if responsibilities:
                                    st.markdown("**Key Responsibilities:**")
                                    for resp in responsibilities:
                                        st.markdown(f"- {resp}")
                            
                            with col2:
                                # Salary information
                                avg_salary = step.get("avg_salary", {})
                                if avg_salary:
                                    amount = avg_salary.get("amount", 0)
                                    currency = avg_salary.get("currency", "USD")
                                    st.metric("Avg. Salary", f"{amount:,} {currency}")
                                
                                # Experience required
                                exp = step.get("experience_required", "N/A")
                                st.metric("Experience", f"{exp} years" if exp != "N/A" else "N/A")
                            
                            # Transition advice
                            if j > 0:
                                transition = step.get("transition_advice", "")
                                if transition:
                                    st.markdown("**Transition Advice:**")
                                    st.info(transition)
                            
                            # Growth opportunities
                            growth = step.get("growth_opportunities", [])
                            if growth:
                                st.markdown("**Growth Opportunities:**")
                                for opp in growth:
                                    st.markdown(f"- {opp}")
                
                # Path comparison
                if i == len(paths) - 1:  # On the last tab, show path comparison
                    st.subheader("Path Comparison")
                    
                    # Create comparison dataframe
                    comparison_data = []
                    for p, path in enumerate(paths):
                        comparison_data.append({
                            "Path": path.get("name", f"Path {p+1}"),
                            "Avg. Time (Years)": path.get("average_time_years", "N/A"),
                            "Salary Growth": f"{path.get('salary_growth_percentage', 'N/A')}%",
                            "Difficulty (1-10)": path.get("difficulty", "N/A"),
                            "Steps": len(path.get("steps", [])),
                            "End Role": path.get("steps", [])[-1].get("role", "N/A") if path.get("steps", []) else "N/A"
                        })
                    
                    # Display comparison table
                    if comparison_data:
                        st.dataframe(pd.DataFrame(comparison_data), hide_index=True)

# Skills recommendation section
st.subheader("Skills for Career Advancement")

# Get skill recommendations
skill_recs = make_api_request(
    "recommendations/skill-development",
    params={"target_role": current_role, "career_goal": career_goal}
)

if "error" not in skill_recs:
    skills = skill_recs.get("recommended_skills", [])
    if skills:
        st.write("Focus on developing these skills to advance in your career path:")
        
        # Display skills as a table with demand and growth trend
        skill_data = []
        for skill in skills:
            skill_data.append({
                "Skill": skill.get("name", ""),
                "Demand Score": skill.get("demand_score", 0),
                "Growth Trend": f"{skill.get('growth_trend', 0)}%",
                "Category": skill.get("category", "Technical")
            })
        
        # Create DataFrame and display
        if skill_data:
            df = pd.DataFrame(skill_data)
            st.dataframe(
                df.style.background_gradient(subset=['Demand Score'], cmap='YlGn'),
                hide_index=True
            )
    else:
        st.info("No specific skill recommendations available.")
else:
    error_message = skill_recs.get('error', '')
    if "404" in error_message:
        # API endpoint doesn't exist yet, use mock data
        st.info("Skill development recommendations are currently being developed. Showing sample data for demonstration purposes.")
        
        # Sample mock skills data
        sample_skills = [
            {"name": "System Architecture", "demand_score": 8, "growth_trend": 15, "category": "Technical"},
            {"name": "Cloud Services (AWS/Azure)", "demand_score": 9, "growth_trend": 20, "category": "Technical"},
            {"name": "CI/CD Pipelines", "demand_score": 7, "growth_trend": 12, "category": "DevOps"},
            {"name": "Team Leadership", "demand_score": 8, "growth_trend": 10, "category": "Soft Skills"},
            {"name": "Microservices", "demand_score": 8, "growth_trend": 18, "category": "Architecture"}
        ]
        
        st.write("Focus on developing these skills to advance in your career path:")
        
        # Display skills as a table with demand and growth trend
        skill_data = []
        for skill in sample_skills:
            skill_data.append({
                "Skill": skill.get("name", ""),
                "Demand Score": skill.get("demand_score", 0),
                "Growth Trend": f"{skill.get('growth_trend', 0)}%",
                "Category": skill.get("category", "Technical")
            })
        
        # Create DataFrame and display
        if skill_data:
            df = pd.DataFrame(skill_data)
            st.dataframe(
                df.style.background_gradient(subset=['Demand Score'], cmap='YlGn'),
                hide_index=True
            )
    else:
        st.error("Failed to load skill recommendations.")

# Learning resources section
st.subheader("Learning Resources")
st.write("Resources to help you develop the skills needed for your career path:")

# Mock learning resources (this would normally come from the API)
categories = ["Courses", "Books", "Communities", "Certifications"]
resource_tabs = st.tabs(categories)

with resource_tabs[0]:  # Courses
    st.markdown("### Online Courses")
    courses = [
        {"title": "Leadership in Tech", "provider": "Coursera", "link": "https://coursera.org"},
        {"title": "Advanced Cloud Architecture", "provider": "Udemy", "link": "https://udemy.com"},
        {"title": "System Design for Senior Engineers", "provider": "edX", "link": "https://edx.org"}
    ]
    
    for course in courses:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{course['title']}**")
            st.markdown(f"_{course['provider']}_")
        with col2:
            st.link_button("View", course["link"])
        st.divider()

with resource_tabs[1]:  # Books
    st.markdown("### Recommended Books")
    books = [
        {"title": "The Manager's Path", "author": "Camille Fournier"},
        {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann"},
        {"title": "Staff Engineer: Leadership Beyond the Management Track", "author": "Will Larson"}
    ]
    
    for book in books:
        st.markdown(f"**{book['title']}** - {book['author']}")
    
with resource_tabs[2]:  # Communities
    st.markdown("### Professional Communities")
    communities = [
        {"name": "Tech Leadership Network", "type": "Online Forum"},
        {"name": "Senior Engineers Hub", "type": "Slack Community"},
        {"name": "Women in Tech Leadership", "type": "Networking Group"}
    ]
    
    for community in communities:
        st.markdown(f"**{community['name']}** ({community['type']})")

with resource_tabs[3]:  # Certifications
    st.markdown("### Valuable Certifications")
    certs = [
        {"name": "AWS Solutions Architect", "org": "Amazon Web Services"},
        {"name": "Google Cloud Professional Engineer", "org": "Google"},
        {"name": "Project Management Professional (PMP)", "org": "PMI"}
    ]
    
    for cert in certs:
        st.markdown(f"**{cert['name']}** - {cert['org']}")

# Feedback section
st.subheader("Provide Feedback")
st.write("Your feedback helps us improve career recommendations:")

with st.form("career_feedback_form"):
    feedback_rating = st.slider("How helpful was this career path information?", 1, 5, 3)
    feedback_text = st.text_area("Additional feedback or suggestions:")
    submit_button = st.form_submit_button("Submit Feedback")

if submit_button:
    # Send feedback to API
    feedback_data = {
        "rating": feedback_rating,
        "comments": feedback_text,
        "feature": "career_paths"
    }
    
    result = make_api_request("feedback", method="POST", data=feedback_data)
    
    if "error" not in result:
        st.success("Thank you for your feedback!")
    else:
        st.error("Failed to submit feedback. Please try again later.") 