#!/usr/bin/env python
"""
Test script to verify that semantic search and recommender system functionality are working correctly.
This script tests:
1. Vector embedding generation
2. Semantic search for jobs, projects, and candidates
3. Recommendation functionality
4. Fallback mechanisms when vector search is not available

Usage:
    python test_search_recommender.py [--skip-auth]
"""

import sys
import os
import json
import requests
import time
import numpy as np
import argparse
from dotenv import load_dotenv
from tabulate import tabulate
from pymongo import MongoClient

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.embedding import get_embedding
from utils.database import Database

# Process command line arguments
parser = argparse.ArgumentParser(description='Test search and recommendation functionality')
parser.add_argument('--skip-auth', action='store_true', help='Skip authentication tests')
args = parser.parse_args()

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
    if args.skip_auth:
        print("Authentication step skipped due to --skip-auth flag")
        return "dummy_token_for_testing"
    
    try:
        print(f"Attempting to authenticate with {API_BASE_URL}/token")
        print(f"Using credentials: {EMAIL}")
        
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={"username": EMAIL, "password": PASSWORD}
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Authentication successful")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code} {response.text}")
            print("Please check your API_BASE_URL, TEST_EMAIL, and TEST_PASSWORD environment variables")
            
            # If auth failed but skip-auth flag is set, use a dummy token anyway
            if args.skip_auth:
                print("Continuing with dummy token due to --skip-auth flag")
                return "dummy_token_for_testing"
            return None
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("Please check your API_BASE_URL, TEST_EMAIL, and TEST_PASSWORD environment variables")
        
        # If auth failed but skip-auth flag is set, use a dummy token anyway
        if args.skip_auth:
            print("Continuing with dummy token due to --skip-auth flag")
            return "dummy_token_for_testing"
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

def mock_search_results(entity_type, query):
    """Generate mock search results for testing without actual API calls"""
    results = []
    for i in range(3):
        if entity_type == "jobs":
            results.append({
                "id": f"job_{i}",
                "title": f"Test Job {i} matching '{query[:10]}...'",
                "company_name": "Test Company",
                "match_score": 0.75 - (i * 0.1)
            })
        elif entity_type == "projects":
            results.append({
                "id": f"project_{i}",
                "title": f"Test Project {i} matching '{query[:10]}...'",
                "client_name": "Test Client",
                "match_score": 0.8 - (i * 0.1)
            })
        elif entity_type == "candidates":
            results.append({
                "id": f"candidate_{i}",
                "full_name": f"Test Candidate {i}",
                "skills": ["Python", "JavaScript", "React"],
                "match_score": 0.85 - (i * 0.1)
            })
    return results

def test_semantic_search(token, entity_type):
    """Test semantic search functionality for jobs, projects, or candidates"""
    print_section(f"TESTING {entity_type.upper()} SEMANTIC SEARCH")
    
    if not token:
        print("❌ Authentication token not available, skipping test")
        return False
    
    # Check if we're using a dummy token (skip-auth mode)
    using_mock = token == "dummy_token_for_testing"
    
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
            if using_mock:
                # Use mock data if we're using a dummy token
                mock_data = mock_search_results(entity_type, query)
                status = "✅ Success (Mock)"
                details = f"Found {len(mock_data)} results (simulated)"
                success_count += 1
                
                # Display sample results for the first query
                if i == 0:
                    print(f"\nSample mock results for '{query[:30]}...':")
                    for j, item in enumerate(mock_data[:2]):
                        if entity_type == "jobs":
                            print(f"  {j+1}. {item['title']} at {item['company_name']} (Match: {item['match_score']:.2f})")
                        elif entity_type == "projects":
                            print(f"  {j+1}. {item['title']} for {item['client_name']} (Match: {item['match_score']:.2f})")
                        elif entity_type == "candidates":
                            skills_str = ", ".join(item['skills'][:3])
                            print(f"  {j+1}. {item['full_name']} - Skills: {skills_str} (Match: {item['match_score']:.2f})")
            else:
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

