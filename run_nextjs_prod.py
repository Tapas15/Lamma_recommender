#!/usr/bin/env python
"""
Run script for the Job Recommender application with Next.js frontend in production mode.
This script starts both the FastAPI backend and Next.js frontend in production mode concurrently.
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
        run_backend_with_cors()
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
        # Check if npm is installed locally in the frontend directory
        frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "lnd-nexus")
        npm_path = os.path.join(frontend_dir, "node_modules", ".bin", "npm")
        next_path = os.path.join(frontend_dir, "node_modules", ".bin", "next")
        
        # On Windows, use the .cmd files
        if os.name == 'nt':
            npm_path += ".cmd"
            next_path += ".cmd"
            
        if os.path.exists(npm_path) and os.path.exists(next_path):
            print(f"Found local npm and next in {frontend_dir}/node_modules/.bin")
            return "local"
        
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

def build_nextjs_frontend():
    """Build the Next.js frontend application"""
    print("Building Next.js frontend...")
    try:
        # Change to the frontend directory
        frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "lnd-nexus")
        os.chdir(frontend_dir)
        
        # Check if npm is installed
        npm_location = check_node_npm()
        if not npm_location:
            print("Cannot build Next.js frontend without Node.js and npm.")
            return False
            
        # Build the Next.js application
        if npm_location == "global":
            # Use global npm
            subprocess.run(
                ["npm", "run", "build"],
                check=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
        else:
            # Use local npm/next
            next_cmd = os.path.join("node_modules", ".bin", "next")
            if os.name == 'nt':  # Windows
                next_cmd += ".cmd"
                
            subprocess.run(
                [next_cmd, "build"],
                check=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
        print("Next.js frontend built successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Frontend build failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except KeyboardInterrupt:
        print("Frontend build terminated by user")
        return False
    except Exception as e:
        print(f"Error building frontend: {str(e)}")
        return False

def run_nextjs_frontend_prod():
    """Run the Next.js frontend application in production mode"""
    print("Starting Next.js frontend in production mode on http://localhost:3005")
    try:
        # Change to the frontend directory
        frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "lnd-nexus")
        os.chdir(frontend_dir)
        
        # Check if npm is installed
        npm_location = check_node_npm()
        if not npm_location:
            print("Cannot start Next.js frontend without Node.js and npm.")
            return False
            
        # Run the Next.js production server
        if npm_location == "global":
            # Use global npm
            subprocess.run(
                ["npm", "run", "start:prod"],
                check=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
        else:
            # Use local npm/next
            next_cmd = os.path.join("node_modules", ".bin", "next")
            if os.name == 'nt':  # Windows
                next_cmd += ".cmd"
                
            # For production, we use next start with the port parameter
            subprocess.run(
                [next_cmd, "start", "-p", "3005"],
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
        description="Run the Job Recommender application with Next.js frontend in production mode"
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
    parser.add_argument(
        "--skip-build", 
        action="store_true",
        help="Skip building the Next.js frontend"
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
        
    print("Job Recommender Application (Next.js Production + FastAPI)")
    print("=======================================================")
    
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
    
    # Build the Next.js frontend unless skipped
    frontend_built = False
    if run_frontend_flag and not args.skip_build:
        frontend_built = build_nextjs_frontend()
        if not frontend_built and not args.skip_build:
            print("ERROR: Failed to build Next.js frontend.")
            if args.frontend_only:
                print("Frontend-only mode requested but frontend cannot be built. Exiting.")
                sys.exit(1)
            else:
                print("Continuing with backend only.")
                run_frontend_flag = False
    
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
            
        if run_frontend_flag and (frontend_built or args.skip_build):
            frontend_process = multiprocessing.Process(target=run_nextjs_frontend_prod)
            frontend_process.start()
            processes.append(frontend_process)
            frontend_started = True
            
        if open_browser_flag and (not run_frontend_flag or frontend_started):
            # Wait a bit longer for production server to start
            time.sleep(5)
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