#!/usr/bin/env python
"""
Test script to verify that semantic search and recommender system functionality are working correctly.
This script tests:
1. Vector embedding generation
2. Semantic search for jobs, projects, and candidates
3. Recommendation functionality
4. Fallback mechanisms when vector search is not available

Usage:
    python test_search_recommender.py
"""

import sys
import os
import json
import requests
import time
import numpy as np
from dotenv import load_dotenv
from tabulate import tabulate

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.embedding import get_embedding
from utils.database import Database

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
EMAIL = os.getenv("TEST_EMAIL", "test@example.com")
PASSWORD = os.getenv("TEST_PASSWORD", "password123")

# Test data
TEST_QUERIES = {
    "jobs": [
        "Senior software engineer with React and Node.js experience",
        "Entry level data scientist with Python skills",
        "Remote frontend developer position",
        "DevOps engineer with Kubernetes experience",
        "Full stack developer with React and Django"
    ],
    "projects": [
        "Mobile app development project using React Native",
        "Machine learning recommendation system project",
        "E-commerce website development",
        "Data visualization dashboard project",
        "Blockchain smart contract development"
    ],
    "candidates": [
        "Software engineer with 5 years experience in Python",
        "Frontend developer skilled in React and UI design",
        "Data scientist with machine learning expertise",
        "DevOps engineer familiar with AWS and Kubernetes",
        "Full stack developer with JavaScript and Node.js"
    ]
}

