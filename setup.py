#!/usr/bin/env python
"""
Setup script for the Job Recommender application.
This script automates the entire installation and setup process.
"""
import os
import sys
import subprocess
import platform
import time
import webbrowser
from pathlib import Path
import requests
import json
import shutil
import uuid

# Define colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Check if we're on Windows
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"
VENV_DIR = "myenv"
VENV_BIN = os.path.join(VENV_DIR, "Scripts" if IS_WINDOWS else "bin")
PYTHON_EXEC = os.path.join(VENV_BIN, "python.exe" if IS_WINDOWS else "python")
PIP_EXEC = os.path.join(VENV_BIN, "pip.exe" if IS_WINDOWS else "pip")

# Ollama constants
OLLAMA_PORT = 11434
OLLAMA_URL = f"http://localhost:{OLLAMA_PORT}"
OLLAMA_MODEL = "llama3.2"
OLLAMA_WINDOWS_URL = "https://ollama.com/download/windows"
OLLAMA_LINUX_INSTALL_CMD = 'curl -fsSL https://ollama.com/install.sh | sh'
OLLAMA_MAC_URL = "https://ollama.com/download/mac"

# Default MongoDB connection
DEFAULT_MONGODB_URL = "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/"

def print_step(step, message):
    """Print a formatted step message"""
    print(f"{Colors.HEADER}[Step {step}]{Colors.ENDC} {Colors.BOLD}{message}{Colors.ENDC}")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def run_command(command, cwd=None, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,  # Changed from text=True to handle binary output
            shell=IS_WINDOWS  # Use shell on Windows
        )
        # Manually decode output with UTF-8 and handle errors
        stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
        stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""
        
        # Create a new CompletedProcess with decoded text
        decoded_result = subprocess.CompletedProcess(
            args=result.args,
            returncode=result.returncode,
            stdout=stdout,
            stderr=stderr
        )
        return decoded_result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(command if isinstance(command, list) else [command])}")
        # Safely decode error output
        error_msg = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else str(e.stderr)
        print(f"Error: {error_msg}")
        return e

def is_ollama_installed():
    """Check if Ollama is installed and running"""
    try:
        # Try to connect to Ollama API
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    
    # Check if ollama executable exists in path
    try:
        if IS_WINDOWS:
            result = run_command(["where", "ollama"], check=False)
        else:
            result = run_command(["which", "ollama"], check=False)
        
        return result.returncode == 0
    except Exception:
        return False

def is_ollama_running():
    """Check if Ollama server is running"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def is_model_available(model_name):
    """Check if a specific model is available in Ollama"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any(model.get("name") == model_name for model in models)
    except requests.exceptions.RequestException:
        pass
    return False