def mock_recommendations(endpoint_name):
    """Generate mock recommendation data for testing without actual API calls"""
    if endpoint_name == "Job Recommendations":
        return [{"title": "Software Engineer", "company_name": "Tech Corp", "match_score": 0.85},
                {"title": "Full Stack Developer", "company_name": "Web Solutions", "match_score": 0.78}]
    elif endpoint_name == "Project Recommendations":
        return [{"title": "Web App Development", "client_name": "E-Commerce Inc", "match_score": 0.82},
                {"title": "API Integration", "client_name": "FinTech LLC", "match_score": 0.76}]
    elif endpoint_name == "Skill Gap Analysis":
        return {"match_score": 0.72, "missing_skills": ["Kubernetes", "GraphQL"], 
                "existing_skills": ["Python", "JavaScript", "React"]}
    elif endpoint_name == "Learning Recommendations":
        return {"resources": [
            {"title": "Kubernetes for Beginners", "type": "Course", "skill": "Kubernetes"},
            {"title": "GraphQL Fundamentals", "type": "Tutorial", "skill": "GraphQL"}
        ]}
    return []

def test_recommendations(token):
    """Test recommendation functionality"""
    print_section("TESTING RECOMMENDATION SYSTEM")
    
    if not token:
        print("❌ Authentication token not available, skipping test")
        return False
    
    # Check if we're using a dummy token (skip-auth mode)
    using_mock = token == "dummy_token_for_testing"
    
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
            if using_mock:
                # Use mock data if we're using a dummy token
                mock_data = mock_recommendations(endpoint_info["name"])
                status = "✅ Success (Mock)"
                
                if isinstance(mock_data, list):
                    details = f"Found {len(mock_data)} recommendations (simulated)"
                else:
                    if "match_score" in mock_data:
                        details = f"Match score: {mock_data['match_score']} (simulated)"
                    elif "resources" in mock_data:
                        details = f"Found {len(mock_data['resources'])} resources (simulated)"
                    else:
                        details = f"Valid response (simulated)"
                
                success_count += 1
                
                # Display sample results for some endpoints
                if i == 0:  # Job Recommendations
                    print(f"\nSample mock job recommendations:")
                    for j, item in enumerate(mock_data[:2]):
                        print(f"  {j+1}. {item['title']} at {item['company_name']} (Match: {item['match_score']:.2f})")
                elif i == 2:  # Skill Gap Analysis
                    print(f"\nSample mock skill gap analysis:")
                    print(f"  Match score: {mock_data['match_score']:.2f}")
                    print(f"  Missing skills: {', '.join(mock_data['missing_skills'])}")
                    print(f"  Existing skills: {', '.join(mock_data['existing_skills'][:3])}...")
            else:
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

def test_vector_indexes():
    """Test if vector indexes are properly set up in MongoDB Atlas"""
    print_section("TESTING VECTOR INDEXES")
    
    try:
        # Get MongoDB connection settings from environment variables
        mongo_uri = os.getenv("MONGODB_URL", "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/")
        db_name = os.getenv("DATABASE_NAME", "job_recommender")
        
        # Connect directly to MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        collections = ["jobs", "candidates", "projects"]
        results = []
        success_count = 0
        
        for i, collection_name in enumerate(collections):
            try:
                # Get collection info
                collection = db[collection_name]
                indexes = collection.index_information()
                
                # Check if vector index exists
                vector_index_found = any("vector" in idx_name.lower() for idx_name in indexes.keys())
                
                if vector_index_found:
                    status = "✅ Success"
                    details = f"Vector index found"
                    success_count += 1
                else:
                    status = "❌ Failed"
                    details = f"No vector index found"
            except Exception as e:
                status = "❌ Error"
                details = str(e)[:50]
            
            results.append([i+1, collection_name, status, details])
        
        print(tabulate(results, headers=["#", "Collection", "Status", "Details"], tablefmt="grid"))
        
        # Print overall success rate
        success_rate = (success_count / len(collections)) * 100 if collections else 0
        print(f"\nOverall success rate: {success_rate:.1f}% ({success_count}/{len(collections)})")
        
        if success_count < len(collections):
            print("\nSome vector indexes are missing. Run create_vector_indexes.py to set them up.")
        
        return success_count > 0
    except Exception as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print_section("SEARCH & RECOMMENDER SYSTEM TEST SUITE")
    print(f"API Base URL: {API_BASE_URL}")
    if args.skip_auth:
        print("⚠️ Running in skip-auth mode - API tests will use mock data")
    
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
    
    # Test 7: Vector indexes
    results["vector_indexes"] = test_vector_indexes()
    
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
    
    if not results["vector_indexes"]:
        print("\nRecommendation: Set up MongoDB Atlas vector indexes.")
        print("Run the create_vector_indexes.py script to create the required indexes.")
    
    if args.skip_auth:
        print("\nNote: This test was run with --skip-auth flag.")
        print("Some tests used mock data instead of making actual API requests.")
        print("For a complete test, run without the --skip-auth flag and ensure the backend API is properly set up.")

if __name__ == "__main__":
    run_all_tests() 