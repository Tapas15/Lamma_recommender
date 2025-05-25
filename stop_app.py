#!/usr/bin/env python
"""
Script to stop running Job Recommender application processes.
This will find and terminate both backend (uvicorn) and frontend (streamlit) processes.
"""
import os
import sys
import psutil
import time
import socket
import requests
from typing import List, Dict, Tuple
from pathlib import Path
from dotenv import load_dotenv

BACKEND_PORT = 8000
FRONTEND_PORT = 8501
LIBRETRANSLATE_PORT = 5000

# Load environment variables from .env file (first from root, then fallback to backend/utils)
root_env_path = ".env"
backend_env_path = os.path.join("backend", "utils", ".env")

def check_env_files():
    """Check for .env files and return info about them"""
    results = []
    
    if os.path.exists(root_env_path):
        results.append(f"Root .env file found: {os.path.abspath(root_env_path)}")
        load_dotenv(dotenv_path=root_env_path)
    
    if os.path.exists(backend_env_path):
        if os.path.exists(root_env_path):
            results.append(f"Backend .env file found: {os.path.abspath(backend_env_path)} (should be synchronized with root)")
        else:
            results.append(f"Backend .env file found: {os.path.abspath(backend_env_path)} (note: no root .env file)")
            load_dotenv(dotenv_path=backend_env_path)
    
    if not results:
        results.append("No .env files found.")
    
    # Add MongoDB URL info if available
    mongodb_url = os.getenv("MONGODB_URL")
    if mongodb_url:
        # Mask password in connection string if present
        if "@" in mongodb_url and "://" in mongodb_url:
            parts = mongodb_url.split("@", 1)
            prefix = parts[0].split("://", 1)
            if len(prefix) > 1:
                masked = f"{prefix[0]}://{prefix[1].split(':')[0]}:******@{parts[1]}"
                results.append(f"MongoDB URL: {masked}")
            else:
                results.append(f"MongoDB URL is set (credentials masked)")
        else:
            results.append(f"MongoDB URL: {mongodb_url}")
    else:
        results.append("MongoDB URL not found in environment.")
        
    return results

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use by attempting to connect to it"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def is_service_responding(url: str) -> bool:
    """Check if a service is responding at the given URL"""
    try:
        response = requests.get(url, timeout=2)
        return response.status_code < 400
    except:
        return False

