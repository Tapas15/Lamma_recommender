import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

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
st.title("Recommendation Feedback Analytics")
st.write("""
Analyze feedback on recommendations to understand their effectiveness and areas for improvement.
This dashboard provides insights into user satisfaction and recommendation accuracy.
""")

# Sidebar for filters
with st.sidebar:
    st.header("Filter Options")
    
    # Recommendation type filter
    recommendation_types = ["All", "jobs", "candidates", "learning", "projects", "career_path"]
    recommendation_type = st.selectbox(
        "Recommendation Type",
        options=recommendation_types,
        index=0,
        help="Filter by recommendation type"
    )
    
    # Time period filter
    time_periods = {
        "7_days": "Last 7 Days",
        "30_days": "Last 30 Days",
        "90_days": "Last 90 Days",
        "6_months": "Last 6 Months",
        "1_year": "Last Year",
        "all_time": "All Time"
    }
    
    time_period = st.selectbox(
        "Time Period",
        options=list(time_periods.keys()),
        format_func=lambda x: time_periods[x],
        index=1,  # Default to 30 days
        help="Select time period for feedback analysis"
    )
    
    # Minimum feedback count
    min_feedback_count = st.slider(
        "Minimum Feedback Count",
        min_value=1,
        max_value=100,
        value=5,
        help="Minimum number of feedback items required for analysis"
    )
    
    # Group by options
    group_by_options = ["recommendation_type", "action_taken", "day", "week", "month"]
    group_by = st.selectbox(
        "Group By",
        options=group_by_options,
        index=0,
        help="Select how to group the feedback data"
    )

# Prepare parameters
params = {
    "time_period": time_period,
    "min_feedback_count": min_feedback_count,
    "group_by": group_by
}

if recommendation_type != "All":
    params["recommendation_type"] = recommendation_type