def download_ollama_windows():
    """Download Ollama installer for Windows"""
    print("Downloading Ollama for Windows...")
    try:
        # Create a temporary directory for the download
        temp_dir = os.path.join(os.environ.get('TEMP', '.'), 'ollama_setup')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download the installer
        installer_path = os.path.join(temp_dir, "ollama-installer.exe")
        with requests.get(OLLAMA_WINDOWS_URL, stream=True) as r:
            r.raise_for_status()
            with open(installer_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        print_success("Ollama installer downloaded successfully.")
        print(f"Please run the installer at: {installer_path}")
        print("After installation, restart this setup script.")
        
        # Ask if user wants to run the installer now
        response = input("Do you want to run the Ollama installer now? (y/n): ").lower()
        if response == 'y':
            print("Running Ollama installer...")
            # Start the installer
            subprocess.Popen([installer_path])
            print("Please complete the installation and then restart this setup script.")
            sys.exit(0)
        else:
            print("Please run the installer manually and then restart this setup script.")
            sys.exit(0)
            
    except Exception as e:
        print_error(f"Failed to download Ollama: {str(e)}")
        print("Please download and install Ollama manually from: https://ollama.com/download/windows")
        print("After installation, restart this setup script.")
        sys.exit(1)

def install_ollama_linux():
    """Install Ollama on Linux"""
    print("Installing Ollama for Linux...")
    try:
        # Run the Ollama installation command
        result = run_command(OLLAMA_LINUX_INSTALL_CMD, check=False, shell=True)
        if result.returncode == 0:
            print_success("Ollama installed successfully.")
            return True
        else:
            print_error("Failed to install Ollama automatically.")
            print("Please install Ollama manually using the following command:")
            print(f"  {OLLAMA_LINUX_INSTALL_CMD}")
            print("After installation, restart this setup script.")
            return False
    except Exception as e:
        print_error(f"Failed to install Ollama: {str(e)}")
        print("Please install Ollama manually using the following command:")
        print(f"  {OLLAMA_LINUX_INSTALL_CMD}")
        print("After installation, restart this setup script.")
        return False

def start_ollama_service():
    """Start the Ollama service"""
    print("Starting Ollama service...")
    try:
        if IS_WINDOWS:
            # On Windows, start ollama.exe with proper encoding
            process = subprocess.Popen(
                ["ollama", "serve"], 
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                env=dict(os.environ, PYTHONIOENCODING="utf-8")  # Set UTF-8 encoding
            )
        else:
            # On Linux/Mac, start ollama service
            run_command(["ollama", "serve"], check=False)
        
        # Wait for service to start
        for _ in range(10):
            if is_ollama_running():
                print_success("Ollama service started successfully.")
                return True
            time.sleep(1)
        
        print_warning("Ollama service might not have started properly.")
        return False
    except Exception as e:
        print_error(f"Failed to start Ollama service: {str(e)}")
        return False

def pull_ollama_model(model_name):
    """Pull a model from Ollama"""
    print(f"Pulling {model_name} model (this might take a while)...")
    try:
        # Use the updated run_command function which now handles Unicode properly
        result = run_command(["ollama", "pull", model_name], check=False)
        
        if result.returncode == 0:
            print_success(f"{model_name} model pulled successfully.")
            return True
        else:
            print_error(f"Failed to pull {model_name} model.")
            if result.stderr:
                print(f"Error details: {result.stderr}")
            print("\nYou can pull the model manually later using:")
            print(f"  ollama pull {model_name}")
            
            # Provide alternative options
            print("\nAlternatively, you can try:")
            print("1. Running the command in PowerShell with UTF-8 encoding:")
            print(f"   $env:PYTHONIOENCODING=\"utf-8\"; ollama pull {model_name}")
            print("2. Using a different model:")
            print("   ollama pull llama3")
            return False
    except Exception as e:
        print_error(f"Failed to pull {model_name} model: {str(e)}")
        print("\nYou can pull the model manually later using:")
        print(f"  ollama pull {model_name}")
        print("\nAlternatively, try running in PowerShell with:")
        print(f"  $env:PYTHONIOENCODING=\"utf-8\"; ollama pull {model_name}")
        return False

def setup_ollama():
    """Set up Ollama and required models"""
    print_step(0, "Setting up Ollama...")
    
    # Check if Ollama is installed
    if is_ollama_installed():
        print_success("Ollama is installed.")
    else:
        print_warning("Ollama is not installed.")
        
        if IS_WINDOWS:
            download_ollama_windows()
            # The script will exit after providing download instructions
        elif IS_LINUX:
            if not install_ollama_linux():
                # If installation failed, continue with warnings
                print_warning("Continuing setup without Ollama.")
                print_warning("You'll need to install Ollama manually later.")
                return False
        else:  # macOS
            print("Please download and install Ollama manually from: https://ollama.com/download/mac")
            print("After installation, restart this setup script.")
            response = input("Press Enter to continue setup without Ollama, or 'q' to quit: ")
            if response.lower() == 'q':
                sys.exit(0)
            else:
                print_warning("Continuing setup without Ollama.")
                return False
    
    # Check if Ollama service is running
    if is_ollama_running():
        print_success("Ollama service is running.")
    else:
        print_warning("Ollama service is not running. Attempting to start...")
        if not start_ollama_service():
            print_warning("Could not start Ollama service.")
            print_warning("You'll need to start it manually later using 'ollama serve'.")
            return False
    
    # Check if required model is available
    if is_model_available(OLLAMA_MODEL):
        print_success(f"{OLLAMA_MODEL} model is available.")
    else:
        print_warning(f"{OLLAMA_MODEL} model is not available. Attempting to pull...")
        if not pull_ollama_model(OLLAMA_MODEL):
            print_warning(f"Could not pull {OLLAMA_MODEL} model.")
            print_warning(f"You'll need to pull it manually later using 'ollama pull {OLLAMA_MODEL}'.")
            return False
    
    return True

def create_virtual_environment():
    """Create a Python virtual environment"""
    print_step(1, "Creating Python virtual environment...")
    
    # Check if virtual environment already exists
    if os.path.exists(VENV_DIR):
        print_warning(f"Virtual environment '{VENV_DIR}' already exists.")
        response = input("Do you want to use the existing virtual environment? (y/n): ").lower()
        if response == 'n':
            print("Removing existing virtual environment...")
            shutil.rmtree(VENV_DIR)
        else:
            print_success("Using existing virtual environment.")
            return True
    
    # Create virtual environment
    result = run_command([sys.executable, "-m", "venv", VENV_DIR])
    if result.returncode == 0:
        print_success("Virtual environment created successfully.")
        return True
    else:
        print_error("Failed to create virtual environment.")
        return False

def install_dependencies():
    """Install required Python packages"""
    print_step(2, "Installing dependencies...")
    
    # Upgrade pip
    print("Upgrading pip...")
    try:
        result = run_command([PIP_EXEC, "install", "--upgrade", "pip"])
        if result.returncode == 0:
            print_success("Pip upgraded successfully.")
        else:
            print_warning("Failed to upgrade pip, but continuing with installation.")
            print_warning("This is not critical and the setup can continue.")
    except Exception as e:
        print_warning(f"Error upgrading pip: {str(e)}")
        print_warning("Continuing with installation without upgrading pip.")
    
    # Install dependencies from requirements.txt
    if os.path.exists("requirements.txt"):
        print("Installing from requirements.txt...")
        result = run_command([PIP_EXEC, "install", "-r", "requirements.txt"])
        if result.returncode != 0:
            print_error("Failed to install dependencies from requirements.txt.")
            return False
    else:
        print_warning("requirements.txt not found. Installing dependencies individually...")
        
        # Install FastAPI and related packages
        print("Installing FastAPI and related packages...")
        result = run_command([
            PIP_EXEC, "install", "fastapi>=0.95.0", "uvicorn>=0.21.1", 
            "python-jose[cryptography]>=3.3.0", "passlib[bcrypt]>=1.7.4",
            "python-dotenv>=1.0.0"
        ])
        if result.returncode != 0:
            print_error("Failed to install FastAPI and related packages.")
            return False
        
        # Install MongoDB-related packages
        print("Installing MongoDB-related packages...")
        result = run_command([PIP_EXEC, "install", "motor>=3.1.1", "pymongo>=4.6.0"])
        if result.returncode != 0:
            print_error("Failed to install MongoDB-related packages.")
            return False
        
        # Install other utilities
        print("Installing utility packages...")
        result = run_command([
            PIP_EXEC, "install", "requests>=2.28.2", "numpy>=1.24.2", 
            "python-multipart>=0.0.6", "pydantic>=2.0.0", "email-validator>=2.0.0"
        ])
        if result.returncode != 0:
            print_error("Failed to install utility packages.")
            return False
    
    # Install streamlit
    print("Installing Streamlit...")
    result = run_command([PIP_EXEC, "install", "streamlit"])
    if result.returncode != 0:
        print_error("Failed to install Streamlit.")
        return False
    
    # Install frontend dependencies (Next.js)
    print_step(2.5, "Installing frontend dependencies...")
    frontend_path = os.path.join("frontend", "lnd-nexus")
    if os.path.exists(frontend_path) and os.path.exists(os.path.join(frontend_path, "package.json")):
        print("Installing frontend dependencies with npm...")
        try:
            # Check if npm is installed
            npm_check = run_command(["npm", "--version"], check=False)
            if npm_check.returncode != 0:
                print_error("npm is not installed. Please install Node.js and npm to set up the frontend.")
                print_warning("You can continue without installing frontend dependencies, but the Next.js frontend will not work.")
                choice = input("Continue without installing frontend dependencies? (y/n): ").lower()
                if choice != 'y':
                    return False
            else:
                # Install frontend dependencies
                npm_result = run_command(["npm", "install"], cwd=frontend_path)
                if npm_result.returncode == 0:
                    print_success("Frontend dependencies installed successfully.")
                else:
                    print_error("Failed to install frontend dependencies.")
                    print_warning("You can continue without frontend dependencies, but the Next.js frontend will not work.")
                    choice = input("Continue without installing frontend dependencies? (y/n): ").lower()
                    if choice != 'y':
                        return False
        except Exception as e:
            print_error(f"Error installing frontend dependencies: {str(e)}")
            print_warning("Continuing without installing frontend dependencies.")
    else:
        print_warning("Frontend directory or package.json not found. Skipping frontend dependencies installation.")
    
    print_success("All dependencies installed successfully.")
    return True

def read_existing_env():
    """Read existing .env file if it exists"""
    env_vars = {
        "OLLAMA_API_BASE": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3.2",
        "SECRET_KEY": f"sk_{uuid.uuid4().hex}",
        "MONGODB_URL": DEFAULT_MONGODB_URL,
        "DATABASE_NAME": "job_recommender"
    }
    
    # Check for .env in root directory first
    root_env_path = ".env"
    if os.path.exists(root_env_path):
        try:
            with open(root_env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
            print_success("Loaded existing environment variables from .env file.")
        except Exception as e:
            print_warning(f"Error reading existing .env file: {str(e)}")
    
    # Also check in backend/utils as fallback
    backend_env_path = os.path.join("backend", "utils", ".env")
    if os.path.exists(backend_env_path) and not os.path.exists(root_env_path):
        try:
            with open(backend_env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
            print_success("Loaded existing environment variables from backend/utils/.env file.")
        except Exception as e:
            print_warning(f"Error reading existing backend .env file: {str(e)}")
    
    return env_vars

def create_env_file():
    """Create .env file if it doesn't exist or update as needed"""
    print_step(3, "Setting up environment variables...")
    
    # Read existing environment variables if any
    env_vars = read_existing_env()
    
    # Ask for MongoDB URL
    print("\nMongoDB Configuration:")
    print("---------------------")
    print("MongoDB URL is required for the application to store data.")
    print(f"Current MongoDB URL: {env_vars['MONGODB_URL']}")
    print("Examples:")
    print("  - Local MongoDB: mongodb://localhost:27017")
    print("  - MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/")
    print("\nLeave blank to use the current value.")
    
    mongodb_url = input("Enter MongoDB URL: ").strip()
    if mongodb_url:
        env_vars["MONGODB_URL"] = mongodb_url
    else:
        print(f"Using existing MongoDB URL: {env_vars['MONGODB_URL']}")
    
    # Create .env file in the root directory
    root_env_path = ".env"
    try:
        with open(root_env_path, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        print_success(".env file created successfully in root directory.")
        
        # Create a symlink or copy in backend/utils for compatibility
        backend_utils_dir = os.path.join("backend", "utils")
        if os.path.exists(backend_utils_dir):
            backend_env_path = os.path.join(backend_utils_dir, ".env")
            
            # If an old .env file exists in backend/utils, remove it
            if os.path.exists(backend_env_path):
                os.remove(backend_env_path)
            
            # Copy the .env file to backend/utils
            shutil.copy2(root_env_path, backend_env_path)
            print_success("Created .env copy in backend/utils directory for compatibility.")
            
        return True
    except Exception as e:
        print_error(f"Failed to create .env file: {str(e)}")
        return False

def initialize_database():
    """Initialize the MongoDB database"""
    print_step(4, "Initializing database...")
    
    # Get MongoDB settings from .env file
    env_vars = read_existing_env()
    mongodb_url = env_vars.get("MONGODB_URL", DEFAULT_MONGODB_URL)
    database_name = env_vars.get("DATABASE_NAME", "job_recommender")
    
    # Check if MongoDB is running
    print("Checking MongoDB connection...")
    try:
        import pymongo
        client = pymongo.MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        client.server_info()  # Will raise an exception if MongoDB is not running
        print_success("MongoDB connection successful.")
    except Exception as e:
        print_error(f"MongoDB connection failed: {str(e)}")
        print_warning("There was an issue connecting to MongoDB.")
        print("You can initialize the database later by running:")
        print(f"  {PYTHON_EXEC} backend/init_db.py")
        return False
    
    # Set environment variables for the database initialization script
    os.environ["MONGODB_URL"] = mongodb_url
    os.environ["DATABASE_NAME"] = database_name
    
    # Run the database initialization script
    result = run_command([PYTHON_EXEC, os.path.join("backend", "init_db.py")])
    if result.returncode == 0:
        print_success("Database initialized successfully.")
        return True
    else:
        print_error("Failed to initialize database.")
        print_warning("You can initialize the database later by running:")
        print(f"  {PYTHON_EXEC} backend/init_db.py")
        return False

def create_run_scripts():
    """Create platform-specific run scripts"""
    print_step(5, "Creating run scripts...")
    
    # Create run script for the current platform
    if IS_WINDOWS:
        # Windows batch file for the full application
        with open("run_app.bat", "w") as f:
            f.write("@echo off\n")
            f.write(f"call {os.path.join(VENV_BIN, 'activate.bat')}\n")
            f.write("echo Starting Job Recommender Application...\n")
            f.write("python run_app.py\n")
            f.write("pause\n")
        
        # Windows batch file for just the backend
        with open("run_backend.bat", "w") as f:
            f.write("@echo off\n")
            f.write(f"call {os.path.join(VENV_BIN, 'activate.bat')}\n")
            f.write("echo Starting Job Recommender API backend...\n")
            f.write("python run_backend.py\n")
            f.write("pause\n")
        
        # Windows batch file for Next.js application (combined backend + Next.js frontend)
        if os.path.exists("run_nextjs_app.py"):
            with open("run_nextjs_app.bat", "w") as f:
                f.write("@echo off\n")
                f.write(f"call {os.path.join(VENV_BIN, 'activate.bat')}\n")
                f.write("echo Starting Job Recommender Application with Next.js frontend...\n")
                f.write("python run_nextjs_app.py\n")
                f.write("pause\n")
        
        # Windows batch file for Next.js frontend only
        frontend_path = os.path.join("frontend", "lnd-nexus")
        if os.path.exists(frontend_path) and os.path.exists(os.path.join(frontend_path, "package.json")):
            with open("run_nextjs.bat", "w") as f:
                f.write("@echo off\n")
                f.write(f"cd {frontend_path}\n")
                f.write("echo Starting Next.js frontend development server...\n")
                f.write("npm run dev\n")
                f.write("pause\n")
            
            with open("run_nextjs_prod.bat", "w") as f:
                f.write("@echo off\n")
                f.write(f"cd {frontend_path}\n")
                f.write("echo Building Next.js frontend for production...\n")
                f.write("npm run build\n")
                f.write("echo Starting Next.js frontend production server...\n")
                f.write("npm start\n")
                f.write("pause\n")
            
            if os.path.exists("run_nextjs_app.py"):
                print_success("Created Windows batch files: run_app.bat, run_backend.bat, run_nextjs_app.bat, run_nextjs.bat, run_nextjs_prod.bat")
            else:
                print_success("Created Windows batch files: run_app.bat, run_backend.bat, run_nextjs.bat, run_nextjs_prod.bat")
        else:
            if os.path.exists("run_nextjs_app.py"):
                print_success("Created Windows batch files: run_app.bat, run_backend.bat, run_nextjs_app.bat")
            else:
                print_success("Created Windows batch files: run_app.bat, run_backend.bat")
    else:
        # Unix shell script for the full application
        with open("run_app.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"source {os.path.join(VENV_BIN, 'activate')}\n")
            f.write("echo Starting Job Recommender Application...\n")
            f.write("python run_app.py\n")
        
        # Unix shell script for just the backend
        with open("run_backend.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"source {os.path.join(VENV_BIN, 'activate')}\n")
            f.write("echo Starting Job Recommender API backend...\n")
            f.write("python run_backend.py\n")
        
        # Unix shell script for Next.js application (combined backend + Next.js frontend)
        if os.path.exists("run_nextjs_app.py"):
            with open("run_nextjs_app.sh", "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"source {os.path.join(VENV_BIN, 'activate')}\n")
                f.write("echo Starting Job Recommender Application with Next.js frontend...\n")
                f.write("python run_nextjs_app.py\n")
            # Make the script executable
            os.chmod("run_nextjs_app.sh", 0o755)
        
        # Make the standard shell scripts executable
        os.chmod("run_app.sh", 0o755)
        os.chmod("run_backend.sh", 0o755)
        
        # Unix shell script for Next.js frontend only
        frontend_path = os.path.join("frontend", "lnd-nexus")
        if os.path.exists(frontend_path) and os.path.exists(os.path.join(frontend_path, "package.json")):
            with open("run_nextjs.sh", "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"cd {frontend_path}\n")
                f.write("echo Starting Next.js frontend development server...\n")
                f.write("npm run dev\n")
            
            with open("run_nextjs_prod.sh", "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"cd {frontend_path}\n")
                f.write("echo Building Next.js frontend for production...\n")
                f.write("npm run build\n")
                f.write("echo Starting Next.js frontend production server...\n")
                f.write("npm start\n")
            
            # Make the Next.js shell scripts executable
            os.chmod("run_nextjs.sh", 0o755)
            os.chmod("run_nextjs_prod.sh", 0o755)
            
            if os.path.exists("run_nextjs_app.py"):
                print_success("Created Unix shell scripts: run_app.sh, run_backend.sh, run_nextjs_app.sh, run_nextjs.sh, run_nextjs_prod.sh")
            else:
                print_success("Created Unix shell scripts: run_app.sh, run_backend.sh, run_nextjs.sh, run_nextjs_prod.sh")
        else:
            if os.path.exists("run_nextjs_app.py"):
                print_success("Created Unix shell scripts: run_app.sh, run_backend.sh, run_nextjs_app.sh")
            else:
                print_success("Created Unix shell scripts: run_app.sh, run_backend.sh")
    
    return True

def print_completion_message():
    """Print completion message with instructions"""
    print("\n" + "="*80)
    print(f"{Colors.GREEN}{Colors.BOLD}Job Recommender Application Setup Complete!{Colors.ENDC}")
    print("="*80)
    
    print("\nTo run the complete application (backend + frontend):")
    
    if IS_WINDOWS:
        print(f"  Option 1: Double-click on {Colors.BOLD}run_app.bat{Colors.ENDC}")
        print("  Option 2: In command prompt/PowerShell:")
        print(f"    1. Activate the virtual environment: {Colors.BOLD}{os.path.join(VENV_BIN, 'activate.bat')}{Colors.ENDC}")
        print(f"    2. Run the application: {Colors.BOLD}python run_app.py{Colors.ENDC}")
    else:
        print(f"  Option 1: Run the shell script: {Colors.BOLD}./run_app.sh{Colors.ENDC}")
        print("  Option 2: In terminal:")
        print(f"    1. Activate the virtual environment: {Colors.BOLD}source {os.path.join(VENV_BIN, 'activate')}{Colors.ENDC}")
        print(f"    2. Run the application: {Colors.BOLD}python run_app.py{Colors.ENDC}")
        
    print("\nTo run the application with Next.js frontend:")
    if os.path.exists("run_nextjs_app.py"):
        if IS_WINDOWS:
            print(f"  Option 1: Double-click on {Colors.BOLD}run_nextjs_app.bat{Colors.ENDC}")
            print(f"  Option 2: In command prompt/PowerShell:")
            print(f"    1. Activate the virtual environment: {Colors.BOLD}{os.path.join(VENV_BIN, 'activate.bat')}{Colors.ENDC}")
            print(f"    2. Run the application: {Colors.BOLD}python run_nextjs_app.py{Colors.ENDC}")
        else:
            print(f"  Option 1: Run the shell script: {Colors.BOLD}./run_nextjs_app.sh{Colors.ENDC}")
            print(f"  Option 2: In terminal:")
            print(f"    1. Activate the virtual environment: {Colors.BOLD}source {os.path.join(VENV_BIN, 'activate')}{Colors.ENDC}")
            print(f"    2. Run the application: {Colors.BOLD}python run_nextjs_app.py{Colors.ENDC}")
    else:
        print(f"  {Colors.WARNING}run_nextjs_app.py not found. Cannot run with Next.js frontend.{Colors.ENDC}")
    
    print("\nTo run just the backend API:")
    
    if IS_WINDOWS:
        print(f"  Option 1: Double-click on {Colors.BOLD}run_backend.bat{Colors.ENDC}")
        print("  Option 2: In command prompt/PowerShell:")
        print(f"    1. Activate the virtual environment: {Colors.BOLD}{os.path.join(VENV_BIN, 'activate.bat')}{Colors.ENDC}")
        print(f"    2. Run the backend: {Colors.BOLD}python run_backend.py{Colors.ENDC}")
    else:
        print(f"  Option 1: Run the shell script: {Colors.BOLD}./run_backend.sh{Colors.ENDC}")
        print("  Option 2: In terminal:")
        print(f"    1. Activate the virtual environment: {Colors.BOLD}source {os.path.join(VENV_BIN, 'activate')}{Colors.ENDC}")
        print(f"    2. Run the backend: {Colors.BOLD}python run_backend.py{Colors.ENDC}")
    
    # Add Next.js frontend instructions
    print("\nTo run the Next.js frontend:")
    frontend_path = os.path.join("frontend", "lnd-nexus")
    if os.path.exists(frontend_path) and os.path.exists(os.path.join(frontend_path, "package.json")):
        print("  In a separate terminal:")
        print(f"    1. Navigate to the frontend directory: {Colors.BOLD}cd {frontend_path}{Colors.ENDC}")
        print(f"    2. Start the development server: {Colors.BOLD}npm run dev{Colors.ENDC}")
        print(f"    3. For production build: {Colors.BOLD}npm run build{Colors.ENDC} followed by {Colors.BOLD}npm start{Colors.ENDC}")
        print(f"  The Next.js frontend will be available at: {Colors.BLUE}http://localhost:3000{Colors.ENDC}")
    else:
        print(f"  {Colors.WARNING}Next.js frontend not found or not set up.{Colors.ENDC}")
    
    print("\nTo stop all running services:")
    print(f"  Run: {Colors.BOLD}python stop_app.py{Colors.ENDC}")
    
    print("\nThe application will be available at:")
    print(f"  - Backend API: {Colors.BLUE}http://localhost:8000{Colors.ENDC}")
    print(f"  - API Documentation: {Colors.BLUE}http://localhost:8000/docs{Colors.ENDC}")
    print(f"  - Streamlit Frontend: {Colors.BLUE}http://localhost:8501{Colors.ENDC}")
    if os.path.exists(frontend_path):
        print(f"  - Next.js Frontend: {Colors.BLUE}http://localhost:3000{Colors.ENDC}")
    
    print("\nFor more information, see:")
    print(f"  - {Colors.BOLD}README.md{Colors.ENDC} - General information about the application")
    print(f"  - {Colors.BOLD}RUN_INSTRUCTIONS.md{Colors.ENDC} - Detailed instructions for running the application")
    if os.path.exists("NEXTJS_INTEGRATION.md"):
        print(f"  - {Colors.BOLD}NEXTJS_INTEGRATION.md{Colors.ENDC} - Details about the Next.js frontend")
    
    print("\n" + "="*80)

def run_application():
    """Ask if user wants to run the application now"""
    print("\nDo you want to run the application now? (y/n): ", end="")
    response = input().lower()
    
    if response == 'y':
        print_step(6, "Running the application with Next.js frontend...")
        
        # Check if run_nextjs_app.py exists
        if os.path.exists("run_nextjs_app.py"):
            try:
                # Run the application with Next.js frontend
                print("Starting the application with Next.js frontend and FastAPI backend...")
                
                # Use subprocess to run the application
                cmd = [PYTHON_EXEC, "run_nextjs_app.py"]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="ignore"
                )
                
                print_success("Application started successfully.")
                print("Press Ctrl+C to stop the application.")
                
                # Keep the main thread running
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nShutting down application...")
                    process.terminate()
                    
            except Exception as e:
                print_error(f"Failed to run application with Next.js: {str(e)}")
        else:
            print_warning("run_nextjs_app.py not found. Falling back to standard application.")
            
            # Import and run the standard application
            try:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from run_app import run_backend, run_frontend, open_browser
                import threading
                
                # Start the backend in a separate thread
                backend_thread = threading.Thread(target=run_backend)
                backend_thread.daemon = True
                backend_thread.start()
                
                # Wait for backend to start
                time.sleep(2)
                
                # Start the frontend in a separate thread
                frontend_thread = threading.Thread(target=run_frontend)
                frontend_thread.daemon = True
                frontend_thread.start()
                
                # Open browser
                open_browser()
                
                print_success("Application started successfully.")
                print("Press Ctrl+C to stop the application.")
                
                # Keep the main thread running
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nShutting down application...")
                    
            except Exception as e:
                print_error(f"Failed to run application: {str(e)}")

def main():
    """Main setup function"""
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}Job Recommender Application Setup{Colors.ENDC}")
    print("=" * 80 + "\n")
    
    # Setup steps
    steps = [
        setup_ollama,            # Step 0
        create_virtual_environment,  # Step 1
        install_dependencies,    # Step 2
        create_env_file,         # Step 3
        initialize_database,     # Step 4
        create_run_scripts,      # Step 5
    ]
    
    # Keep track of any warnings or errors
    issues = []
    
    # Run each step
    for step_func in steps:
        success = step_func()
        if not success:
            issues.append(step_func.__name__)
    
    # Print completion message
    print_completion_message()
    
    # Print issues summary if any
    if issues:
        print("\n" + "-" * 80)
        print(f"{Colors.WARNING}Setup completed with some issues:{Colors.ENDC}")
        for issue in issues:
            print(f" - {issue}")
        print("-" * 80)
    
    # Ask to run the application
    run_application()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 