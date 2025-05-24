#!/usr/bin/env python
"""
Run script for the Job Recommender application with Next.js frontend.
This script starts both the FastAPI backend and Next.js frontend concurrently.
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
    """Run the FastAPI backend server with CORS enabled"""
    print("Starting Job Recommender API backend on http://localhost:8000")
    try:
        # Import and run the backend with CORS middleware
        from run_cors_backend import run_backend_with_cors
        run_backend_with_cors(reload_mode=True)
    except ImportError:
        print("Failed to import run_cors_backend. Falling back to subprocess method.")
        try:
            # Fall back to subprocess method
            subprocess.run(
                ["python", "run_cors_backend.py"],
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

def check_node_npm():
    """Check if Node.js and npm are installed and in PATH or locally in the frontend directory"""
    # First try global npm and node
    try:
        # Check if npm is installed globally
        npm_version = subprocess.run(
            ["npm", "--version"], 
            check=True, 
            capture_output=True, 
            text=True
        ).stdout.strip()
        
        # Check if node is installed globally
        node_version = subprocess.run(
            ["node", "--version"], 
            check=True, 
            capture_output=True, 
            text=True
        ).stdout.strip()
        
        print(f"Found global Node.js {node_version} and npm {npm_version}")
        return "global"
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Global Node.js/npm not found. Checking for local installation...")
        
        # Check if npm is installed locally in the frontend directory
        frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "lnd-nexus")
        bin_dir = os.path.join(frontend_dir, "node_modules", ".bin")
        
        if not os.path.exists(bin_dir):
            print(f"ERROR: .bin directory not found at {bin_dir}")
            return False
            
        print(f"Found .bin directory at {bin_dir}")
        
        # List all files in .bin directory to help debug
        try:
            bin_files = os.listdir(bin_dir)
            print(f"Files in .bin directory: {', '.join(bin_files)}")
        except Exception as e:
            print(f"Error listing .bin directory: {str(e)}")
        
        # Check for next executable
        next_cmd = os.path.join(bin_dir, "next")
        next_cmd_windows = os.path.join(bin_dir, "next.cmd")
        
        if os.name == 'nt':  # Windows
            if os.path.exists(next_cmd_windows):
                print(f"Found next.cmd at {next_cmd_windows}")
                return "local"
            else:
                print(f"next.cmd not found at {next_cmd_windows}")
        elif os.path.exists(next_cmd):
            print(f"Found next at {next_cmd}")
            return "local"
        else:
            print(f"next not found at {next_cmd}")
        
        print("ERROR: Node.js or npm is not installed globally or locally.")
        print("Please install Node.js and npm from https://nodejs.org/")
        print("Make sure they are added to your PATH environment variable.")
        
        if os.name == 'nt':  # Windows
            print("\nOn Windows, you can:")
            print("1. Download the installer from https://nodejs.org/")
            print("2. Run the installer and make sure to check 'Add to PATH' during installation")
            print("3. Restart your terminal/command prompt")
        else:  # Unix/Linux/Mac
            print("\nOn Unix/Linux/Mac, you can:")
            print("1. Use a package manager like apt, brew, or nvm")
            print("   Example: brew install node")
            print("2. Restart your terminal")
        
        return False

def run_nextjs_frontend():
    """Run the Next.js frontend application"""
    print("Starting Next.js frontend on http://localhost:3005")
    try:
        # Change to the frontend directory
        frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "lnd-nexus")
        os.chdir(frontend_dir)
        
        # Check if npm is installed
        npm_location = check_node_npm()
        if not npm_location:
            print("Cannot start Next.js frontend without Node.js and npm.")
            return False
            
        # Run the Next.js development server with custom port
        if npm_location == "global":
            # Use global npm
            subprocess.run(
                ["npm", "run", "dev", "--", "-p", "3005"],
                check=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
        else:
            # Use local npm/next
            bin_dir = os.path.join("node_modules", ".bin")
            next_cmd = os.path.join(bin_dir, "next")
            if os.name == 'nt':  # Windows
                next_cmd = os.path.join(bin_dir, "next.cmd")
                
            print(f"Running Next.js with local executable: {next_cmd}")
            
            # Make sure the file exists
            if not os.path.exists(next_cmd):
                print(f"ERROR: Next.js executable not found at {next_cmd}")
                return False
                
            subprocess.run(
                [next_cmd, "dev", "-p", "3005"],
                check=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Frontend process failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except KeyboardInterrupt:
        print("Frontend process terminated by user")
        return False
    except Exception as e:
        print(f"Error running frontend: {str(e)}")
        return False

def open_browser():
    """Open browser tabs for both applications after a short delay"""
    time.sleep(5)  # Wait for servers to start
    webbrowser.open("http://localhost:8000/docs")  # FastAPI Swagger docs
    webbrowser.open("http://localhost:3005")  # Next.js app

def handle_interrupt(signum, frame):
    """Handle keyboard interrupt to terminate all processes gracefully"""
    print("\nShutting down all services...")
    sys.exit(0)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run the Job Recommender application with Next.js frontend and FastAPI backend"
    )
    parser.add_argument(
        "--frontend-only", 
        action="store_true",
        help="Start only the frontend (Next.js) service"
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
        
    if frontend_required and is_port_in_use(3005):
        print("ERROR: Port 3005 is already in use. Next.js frontend cannot start.")
        print("Make sure no other Next.js applications are running.")
        return False
        
    return True

if __name__ == "__main__":
    # Set encoding environment variable to UTF-8 to avoid encoding issues on Windows
    if os.name == 'nt':  # Windows
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
    print("Job Recommender Application (Next.js + FastAPI)")
    print("==============================================")
    
    # Parse command line arguments
    args = parse_args()
    
    # Verify environment unless skipped
    if not args.skip_env_check:
        verify_environment()
    
    # Determine which components to run
    run_backend_flag = not args.frontend_only
    run_frontend_flag = not args.backend_only
    open_browser_flag = not args.no_browser
    
    # Check if ports are available
    if not check_ports(
        backend_required=run_backend_flag, 
        frontend_required=run_frontend_flag
    ):
        sys.exit(1)
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, handle_interrupt)
    
    # Start processes
    processes = []
    frontend_started = False
    
    try:
        if run_backend_flag:
            backend_process = multiprocessing.Process(target=run_backend)
            backend_process.start()
            processes.append(backend_process)
            
        if run_frontend_flag:
            # First check if Node.js and npm are installed
            if check_node_npm():
                frontend_process = multiprocessing.Process(target=run_nextjs_frontend)
                frontend_process.start()
                processes.append(frontend_process)
                frontend_started = True
            else:
                print("Cannot start frontend. Continuing with backend only.")
                if args.frontend_only:
                    print("Frontend-only mode requested but frontend cannot start. Exiting.")
                    sys.exit(1)
            
        if open_browser_flag and (not run_frontend_flag or frontend_started):
            # Wait a bit to let servers start
            time.sleep(2)
            browser_process = multiprocessing.Process(target=open_browser)
            browser_process.start()
            processes.append(browser_process)
        
        # Wait for all processes to complete (which they won't unless there's an error)
        for process in processes:
            process.join()
            
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Shutting down...")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Terminate all processes
        for process in processes:
            if process.is_alive():
                process.terminate()
                
        print("All services stopped.") 