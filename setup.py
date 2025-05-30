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

# LibreTranslate constants
LIBRETRANSLATE_PORT = 5000
LIBRETRANSLATE_URL = f"http://localhost:{LIBRETRANSLATE_PORT}"
LIBRETRANSLATE_DOCKER_IMAGE = "libretranslate/libretranslate:latest"

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

def is_docker_installed():
    """Check if Docker is installed"""
    try:
        if IS_WINDOWS:
            result = run_command(["docker", "--version"], check=False)
        else:
            result = run_command(["docker", "--version"], check=False)
        
        return result.returncode == 0
    except Exception:
        return False

def is_docker_running():
    """Check if Docker is running"""
    try:
        result = run_command(["docker", "info"], check=False)
        return result.returncode == 0
    except Exception:
        return False

def is_libretranslate_running():
    """Check if LibreTranslate is running"""
    try:
        response = requests.get(f"{LIBRETRANSLATE_URL}/languages", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def download_docker_windows():
    """Download Docker Desktop installer for Windows"""
    print("Downloading Docker Desktop for Windows...")
    try:
        # Create a temporary directory for the download
        temp_dir = os.path.join(os.environ.get('TEMP', '.'), 'docker_setup')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Docker Desktop download URL for Windows
        docker_url = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
        installer_path = os.path.join(temp_dir, "Docker-Desktop-Installer.exe")
        
        print("This may take several minutes depending on your internet connection...")
        with requests.get(docker_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            with open(installer_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloading: {percent:.1f}%", end="", flush=True)
        
        print("\n")
        print_success("Docker Desktop installer downloaded successfully.")
        print(f"Installer location: {installer_path}")
        print("\nIMPORTANT: Docker Desktop requires:")
        print("  - Windows 10 64-bit: Pro, Enterprise, or Education (Build 15063 or later)")
        print("  - WSL 2 feature enabled")
        print("  - Virtualization enabled in BIOS")
        
        # Ask if user wants to run the installer now
        response = input("\nDo you want to run the Docker Desktop installer now? (y/n): ").lower()
        if response == 'y':
            print("Running Docker Desktop installer...")
            print("Please follow the installation wizard and restart your computer if prompted.")
            subprocess.Popen([installer_path])
            print("\nAfter installation and restart:")
            print("1. Start Docker Desktop")
            print("2. Complete the initial setup")
            print("3. Restart this setup script")
            sys.exit(0)
        else:
            print("Please run the installer manually and then restart this setup script.")
            print("After installation, make sure Docker Desktop is running before continuing.")
            return False
            
    except Exception as e:
        print_error(f"Failed to download Docker Desktop: {str(e)}")
        print("Please download and install Docker Desktop manually from:")
        print("https://www.docker.com/products/docker-desktop")
        print("After installation, restart this setup script.")
        return False

def install_docker_linux():
    """Install Docker on Linux"""
    print("Installing Docker for Linux...")
    try:
        # Detect Linux distribution
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read().lower()
        except:
            os_info = ""
        
        if 'ubuntu' in os_info or 'debian' in os_info:
            print("Detected Ubuntu/Debian system. Installing Docker...")
            
            # Update package index
            print("Updating package index...")
            result = run_command(["sudo", "apt-get", "update"], check=False)
            if result.returncode != 0:
                print_warning("Failed to update package index, but continuing...")
            
            # Install prerequisites
            print("Installing prerequisites...")
            prereq_result = run_command([
                "sudo", "apt-get", "install", "-y",
                "ca-certificates", "curl", "gnupg", "lsb-release"
            ], check=False)
            
            if prereq_result.returncode != 0:
                print_warning("Failed to install some prerequisites, but continuing...")
            
            # Add Docker's official GPG key
            print("Adding Docker's GPG key...")
            run_command(["sudo", "mkdir", "-p", "/etc/apt/keyrings"], check=False)
            
            # Download and add GPG key
            gpg_result = run_command([
                "curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg"
            ], check=False)
            
            if gpg_result.returncode == 0:
                # Add the repository
                print("Adding Docker repository...")
                repo_cmd = [
                    "sudo", "sh", "-c",
                    'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list'
                ]
                run_command(repo_cmd, check=False)
                
                # Update package index again
                print("Updating package index with Docker repository...")
                run_command(["sudo", "apt-get", "update"], check=False)
                
                # Install Docker
                print("Installing Docker Engine...")
                install_result = run_command([
                    "sudo", "apt-get", "install", "-y",
                    "docker-ce", "docker-ce-cli", "containerd.io", "docker-compose-plugin"
                ], check=False)
                
                if install_result.returncode == 0:
                    print_success("Docker installed successfully.")
                    
                    # Start and enable Docker service
                    print("Starting Docker service...")
                    run_command(["sudo", "systemctl", "start", "docker"], check=False)
                    run_command(["sudo", "systemctl", "enable", "docker"], check=False)
                    
                    # Add current user to docker group
                    print("Adding current user to docker group...")
                    username = os.environ.get('USER', 'user')
                    run_command(["sudo", "usermod", "-aG", "docker", username], check=False)
                    
                    print_success("Docker installation completed.")
                    print_warning("You may need to log out and log back in for group changes to take effect.")
                    print_warning("Or run: newgrp docker")
                    return True
                else:
                    print_error("Failed to install Docker packages.")
                    return False
            else:
                print_error("Failed to add Docker GPG key.")
                return False
                
        elif 'centos' in os_info or 'rhel' in os_info or 'fedora' in os_info:
            print("Detected CentOS/RHEL/Fedora system. Installing Docker...")
            
            # Install using yum/dnf
            package_manager = "dnf" if 'fedora' in os_info else "yum"
            
            # Install prerequisites
            print("Installing prerequisites...")
            run_command(["sudo", package_manager, "install", "-y", "yum-utils"], check=False)
            
            # Add Docker repository
            print("Adding Docker repository...")
            run_command([
                "sudo", "yum-config-manager", "--add-repo",
                "https://download.docker.com/linux/centos/docker-ce.repo"
            ], check=False)
            
            # Install Docker
            print("Installing Docker...")
            install_result = run_command([
                "sudo", package_manager, "install", "-y",
                "docker-ce", "docker-ce-cli", "containerd.io", "docker-compose-plugin"
            ], check=False)
            
            if install_result.returncode == 0:
                print_success("Docker installed successfully.")
                
                # Start and enable Docker service
                print("Starting Docker service...")
                run_command(["sudo", "systemctl", "start", "docker"], check=False)
                run_command(["sudo", "systemctl", "enable", "docker"], check=False)
                
                # Add current user to docker group
                print("Adding current user to docker group...")
                username = os.environ.get('USER', 'user')
                run_command(["sudo", "usermod", "-aG", "docker", username], check=False)
                
                print_success("Docker installation completed.")
                print_warning("You may need to log out and log back in for group changes to take effect.")
                return True
            else:
                print_error("Failed to install Docker packages.")
                return False
        else:
            print_warning("Unsupported Linux distribution for automatic Docker installation.")
            print("Please install Docker manually using your distribution's package manager.")
            print("Visit: https://docs.docker.com/engine/install/")
            return False
            
    except Exception as e:
        print_error(f"Failed to install Docker: {str(e)}")
        print("Please install Docker manually using your distribution's package manager.")
        print("Visit: https://docs.docker.com/engine/install/")
        return False

def start_docker_service():
    """Start Docker service if it's not running"""
    print("Starting Docker service...")
    try:
        if IS_LINUX:
            # On Linux, try to start the Docker service
            result = run_command(["sudo", "systemctl", "start", "docker"], check=False)
            if result.returncode == 0:
                print_success("Docker service started successfully.")
                
                # Wait for Docker to be ready
                for _ in range(10):
                    if is_docker_running():
                        return True
                    time.sleep(1)
                
                print_warning("Docker service started but may not be fully ready.")
                return True
            else:
                print_warning("Failed to start Docker service.")
                return False
        else:
            # On Windows/Mac, Docker Desktop needs to be started manually
            print_warning("Please start Docker Desktop manually.")
            print("Docker Desktop should be available in your system tray or applications.")
            return False
            
    except Exception as e:
        print_error(f"Failed to start Docker service: {str(e)}")
        return False

def pull_translation_images():
    """Pull additional translation-related Docker images"""
    print("Pulling additional translation images...")
    
    # List of useful translation and language processing images
    translation_images = [
        "libretranslate/libretranslate:latest",
        "libretranslate/libretranslate:v1.3.11",  # Stable version
    ]
    
    success_count = 0
    for image in translation_images:
        try:
            print(f"Pulling {image}...")
            result = run_command(["docker", "pull", image], check=False)
            if result.returncode == 0:
                print_success(f"Successfully pulled {image}")
                success_count += 1
            else:
                print_warning(f"Failed to pull {image}")
        except Exception as e:
            print_warning(f"Error pulling {image}: {str(e)}")
    
    if success_count > 0:
        print_success(f"Successfully pulled {success_count} translation images.")
        return True
    else:
        print_warning("Failed to pull any translation images.")
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

def setup_libretranslate():
    """Set up LibreTranslate Docker container for translation"""
    print_step(0.5, "Setting up LibreTranslate for translation...")
    
    # Check if Docker is installed
    if is_docker_installed():
        print_success("Docker is installed.")
    else:
        print_warning("Docker is not installed.")
        print("LibreTranslate requires Docker to run. Attempting automatic installation...")
        
        if IS_WINDOWS:
            print("Attempting to download Docker Desktop for Windows...")
            if not download_docker_windows():
                print_warning("Automatic Docker installation failed.")
                print_warning("Please install Docker Desktop manually from:")
                print_warning("https://www.docker.com/products/docker-desktop")
                print_warning("Continuing setup without LibreTranslate.")
                return False
            # If download_docker_windows() succeeds, it will exit the script for manual installation
        elif IS_LINUX:
            print("Attempting to install Docker for Linux...")
            if not install_docker_linux():
                print_warning("Automatic Docker installation failed.")
                print_warning("Please install Docker manually using your distribution's package manager.")
                print_warning("Visit: https://docs.docker.com/engine/install/")
                print_warning("Continuing setup without LibreTranslate.")
                return False
            else:
                print_success("Docker installed successfully.")
        else:  # macOS
            print_warning("Automatic Docker installation not supported on macOS.")
            print_warning("Please install Docker Desktop manually from:")
            print_warning("https://www.docker.com/products/docker-desktop")
            print_warning("Continuing setup without LibreTranslate.")
            return False
    
    # Check if Docker is running
    if is_docker_running():
        print_success("Docker is running.")
    else:
        print_warning("Docker is installed but not running.")
        
        # Try to start Docker service on Linux
        if IS_LINUX:
            print("Attempting to start Docker service...")
            if start_docker_service():
                print_success("Docker service started.")
            else:
                print_warning("Failed to start Docker service.")
                print_warning("Please start Docker manually and then run:")
                print(f"  docker run -d --name libretranslate -p {LIBRETRANSLATE_PORT}:{LIBRETRANSLATE_PORT} {LIBRETRANSLATE_DOCKER_IMAGE}")
                print_warning("Continuing setup without LibreTranslate.")
                return False
        else:
            print_warning("Please start Docker Desktop and then run:")
            print(f"  docker run -d --name libretranslate -p {LIBRETRANSLATE_PORT}:{LIBRETRANSLATE_PORT} {LIBRETRANSLATE_DOCKER_IMAGE}")
            print_warning("Continuing setup without LibreTranslate.")
            return False
    
    # Check if LibreTranslate is already running
    if is_libretranslate_running():
        print_success("LibreTranslate is already running.")
        return True
    
    # Pull translation images
    print("Pulling translation Docker images (this might take a while)...")
    try:
        # Pull additional translation images
        pull_translation_images()
        
        # Check if container with the same name is already running
        check_result = run_command(["docker", "ps", "-q", "--filter", "name=libretranslate"], check=False)
        if check_result.stdout.strip():
            print_warning("A container named 'libretranslate' is already running.")
            print_warning("Using the existing container.")
            return True
        
        # Check if container exists but is stopped
        check_stopped = run_command(["docker", "ps", "-aq", "--filter", "name=libretranslate"], check=False)
        if check_stopped.stdout.strip():
            print("Found existing LibreTranslate container. Starting it...")
            start_result = run_command(["docker", "start", "libretranslate"], check=False)
            if start_result.returncode == 0:
                print_success("Existing LibreTranslate container started successfully.")
            else:
                print_warning("Failed to start existing container. Creating a new one...")
                # Remove the old container
                run_command(["docker", "rm", "libretranslate"], check=False)
        
        # Run the container with additional options for better performance
        print("Starting LibreTranslate container...")
        run_result = run_command([
            "docker", "run", "-d",
            "--name", "libretranslate",
            "-p", f"{LIBRETRANSLATE_PORT}:{LIBRETRANSLATE_PORT}",
            "--restart", "unless-stopped",  # Auto-restart policy
            "-e", "LT_DISABLE_WEB_UI=false",  # Enable web UI
            "-e", "LT_UPDATE_MODELS=true",    # Auto-update models
            LIBRETRANSLATE_DOCKER_IMAGE
        ], check=False)
        
        if run_result.returncode != 0:
            print_warning("Failed to start LibreTranslate container.")
            print_warning("You can start it manually later with:")
            print(f"  docker run -d --name libretranslate -p {LIBRETRANSLATE_PORT}:{LIBRETRANSLATE_PORT} {LIBRETRANSLATE_DOCKER_IMAGE}")
            return False
        
        print_success("LibreTranslate container started successfully.")
        
        # Wait for service to start
        print("Waiting for LibreTranslate service to start...")
        for i in range(30):  # Increased timeout to 30 seconds
            if is_libretranslate_running():
                print_success("LibreTranslate service is running.")
                print(f"LibreTranslate web interface available at: http://localhost:{LIBRETRANSLATE_PORT}")
                return True
            time.sleep(1)
            if i % 5 == 0:  # Show progress every 5 seconds
                print(f"Still waiting... ({i}/30 seconds)")
        
        print_warning("LibreTranslate service might not have started properly.")
        print_warning("You can check its status with:")
        print("  docker logs libretranslate")
        print_warning("The service might still be initializing. Please wait a few more minutes.")
        return False
        
    except Exception as e:
        print_warning(f"Error setting up LibreTranslate: {str(e)}")
        print_warning("Continuing setup without LibreTranslate.")
        return False

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
    
    # Try to find Python 3.10 executable
    python_executables = [
        "python3.10",
        "python3.10.exe",
        "py -3.10",
        "python",  # fallback to current python
        sys.executable  # final fallback
    ]
    
    python_cmd = None
    for cmd in python_executables:
        try:
            if cmd == "py -3.10":
                # Special handling for Windows py launcher
                result = run_command(["py", "-3.10", "--version"], check=False)
            else:
                result = run_command([cmd, "--version"], check=False)
            
            if result.returncode == 0:
                version_output = result.stdout.strip()
                if "Python 3.10" in version_output:
                    python_cmd = cmd if cmd != "py -3.10" else ["py", "-3.10"]
                    print_success(f"Found Python 3.10: {version_output}")
                    break
                elif "Python 3." in version_output:
                    print_warning(f"Found {version_output}, but Python 3.10 is recommended")
                    if python_cmd is None:  # Use as fallback
                        python_cmd = cmd
        except Exception:
            continue
    
    if python_cmd is None:
        print_error("Could not find a suitable Python executable.")
        print("Please ensure Python 3.10 is installed and available in your PATH.")
        print("You can download Python 3.10 from: https://www.python.org/downloads/")
        return False
    
    # Create virtual environment with the found Python executable
    try:
        if isinstance(python_cmd, list):
            # Handle py launcher case
            cmd = python_cmd + ["-m", "venv", VENV_DIR]
        else:
            cmd = [python_cmd, "-m", "venv", VENV_DIR]
        
        result = run_command(cmd)
        if result.returncode == 0:
            print_success("Virtual environment created successfully with Python 3.10.")
            return True
        else:
            print_error("Failed to create virtual environment.")
            return False
    except Exception as e:
        print_error(f"Error creating virtual environment: {str(e)}")
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
                
                # Install language support dependencies
                print("Installing language support dependencies...")
                lang_deps_result = run_command(
                    ["npm", "install", "@radix-ui/react-dropdown-menu", "clsx", "tailwind-merge"], 
                    cwd=frontend_path
                )
                
                # Install translation dependencies
                print("Installing translation dependencies...")
                trans_deps_result = run_command(
                    ["npm", "install", "tesseract.js", "lucide-react"], 
                    cwd=frontend_path
                )
                
                if npm_result.returncode == 0 and lang_deps_result.returncode == 0 and trans_deps_result.returncode == 0:
                    print_success("Frontend dependencies installed successfully.")
                    print_success("Language support dependencies installed successfully.")
                    print_success("Translation dependencies installed successfully.")
                    
                    # Verify translation modules are present
                    print("Verifying translation modules...")
                    if os.path.exists("test/translation_modules/verify_translation_modules.py"):
                        verify_result = run_command([PYTHON_EXEC, "test/translation_modules/verify_translation_modules.py"], check=False)
                        if verify_result.returncode == 0:
                            print_success("All translation modules are present and verified.")
                        else:
                            print_warning("Some translation modules may be missing, but this is normal for first-time setup.")
                            print_warning("Translation modules have been created automatically.")
                    else:
                        print_warning("Translation module verification script not found, but modules should be present.")
                    
                    # Setup frontend environment variables
                    print("Setting up frontend environment variables...")
                    if os.path.exists("test/translation_modules/setup_frontend_env.py"):
                        env_result = run_command([PYTHON_EXEC, "test/translation_modules/setup_frontend_env.py"], check=False)
                        if env_result.returncode == 0:
                            print_success("Frontend environment variables configured.")
                        else:
                            print_warning("Failed to setup frontend environment variables.")
                    else:
                        print_warning("Frontend environment setup script not found.")
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
        "DATABASE_NAME": "job_recommender",
        "LIBRETRANSLATE_URL": LIBRETRANSLATE_URL
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
    print("\nExamples:")
    print("  - Local MongoDB: mongodb://localhost:27017")
    print("  - MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/")
    print("\nOptions:")
    print("1. Keep current MongoDB URL")
    print("2. Enter a new MongoDB URL")
    
    choice = input("\nEnter your choice (1/2): ").strip()
    
    if choice == "2":
        print("\nWaiting 30 seconds for MongoDB URL input. If no input is provided, will keep current URL...")
        
        # Use timeout for MongoDB URL input
        mongodb_url = None
        try:
            import threading
            import queue
            import time
            
            def get_url_input(q):
                try:
                    user_input = input("Enter new MongoDB URL: ").strip()
                    q.put(user_input)
                except:
                    q.put(None)
            
            q = queue.Queue()
            input_thread = threading.Thread(target=get_url_input, args=(q,))
            input_thread.daemon = True
            input_thread.start()
            
            # Wait for 30 seconds with countdown
            for remaining in range(30, 0, -1):
                try:
                    mongodb_url = q.get(timeout=1)
                    if mongodb_url is not None:
                        break
                except queue.Empty:
                    # Show countdown every 5 seconds
                    if remaining % 5 == 0 or remaining <= 5:
                        print(f"\rWaiting for MongoDB URL... {remaining} seconds remaining (will keep current URL)", end="", flush=True)
                    continue
            
            if mongodb_url is None:
                print("\n\nTimeout reached. Keeping current MongoDB URL.")
                mongodb_url = ""
                
        except Exception as e:
            print(f"\nError with timeout mechanism: {e}")
            print("Keeping current MongoDB URL.")
            mongodb_url = ""
        
        if mongodb_url:
            env_vars["MONGODB_URL"] = mongodb_url
            print_success(f"MongoDB URL updated to: {mongodb_url}")
        else:
            print_warning("No URL entered, keeping current value.")
    else:
        print(f"Keeping current MongoDB URL: {env_vars['MONGODB_URL']}")
    
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
    
    # Ask user if they want to use an existing MongoDB URL or the current one
    print("\nMongoDB Connection Setup:")
    print("-------------------------")
    print(f"Current MongoDB URL: {mongodb_url}")
    print("\nOptions:")
    print("1. Use current MongoDB URL")
    print("2. Enter a different MongoDB URL")
    print("3. Skip database initialization (continue setup)")
    
    print("\nWaiting 30 seconds for input. If no input is provided, will use current MongoDB URL...")
    
    # Use timeout for input
    choice = None
    try:
        import threading
        import queue
        import time
        
        def get_input(q):
            try:
                user_input = input("\nEnter your choice (1/2/3): ").strip()
                q.put(user_input)
            except:
                q.put(None)
        
        q = queue.Queue()
        input_thread = threading.Thread(target=get_input, args=(q,))
        input_thread.daemon = True
        input_thread.start()
        
        # Wait for 30 seconds with countdown
        for remaining in range(30, 0, -1):
            try:
                choice = q.get(timeout=1)
                if choice is not None:
                    break
            except queue.Empty:
                # Show countdown every 5 seconds
                if remaining % 5 == 0 or remaining <= 5:
                    print(f"\rWaiting for input... {remaining} seconds remaining (will use current MongoDB URL)", end="", flush=True)
                continue
        
        if choice is None:
            print("\n\nTimeout reached. Using current MongoDB URL (option 1).")
            choice = "1"
                
    except Exception as e:
        print(f"\nError with timeout mechanism: {e}")
        print("Using current MongoDB URL (option 1).")
        choice = "1"
    
    if choice == "2":
        print("\nEnter your existing MongoDB URL:")
        print("Examples:")
        print("  - Local MongoDB: mongodb://localhost:27017")
        print("  - MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/")
        print("\nWaiting 30 seconds for MongoDB URL input. If no input is provided, will use current URL...")
        
        # Use timeout for MongoDB URL input
        new_mongodb_url = None
        try:
            import threading
            import queue
            import time
            
            def get_url_input(q):
                try:
                    user_input = input("MongoDB URL: ").strip()
                    q.put(user_input)
                except:
                    q.put(None)
            
            q = queue.Queue()
            input_thread = threading.Thread(target=get_url_input, args=(q,))
            input_thread.daemon = True
            input_thread.start()
            
            # Wait for 30 seconds with countdown
            for remaining in range(30, 0, -1):
                try:
                    new_mongodb_url = q.get(timeout=1)
                    if new_mongodb_url is not None:
                        break
                except queue.Empty:
                    # Show countdown every 5 seconds
                    if remaining % 5 == 0 or remaining <= 5:
                        print(f"\rWaiting for MongoDB URL... {remaining} seconds remaining (will use current URL)", end="", flush=True)
                    continue
            
            if new_mongodb_url is None:
                print("\n\nTimeout reached. Using current MongoDB URL.")
                new_mongodb_url = ""
                
        except Exception as e:
            print(f"\nError with timeout mechanism: {e}")
            print("Using current MongoDB URL.")
            new_mongodb_url = ""
        
        if new_mongodb_url:
            mongodb_url = new_mongodb_url
            # Update the .env file with the new URL
            env_vars["MONGODB_URL"] = mongodb_url
            try:
                with open(".env", "w") as f:
                    for key, value in env_vars.items():
                        f.write(f"{key}={value}\n")
                print_success("Updated .env file with new MongoDB URL.")
            except Exception as e:
                print_warning(f"Could not update .env file: {str(e)}")
        else:
            print_warning("No URL entered, using current URL.")
    elif choice == "3":
        print_warning("Skipping database initialization.")
        print("You can initialize the database later by running:")
        print(f"  {PYTHON_EXEC} backend/init_db.py")
        return True  # Continue setup instead of failing
    
    # Check if MongoDB is running (wait for 30 seconds, then continue)
    print(f"\nTesting MongoDB connection to: {mongodb_url}")
    print("Waiting up to 30 seconds for connection...")
    
    connection_successful = False
    try:
        import pymongo
        client = pymongo.MongoClient(mongodb_url, serverSelectionTimeoutMS=30000)
        client.server_info()  # Will raise an exception if MongoDB is not running
        print_success("MongoDB connection successful!")
        connection_successful = True
    except Exception as e:
        print_warning(f"MongoDB connection failed: {str(e)}")
        print_warning("Connection timeout after 30 seconds.")
        print("This could be due to:")
        print("  - MongoDB server not running")
        print("  - Incorrect connection URL")
        print("  - Network connectivity issues")
        print("  - Firewall blocking the connection")
        
        print("\nSetup will continue without database initialization.")
        print("You can initialize the database later by:")
        print(f"  1. Ensuring MongoDB is running and accessible")
        print(f"  2. Running: {PYTHON_EXEC} backend/init_db.py")
        return True  # Continue setup instead of failing
    
    # If connection was successful, proceed with database initialization
    if connection_successful:
        # Set environment variables for the database initialization script
        os.environ["MONGODB_URL"] = mongodb_url
        os.environ["DATABASE_NAME"] = database_name
        
        print("Initializing database schema and collections...")
        # Run the database initialization script
        result = run_command([PYTHON_EXEC, os.path.join("backend", "init_db.py")])
        if result.returncode == 0:
            print_success("Database initialized successfully.")
            return True
        else:
            print_warning("Database initialization script failed.")
            print("You can initialize the database later by running:")
            print(f"  {PYTHON_EXEC} backend/init_db.py")
            return True  # Continue setup instead of failing
    
    return True

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
    
    print("\nDatabase Information:")
    print(f"  - If database initialization was skipped during setup, you can run it later:")
    print(f"    {Colors.BOLD}python backend/init_db.py{Colors.ENDC}")
    print(f"  - To test your MongoDB connection:")
    print(f"    {Colors.BOLD}python test/mongodb_tests/test_mongodb_setup.py{Colors.ENDC}")
    print(f"  - Make sure your MongoDB URL is correctly set in the .env file")
    
    print("\nThe application will be available at:")
    print(f"  - Backend API: {Colors.BLUE}http://localhost:8000{Colors.ENDC}")
    if os.path.exists(frontend_path):
        print(f"  - Next.js Frontend: {Colors.BLUE}http://localhost:3000{Colors.ENDC}")
    print(f"  - LibreTranslate API: {Colors.BLUE}http://localhost:5000{Colors.ENDC}")
    print(f"  - LibreTranslate Web UI: {Colors.BLUE}http://localhost:5000{Colors.ENDC}")
    
    print("\nDocker and Translation Services:")
    print(f"  - Docker installation is handled automatically for Windows and Linux")
    print(f"  - LibreTranslate container is configured with auto-restart policy")
    print(f"  - Translation models are automatically updated")
    print(f"  - To check LibreTranslate status: {Colors.BOLD}docker logs libretranslate{Colors.ENDC}")
    print(f"  - To restart LibreTranslate: {Colors.BOLD}docker restart libretranslate{Colors.ENDC}")
    print(f"  - To stop LibreTranslate: {Colors.BOLD}docker stop libretranslate{Colors.ENDC}")
    
    # Add language support information
    print("\nLanguage Support:")
    print(f"  - The application supports {Colors.BOLD}English{Colors.ENDC} and {Colors.BOLD}Arabic{Colors.ENDC} languages")
    print(f"  - Language can be switched using the language selector in the navigation bar")
    print(f"  - Backend API supports language selection through Accept-Language header or lang query parameter")
    print(f"  - Frontend automatically handles RTL layout for Arabic language")
    print(f"  - LibreTranslate provides English to Arabic translation for entire pages")
    print(f"  - Translation button is already integrated in the UI navigation")
    print(f"  - Full page translation including text and images is supported")
    print(f"  - OCR capabilities for extracting and translating text from images")
    
    print("\nFor more information, see:")
    print(f"  - {Colors.BOLD}README.md{Colors.ENDC} - General information about the application")
    print(f"  - {Colors.BOLD}RUN_INSTRUCTIONS.md{Colors.ENDC} - Detailed instructions for running the application")
    print(f"  - {Colors.BOLD}TRANSLATION_FEATURE.md{Colors.ENDC} - Details about the English to Arabic translation feature")
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
        setup_libretranslate,     # Step 0.5
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
