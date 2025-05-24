#!/usr/bin/env python
"""
Test script for the skill clusters API endpoint.
This script will:
1. Login as a user
2. Test the skill clusters endpoint with various parameter combinations
3. Display the results

Usage:
    python test_skill_clusters.py
"""

import requests
import json
import sys
from tabulate import tabulate

# API configuration
BASE_URL = "http://localhost:8000"
EMAIL = "johndoe@example.com"  # Can be either employer or candidate
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
            # Try employer login if candidate login fails
            login_data["username"] = "techcorp@example.com"
            response = requests.post(f"{BASE_URL}/token", data=login_data)
            if response.status_code == 200:
                token_data = response.json()
                return token_data["access_token"]
            else:
                print(f"Employer login also failed: {response.status_code} - {response.text}")
                sys.exit(1)
    except Exception as e:
        print(f"Error during login: {str(e)}")
        sys.exit(1)

def test_skill_clusters(access_token, params=None):
    """Test the skill clusters endpoint with given parameters"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/ml/skills/clusters"
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Skill clusters request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during skill clusters request: {str(e)}")
        return None

def display_clusters(clusters_data, test_name):
    """Display skill clusters in a formatted way"""
    if not clusters_data:
        print(f"\n{test_name}: No results or error occurred")
        return
    
    print(f"\n{test_name}")
    print("=" * len(test_name))
    
    # Display metadata
    metadata = clusters_data.get("metadata", {})
    print("\nMetadata:")
    metadata_table = []
    for key, value in metadata.items():
        metadata_table.append([key, value])
    print(tabulate(metadata_table, headers=["Field", "Value"], tablefmt="grid"))
    
    # Display statistics if available
    statistics = clusters_data.get("statistics", {})
    if statistics:
        print("\nStatistics:")
        stats_table = []
        for key, value in statistics.items():
            if key not in ["skill_distribution", "industry_relevance"]:  # Skip complex nested objects
                stats_table.append([key, value])
        print(tabulate(stats_table, headers=["Statistic", "Value"], tablefmt="grid"))
    
    # Display clusters
    clusters = clusters_data.get("clusters", [])
    print(f"\nClusters ({len(clusters)}):")
    
    for i, cluster in enumerate(clusters, 1):
        print(f"\n{i}. {cluster.get('name', 'Unnamed Cluster')} (Confidence: {cluster.get('confidence', 'N/A')})")
        
        # Display skills
        skills = cluster.get("skills", [])
        print(f"   Skills ({len(skills)}): {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")
        
        # Display details if available
        details = cluster.get("details", {})
        if details:
            print("   Details:")
            core_skills = details.get("core_skills", [])
            related_skills = details.get("related_skills", [])
            
            print(f"   - Core Skills: {', '.join(core_skills[:3])}{'...' if len(core_skills) > 3 else ''}")
            print(f"   - Related Skills: {', '.join(related_skills[:3])}{'...' if len(related_skills) > 3 else ''}")
            print(f"   - Growth Rate: {details.get('growth_rate', 'N/A')}")
            print(f"   - Market Demand: {details.get('market_demand', 'N/A')}")
            
            # Display industry relevance
            industries = details.get("industry_relevance", [])
            if industries:
                print(f"   - Industries: {', '.join(industries[:3])}{'...' if len(industries) > 3 else ''}")
    
    # Note on truncation
    if len(clusters) > 5:
        print("\nNote: Only showing details for the first 5 clusters.")

def test_invalid_parameters(access_token):
    """Test the skill clusters endpoint with invalid parameters"""
    print("\nTesting Invalid Parameters")
    print("=========================")
    
    # Test invalid min_confidence
    invalid_confidence_params = {
        "min_confidence": 1.5  # Should be between 0.0 and 1.0
    }
    
    print("\nTesting with invalid min_confidence (1.5):")
    response = requests.get(
        f"{BASE_URL}/ml/skills/clusters",
        headers={"Authorization": f"Bearer {access_token}"},
        params=invalid_confidence_params
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test invalid max_clusters
    invalid_clusters_params = {
        "max_clusters": 100  # Should be between 1 and 50
    }
    
    print("\nTesting with invalid max_clusters (100):")
    response = requests.get(
        f"{BASE_URL}/ml/skills/clusters",
        headers={"Authorization": f"Bearer {access_token}"},
        params=invalid_clusters_params
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

def main():
    """Main test function"""
    print("Skill Clusters API Test")
    print("======================\n")
    
    # Login
    access_token = login()
    print("Successfully logged in")
    
    # Test 1: Default parameters
    test1_results = test_skill_clusters(access_token)
    display_clusters(test1_results, "Test 1: Default Parameters")
    
    # Test 2: Higher confidence threshold
    test2_params = {
        "min_confidence": 0.9
    }
    test2_results = test_skill_clusters(access_token, test2_params)
    display_clusters(test2_results, "Test 2: High Confidence Threshold (0.9)")
    
    # Test 3: Limited number of clusters
    test3_params = {
        "max_clusters": 5
    }
    test3_results = test_skill_clusters(access_token, test3_params)
    display_clusters(test3_results, "Test 3: Limited Clusters (5)")
    
    # Test 4: No details
    test4_params = {
        "include_details": False
    }
    test4_results = test_skill_clusters(access_token, test4_params)
    display_clusters(test4_results, "Test 4: No Details")
    
    # Test with invalid parameters
    test_invalid_parameters(access_token)
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 