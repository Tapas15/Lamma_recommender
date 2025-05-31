#!/usr/bin/env python
"""
Streamlit Configuration Check Script
This script diagnoses and fixes common issues preventing Streamlit from running.
"""
import sys
import os
import subprocess
import requests
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Warning: Python 3.8+ recommended for Streamlit")
        return False
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = ['streamlit', 'requests', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nTo install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    return True

def check_backend_connection():
    """Check if backend API is accessible"""
    api_url = "http://localhost:8000"
    endpoints_to_check = [
        "/health",
        "/docs", 
        "/"
    ]
    
    print(f"\nChecking backend connection to {api_url}...")
    
    backend_running = False
    for endpoint in endpoints_to_check:
        try:
            response = requests.get(f"{api_url}{endpoint}", timeout=5)
            if response.status_code in [200, 404]:  # 404 is okay for some endpoints
                print(f"✓ Backend responding at {endpoint}")
                backend_running = True
                break
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {endpoint}")
        except Exception as e:
            print(f"❌ Error checking {endpoint}: {str(e)}")
    
    if not backend_running:
        print("\n🚨 Backend is not running!")
        print("To start the backend, run one of these commands:")
        print("  python run_cors_backend.py")
        print("  python app_with_candidates.py")
        print("  uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000")
        return False
    
    return True

def check_streamlit_config():
    """Check Streamlit configuration and common issues"""
    print("\nChecking Streamlit configuration...")
    
    # Check if streamlit_app.py exists
    if not os.path.exists('streamlit_app.py'):
        print("❌ streamlit_app.py not found in current directory")
        return False
    else:
        print("✓ streamlit_app.py found")
    
    # Check pages directory
    if not os.path.exists('pages'):
        print("❌ pages/ directory not found")
        return False
    else:
        print("✓ pages/ directory found")
        
        # List page files
        page_files = [f for f in os.listdir('pages') if f.endswith('.py')]
        print(f"✓ Found {len(page_files)} page files")
    
    return True

def check_port_availability():
    """Check if Streamlit's default port is available"""
    import socket
    
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    streamlit_port = 8501
    if is_port_in_use(streamlit_port):
        print(f"⚠️  Port {streamlit_port} is already in use")
        print("You can specify a different port with: streamlit run streamlit_app.py --server.port 8502")
        return False
    else:
        print(f"✓ Port {streamlit_port} is available")
        return True

def run_streamlit_diagnosis():
    """Run comprehensive Streamlit diagnosis"""
    print("=" * 60)
    print("STREAMLIT APP DIAGNOSTIC REPORT")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Streamlit Config", check_streamlit_config),
        ("Backend Connection", check_backend_connection),
        ("Port Availability", check_port_availability),
    ]
    
    results = {}
    
    for check_name, check_function in checks:
        print(f"\n--- {check_name} ---")
        try:
            results[check_name] = check_function()
        except Exception as e:
            print(f"❌ Error during {check_name}: {str(e)}")
            results[check_name] = False
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Streamlit should run successfully.")
        print("\nTo start the app, run:")
        print("  streamlit run streamlit_app.py")
    else:
        print("\n⚠️  Some issues found. Please fix the failed checks above.")
        print("\n📋 Quick fix commands:")
        if not results.get("Backend Connection", False):
            print("  1. Start backend: python run_cors_backend.py")
        if not results.get("Dependencies", False):
            print("  2. Install deps: pip install streamlit requests pandas")
        print("  3. Then run: streamlit run streamlit_app.py")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = run_streamlit_diagnosis()
        
        if success:
            print("\n🚀 Ready to launch Streamlit!")
            user_input = input("\nWould you like to start Streamlit now? (y/n): ")
            if user_input.lower() in ['y', 'yes']:
                print("Starting Streamlit...")
                subprocess.run(['streamlit', 'run', 'streamlit_app.py'])
        else:
            print("\n❌ Please fix the issues above before running Streamlit.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnostic cancelled by user")
    except Exception as e:
        print(f"\n💥 Diagnostic error: {str(e)}")
        import traceback
        traceback.print_exc() 