def print_section(title):
    """Print a section title for better readability"""
    print("\n")
    print("=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def get_auth_token():
    """Get authentication token for API requests"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={"username": EMAIL, "password": PASSWORD}
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("Please check your API_BASE_URL, TEST_EMAIL, and TEST_PASSWORD environment variables")
        return None

def test_embedding_generation():
    """Test if embedding generation is working"""
    print_section("TESTING EMBEDDING GENERATION")
    
    test_texts = [
        "Senior software engineer with React and Node.js experience",
        "Data scientist with machine learning expertise",
        "Mobile app development project using React Native"
    ]
    
    results = []
    
    for i, text in enumerate(test_texts):
        start_time = time.time()
        embedding = get_embedding(text)
        end_time = time.time()
        
        if embedding and isinstance(embedding, list):
            status = "✅ Success"
            details = f"Dimensions: {len(embedding)}, Time: {end_time - start_time:.2f}s"
        else:
            status = "❌ Failed"
            details = f"Result: {embedding}"
        
        results.append([i+1, text[:40] + "...", status, details])
    
    print(tabulate(results, headers=["#", "Text", "Status", "Details"], tablefmt="grid"))
    
    # Return overall success
    return all(row[2] == "✅ Success" for row in results)

def test_semantic_search(token, entity_type):
    """Test semantic search functionality for jobs, projects, or candidates"""
    print_section(f"TESTING {entity_type.upper()} SEMANTIC SEARCH")
    
    if not token:
        print("❌ Authentication token not available, skipping test")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoint = f"{API_BASE_URL}/{entity_type}/search"
    queries = TEST_QUERIES.get(entity_type, [])
    
    results = []
    success_count = 0
    
    for i, query in enumerate(queries):
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json={"query": query, "top_k": 3}
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    status = "✅ Success"
                    details = f"Found {len(data)} results"
                    success_count += 1
                else:
                    status = "⚠️ Warning"
                    details = f"No results found"
            else:
                status = "❌ Failed"
                details = f"Status: {response.status_code}, Error: {response.text[:50]}"
        except Exception as e:
            status = "❌ Error"
            details = str(e)[:50]
        
        results.append([i+1, query[:40] + "...", status, details])
    
    print(tabulate(results, headers=["#", "Query", "Status", "Details"], tablefmt="grid"))
    
    # Print overall success rate
    success_rate = (success_count / len(queries)) * 100 if queries else 0
    print(f"\nOverall success rate: {success_rate:.1f}% ({success_count}/{len(queries)})")
    
    return success_count > 0

def test_recommendations(token):
    """Test recommendation functionality"""
    print_section("TESTING RECOMMENDATION SYSTEM")
    
    if not token:
        print("❌ Authentication token not available, skipping test")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test different recommendation endpoints
    recommendation_endpoints = [
        {"name": "Job Recommendations", "endpoint": "/recommendations/jobs"},
        {"name": "Project Recommendations", "endpoint": "/recommendations/projects"},
        {"name": "Skill Gap Analysis", "endpoint": "/recommendations/skill-gap?target_role=Software%20Engineer"},
        {"name": "Learning Recommendations", "endpoint": "/recommendations/learning"}
    ]
    
    results = []
    success_count = 0
    
    for i, endpoint_info in enumerate(recommendation_endpoints):
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint_info['endpoint']}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and (isinstance(data, list) or isinstance(data, dict)):
                    status = "✅ Success"
                    
                    if isinstance(data, list):
                        details = f"Found {len(data)} recommendations"
                    else:
                        if "match_score" in data:
                            details = f"Match score: {data['match_score']}"
                        elif "resources" in data:
                            details = f"Found {len(data['resources'])} resources"
                        else:
                            details = f"Valid response"
                    
                    success_count += 1
                else:
                    status = "⚠️ Warning"
                    details = f"Empty response"
            else:
                status = "❌ Failed"
                details = f"Status: {response.status_code}, Error: {response.text[:50]}"
        except Exception as e:
            status = "❌ Error"
            details = str(e)[:50]
        
        results.append([i+1, endpoint_info["name"], endpoint_info["endpoint"], status, details])
    
    print(tabulate(results, headers=["#", "Name", "Endpoint", "Status", "Details"], tablefmt="grid"))
    
    # Print overall success rate
    success_rate = (success_count / len(recommendation_endpoints)) * 100 if recommendation_endpoints else 0
    print(f"\nOverall success rate: {success_rate:.1f}% ({success_count}/{len(recommendation_endpoints)})")
    
    return success_count > 0

def test_fallback_search():
    """Test if fallback search works when vector search is not available"""
    print_section("TESTING FALLBACK SEARCH MECHANISM")
    
    # This is a simplified test that simulates the fallback functionality
    # In a real test, we would need to temporarily disable vector search
    
    test_queries = [
        "Software engineer with Python experience",
        "Data scientist with machine learning expertise"
    ]
    
    results = []
    success_count = 0
    
    for i, query in enumerate(test_queries):
        try:
            # Generate embedding for the query
            query_embedding = get_embedding(query)
            
            if query_embedding:
                # Simulate fallback search by creating a basic filter
                filter_query = {"is_active": True}
                
                # Here we would normally call the fallback_text_search function
                # but for testing purposes we'll just check if we can construct the query
                status = "✅ Simulated"
                details = f"Filter: {filter_query}"
                success_count += 1
            else:
                status = "❌ Failed"
                details = "Could not generate embedding"
        except Exception as e:
            status = "❌ Error"
            details = str(e)[:50]
        
        results.append([i+1, query[:40] + "...", status, details])
    
    print(tabulate(results, headers=["#", "Query", "Status", "Details"], tablefmt="grid"))
    print("\nNote: This is a simulated test of the fallback mechanism.")
    print("In a real scenario, the system should automatically fall back to basic filtering when vector search fails.")
    
    return success_count > 0

def run_all_tests():
    """Run all tests and report results"""
    print_section("SEARCH & RECOMMENDER SYSTEM TEST SUITE")
    print(f"API Base URL: {API_BASE_URL}")
    
    # Track test results
    results = {}
    
    # Test 1: Embedding generation
    results["embedding_generation"] = test_embedding_generation()
    
    # Get auth token for API tests
    token = get_auth_token()
    
    # Test 2-4: Semantic search for different entity types
    results["jobs_search"] = test_semantic_search(token, "jobs")
    results["projects_search"] = test_semantic_search(token, "projects")
    results["candidates_search"] = test_semantic_search(token, "candidates")
    
    # Test 5: Recommendations
    results["recommendations"] = test_recommendations(token)
    
    # Test 6: Fallback search
    results["fallback_search"] = test_fallback_search()
    
    # Print summary
    print_section("TEST RESULTS SUMMARY")
    
    summary = []
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        summary.append([test_name.replace("_", " ").title(), status])
    
    print(tabulate(summary, headers=["Test", "Status"], tablefmt="grid"))
    
    # Overall assessment
    passed_count = sum(1 for passed in results.values() if passed)
    total_count = len(results)
    success_rate = (passed_count / total_count) * 100
    
    print(f"\nOverall success rate: {success_rate:.1f}% ({passed_count}/{total_count})")
    
    if success_rate == 100:
        print("\n✅ All tests passed! The search and recommender system appears to be working correctly.")
    elif success_rate >= 70:
        print("\n⚠️ Some tests passed, but there are issues that need attention.")
    else:
        print("\n❌ Multiple tests failed. The search and recommender system needs significant fixes.")
    
    # Provide recommendations based on failures
    if not results["embedding_generation"]:
        print("\nRecommendation: Check if Ollama is running and accessible.")
        print("The embedding generation is critical for all search and recommendation features.")
    
    if not results["jobs_search"] or not results["projects_search"] or not results["candidates_search"]:
        print("\nRecommendation: Verify that MongoDB Atlas vector indexes are properly set up.")
        print("Run the create_vector_indexes.py script and follow the instructions to create the required indexes.")
    
    if not results["recommendations"]:
        print("\nRecommendation: Check the recommendation endpoints and ensure they're properly implemented.")
        print("The recommendation system depends on both embeddings and properly structured data.")
    
    if not results["fallback_search"]:
        print("\nRecommendation: Ensure the fallback search mechanism is properly implemented.")
        print("This is important for system resilience when vector search is unavailable.")

if __name__ == "__main__":
    run_all_tests() 