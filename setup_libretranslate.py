#!/usr/bin/env python3
"""
LibreTranslate Setup Script
Helps set up LibreTranslate service for the job recommendation system.
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def check_docker():
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker found: {result.stdout.strip()}")
        
        # Check if Docker daemon is running
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, check=True)
        print("✅ Docker daemon is running")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker is not installed or not running")
        return False

def check_python_libretranslate():
    """Check if LibreTranslate Python package is available."""
    try:
        import libretranslate
        print("✅ LibreTranslate Python package is installed")
        return True
    except ImportError:
        print("❌ LibreTranslate Python package not found")
        return False

def install_libretranslate_pip():
    """Install LibreTranslate via pip."""
    print("\n🔧 Installing LibreTranslate via pip...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'libretranslate'], 
                      check=True)
        print("✅ LibreTranslate installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install LibreTranslate: {e}")
        return False

def run_libretranslate_docker():
    """Run LibreTranslate using Docker."""
    print("\n🐳 Starting LibreTranslate with Docker...")
    
    docker_cmd = [
        'docker', 'run', '-d',
        '--name', 'libretranslate',
        '-p', '5000:5000',
        'libretranslate/libretranslate'
    ]
    
    try:
        # Stop existing container if running
        subprocess.run(['docker', 'stop', 'libretranslate'], 
                      capture_output=True, check=False)
        subprocess.run(['docker', 'rm', 'libretranslate'], 
                      capture_output=True, check=False)
        
        # Start new container
        result = subprocess.run(docker_cmd, capture_output=True, text=True, check=True)
        print(f"✅ LibreTranslate Docker container started: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Docker container: {e}")
        return False

def run_libretranslate_pip():
    """Run LibreTranslate using pip installation."""
    print("\n🐍 Starting LibreTranslate with Python...")
    
    try:
        # Run LibreTranslate in background
        process = subprocess.Popen([
            sys.executable, '-m', 'libretranslate',
            '--host', '0.0.0.0',
            '--port', '5000',
            '--api-keys'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ LibreTranslate started with PID: {process.pid}")
        print("📝 Note: LibreTranslate is running in the background")
        
        # Save PID for later stopping
        with open('libretranslate.pid', 'w') as f:
            f.write(str(process.pid))
        
        return True
    except Exception as e:
        print(f"❌ Failed to start LibreTranslate: {e}")
        return False

def check_service_health():
    """Check if LibreTranslate service is responding."""
    print("\n🔍 Checking LibreTranslate service health...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:5000/languages', timeout=5)
            if response.status_code == 200:
                languages = response.json()
                print(f"✅ LibreTranslate is running! Available languages: {len(languages)}")
                print("🌐 Service URL: http://localhost:5000")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_attempts - 1:
            print(f"⏳ Waiting for service to start... ({attempt + 1}/{max_attempts})")
            time.sleep(2)
    
    print("❌ LibreTranslate service is not responding")
    return False

def create_stop_script():
    """Create a script to stop LibreTranslate service."""
    stop_script = """#!/usr/bin/env python3
import subprocess
import os
import sys

def stop_libretranslate():
    print("🛑 Stopping LibreTranslate service...")
    
    # Stop Docker container
    try:
        subprocess.run(['docker', 'stop', 'libretranslate'], 
                      capture_output=True, check=True)
        subprocess.run(['docker', 'rm', 'libretranslate'], 
                      capture_output=True, check=True)
        print("✅ Docker container stopped")
    except subprocess.CalledProcessError:
        pass
    
    # Stop pip process
    if os.path.exists('libretranslate.pid'):
        try:
            with open('libretranslate.pid', 'r') as f:
                pid = int(f.read().strip())
            
            if sys.platform == 'win32':
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
            else:
                subprocess.run(['kill', str(pid)], check=True)
            
            os.remove('libretranslate.pid')
            print("✅ Python process stopped")
        except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
            pass
    
    print("🎉 LibreTranslate service stopped")

if __name__ == "__main__":
    stop_libretranslate()
"""
    
    with open('stop_libretranslate.py', 'w') as f:
        f.write(stop_script)
    
    print("📝 Created stop_libretranslate.py script")

def main():
    print("LibreTranslate Setup for Job Recommendation System")
    print("=" * 50)
    
    print("\n🔍 Checking system requirements...")
    
    docker_available = check_docker()
    python_available = check_python_libretranslate()
    
    if not docker_available and not python_available:
        print("\n🤔 LibreTranslate is not available. Choose installation method:")
        print("1. Install via Docker (recommended)")
        print("2. Install via pip")
        print("3. Skip translation setup")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            if not docker_available:
                print("❌ Docker is required for this option")
                print("Please install Docker Desktop and try again")
                return False
        elif choice == "2":
            if not install_libretranslate_pip():
                return False
            python_available = True
        elif choice == "3":
            print("⏭️  Skipping translation setup")
            print("💡 You can run this script later to set up translation")
            return True
        else:
            print("❌ Invalid choice")
            return False
    
    # Start the service
    service_started = False
    
    if docker_available:
        print("\n🐳 Attempting to start with Docker...")
        service_started = run_libretranslate_docker()
    
    if not service_started and python_available:
        print("\n🐍 Attempting to start with Python...")
        service_started = run_libretranslate_pip()
    
    if not service_started:
        print("❌ Failed to start LibreTranslate service")
        return False
    
    # Check if service is healthy
    if check_service_health():
        create_stop_script()
        print("\n🎉 LibreTranslate setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Your frontend translation features should now work")
        print("2. Test the translation by visiting your Next.js app")
        print("3. Use 'python stop_libretranslate.py' to stop the service")
        return True
    else:
        print("❌ Service started but not responding properly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 