def is_docker_installed() -> bool:
    """Check if Docker is installed"""
    try:
        import subprocess
        result = subprocess.run(["docker", "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               check=False)
        return result.returncode == 0
    except:
        return False

def is_libretranslate_container_running() -> bool:
    """Check if the LibreTranslate container is running"""
    if not is_docker_installed():
        return False
    
    try:
        import subprocess
        result = subprocess.run(["docker", "ps", "-q", "--filter", "name=libretranslate"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               check=False)
        return bool(result.stdout.strip())
    except:
        return False

def stop_libretranslate_container() -> bool:
    """Stop the LibreTranslate Docker container"""
    if not is_docker_installed():
        return False
    
    try:
        import subprocess
        result = subprocess.run(["docker", "stop", "libretranslate"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               check=False)
        return result.returncode == 0
    except:
        return False

def find_app_processes() -> Dict[str, List[psutil.Process]]:
    """Find all processes related to our app"""
    processes = {
        "backend": [],
        "frontend": []
    }
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline:
                cmdline_str = ' '.join(cmdline)
                
                # Backend processes (uvicorn)
                if 'uvicorn' in cmdline_str and 'backend.app:app' in cmdline_str:
                    processes['backend'].append(proc)
                
                # Frontend processes (streamlit)
                if 'streamlit' in cmdline_str and 'streamlit_app.py' in cmdline_str:
                    processes['frontend'].append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return processes

def kill_process_tree(process: psutil.Process) -> None:
    """Kill a process and all its children"""
    try:
        children = process.children(recursive=True)
        process.terminate()
        
        _, still_alive = psutil.wait_procs([process], timeout=3)
        if still_alive:
            for p in still_alive:
                p.kill()
        
        for child in children:
            try:
                if child.is_running():
                    child.terminate()
                    
                if child.is_running():
                    child.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
        print(f"Error killing process {process.pid}: {e}")

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
        else:
            print("WARNING: Not running in a virtual environment. This may cause dependency issues.")
        
        return False

def main():
    """Main function to stop all app processes"""
    print("Job Recommender Application - Process Manager")
    print("============================================")
    
    # Verify environment
    verify_environment()
    
    # Check .env files
    print("\nEnvironment Configuration:")
    for info in check_env_files():
        print(f"- {info}")
    
    # Check if services are running by checking ports
    backend_running = is_port_in_use(BACKEND_PORT)
    frontend_running = is_port_in_use(FRONTEND_PORT)
    libretranslate_running = is_port_in_use(LIBRETRANSLATE_PORT)
    libretranslate_container = is_libretranslate_container_running()
    
    print(f"\nService Status:")
    print(f"- Backend (port {BACKEND_PORT}): {'RUNNING' if backend_running else 'NOT RUNNING'}")
    print(f"- Frontend (port {FRONTEND_PORT}): {'RUNNING' if frontend_running else 'NOT RUNNING'}")
    print(f"- LibreTranslate (port {LIBRETRANSLATE_PORT}): {'RUNNING' if libretranslate_running else 'NOT RUNNING'}")
    print(f"- LibreTranslate Docker Container: {'RUNNING' if libretranslate_container else 'NOT RUNNING'}")
    
    if not backend_running and not frontend_running and not libretranslate_running and not libretranslate_container:
        print("\nNo application services appear to be running.")
        return 0
    
    # Find processes
    app_processes = find_app_processes()
    backend_count = len(app_processes["backend"])
    frontend_count = len(app_processes["frontend"])
    
    print(f"\nFound {backend_count} backend processes and {frontend_count} frontend processes.")
    
    # Kill processes
    if backend_count > 0 or frontend_count > 0 or libretranslate_container:
        confirmation = input("\nDo you want to stop these processes and containers? (y/n): ")
        if confirmation.lower() != 'y':
            print("Operation cancelled.")
            return 0
        
        # Kill backend processes
        for proc in app_processes["backend"]:
            try:
                print(f"Stopping backend process {proc.pid}...")
                kill_process_tree(proc)
            except Exception as e:
                print(f"Error stopping process: {e}")
        
        # Kill frontend processes
        for proc in app_processes["frontend"]:
            try:
                print(f"Stopping frontend process {proc.pid}...")
                kill_process_tree(proc)
            except Exception as e:
                print(f"Error stopping process: {e}")
        
        # Stop LibreTranslate Docker container if running
        if libretranslate_container:
            print("\nStopping LibreTranslate Docker container...")
            if stop_libretranslate_container():
                print("LibreTranslate Docker container stopped successfully.")
            else:
                print("Failed to stop LibreTranslate Docker container.")
                print("You may need to stop it manually with: docker stop libretranslate")
        
        # Verify services are stopped
        time.sleep(2)
        backend_still_running = is_port_in_use(BACKEND_PORT)
        frontend_still_running = is_port_in_use(FRONTEND_PORT)
        libretranslate_still_running = is_port_in_use(LIBRETRANSLATE_PORT)
        libretranslate_container_still_running = is_libretranslate_container_running()
        
        print("\nFinal Status:")
        print(f"- Backend: {'STILL RUNNING' if backend_still_running else 'STOPPED'}")
        print(f"- Frontend: {'STILL RUNNING' if frontend_still_running else 'STOPPED'}")
        print(f"- LibreTranslate: {'STILL RUNNING' if libretranslate_still_running else 'STOPPED'}")
        print(f"- LibreTranslate Container: {'STILL RUNNING' if libretranslate_container_still_running else 'STOPPED'}")
        
        if backend_still_running or frontend_still_running or libretranslate_still_running or libretranslate_container_still_running:
            print("\nSome services are still running. You may need to kill them manually.")
            return 1
        else:
            print("\nAll services have been stopped successfully.")
            return 0
    else:
        print("No matching processes found, though ports appear to be in use.")
        print("The services might be running under different process names.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 