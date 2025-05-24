import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

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
st.title("Market Trends Analysis")
st.write("""
Analyze market trends for skills and technologies to make informed career decisions.
This analysis helps you understand which skills are growing in demand and which industries are adopting them.
""")

# Sidebar for filters
with st.sidebar:
    st.header("Analysis Settings")
    
    # Timeframe selection
    timeframe_options = {
        "3_months": "3 Months",
        "6_months": "6 Months",
        "1_year": "1 Year",
        "2_years": "2 Years",
        "5_years": "5 Years"
    }
    
    timeframe = st.selectbox(
        "Prediction Timeframe",
        options=list(timeframe_options.keys()),
        format_func=lambda x: timeframe_options[x],
        index=2,  # Default to 1 year
        help="Select the timeframe for market trend predictions"
    )
    
    # Skill categories
    skill_categories = st.multiselect(
        "Skill Categories",
        options=["Programming", "Data Science", "Design", "Marketing", "Management", "Communication", "All"],
        default=["All"],
        help="Filter by skill categories"
    )
    
    # Number of skills to display
    max_skills = st.slider(
        "Maximum Skills",
        min_value=5,
        max_value=50,
        value=10,
        help="Maximum number of skills to display"
    )
    
    # Minimum growth rate
    min_growth = st.slider(
        "Minimum Growth Rate (%)",
        min_value=-50,
        max_value=100,
        value=0,
        help="Only show skills with growth rate above this threshold"
    )
    
    # Industry filter
    industries = st.multiselect(
        "Industries",
        options=["Technology", "Finance", "Healthcare", "Education", "E-commerce", 
                "Manufacturing", "Retail", "Media", "Consulting", "All"],
        default=["All"],
        help="Filter by industries"
    )

# Prepare parameters
params = {
    "timeframe": timeframe,
    "max_skills": max_skills,
    "min_growth": min_growth
}

if "All" not in skill_categories:
    params["categories"] = json.dumps(skill_categories)

if "All" not in industries:
    params["industries"] = json.dumps(industries)

