#!/usr/bin/env python
"""
Main test runner for the Job Recommender System test suite.
Handles service management and test execution.
"""
import os
import sys
import argparse
import time
from rich.console import Console

# Add the project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Import test modules
from test_suite.test_services import ServiceManager
from test_suite.test_flow import run_tests
from test_suite.test_config import API_BASE_URL, STREAMLIT_URL

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run comprehensive tests for the Job Recommender System"
    )
    parser.add_argument(
        "--api-url", 
        default=API_BASE_URL,
        help=f"URL of the API server (default: {API_BASE_URL})"
    )
    parser.add_argument(
        "--streamlit-url", 
        default=STREAMLIT_URL,
        help=f"URL of the Streamlit server (default: {STREAMLIT_URL})"
    )
    parser.add_argument(
        "--no-services", 
        action="store_true",
        help="Don't start or manage services (assumes they are already running)"
    )
    parser.add_argument(
        "--no-cleanup", 
        action="store_true",
        help="Don't stop services after tests complete"
    )
    parser.add_argument(
        "--wait-time", 
        type=int,
        default=5,
        help="Additional time to wait for services to fully initialize (seconds)"
    )
    
    return parser.parse_args()

def main():
    """Main function to run the tests"""
    console = Console()
    args = parse_args()
    
    console.print("[bold]Job Recommender System - Comprehensive Test[/bold]")
    console.print("=============================================")
    console.print(f"API URL: {args.api_url}")
    console.print(f"Streamlit URL: {args.streamlit_url}")
    
    python_path = sys.executable
    console.print(f"Using Python executable:\n{python_path}")
    
    service_manager = None
    if not args.no_services:
        # Start or verify services
        service_manager = ServiceManager(args.api_url, args.streamlit_url)
        
        console.print("[bold]Ensuring services are running...[/bold]")
        if not service_manager.ensure_services_running():
            console.print("[bold red]Failed to start all required services. Exiting.[/bold red]")
            return 1
        
        # Additional wait time for services to fully initialize
        if args.wait_time > 0:
            console.print(f"[yellow]Waiting {args.wait_time} additional seconds for services to fully initialize...[/yellow]")
            time.sleep(args.wait_time)
    
    try:
        # Run the tests
        console.print("[bold green]Starting tests...[/bold green]")
        test_results = run_tests(api_url=args.api_url)
        
        # Display test results
        if test_results:
            console.print("[bold green]Tests completed successfully![/bold green]")
        else:
            console.print("[bold yellow]Some tests failed. Check the output above for details.[/bold yellow]")
            
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Test execution interrupted by user.[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error during test execution: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
    finally:
        # Clean up services
        if service_manager and not args.no_cleanup:
            console.print("\n[bold]Cleaning up services...[/bold]")
            service_manager.stop_services()
    
    return 0

if __name__ == "__main__":
    # Set encoding environment variable to UTF-8 to avoid encoding issues
    if os.name == 'nt':  # Windows
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    sys.exit(main()) 