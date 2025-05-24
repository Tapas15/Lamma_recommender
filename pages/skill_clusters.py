import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

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
st.title("Skill Clusters Analysis")
st.write("""
Discover relationships between skills and identify skill clusters that are commonly found together.
This analysis helps you understand which skills complement each other and how to build a balanced skill portfolio.
""")

# Sidebar for filters
with st.sidebar:
    st.header("Analysis Settings")
    
    # Confidence threshold slider
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Minimum confidence level for skill relationships (higher = more confident)"
    )
    
    # Skill categories
    skill_categories = st.multiselect(
        "Skill Categories",
        options=["Programming", "Data Science", "Design", "Marketing", "Management", "Communication", "All"],
        default=["All"],
        help="Filter by skill categories"
    )
    
    # Number of clusters to display
    max_clusters = st.slider(
        "Maximum Clusters",
        min_value=1,
        max_value=20,
        value=5,
        help="Maximum number of skill clusters to display"
    )
    
    # Display settings
    st.subheader("Display Settings")
    show_growth_rate = st.checkbox("Show Growth Rate", value=True)
    show_industry_relevance = st.checkbox("Show Industry Relevance", value=True)
    show_market_demand = st.checkbox("Show Market Demand", value=True)

# Prepare parameters
params = {
    "confidence_threshold": confidence_threshold,
    "max_clusters": max_clusters
}

if "All" not in skill_categories:
    params["categories"] = json.dumps(skill_categories)

