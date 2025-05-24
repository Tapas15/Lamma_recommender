#!/usr/bin/env python
"""
Wrapper script to run search and recommender system tests with mocked API calls.
This script provides a convenient way to run tests without needing authentication.

Usage:
    python run_mock_tests.py
"""

import sys
import os
import subprocess
import argparse

def print_section(title):
    """Print a section title for better readability"""
    print("\n")
    print("=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def run_test_with_mock():
    """Run the test_search_recommender.py with --skip-auth flag"""
    print_section("RUNNING TESTS WITH MOCK DATA")
    print("This script will run the test_search_recommender.py with the --skip-auth flag")
    print("Tests will use mock data instead of real API calls that require authentication")
    print("=" * 80)
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build the path to the test script
    test_script = os.path.join(script_dir, "test_search_recommender.py")
    
    if not os.path.exists(test_script):
        print(f"❌ Error: Test script not found at {test_script}")
        return False
    
    # Prepare the command to run the test script with --skip-auth flag
    cmd = [sys.executable, test_script, "--skip-auth"]
    
    try:
        # Run the command
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Tests completed with exit code {result.returncode}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")
        return False

def run_recommendation_tests_with_mock():
    """Run the test_recommendation_system.py with --mock-api flag"""
    print_section("RUNNING RECOMMENDATION TESTS WITH MOCK DATA")
    print("This script will run the test_recommendation_system.py with the --mock-api flag")
    print("Tests will use mock data instead of real API calls that require authentication")
    print("=" * 80)
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build the path to the test script
    recommendation_script = os.path.join(script_dir, "test_recommendation_system.py")
    
    if not os.path.exists(recommendation_script):
        print(f"❌ Error: Recommendation test script not found at {recommendation_script}")
        return False
    
    # Prepare the command to run the test script with --mock-api flag
    cmd = [sys.executable, recommendation_script, "--mock-api"]
    
    try:
        # Run the command
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Recommendation tests completed with exit code {result.returncode}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Recommendation tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Error running recommendation tests: {str(e)}")
        return False

def run_vector_checks():
    """Run the check_all_embeddings.py script"""
    print_section("CHECKING VECTOR EMBEDDINGS")
    print("This script will run check_all_embeddings.py to verify embedding functionality")
    print("=" * 80)
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build the path to the embedding check script
    check_script = os.path.join(script_dir, "check_all_embeddings.py")
    
    if not os.path.exists(check_script):
        print(f"❌ Error: Embedding check script not found at {check_script}")
        return False
    
    # Prepare the command to run the check script
    cmd = [sys.executable, check_script]
    
    try:
        # Run the command
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Embedding checks completed with exit code {result.returncode}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Embedding checks failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Error running embedding checks: {str(e)}")
        return False

def main():
    """Parse arguments and run tests"""
    parser = argparse.ArgumentParser(description='Run tests with mock data')
    parser.add_argument('--search', action='store_true', help='Run search and recommender tests')
    parser.add_argument('--rec', action='store_true', help='Run recommendation system tests')
    parser.add_argument('--vectors', action='store_true', help='Run vector embedding checks')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    # If no specific test is requested, run all tests
    if not (args.search or args.rec or args.vectors or args.all):
        args.all = True
    
    results = {}
    
    if args.search or args.all:
        results["search"] = run_test_with_mock()
        
    if args.rec or args.all:
        results["recommendation"] = run_recommendation_tests_with_mock()
        
    if args.vectors or args.all:
        results["vectors"] = run_vector_checks()
    
    # Print summary
    print_section("TEST SUMMARY")
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.title()} Tests: {status}")
    
    # Return exit code based on test results
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main()) 