# Get market trends data
with st.spinner("Analyzing market trends..."):
    trends_data = make_api_request("ml/market-trends", params=params)
    
    if "error" in trends_data:
        st.error(f"Failed to get market trends: {trends_data.get('error')}")
        if "detail" in trends_data:
            st.error(f"Details: {trends_data['detail']}")
        if st.button("Retry"):
            st.rerun()
    else:
        # Display the market trends
        trends = trends_data.get("trends", [])
        metadata = trends_data.get("metadata", {})
        
        # Show metadata
        st.subheader("Analysis Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Skills Analyzed", metadata.get("total_skills_analyzed", 0))
        with col2:
            st.metric("Average Growth Rate", f"{metadata.get('average_growth_rate', 0):.2f}%")
        with col3:
            st.metric("Timeframe", timeframe_options.get(timeframe, timeframe))
        
        if not trends:
            st.info("No market trends found with the current settings. Try adjusting your filters.")
        else:
            st.subheader(f"Found {len(trends)} Trending Skills")
            
            # Create tabs for different visualization options
            tab1, tab2, tab3 = st.tabs(["Growth Chart", "Skill Details", "Salary Projections"])
            
            with tab1:
                # Create growth rate chart
                st.write("### Skill Growth Rate Projections")
                
                # Prepare data for chart
                chart_data = []
                for trend in trends:
                    chart_data.append({
                        "Skill": trend.get("skill", "Unknown"),
                        "Growth Rate (%)": trend.get("growth_rate", 0),
                        "Current Demand": trend.get("current_demand", 0),
                        "Projected Demand": trend.get("projected_demand", 0),
                        "Confidence": trend.get("confidence", 0)
                    })
                
                if chart_data:
                    # Convert to DataFrame and sort
                    df = pd.DataFrame(chart_data)
                    df = df.sort_values("Growth Rate (%)", ascending=False)
                    
                    # Create bar chart
                    fig = px.bar(
                        df,
                        x="Skill",
                        y="Growth Rate (%)",
                        color="Growth Rate (%)",
                        hover_data=["Current Demand", "Projected Demand", "Confidence"],
                        color_continuous_scale=px.colors.sequential.Viridis,
                        height=500
                    )
                    
                    fig.update_layout(
                        xaxis_title="Skill",
                        yaxis_title="Projected Growth Rate (%)",
                        coloraxis_showscale=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data to create visualization.")
            
            with tab2:
                # Display each trend with details
                for i, trend in enumerate(trends):
                    with st.expander(f"{i+1}. {trend.get('skill', 'Unknown Skill')} - {trend.get('growth_rate', 0):.2f}% Growth"):
                        # Create columns for metrics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Current Demand", f"{trend.get('current_demand', 0):.2f}/10")
                        with col2:
                            st.metric("Projected Demand", f"{trend.get('projected_demand', 0):.2f}/10")
                        with col3:
                            st.metric("Confidence", f"{trend.get('confidence', 0):.2f}/10")
                        
                        # Industry relevance
                        if trend.get("industry_relevance"):
                            st.write("**Industry Relevance:**")
                            industry_data = []
                            for industry, score in trend["industry_relevance"].items():
                                industry_data.append({"Industry": industry, "Relevance": score})
                            
                            if industry_data:
                                ind_df = pd.DataFrame(industry_data)
                                st.dataframe(ind_df.sort_values("Relevance", ascending=False), hide_index=True)
                        
                        # Complementary skills
                        if trend.get("complementary_skills"):
                            st.write("**Complementary Skills:**")
                            st.write(", ".join(trend.get("complementary_skills", [])))
                        
                        # Market factors
                        if trend.get("market_factors"):
                            st.write("**Market Factors:**")
                            for factor in trend.get("market_factors", []):
                                st.write(f"- {factor}")
            
            with tab3:
                # Create salary projection chart
                st.write("### Salary Projections")
                
                # Prepare data for chart
                salary_data = []
                for trend in trends:
                    if "salary_projection" in trend:
                        salary_data.append({
                            "Skill": trend.get("skill", "Unknown"),
                            "Current Salary": trend.get("salary_projection", {}).get("current", 0),
                            "Projected Salary": trend.get("salary_projection", {}).get("projected", 0),
                            "Growth Rate (%)": trend.get("growth_rate", 0)
                        })
                
                if salary_data:
                    # Convert to DataFrame and sort
                    df = pd.DataFrame(salary_data)
                    df = df.sort_values("Projected Salary", ascending=False)
                    
                    # Create grouped bar chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=df["Skill"],
                        y=df["Current Salary"],
                        name="Current Salary",
                        marker_color='lightblue'
                    ))
                    
                    fig.add_trace(go.Bar(
                        x=df["Skill"],
                        y=df["Projected Salary"],
                        name=f"Projected Salary ({timeframe_options.get(timeframe, timeframe)})",
                        marker_color='darkblue'
                    ))
                    
                    fig.update_layout(
                        title=f"Salary Comparison: Current vs Projected ({timeframe_options.get(timeframe, timeframe)})",
                        xaxis_title="Skill",
                        yaxis_title="Annual Salary ($)",
                        barmode='group',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No salary projection data available.")

# Additional information section
st.subheader("About Market Trends Analysis")
st.write("""
Market trends analysis helps you understand how skill demand is evolving over time.
This information can guide your:

- Career development planning
- Learning path prioritization
- Job search strategy
- Salary negotiations
- Industry transition decisions
""")

# Call to action
st.subheader("Next Steps")
col1, col2 = st.columns(2)
with col1:
    if st.button("View Skill Clusters"):
        st.switch_page("pages/skill_clusters.py")
with col2:
    if st.button("Explore Learning Recommendations"):
        st.switch_page("pages/learning_recommendations.py") 