# Get skill clusters data
with st.spinner("Analyzing skill relationships..."):
    clusters_data = make_api_request("ml/skills/clusters", params=params)
    
    if "error" in clusters_data:
        st.error(f"Failed to get skill clusters: {clusters_data.get('error')}")
        if "detail" in clusters_data:
            st.error(f"Details: {clusters_data['detail']}")
        if st.button("Retry"):
            st.rerun()
    else:
        # Display the skill clusters
        clusters = clusters_data.get("clusters", [])
        metadata = clusters_data.get("metadata", {})
        
        # Show metadata
        st.subheader("Analysis Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Clusters", metadata.get("total_clusters", len(clusters)))
        with col2:
            st.metric("Total Skills Analyzed", metadata.get("total_skills_analyzed", 0))
        with col3:
            st.metric("Average Confidence", f"{metadata.get('average_confidence', 0):.2f}")
        
        if not clusters:
            st.info("No skill clusters found with the current settings. Try lowering the confidence threshold or selecting different categories.")
        else:
            st.subheader(f"Found {len(clusters)} Skill Clusters")
            
            # Create tabs for different visualization options
            tab1, tab2 = st.tabs(["Cluster Details", "Visualization"])
            
            with tab1:
                # Display each cluster with details
                for i, cluster in enumerate(clusters):
                    with st.expander(f"Cluster {i+1}: {cluster.get('name', f'Cluster {i+1}')}"):
                        # Core skills
                        st.write("**Core Skills:**")
                        st.write(", ".join(cluster.get("core_skills", [])))
                        
                        # Related skills
                        if cluster.get("related_skills"):
                            st.write("**Related Skills:**")
                            st.write(", ".join(cluster.get("related_skills", [])))
                        
                        # Metrics in columns
                        if show_growth_rate or show_industry_relevance or show_market_demand:
                            st.write("**Metrics:**")
                            metrics_cols = st.columns(3)
                            
                            col_idx = 0
                            if show_growth_rate and "growth_rate" in cluster:
                                with metrics_cols[col_idx]:
                                    st.metric("Growth Rate", f"{cluster['growth_rate']:.2f}%")
                                col_idx += 1
                                
                            if show_industry_relevance and "industry_relevance" in cluster:
                                with metrics_cols[col_idx]:
                                    st.metric("Industry Relevance", f"{cluster['industry_relevance']:.2f}/10")
                                col_idx += 1
                                
                            if show_market_demand and "market_demand" in cluster:
                                with metrics_cols[col_idx]:
                                    st.metric("Market Demand", f"{cluster['market_demand']:.2f}/10")
                        
                        # Confidence scores table
                        if cluster.get("confidence_scores"):
                            st.write("**Confidence Scores:**")
                            conf_data = []
                            for skill, score in cluster["confidence_scores"].items():
                                conf_data.append({"Skill": skill, "Confidence": score})
                            
                            if conf_data:
                                conf_df = pd.DataFrame(conf_data)
                                st.dataframe(conf_df.sort_values("Confidence", ascending=False), hide_index=True)
            
            with tab2:
                # Create network graph visualization
                st.write("### Skill Relationship Network")
                st.write("This visualization shows how skills are connected within clusters.")
                
                # Prepare data for network visualization
                nodes = []
                edges = []
                node_sizes = []
                node_colors = []
                
                # Color mapping for clusters
                color_scale = px.colors.qualitative.Plotly
                
                for i, cluster in enumerate(clusters):
                    cluster_color = color_scale[i % len(color_scale)]
                    
                    # Add core skills as nodes
                    for skill in cluster.get("core_skills", []):
                        if skill not in [n["name"] for n in nodes]:
                            nodes.append({
                                "name": skill,
                                "cluster": i,
                                "is_core": True
                            })
                            node_sizes.append(15)  # Larger size for core skills
                            node_colors.append(cluster_color)
                    
                    # Add related skills as nodes
                    for skill in cluster.get("related_skills", []):
                        if skill not in [n["name"] for n in nodes]:
                            nodes.append({
                                "name": skill,
                                "cluster": i,
                                "is_core": False
                            })
                            node_sizes.append(10)  # Smaller size for related skills
                            node_colors.append(cluster_color)
                    
                    # Create edges between core skills
                    core_skills = cluster.get("core_skills", [])
                    for j, skill1 in enumerate(core_skills):
                        for skill2 in core_skills[j+1:]:
                            edges.append({
                                "source": [n["name"] for n in nodes].index(skill1),
                                "target": [n["name"] for n in nodes].index(skill2),
                                "weight": 2
                            })
                    
                    # Create edges from core to related skills
                    for core_skill in core_skills:
                        for related_skill in cluster.get("related_skills", []):
                            edges.append({
                                "source": [n["name"] for n in nodes].index(core_skill),
                                "target": [n["name"] for n in nodes].index(related_skill),
                                "weight": 1
                            })
                
                # Create network graph if we have nodes
                if nodes:
                    # Create positions for nodes using a simple layout algorithm
                    # (in a real app, you might want to use a more sophisticated layout)
                    n_nodes = len(nodes)
                    radius = 1
                    angles = np.linspace(0, 2*np.pi, n_nodes, endpoint=False)
                    
                    # Adjust positions to separate clusters
                    pos = {}
                    for i, node in enumerate(nodes):
                        cluster_id = node["cluster"]
                        angle = angles[i]
                        # Offset based on cluster
                        cluster_offset = 0.3 * cluster_id
                        x = radius * np.cos(angle) + cluster_offset
                        y = radius * np.sin(angle)
                        pos[i] = (x, y)
                    
                    # Create the graph
                    edge_x = []
                    edge_y = []
                    for edge in edges:
                        x0, y0 = pos[edge["source"]]
                        x1, y1 = pos[edge["target"]]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                    
                    node_x = [pos[i][0] for i in range(n_nodes)]
                    node_y = [pos[i][1] for i in range(n_nodes)]
                    
                    # Create the figure
                    fig = go.Figure()
                    
                    # Add edges
                    fig.add_trace(go.Scatter(
                        x=edge_x, y=edge_y,
                        line=dict(width=0.5, color='#888'),
                        hoverinfo='none',
                        mode='lines'
                    ))
                    
                    # Add nodes
                    fig.add_trace(go.Scatter(
                        x=node_x, y=node_y,
                        mode='markers',
                        hoverinfo='text',
                        marker=dict(
                            showscale=False,
                            color=node_colors,
                            size=node_sizes,
                            line=dict(width=1, color='#888')
                        ),
                        text=[node["name"] for node in nodes],
                    ))
                    
                    # Update layout
                    fig.update_layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=600,
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data to create visualization.")

# Additional information section
st.subheader("About Skill Clusters")
st.write("""
Skill clusters represent groups of related skills that are commonly found together in job postings and professional profiles.
Understanding these relationships can help you:

- Identify complementary skills to develop
- Recognize skill patterns valued in your industry
- Plan your learning path more effectively
- Discover emerging skill combinations
""")

# Call to action
st.subheader("Next Steps")
col1, col2 = st.columns(2)
with col1:
    if st.button("View Skill Gap Analysis"):
        st.switch_page("pages/skill_gap.py")
with col2:
    if st.button("Explore Market Trends"):
        st.switch_page("pages/market_trends.py") 