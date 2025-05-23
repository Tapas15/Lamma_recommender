#!/usr/bin/env python
"""
Test script to verify that the recommendation system functionality is working correctly.
This script tests:
1. Job recommendations for candidates
2. Candidate recommendations for jobs
3. Project recommendations for candidates
4. Skill gap analysis
5. Learning recommendations

Usage:
    python test_recommendation_system.py
"""

import sys
import os
import json
import requests
import time
import numpy as np
from dotenv import load_dotenv
from tabulate import tabulate
from pprint import pprint

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.embedding import get_embedding
from utils.database import Database

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
CANDIDATE_EMAIL = os.getenv("TEST_CANDIDATE_EMAIL", "test_candidate@example.com")
CANDIDATE_PASSWORD = os.getenv("TEST_CANDIDATE_PASSWORD", "password123")
EMPLOYER_EMAIL = os.getenv("TEST_EMPLOYER_EMAIL", "test_employer@example.com")
EMPLOYER_PASSWORD = os.getenv("TEST_EMPLOYER_PASSWORD", "password123")

def print_section(title):
    """Print a section title for better readability"""
    print("\n")
    print("=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def get_auth_token(email, password):
    """Get authentication token for API requests"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={"username": email, "password": password}
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        print(f"Please check your API_BASE_URL and credentials for {email}")
        return None

def test_job_recommendations_for_candidate(candidate_token):
    """Test job recommendations for a candidate"""
    print_section("TESTING JOB RECOMMENDATIONS FOR CANDIDATE")
    
    if not candidate_token:
        print("❌ Candidate authentication token not available, skipping test")
        return False
    
    headers = {
        "Authorization": f"Bearer {candidate_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get job recommendations
        response = requests.get(
            f"{API_BASE_URL}/recommendations/jobs",
            headers=headers
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            
            if isinstance(recommendations, list) and len(recommendations) > 0:
                print(f"✅ Successfully retrieved {len(recommendations)} job recommendations")
                
                # Display sample recommendation
                if len(recommendations) > 0:
                    sample = recommendations[0]
                    print("\nSample recommendation:")
                    print(f"Job Title: {sample.get('title', 'Unknown')}")
                    print(f"Company: {sample.get('company_name', 'Unknown')}")
                    print(f"Match Score: {sample.get('match_score', 'N/A')}")
                    
                    # Check if match scores are present and reasonable
                    has_scores = all('match_score' in job for job in recommendations)
                    if has_scores:
                        scores = [job.get('match_score', 0) for job in recommendations]
                        print(f"\nMatch scores range: {min(scores):.2f} - {max(scores):.2f}")
                        print(f"Average match score: {sum(scores)/len(scores):.2f}")
                    else:
                        print("\n⚠️ Warning: Match scores not present in all recommendations")
                
                return True
            else:
                print("⚠️ No job recommendations found")
                print("This could be normal if there are no suitable jobs or the candidate profile is incomplete")
                return False
        else:
            print(f"❌ Failed to get job recommendations: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing job recommendations: {str(e)}")
        return False

def test_candidate_recommendations_for_job(employer_token):
    """Test candidate recommendations for a job"""
    print_section("TESTING CANDIDATE RECOMMENDATIONS FOR JOB")
    
    if not employer_token:
        print("❌ Employer authentication token not available, skipping test")
        return False
    
    headers = {
        "Authorization": f"Bearer {employer_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # First, get a list of employer's jobs
        response = requests.get(
            f"{API_BASE_URL}/jobs/employer",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get employer jobs: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False
        
        jobs = response.json()
        if not jobs or len(jobs) == 0:
            print("⚠️ No jobs found for this employer, cannot test candidate recommendations")
            return False
        
        # Use the first job to get candidate recommendations
        job_id = jobs[0].get("id")
        job_title = jobs[0].get("title", "Unknown job")
        
        print(f"Testing candidate recommendations for job: {job_title} (ID: {job_id})")
        
        # Get candidate recommendations for this job
        response = requests.get(
            f"{API_BASE_URL}/recommendations/candidates?job_id={job_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            
            if isinstance(recommendations, list) and len(recommendations) > 0:
                print(f"✅ Successfully retrieved {len(recommendations)} candidate recommendations")
                
                # Display sample recommendation
                if len(recommendations) > 0:
                    sample = recommendations[0]
                    print("\nSample recommendation:")
                    print(f"Candidate Name: {sample.get('full_name', 'Unknown')}")
                    print(f"Skills: {', '.join(sample.get('skills', [])[:5])}...")
                    print(f"Match Score: {sample.get('match_score', 'N/A')}")
                    
                    # Check if match scores are present and reasonable
                    has_scores = all('match_score' in candidate for candidate in recommendations)
                    if has_scores:
                        scores = [candidate.get('match_score', 0) for candidate in recommendations]
                        print(f"\nMatch scores range: {min(scores):.2f} - {max(scores):.2f}")
                        print(f"Average match score: {sum(scores)/len(scores):.2f}")
                    else:
                        print("\n⚠️ Warning: Match scores not present in all recommendations")
                
                return True
            else:
                print("⚠️ No candidate recommendations found")
                print("This could be normal if there are no suitable candidates or the job description is vague")
                return False
        else:
            print(f"❌ Failed to get candidate recommendations: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing candidate recommendations: {str(e)}")
        return False

def test_project_recommendations_for_candidate(candidate_token):
    """Test project recommendations for a candidate"""
    print_section("TESTING PROJECT RECOMMENDATIONS FOR CANDIDATE")
    
    if not candidate_token:
        print("❌ Candidate authentication token not available, skipping test")
        return False
    
    headers = {
        "Authorization": f"Bearer {candidate_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get project recommendations
        response = requests.get(
            f"{API_BASE_URL}/recommendations/projects",
            headers=headers
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            
            if isinstance(recommendations, list) and len(recommendations) > 0:
                print(f"✅ Successfully retrieved {len(recommendations)} project recommendations")
                
                # Display sample recommendation
                if len(recommendations) > 0:
                    sample = recommendations[0]
                    print("\nSample recommendation:")
                    print(f"Project Title: {sample.get('title', 'Unknown')}")
                    print(f"Client: {sample.get('client_name', 'Unknown')}")
                    print(f"Match Score: {sample.get('match_score', 'N/A')}")
                    
                    # Check if match scores are present and reasonable
                    has_scores = all('match_score' in project for project in recommendations)
                    if has_scores:
                        scores = [project.get('match_score', 0) for project in recommendations]
                        print(f"\nMatch scores range: {min(scores):.2f} - {max(scores):.2f}")
                        print(f"Average match score: {sum(scores)/len(scores):.2f}")
                    else:
                        print("\n⚠️ Warning: Match scores not present in all recommendations")
                
                return True
            else:
                print("⚠️ No project recommendations found")
                print("This could be normal if there are no suitable projects or the candidate profile is incomplete")
                return False
        else:
            print(f"❌ Failed to get project recommendations: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing project recommendations: {str(e)}")
        return False

def test_skill_gap_analysis(candidate_token):
    """Test skill gap analysis functionality"""
    print_section("TESTING SKILL GAP ANALYSIS")
    
    if not candidate_token:
        print("❌ Candidate authentication token not available, skipping test")
        return False
    
    headers = {
        "Authorization": f"Bearer {candidate_token}",
        "Content-Type": "application/json"
    }
    
    # Test roles to analyze skill gaps for
    test_roles = [
        "Software Engineer",
        "Data Scientist",
        "Frontend Developer",
        "DevOps Engineer"
    ]
    
    results = []
    success_count = 0
    
    for i, role in enumerate(test_roles):
        try:
            # Get skill gap analysis
            response = requests.get(
                f"{API_BASE_URL}/recommendations/skill-gap?target_role={role.replace(' ', '%20')}",
                headers=headers
            )
            
            if response.status_code == 200:
                analysis = response.json()
                
                if isinstance(analysis, dict) and "missing_skills" in analysis:
                    missing_skills = analysis.get("missing_skills", [])
                    match_score = analysis.get("match_score", 0)
                    
                    status = "✅ Success"
                    details = f"Match: {match_score:.2f}, Missing skills: {len(missing_skills)}"
                    success_count += 1
                else:
                    status = "⚠️ Warning"
                    details = "Invalid response format"
            else:
                status = "❌ Failed"
                details = f"Status: {response.status_code}, Error: {response.text[:50]}"
        except Exception as e:
            status = "❌ Error"
            details = str(e)[:50]
        
        results.append([i+1, role, status, details])
    
    print(tabulate(results, headers=["#", "Target Role", "Status", "Details"], tablefmt="grid"))
    
    # Print overall success rate
    success_rate = (success_count / len(test_roles)) * 100 if test_roles else 0
    print(f"\nOverall success rate: {success_rate:.1f}% ({success_count}/{len(test_roles)})")
    
    # If at least one test was successful, show detailed results
    if success_count > 0:
        # Get a successful response to show details
        for role in test_roles:
            try:
                response = requests.get(
                    f"{API_BASE_URL}/recommendations/skill-gap?target_role={role.replace(' ', '%20')}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    analysis = response.json()
                    if isinstance(analysis, dict) and "missing_skills" in analysis:
                        print(f"\nDetailed skill gap analysis for {role}:")
                        print(f"Match Score: {analysis.get('match_score', 0):.2f}")
                        print(f"Missing Skills: {', '.join(analysis.get('missing_skills', [])[:10])}")
                        if len(analysis.get('missing_skills', [])) > 10:
                            print(f"... and {len(analysis.get('missing_skills', [])) - 10} more")
                        print(f"Existing Skills: {', '.join(analysis.get('existing_skills', [])[:10])}")
                        if len(analysis.get('existing_skills', [])) > 10:
                            print(f"... and {len(analysis.get('existing_skills', [])) - 10} more")
                        break
            except:
                continue
    
    return success_count > 0

def test_learning_recommendations(candidate_token):
    """Test learning recommendations functionality"""
    print_section("TESTING LEARNING RECOMMENDATIONS")
    
    if not candidate_token:
        print("❌ Candidate authentication token not available, skipping test")
        return False
    
    headers = {
        "Authorization": f"Bearer {candidate_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get learning recommendations
        response = requests.get(
            f"{API_BASE_URL}/recommendations/learning",
            headers=headers
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            
            if isinstance(recommendations, dict) and "resources" in recommendations:
                resources = recommendations.get("resources", [])
                print(f"✅ Successfully retrieved {len(resources)} learning resources")
                
                # Display sample resources
                if len(resources) > 0:
                    print("\nSample learning resources:")
                    for i, resource in enumerate(resources[:3]):
                        print(f"\n{i+1}. {resource.get('title', 'Unknown')}")
                        print(f"   Type: {resource.get('type', 'Unknown')}")
                        print(f"   Skill: {resource.get('skill', 'Unknown')}")
                        print(f"   URL: {resource.get('url', 'N/A')}")
                
                return True
            else:
                print("⚠️ No learning recommendations found or invalid response format")
                return False
        else:
            print(f"❌ Failed to get learning recommendations: Status {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing learning recommendations: {str(e)}")
        return False

def run_all_tests():
    """Run all recommendation system tests and report results"""
    print_section("RECOMMENDATION SYSTEM TEST SUITE")
    print(f"API Base URL: {API_BASE_URL}")
    
    # Get authentication tokens
    candidate_token = get_auth_token(CANDIDATE_EMAIL, CANDIDATE_PASSWORD)
    employer_token = get_auth_token(EMPLOYER_EMAIL, EMPLOYER_PASSWORD)
    
    # Track test results
    results = {}
    
    # Test 1: Job recommendations for candidate
    results["job_recommendations"] = test_job_recommendations_for_candidate(candidate_token)
    
    # Test 2: Candidate recommendations for job
    results["candidate_recommendations"] = test_candidate_recommendations_for_job(employer_token)
    
    # Test 3: Project recommendations for candidate
    results["project_recommendations"] = test_project_recommendations_for_candidate(candidate_token)
    
    # Test 4: Skill gap analysis
    results["skill_gap_analysis"] = test_skill_gap_analysis(candidate_token)
    
    # Test 5: Learning recommendations
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
    elif success_rate >= 60:
        print("\n⚠️ Some tests passed, but there are issues that need attention.")
    else:
        print("\n❌ Multiple tests failed. The recommendation system needs significant fixes.")
    
    # Provide recommendations based on failures
    if not results["job_recommendations"] or not results["project_recommendations"]:
        print("\nRecommendation: Check if candidate profile data is complete and has embeddings.")
        print("The recommendation system relies on candidate profile data to make job and project recommendations.")
    
    if not results["candidate_recommendations"]:
        print("\nRecommendation: Check if job data is complete and has embeddings.")
        print("The recommendation system relies on job data to make candidate recommendations.")
    
    if not results["skill_gap_analysis"]:
        print("\nRecommendation: Check the skill gap analysis implementation.")
        print("This feature requires a database of role-specific skills and candidate skills data.")
    
    if not results["learning_recommendations"]:
        print("\nRecommendation: Check the learning resources database and recommendation logic.")
        print("This feature requires a database of learning resources mapped to skills.")

if __name__ == "__main__":
    run_all_tests() 