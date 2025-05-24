#!/usr/bin/env python
"""
Test script to verify the recommendation system is working correctly.
This script tests:
1. Job recommendations for candidates
2. Project recommendations for candidates 
3. Skill gap analysis
4. Learning recommendations

Usage:
    python test_recommendation_system.py [--mock-api]
"""

import sys
import os
import json
import requests
import time
import argparse
import pymongo
from tabulate import tabulate
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.embedding import get_embedding
from utils.database import Database

# Parse command line arguments
parser = argparse.ArgumentParser(description='Test recommendation system')
parser.add_argument('--mock-api', action='store_true', help='Use mock data instead of making real API calls')
args = parser.parse_args()

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
CANDIDATE_EMAIL = os.getenv("TEST_CANDIDATE_EMAIL", "test_candidate@example.com")
CANDIDATE_PASSWORD = os.getenv("TEST_CANDIDATE_PASSWORD", "password123")
EMPLOYER_EMAIL = os.getenv("TEST_EMPLOYER_EMAIL", "test_employer@example.com")
EMPLOYER_PASSWORD = os.getenv("TEST_EMPLOYER_PASSWORD", "password123")

# Database setup
MONGO_URI = os.getenv("MONGODB_URL", "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/")
DB_NAME = os.getenv("DATABASE_NAME", "job_recommender")

def print_section(title):
    """Print a section title for better readability"""
    print("\n")
    print("=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def get_auth_token(email, password):
    """Get authentication token for API requests"""
    if args.mock_api:
        print(f"Using mock authentication for {email}")
        return "mock_token_for_testing"
        
    try:
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={"username": email, "password": password}
        )
        
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Authentication failed: Status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        print(f"Please check your API_BASE_URL and credentials for {email}")
        return None

def mock_job_recommendations():
    """Generate mock job recommendations for testing"""
    return [
        {
            "job_id": "job_1",
            "match_score": 87.5,
            "explanation": "Match score: 87.5. Matching skills: Python, React, Node.js.",
            "title": "Senior Software Engineer",
            "company_name": "Tech Innovations Inc.",
            "location": "Remote",
            "employment_type": "Full-time"
        },
        {
            "job_id": "job_2",
            "match_score": 82.3,
            "explanation": "Match score: 82.3. Matching skills: JavaScript, AWS, Docker.",
            "title": "Full Stack Developer",
            "company_name": "Digital Solutions",
            "location": "San Francisco, CA",
            "employment_type": "Full-time"
        },
        {
            "job_id": "job_3",
            "match_score": 75.1,
            "explanation": "Match score: 75.1. Matching skills: Python, Docker, CI/CD.",
            "title": "DevOps Engineer",
            "company_name": "Cloud Systems",
            "location": "New York, NY",
            "employment_type": "Contract"
        }
    ]

def mock_project_recommendations():
    """Generate mock project recommendations for testing"""
    return [
        {
            "project_id": "project_1",
            "match_score": 85.2,
            "explanation": "Match score: 85.2. Matching skills: React, Node.js, MongoDB.",
            "project_details": {
                "title": "E-commerce Platform Development",
                "company": "Retail Innovations",
                "description": "Develop a modern e-commerce platform with product recommendations",
                "project_type": "Web Development",
                "skills_required": ["React", "Node.js", "MongoDB", "GraphQL"]
            }
        },
        {
            "project_id": "project_2",
            "match_score": 78.9,
            "explanation": "Match score: 78.9. Matching skills: Python, Machine Learning, Data Analysis.",
            "project_details": {
                "title": "AI-Powered Recommendation Engine",
                "company": "DataTech",
                "description": "Build a recommendation system using machine learning algorithms",
                "project_type": "Data Science",
                "skills_required": ["Python", "Machine Learning", "Data Analysis", "TensorFlow"]
            }
        }
    ]

def mock_skill_gap_analysis():
    """Generate mock skill gap analysis for testing"""
    return {
        "target_role": "Software Engineer",
        "experience_level": "Mid-level",
        "match_score": 72.5,
        "existing_skills": [
            {"name": "Python", "proficiency": "Expert", "is_match": True},
            {"name": "JavaScript", "proficiency": "Advanced", "is_match": True},
            {"name": "React", "proficiency": "Intermediate", "is_match": True},
            {"name": "Node.js", "proficiency": "Intermediate", "is_match": True}
        ],
        "missing_skills": [
            {"name": "Kubernetes", "importance": "High"},
            {"name": "GraphQL", "importance": "Medium"},
            {"name": "CI/CD", "importance": "High"}
        ],
        "recommended_learning_path": [
            "Master Kubernetes for cloud-native applications",
            "Learn GraphQL for modern API development",
            "Implement CI/CD pipelines for automated testing and deployment"
        ]
    }

