#!/usr/bin/env python
"""
Main entry point for running the Job Recommender System test suite directly.
Example: python -m test_suite
"""
import os
import sys
import argparse
from rich.console import Console

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_suite.test_runner import TestRunner
from test_suite.test_services import ServiceManager
from test_suite.test_config import API_BASE_URL, STREAMLIT_URL

console = Console()

def main():
    """Run the test suite when invoked as a module"""
    parser = argparse.ArgumentParser(description="Job Recommender System Test Suite")
    parser.add_argument("--url", help=f"API base URL (default: {API_BASE_URL})", default=API_BASE_URL)
    parser.add_argument("--streamlit-url", help=f"Streamlit URL (default: {STREAMLIT_URL})", default=STREAMLIT_URL)
    parser.add_argument("--employer-only", help="Run only employer flow tests", action="store_true")
    parser.add_argument("--candidate-only", help="Run only candidate flow tests", action="store_true")
    parser.add_argument("--no-auto-start", help="Don't automatically start services", action="store_true")
    parser.add_argument("--keep-running", help="Keep services running after tests", action="store_true")
    args = parser.parse_args()
    
    console.print("[bold purple]Job Recommender System - Test Suite[/bold purple]")
    console.print("=============================================")
    console.print(f"API URL: {args.url}")
    
    # Set up service manager and start services if needed
    service_manager = None
    if not args.no_auto_start:
        service_manager = ServiceManager(args.url, args.streamlit_url)
        services_running = service_manager.ensure_services_running()
        
        if not services_running:
            console.print("[bold red]Failed to start required services. Tests cannot run.[/bold red]")
            return
    
    # Create and run the test runner
    runner = TestRunner(args.url)
    
    try:
        if args.employer_only:
            console.print("\n[bold]Running employer flow tests only...[/bold]")
            runner.run_employer_flow()
        elif args.candidate_only:
            console.print("\n[bold]Running candidate flow tests only...[/bold]")
            # Note: This may fail if there are no jobs/projects in the system
            runner.run_candidate_flow({})
        else:
            console.print("\n[bold]Running all tests...[/bold]")
            runner.run_all_tests()
    finally:
        # Always clean up services unless --keep-running is specified
        if service_manager and not args.keep_running:
            console.print("\n[yellow]Stopping services...[/yellow]")
            service_manager.stop_services()
        elif service_manager and args.keep_running:
            console.print("\n[yellow]Services will be kept running.[/yellow]")

if __name__ == "__main__":
    main() 