# Get feedback summary data
with st.spinner("Loading feedback analytics..."):
    feedback_data = make_api_request("recommendations/feedback/summary", params=params)
    
    if "error" in feedback_data:
        st.error(f"Failed to get feedback summary: {feedback_data.get('error')}")
        if "detail" in feedback_data:
            st.error(f"Details: {feedback_data['detail']}")
        if st.button("Retry"):
            st.rerun()
    else:
        # Display the feedback summary
        summary = feedback_data.get("summary", {})
        feedback_groups = feedback_data.get("feedback_groups", [])
        metadata = feedback_data.get("metadata", {})
        
        # Show overall metrics
        st.subheader("Overall Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Feedback", metadata.get("total_feedback", 0))
        with col2:
            st.metric("Avg. Relevance", f"{summary.get('average_relevance_score', 0):.2f}/10")
        with col3:
            st.metric("Avg. Accuracy", f"{summary.get('average_accuracy_score', 0):.2f}/10")
        with col4:
            st.metric("Time Period", time_periods.get(time_period, time_period))
        
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["Score Trends", "Action Analysis", "Feedback Details", "Comments"])
        
        with tab1:
            st.subheader("Recommendation Score Trends")
            
            # Check if we have time-based data for trends
            has_trend_data = any(group.get("period") for group in feedback_groups)
            
            if has_trend_data and group_by in ["day", "week", "month"]:
                # Create time series data
                trend_data = []
                for group in feedback_groups:
                    if "period" in group:
                        trend_data.append({
                            "Period": group.get("period"),
                            "Relevance Score": group.get("average_relevance_score", 0),
                            "Accuracy Score": group.get("average_accuracy_score", 0),
                            "Feedback Count": group.get("feedback_count", 0)
                        })
                
                if trend_data:
                    # Convert to DataFrame and sort by period
                    df = pd.DataFrame(trend_data)
                    df["Period"] = pd.to_datetime(df["Period"])
                    df = df.sort_values("Period")
                    
                    # Create line chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=df["Period"],
                        y=df["Relevance Score"],
                        name="Relevance Score",
                        mode="lines+markers",
                        line=dict(color="blue", width=2)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df["Period"],
                        y=df["Accuracy Score"],
                        name="Accuracy Score",
                        mode="lines+markers",
                        line=dict(color="green", width=2)
                    ))
                    
                    # Add feedback count as bar chart on secondary y-axis
                    fig.add_trace(go.Bar(
                        x=df["Period"],
                        y=df["Feedback Count"],
                        name="Feedback Count",
                        opacity=0.3,
                        marker=dict(color="gray"),
                        yaxis="y2"
                    ))
                    
                    # Update layout with secondary y-axis
                    fig.update_layout(
                        title=f"Score Trends Over Time ({time_periods.get(time_period, time_period)})",
                        xaxis_title="Time Period",
                        yaxis=dict(
                            title="Score (0-10)",
                            range=[0, 10]
                        ),
                        yaxis2=dict(
                            title="Feedback Count",
                            overlaying="y",
                            side="right"
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough time-based data to show trends.")
            else:
                # Create bar chart comparing scores by group
                group_data = []
                for group in feedback_groups:
                    group_name = group.get("group_value", "Unknown")
                    group_data.append({
                        "Group": group_name,
                        "Relevance Score": group.get("average_relevance_score", 0),
                        "Accuracy Score": group.get("average_accuracy_score", 0),
                        "Feedback Count": group.get("feedback_count", 0)
                    })
                
                if group_data:
                    # Convert to DataFrame
                    df = pd.DataFrame(group_data)
                    
                    # Create grouped bar chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=df["Group"],
                        y=df["Relevance Score"],
                        name="Relevance Score",
                        marker_color="blue"
                    ))
                    
                    fig.add_trace(go.Bar(
                        x=df["Group"],
                        y=df["Accuracy Score"],
                        name="Accuracy Score",
                        marker_color="green"
                    ))
                    
                    fig.update_layout(
                        title=f"Scores by {group_by.replace('_', ' ').title()}",
                        xaxis_title=group_by.replace('_', ' ').title(),
                        yaxis_title="Average Score (0-10)",
                        yaxis=dict(range=[0, 10]),
                        barmode="group",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough grouped data to show comparison.")
        
        with tab2:
            st.subheader("User Action Analysis")
            
            # Check if we have action data
            action_data = []
            if group_by == "action_taken":
                action_data = feedback_groups
            else:
                # Try to extract action data from summary
                actions = summary.get("actions_breakdown", {})
                if actions:
                    for action, count in actions.items():
                        action_data.append({
                            "group_value": action,
                            "feedback_count": count,
                            "average_relevance_score": 0,  # We don't have this broken down by action
                            "average_accuracy_score": 0    # We don't have this broken down by action
                        })
            
            if action_data:
                # Create pie chart for actions
                action_counts = {}
                for item in action_data:
                    action = item.get("group_value", "Unknown")
                    count = item.get("feedback_count", 0)
                    action_counts[action] = count
                
                fig = px.pie(
                    values=list(action_counts.values()),
                    names=list(action_counts.keys()),
                    title="Actions Taken on Recommendations",
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Create action breakdown table
                st.write("### Action Breakdown")
                
                action_table_data = []
                for item in action_data:
                    action_table_data.append({
                        "Action": item.get("group_value", "Unknown"),
                        "Count": item.get("feedback_count", 0),
                        "Percentage": f"{(item.get('feedback_count', 0) / metadata.get('total_feedback', 1)) * 100:.1f}%"
                    })
                
                if action_table_data:
                    action_df = pd.DataFrame(action_table_data)
                    st.dataframe(action_df.sort_values("Count", ascending=False), hide_index=True)
            else:
                st.info("No action data available. Try grouping by 'action_taken'.")
        
        with tab3:
            st.subheader("Feedback Details by Group")
            
            # Display each group with details
            if feedback_groups:
                for i, group in enumerate(feedback_groups):
                    group_name = group.get("group_value", f"Group {i+1}")
                    feedback_count = group.get("feedback_count", 0)
                    
                    with st.expander(f"{group_name} ({feedback_count} feedback items)"):
                        # Create columns for metrics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Relevance Score", f"{group.get('average_relevance_score', 0):.2f}/10")
                        with col2:
                            st.metric("Accuracy Score", f"{group.get('average_accuracy_score', 0):.2f}/10")
                        with col3:
                            st.metric("Feedback Count", group.get("feedback_count", 0))
                        
                        # Action breakdown if available
                        if group.get("actions_breakdown"):
                            st.write("**Actions Breakdown:**")
                            actions_data = []
                            for action, count in group["actions_breakdown"].items():
                                actions_data.append({"Action": action, "Count": count})
                            
                            if actions_data:
                                actions_df = pd.DataFrame(actions_data)
                                st.dataframe(actions_df.sort_values("Count", ascending=False), hide_index=True)
                        
                        # Recent comments if available
                        if group.get("recent_comments"):
                            st.write("**Recent Comments:**")
                            for comment in group.get("recent_comments", []):
                                st.info(comment)
            else:
                st.info("No feedback groups available with the current filters.")
        
        with tab4:
            st.subheader("User Comments Analysis")
            
            # Display recent comments
            recent_comments = summary.get("recent_comments", [])
            if recent_comments:
                st.write("### Recent Comments")
                for comment in recent_comments:
                    st.info(comment)
            else:
                st.info("No comments available.")
            
            # Display common themes if available
            common_themes = summary.get("common_themes", [])
            if common_themes:
                st.write("### Common Themes")
                for theme in common_themes:
                    st.write(f"- {theme}")

# Additional information section
st.subheader("About Feedback Analytics")
st.write("""
Feedback analytics help us understand how users perceive our recommendations and identify areas for improvement.
Key insights from this dashboard:

- Overall satisfaction with recommendations
- Trends in relevance and accuracy scores
- Actions users take on recommendations
- Common themes in user feedback
""")

# Call to action
st.subheader("Next Steps")
col1, col2 = st.columns(2)
with col1:
    if st.button("View Learning Recommendations"):
        st.switch_page("pages/learning_recommendations.py")
with col2:
    if st.button("Explore Market Trends"):
        st.switch_page("pages/market_trends.py") 