import requests
import json
import sys
import os
from tabulate import tabulate
from dotenv import load_dotenv
import time

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_CANDIDATE_EMAIL = os.getenv("TEST_CANDIDATE_EMAIL", "test@example.com")
TEST_CANDIDATE_PASSWORD = os.getenv("TEST_CANDIDATE_PASSWORD", "password")
TEST_EMPLOYER_EMAIL = os.getenv("TEST_EMPLOYER_EMAIL", "employer@example.com")
TEST_EMPLOYER_PASSWORD = os.getenv("TEST_EMPLOYER_PASSWORD", "password")

def get_token():
    """Get authentication token"""
    login_data = {
        "username": TEST_CANDIDATE_EMAIL,
        "password": TEST_CANDIDATE_PASSWORD
    }
    
    response = requests.post(f"{API_BASE_URL}/token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get token: {response.status_code} - {response.text}")
        return None

def test_market_trends(token, timeframe="6_months", skill_category="software_development", include_details=True):
    """Test the market trends endpoint with different parameters"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Build query parameters
    params = {
        "timeframe": timeframe,
        "skill_category": skill_category,
        "include_details": str(include_details).lower()
    }
    
    # Make request
    start_time = time.time()
    response = requests.get(
        f"{API_BASE_URL}/ml/market-trends", 
        headers=headers,
        params=params
    )
    end_time = time.time()
    
    # Print response time
    print(f"\nResponse time: {(end_time - start_time):.2f} seconds")
    
    # Check response status
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    
    # Parse response
    result = response.json()
    
    # Print basic information
    print("\n===== Market Trends Analysis =====")
    print(f"Timeframe: {result.get('timeframe')}")
    print(f"Skill Category: {result.get('skill_category')}")
    
    # Print metadata
    metadata = result.get("metadata", {})
    if metadata:
        print("\nMetadata:")
        meta_data = [
            ["Analysis Timestamp", metadata.get("analysis_timestamp", "N/A")],
            ["Confidence Score", metadata.get("confidence_score", "N/A")],
            ["Prediction Model", metadata.get("prediction_model", "N/A")],
            ["Data Sources", ", ".join(metadata.get("data_sources", []))]
        ]
        print(tabulate(meta_data, tablefmt="grid"))
    
    # Print trends
    trends = result.get("trends", [])
    if trends:
        print("\nTop Skill Trends:")
        trend_data = []
        
        # Prepare table data
        for trend in trends[:10]:  # Show top 10 trends
            trend_data.append([
                trend.get("skill", "N/A"),
                f"{trend.get('current_demand', 0)}%",
                f"{trend.get('projected_demand', 0)}%",
                f"{trend.get('growth_rate', 0)}%",
                trend.get("confidence", "N/A")
            ])
        
        # Print table
        print(tabulate(
            trend_data, 
            headers=["Skill", "Current Demand", "Projected Demand", "Growth Rate", "Confidence"],
            tablefmt="grid"
        ))
        
        # Print detailed information for top trend if available
        if include_details and trends and "details" in trends[0]:
            top_trend = trends[0]
            print(f"\nDetailed Analysis for Top Trend: {top_trend.get('skill')}")
            
            # Print salary data
            salary_data = top_trend.get("details", {}).get("salary_data", {})
            if salary_data:
                print("\nSalary Data:")
                salary_table = [
                    ["Current Average", salary_data.get("current_avg", "N/A")],
                    ["Projected Average", salary_data.get("projected_avg", "N/A")],
                    ["Growth Percentage", f"{salary_data.get('growth_percentage', 0)}%"]
                ]
                print(tabulate(salary_table, tablefmt="grid"))
            
            # Print industry relevance
            industry_relevance = top_trend.get("details", {}).get("industry_relevance", {})
            if industry_relevance:
                print("\nIndustry Relevance:")
                industry_table = []
                for industry, score in industry_relevance.items():
                    industry_table.append([industry, f"{score:.2f}"])
                print(tabulate(industry_table, headers=["Industry", "Relevance Score"], tablefmt="grid"))
            
            # Print complementary skills
            complementary_skills = top_trend.get("details", {}).get("complementary_skills", [])
            if complementary_skills:
                print(f"\nComplementary Skills: {', '.join(complementary_skills)}")
            
            # Print market factors
            market_factors = top_trend.get("details", {}).get("market_factors", [])
            if market_factors:
                print("\nMarket Factors:")
                for factor in market_factors:
                    print(f"- {factor}")
    
    # Return the result for further processing if needed
    return result

def test_multiple_timeframes(token):
    """Test the market trends endpoint with different timeframes"""
    timeframes = ["3_months", "6_months", "1_year", "2_years", "5_years"]
    
    for timeframe in timeframes:
        print(f"\n\n===== Testing Timeframe: {timeframe} =====")
        test_market_trends(token, timeframe=timeframe)

def test_multiple_categories(token):
    """Test the market trends endpoint with different skill categories"""
    categories = [
        "software_development", 
        "data_science", 
        "cloud_computing", 
        "cybersecurity", 
        "devops", 
        "artificial_intelligence"
    ]
    
    for category in categories:
        print(f"\n\n===== Testing Category: {category} =====")
        test_market_trends(token, skill_category=category)

def run_tests():
    """Run all tests"""
    # Get authentication token
    token = get_token()
    if not token:
        print("Failed to get authentication token. Exiting.")
        return
    
    # Run basic test
    print("\n===== Basic Market Trends Test =====")
    test_market_trends(token)
    
    # Test with different timeframes
    test_multiple_timeframes(token)
    
    # Test with different categories
    test_multiple_categories(token)
    
    print("\n===== All tests completed =====")

if __name__ == "__main__":
    run_tests() 