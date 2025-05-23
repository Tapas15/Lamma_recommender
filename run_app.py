#!/usr/bin/env python
"""
Run script for the complete Job Recommender application.
This script starts both the FastAPI backend and Streamlit frontend concurrently.
"""
import multiprocessing
import subprocess
import sys
import os
import time
import webbrowser
import signal
import argparse
import socket
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file (first from root, then fallback to backend/utils)
root_env_path = ".env"
backend_env_path = os.path.join("backend", "utils", ".env")

if os.path.exists(root_env_path):
    load_dotenv(dotenv_path=root_env_path)
    print(f"Loaded environment from {root_env_path}")
elif os.path.exists(backend_env_path):
    load_dotenv(dotenv_path=backend_env_path)
    print(f"Loaded environment from {backend_env_path}")
else:
    print("Warning: No .env file found. Using default environment variables.")

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use by attempting to connect to it"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def verify_environment() -> bool:
    """Verify that we're running in the correct environment"""
    # Check if we're in a virtual environment
    in_virtualenv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_virtualenv:
        venv_path = sys.prefix
        python_path = sys.executable
        print(f"Running in virtual environment: {venv_path}")
        print(f"Python executable: {python_path}")
        return True
    else:
        # Check if myenv exists in the current directory
        myenv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "myenv")
        if os.path.exists(myenv_dir):
            print(f"WARNING: Not running in virtual environment, but virtual environment exists at: {myenv_dir}")
            
            if os.name == 'nt':  # Windows
                print(f"Activate using: {os.path.join(myenv_dir, 'Scripts', 'activate')}")
            else:  # Unix/Linux/Mac
                print(f"Activate using: source {os.path.join(myenv_dir, 'bin', 'activate')}")
            
            confirmation = input("Do you want to continue without activating the virtual environment? (y/n): ")
            if confirmation.lower() != 'y':
                print("Operation cancelled. Please activate the virtual environment and try again.")
                sys.exit(1)
        else:
            print("WARNING: Not running in a virtual environment. This may cause dependency issues.")
            confirmation = input("Do you want to continue? (y/n): ")
            if confirmation.lower() != 'y':
                print("Operation cancelled.")
                sys.exit(1)
        
        return False

def run_backend():
    """Run the FastAPI backend server"""
    print("Starting Job Recommender API backend on http://localhost:8000")
    try:
        subprocess.run(
            ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            check=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
    except subprocess.CalledProcessError as e:
        print(f"Backend process failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Backend process terminated by user")
    except Exception as e:
        print(f"Error running backend: {str(e)}")
        sys.exit(1)

def run_frontend():
    """Run the Streamlit frontend application"""
    print("Starting Streamlit frontend on http://localhost:8501")
    try:
        subprocess.run(
            ["streamlit", "run", "streamlit_app.py"],
            check=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
    except subprocess.CalledProcessError as e:
        print(f"Frontend process failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Frontend process terminated by user")
    except Exception as e:
        print(f"Error running frontend: {str(e)}")
        sys.exit(1)

def open_browser():
    """Open browser tabs for both applications after a short delay"""
    time.sleep(3)  # Wait for servers to start
    webbrowser.open("http://localhost:8000/docs")  # FastAPI Swagger docs
    webbrowser.open("http://localhost:8501")  # Streamlit app

def handle_interrupt(signum, frame):
    """Handle keyboard interrupt to terminate all processes gracefully"""
    print("\nShutting down all services...")
    sys.exit(0)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run the Job Recommender application with backend and/or frontend"
    )
    parser.add_argument(
        "--frontend-only", 
        action="store_true",
        help="Start only the frontend (Streamlit) service"
    )
    parser.add_argument(
        "--backend-only", 
        action="store_true",
        help="Start only the backend (FastAPI) service"
    )
    parser.add_argument(
        "--no-browser", 
        action="store_true",
        help="Don't open browser tabs automatically"
    )
    parser.add_argument(
        "--skip-env-check", 
        action="store_true",
        help="Skip environment verification"
    )
    
    return parser.parse_args()

def check_ports(backend_required=True, frontend_required=True):
    """Check if required ports are available"""
    if backend_required and is_port_in_use(8000):
        print("ERROR: Port 8000 is already in use. Backend cannot start.")
        print("Use stop_app.py to stop any running instances first.")
        return False
        
    if frontend_required and is_port_in_use(8501):
        print("ERROR: Port 8501 is already in use. Frontend cannot start.")
        print("Use stop_app.py to stop any running instances first.")
        return False
        
    return True

if __name__ == "__main__":
    # Set encoding environment variable to UTF-8 to avoid encoding issues on Windows
    if os.name == 'nt':  # Windows
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
    print("Job Recommender Application")
    print("==========================")
    
    # Parse command line arguments
    args = parse_args()
    
    # Verify environment unless skipped
    if not args.skip_env_check:
        verify_environment()
    
    # Determine which components to run
    run_backend_flag = not args.frontend_only
    run_frontend_flag = not args.backend_only
    open_browser_flag = not args.no_browser and not (args.frontend_only or args.backend_only)
    
    # Check if ports are available
    if not check_ports(backend_required=run_backend_flag, frontend_required=run_frontend_flag):
        sys.exit(1)
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, handle_interrupt)
    
    if run_backend_flag and run_frontend_flag:
        print("\nStarting complete Job Recommender application...")
    elif run_backend_flag:
        print("\nStarting Job Recommender backend only...")
    elif run_frontend_flag:
        print("\nStarting Job Recommender frontend only...")
    
    # Create processes based on flags
    processes = []
    
    if run_backend_flag:
        backend_process = multiprocessing.Process(target=run_backend)
        processes.append(backend_process)
        backend_process.start()
        time.sleep(2)  # Give backend time to start before frontend
    
    if run_frontend_flag:
        frontend_process = multiprocessing.Process(target=run_frontend)
        processes.append(frontend_process)
        frontend_process.start()
    
    if open_browser_flag:
        browser_process = multiprocessing.Process(target=open_browser)
        processes.append(browser_process)
        browser_process.start()
    
    print("\nServices started. Press Ctrl+C to stop all services.")
    print("You can also run stop_app.py in another terminal to stop these services.")
    
    try:
        # Wait for processes to complete (which they won't unless interrupted)
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print("\nShutting down all services...")
    finally:
        # Ensure all processes are terminated
        for process in processes:
            if process.is_alive():
                process.terminate()
                try:
                    process.join(timeout=5)  # Give it 5 seconds to terminate
                    if process.is_alive():
                        process.kill()  # Force kill if still running
                except Exception:
                    pass
        
        print("All services shut down successfully.") 