def mock_learning_recommendations():
    """Generate mock learning recommendations for testing"""
    return {
        "skills": ["Kubernetes", "GraphQL", "CI/CD"],
        "resources": [
            {
                "title": "Kubernetes for Developers",
                "provider": "Udemy",
                "description": "Learn Kubernetes from scratch",
                "url": "https://www.udemy.com/course/kubernetes-for-developers"
            },
            {
                "title": "GraphQL Full Course",
                "provider": "freeCodeCamp",
                "description": "Complete GraphQL tutorial",
                "url": "https://www.youtube.com/watch?v=ed8SzALpx1Q"
            },
            {
                "title": "CI/CD Pipeline Implementation",
                "provider": "Coursera",
                "description": "Learn to build automated pipelines",
                "url": "https://www.coursera.org/learn/continuous-integration-continuous-deployment"
            }
        ]
    }

def test_job_recommendations(candidate_token):
    """Test job recommendations for a candidate"""
    print_section("TESTING JOB RECOMMENDATIONS")
    
    if not candidate_token:
        print("❌ Candidate authentication token not available, skipping test")
        return False
    
    if args.mock_api:
        print("Using mock data for job recommendations")
        recommendations = mock_job_recommendations()
        print(f"✅ Successfully retrieved {len(recommendations)} job recommendations (MOCK DATA)")
        
        # Display the mock recommendations
        print("\nSample recommendations:")
        for i, rec in enumerate(recommendations[:2]):
            print(f"\n{i+1}. {rec.get('title')} - {rec.get('company_name')}")
            print(f"   Match score: {rec.get('match_score'):.1f}")
            print(f"   Explanation: {rec.get('explanation')}")
        
        return True
    
    headers = {
        "Authorization": f"Bearer {candidate_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/recommendations/jobs",
            headers=headers
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            
            if isinstance(recommendations, list) and len(recommendations) > 0:
                print(f"✅ Successfully retrieved {len(recommendations)} job recommendations")
                
                # Display the first two recommendations
                print("\nSample recommendations:")
                for i, rec in enumerate(recommendations[:2]):
                    print(f"\n{i+1}. {rec.get('title')} - {rec.get('company_name', 'Unknown company')}")
                    print(f"   Match score: {rec.get('match_score', 'N/A')}")
                    print(f"   Explanation: {rec.get('explanation', 'N/A')}")
                
                return True
            else:
                print("⚠️ No job recommendations found")
                print("This could be normal if there are no suitable jobs or your candidate profile is incomplete")
                return False
        else:
            print(f"❌ Failed to get job recommendations: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing job recommendations: {str(e)}")
        return False

def test_project_recommendations(candidate_token):
    """Test project recommendations for a candidate"""
    print_section("TESTING PROJECT RECOMMENDATIONS")
    
    if not candidate_token:
        print("❌ Candidate authentication token not available, skipping test")
        return False
    
    if args.mock_api:
        print("Using mock data for project recommendations")
        recommendations = mock_project_recommendations()
        print(f"✅ Successfully retrieved {len(recommendations)} project recommendations (MOCK DATA)")
        
        # Display the mock recommendations
        print("\nSample recommendations:")
        for i, rec in enumerate(recommendations[:2]):
            details = rec.get('project_details', {})
            print(f"\n{i+1}. {details.get('title')} - {details.get('company')}")
            print(f"   Project type: {details.get('project_type')}")
            print(f"   Match score: {rec.get('match_score'):.1f}")
            print(f"   Explanation: {rec.get('explanation')}")
        
        return True
    
    headers = {
        "Authorization": f"Bearer {candidate_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/recommendations/projects",
            headers=headers
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            
            if isinstance(recommendations, list) and len(recommendations) > 0:
                print(f"✅ Successfully retrieved {len(recommendations)} project recommendations")
                
                # Display the first two recommendations
                print("\nSample recommendations:")
                for i, rec in enumerate(recommendations[:2]):
                    details = rec.get('project_details', {})
                    print(f"\n{i+1}. {details.get('title', 'Unknown project')} - {details.get('company', 'Unknown company')}")
                    print(f"   Project type: {details.get('project_type', 'N/A')}")
                    print(f"   Match score: {rec.get('match_score', 'N/A')}")
                    print(f"   Explanation: {rec.get('explanation', 'N/A')}")
                
                return True
            else:
                print("⚠️ No project recommendations found")
                print("This could be normal if there are no suitable projects or your candidate profile is incomplete")
                return False
        else:
            print(f"❌ Failed to get project recommendations: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing project recommendations: {str(e)}")
        return False

def test_skill_gap_analysis(candidate_token):
    """Test skill gap analysis for a candidate"""
    print_section("TESTING SKILL GAP ANALYSIS")
    
    if not candidate_token:
        print("❌ Candidate authentication token not available, skipping test")
        return False
    
    if args.mock_api:
        print("Using mock data for skill gap analysis")
        analysis = mock_skill_gap_analysis()
        print(f"✅ Successfully retrieved skill gap analysis for {analysis.get('target_role')} (MOCK DATA)")
        
        # Display mock analysis
        print(f"\nTarget role: {analysis.get('target_role')} ({analysis.get('experience_level')})")
        print(f"Match score: {analysis.get('match_score'):.1f}%")
        
        print("\nExisting skills:")
        for skill in analysis.get('existing_skills', [])[:3]:
            print(f"- {skill.get('name')} ({skill.get('proficiency')})")
        
        print("\nSkills to develop:")
        for skill in analysis.get('missing_skills', [])[:3]:
            print(f"- {skill.get('name')} (Importance: {skill.get('importance')})")
        
        return True
    
    headers = {
        "Authorization": f"Bearer {candidate_token}",
        "Content-Type": "application/json"
    }
    
    target_role = "Software Engineer"
    experience_level = "Mid-level"
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/recommendations/skill-gap?target_role={target_role}&experience_level={experience_level}",
            headers=headers
        )
        
        if response.status_code == 200:
            analysis = response.json()
            
            if isinstance(analysis, dict) and "match_score" in analysis:
                print(f"✅ Successfully retrieved skill gap analysis for {target_role}")
                
                print(f"\nTarget role: {analysis.get('target_role', target_role)} ({analysis.get('experience_level', experience_level)})")
                print(f"Match score: {analysis.get('match_score', 'N/A')}%")
                
                existing_skills = analysis.get('existing_skills', [])
                missing_skills = analysis.get('missing_skills', [])
                
                if existing_skills:
                    print("\nExisting skills:")
                    for skill in existing_skills[:3]:
                        print(f"- {skill.get('name')} ({skill.get('proficiency', 'N/A')})")
                
                if missing_skills:
                    print("\nSkills to develop:")
                    for skill in missing_skills[:3]:
                        print(f"- {skill.get('name')} (Importance: {skill.get('importance', 'N/A')})")
                
                return True
            else:
                print("⚠️ Invalid skill gap analysis response format")
                print(f"Response: {json.dumps(analysis, indent=2)}")
                return False
        else:
            print(f"❌ Failed to get skill gap analysis: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing skill gap analysis: {str(e)}")
        return False

def test_learning_recommendations(candidate_token):
    """Test learning recommendations for a candidate"""
    print_section("TESTING LEARNING RECOMMENDATIONS")
    
    if not candidate_token:
        print("❌ Candidate authentication token not available, skipping test")
        return False
    
    if args.mock_api:
        print("Using mock data for learning recommendations")
        recommendations = mock_learning_recommendations()
        
        print(f"✅ Successfully retrieved learning recommendations for skills: {', '.join(recommendations.get('skills', []))} (MOCK DATA)")
        
        # Display mock learning resources
        print("\nRecommended learning resources:")
        for i, resource in enumerate(recommendations.get('resources', [])[:3]):
            print(f"\n{i+1}. {resource.get('title')}")
            print(f"   Provider: {resource.get('provider')}")
            print(f"   Description: {resource.get('description')}")
        
        return True
    
    headers = {
        "Authorization": f"Bearer {candidate_token}",
        "Content-Type": "application/json"
    }
    
    # Use some sample skills to test
    test_skills = ["Python", "React", "Machine Learning"]
    skills_param = json.dumps(test_skills)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/recommendations/learning?skills={skills_param}",
            headers=headers
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            
            if isinstance(recommendations, dict) and "resources" in recommendations:
                resources = recommendations.get('resources', [])
                print(f"✅ Successfully retrieved {len(resources)} learning recommendations")
                
                # Display some resources
                if resources:
                    print("\nRecommended learning resources:")
                    for i, resource in enumerate(resources[:3]):
                        print(f"\n{i+1}. {resource.get('title', 'Untitled resource')}")
                        print(f"   Provider: {resource.get('provider', 'Unknown provider')}")
                        print(f"   Description: {resource.get('description', 'No description')}")
                
                return True
            else:
                print("⚠️ Invalid learning recommendations response format")
                print(f"Response: {json.dumps(recommendations, indent=2)}")
                return False
        else:
            print(f"❌ Failed to get learning recommendations: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing learning recommendations: {str(e)}")
        return False

def check_mongodb_data():
    """Check if MongoDB has required data for recommendations to work"""
    print_section("CHECKING MONGODB DATA")
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        collections = ["jobs", "projects", "candidates", "recommendations"]
        results = []
        
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            
            if count > 0:
                status = "✅ Data present"
                details = f"Found {count} documents"
            else:
                status = "⚠️ No data"
                details = "Collection exists but has no documents"
            
            # Check for embeddings in first 3 collections
            if collection_name in ["jobs", "projects", "candidates"]:
                with_embeddings = collection.count_documents({"embedding": {"$exists": True}})
                if with_embeddings > 0:
                    embedding_status = f"{with_embeddings}/{count} have embeddings"
                else:
                    embedding_status = "No embeddings found"
                details += f", {embedding_status}"
            
            results.append([collection_name, status, details])
        
        print(tabulate(results, headers=["Collection", "Status", "Details"], tablefmt="grid"))
        client.close()
        
        # Return True if we have at least some data in jobs and candidates
        jobs_count = next((r[2].split(",")[0] for r in results if r[0] == "jobs"), "Found 0 documents")
        candidates_count = next((r[2].split(",")[0] for r in results if r[0] == "candidates"), "Found 0 documents")
        
        has_jobs = "Found 0 documents" not in jobs_count
        has_candidates = "Found 0 documents" not in candidates_count
        
        if has_jobs and has_candidates:
            print("\n✅ MongoDB has necessary data for recommendations to work")
            return True
        else:
            missing = []
            if not has_jobs:
                missing.append("jobs")
            if not has_candidates:
                missing.append("candidates")
                
            print(f"\n⚠️ Missing data in these collections: {', '.join(missing)}")
            print("Recommendations may not work properly without this data")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {str(e)}")
        return False

def run_all_tests():
    """Run all recommendation system tests"""
    print_section("RECOMMENDATION SYSTEM TEST SUITE")
    print(f"API Base URL: {API_BASE_URL}")
    
    if args.mock_api:
        print("⚠️ Running with mock data - API calls will return simulated responses")
    
    # Check MongoDB data first
    mongodb_status = check_mongodb_data()
    
    # Get authentication tokens
    candidate_token = get_auth_token(CANDIDATE_EMAIL, CANDIDATE_PASSWORD)
    if not candidate_token and not args.mock_api:
        print("❌ Failed to authenticate as candidate. Tests will likely fail.")
    
    # Run tests
    results = {}
    
    # Test job recommendations for candidates
    results["job_recommendations"] = test_job_recommendations(candidate_token)
    
    # Test project recommendations for candidates
    results["project_recommendations"] = test_project_recommendations(candidate_token)
    
    # Test skill gap analysis
    results["skill_gap_analysis"] = test_skill_gap_analysis(candidate_token)
    
    # Test learning recommendations
    results["learning_recommendations"] = test_learning_recommendations(candidate_token)
    
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
        print("\n✅ All tests passed! The recommendation system appears to be working correctly.")
    elif success_rate >= 50:
        print("\n⚠️ Some tests passed, but there are issues that need attention.")
    else:
        print("\n❌ Multiple tests failed. The recommendation system needs significant fixes.")
    
    # Provide recommendations based on failures
    if not mongodb_status:
        print("\nImportant: MongoDB data issues detected.")
        print("1. Make sure you have created test jobs and candidates in the database")
        print("2. Verify that documents have embedding vectors generated")
        print("3. Check MongoDB connection settings")
    
    if not results["job_recommendations"] or not results["project_recommendations"]:
        print("\nRecommendation: Check the matching algorithm and vector search functionality.")
        print("Issues with job or project recommendations often indicate problems with:")
        print("1. Vector embedding generation")
        print("2. Similarity calculation")
        print("3. Missing skills in candidate or job/project documents")
    
    if not results["skill_gap_analysis"]:
        print("\nRecommendation: Review the skill gap analysis implementation.")
        print("Verify that the necessary data for target roles and skills is available in the system.")
    
    if not results["learning_recommendations"]:
        print("\nRecommendation: Check the learning recommendations module.")
        print("Ensure that learning resources are properly configured for various skills.")
    
    if args.mock_api:
        print("\nNote: This test was run with --mock-api flag.")
        print("For a complete test with actual API calls, run without this flag")
        print("and ensure the backend API is properly set up with test accounts.")

if __name__ == "__main__":
    run_all_tests() 