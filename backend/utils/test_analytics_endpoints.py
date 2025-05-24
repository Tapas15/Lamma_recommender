#!/usr/bin/env python
"""
Test script for the analytics API endpoints.
This script will:
1. Login as a user
2. Test the recommendation impact metrics endpoint
3. Test the recommendation algorithm performance endpoint
4. Display the results

Usage:
    python test_analytics_endpoints.py
"""

import requests
import json
import sys
from tabulate import tabulate
import matplotlib.pyplot as plt
from datetime import datetime

# API configuration
BASE_URL = "http://localhost:8000"
EMAIL = "testemployer@example.com"  # Can be either employer or candidate
PASSWORD = "password123"

def login():
    """Login and get access token"""
    print("Logging in...")
    
    login_data = {
        "username": EMAIL,
        "password": PASSWORD,
    }
    
    try:
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Error during login: {str(e)}")
        sys.exit(1)

def test_recommendation_impact(access_token, period="last_30_days", recommendation_type="all"):
    """Test the recommendation impact metrics endpoint"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/analytics/recommendations/impact"
    params = {
        "period": period,
        "recommendation_type": recommendation_type
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Recommendation impact metrics request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during recommendation impact metrics request: {str(e)}")
        return None

def test_algorithm_performance(access_token, algorithm_version="latest"):
    """Test the recommendation algorithm performance endpoint"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/analytics/recommendations/performance"
    params = {
        "algorithm_version": algorithm_version
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Algorithm performance request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during algorithm performance request: {str(e)}")
        return None

def display_impact_metrics(metrics, test_name):
    """Display recommendation impact metrics in a formatted way"""
    if not metrics:
        print(f"\n{test_name}: No results or error occurred")
        return
    
    print(f"\n{test_name}")
    print("=" * len(test_name))
    
    # Display period information
    period = metrics.get("period", {})
    period_name = period.get("name", "N/A")
    start_date = period.get("start_date", "N/A")
    end_date = period.get("end_date", "N/A")
    
    print(f"Period: {period_name} ({start_date} to {end_date})")
    print(f"Recommendation Type: {metrics.get('recommendation_type', 'all')}")
    
    # Display summary metrics
    summary = metrics.get("summary", {})
    if summary:
        print("\nSummary Metrics:")
        summary_data = []
        for key, value in summary.items():
            # Format conversion rate as percentage
            if "rate" in key and isinstance(value, (int, float)):
                summary_data.append([key.replace("_", " ").title(), f"{value:.1%}"])
            else:
                summary_data.append([key.replace("_", " ").title(), value])
        print(tabulate(summary_data, headers=["Metric", "Value"], tablefmt="grid"))
    
    # Display recommendation-specific metrics
    for rec_type in ["candidates", "jobs", "projects"]:
        if rec_type in metrics:
            print(f"\n{rec_type.title()} Metrics:")
            rec_data = []
            for key, value in metrics[rec_type].items():
                # Format rates as percentages
                if "rate" in key and isinstance(value, (int, float)):
                    rec_data.append([key.replace("_", " ").title(), f"{value:.1%}"])
                else:
                    rec_data.append([key.replace("_", " ").title(), value])
            print(tabulate(rec_data, headers=["Metric", "Value"], tablefmt="grid"))
    
    # Display top performing items
    top_performing = metrics.get("top_performing", [])
    if top_performing:
        print("\nTop Performing Items:")
        for item in top_performing:
            item_type = item.get("type", "").title()
            item_name = item.get("name", item.get("title", "Unknown"))
            print(f"\n{item_type}: {item_name}")
            
            item_metrics = item.get("metrics", {})
            if item_metrics:
                item_data = []
                for key, value in item_metrics.items():
                    # Format rates as percentages
                    if "rate" in key and isinstance(value, (int, float)):
                        item_data.append([key.replace("_", " ").title(), f"{value:.1%}"])
                    else:
                        item_data.append([key.replace("_", " ").title(), value])
                print(tabulate(item_data, headers=["Metric", "Value"], tablefmt="grid"))
    
    # Display trend data
    trends = metrics.get("trends", {})
    if trends:
        dates = trends.get("dates", [])
        views = trends.get("views", [])
        actions = trends.get("actions", [])
        match_scores = trends.get("match_scores", [])
        
        if dates and (views or actions or match_scores):
            print(f"\nTrend Data ({trends.get('interval', 'daily')}):")
            
            # Create a simple table of trend data
            trend_data = []
            for i in range(min(len(dates), 7)):  # Show only the last 7 data points
                row = [dates[i]]
                if i < len(views):
                    row.append(views[i])
                else:
                    row.append("N/A")
                    
                if i < len(actions):
                    row.append(actions[i])
                else:
                    row.append("N/A")
                    
                if i < len(match_scores):
                    row.append(match_scores[i])
                else:
                    row.append("N/A")
                    
                trend_data.append(row)
            
            headers = ["Date", "Views", "Actions", "Match Score"]
            print(tabulate(trend_data, headers=headers, tablefmt="grid"))
            print("Note: Showing only the last 7 data points. Full data available in the API response.")

def display_algorithm_performance(metrics, test_name):
    """Display algorithm performance metrics in a formatted way"""
    if not metrics:
        print(f"\n{test_name}: No results or error occurred")
        return
    
    print(f"\n{test_name}")
    print("=" * len(test_name))
    
    # Display basic info
    version = metrics.get("algorithm_version", "N/A")
    last_updated = metrics.get("last_updated", "N/A")
    
    print(f"Algorithm Version: {version}")
    print(f"Last Updated: {last_updated}")
    
    # Display overall metrics
    print("\nOverall Metrics:")
    overall_metrics = [
        ["Accuracy", metrics.get("overall_accuracy", "N/A")],
        ["Precision", metrics.get("precision", "N/A")],
        ["Recall", metrics.get("recall", "N/A")],
        ["F1 Score", metrics.get("f1_score", "N/A")],
        ["Average Match Score", metrics.get("average_match_score", "N/A")]
    ]
    print(tabulate(overall_metrics, headers=["Metric", "Value"], tablefmt="grid"))
    
    # Display recommendation type specific metrics
    rec_types = metrics.get("recommendation_types", {})
    if rec_types:
        print("\nMetrics by Recommendation Type:")
        
        # Create a comparison table
        headers = ["Metric"]
        for rec_type in rec_types:
            headers.append(rec_type.title())
        
        rows = []
        metrics_to_compare = ["accuracy", "precision", "recall", "f1_score", "average_match_score"]
        
        for metric in metrics_to_compare:
            row = [metric.replace("_", " ").title()]
            for rec_type, rec_metrics in rec_types.items():
                row.append(rec_metrics.get(metric, "N/A"))
            rows.append(row)
        
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    # Display embedding metrics
    embedding_metrics = metrics.get("embedding_metrics", {})
    if embedding_metrics:
        print("\nEmbedding Metrics:")
        embedding_data = []
        for key, value in embedding_metrics.items():
            embedding_data.append([key.replace("_", " ").title(), value])
        print(tabulate(embedding_data, headers=["Metric", "Value"], tablefmt="grid"))
    
    # Display version comparison
    version_comparison = metrics.get("version_comparison", [])
    if version_comparison:
        print("\nVersion Comparison:")
        version_data = []
        for ver in version_comparison:
            version_data.append([
                ver.get("version", "N/A"),
                ver.get("accuracy", "N/A"),
                ver.get("improvement", "N/A")
            ])
        print(tabulate(version_data, headers=["Version", "Accuracy", "Improvement"], tablefmt="grid"))

def main():
    """Main test function"""
    print("Analytics API Endpoints Test")
    print("===========================\n")
    
    # Login
    access_token = login()
    if not access_token:
        return
    
    print("Successfully logged in")
    
    # Test 1: Recommendation impact metrics with default parameters
    test1_results = test_recommendation_impact(access_token)
    display_impact_metrics(test1_results, "Test 1: Default Recommendation Impact Metrics")
    
    # Test 2: Recommendation impact metrics for candidates only
    test2_results = test_recommendation_impact(access_token, recommendation_type="candidates")
    display_impact_metrics(test2_results, "Test 2: Candidate Recommendation Impact Metrics")
    
    # Test 3: Recommendation impact metrics for last 7 days
    test3_results = test_recommendation_impact(access_token, period="last_7_days")
    display_impact_metrics(test3_results, "Test 3: Last 7 Days Impact Metrics")
    
    # Test 4: Algorithm performance with default parameters
    test4_results = test_algorithm_performance(access_token)
    display_algorithm_performance(test4_results, "Test 4: Default Algorithm Performance")
    
    # Test 5: Algorithm performance for v1
    test5_results = test_algorithm_performance(access_token, algorithm_version="v1")
    display_algorithm_performance(test5_results, "Test 5: V1 Algorithm Performance")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 