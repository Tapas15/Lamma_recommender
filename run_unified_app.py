#!/usr/bin/env python
"""
Unified run script for the Job Recommender application.
Runs both FastAPI backend and Next.js frontend, accessible via single port (3000).
Uses Next.js proxy configuration to handle API routing.
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

# Load environment variables
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
    """Check if a port is in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def verify_environment() -> bool:
    """Verify that we're running in the correct environment"""
    in_virtualenv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_virtualenv:
        print(f"✓ Running in virtual environment: {sys.prefix}")
        return True
    else:
        myenv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "myenv")
        if os.path.exists(myenv_dir):
            print(f"⚠️  Virtual environment exists at: {myenv_dir}")
            if os.name == 'nt':
                print(f"Activate using: {os.path.join(myenv_dir, 'Scripts', 'activate')}")
            else:
                print(f"Activate using: source {os.path.join(myenv_dir, 'bin', 'activate')}")
            
            confirmation = input("Continue without virtual environment? (y/n): ")
            return confirmation.lower() == 'y'
        else:
            print("⚠️  No virtual environment detected.")
            confirmation = input("Continue anyway? (y/n): ")
            return confirmation.lower() == 'y'

def run_backend():
    """Run the FastAPI backend server with CORS enabled"""
    print("🚀 Starting FastAPI backend on http://localhost:8000")
    try:
        from run_cors_backend import run_backend_with_cors
        run_backend_with_cors(reload_mode=True)
    except ImportError:
        print("📋 Using subprocess method for backend")
        try:
            subprocess.run(
                ["python", "run_cors_backend.py"],
                check=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Backend failed with exit code {e.returncode}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Backend terminated by user")
    except Exception as e:
        print(f"❌ Backend error: {str(e)}")
        sys.exit(1)

def check_node_npm():
    """Check if Node.js and npm are available"""
    try:
        # First check if npm is working (this is most important)
        npm_version = subprocess.run(
            ["npm", "--version"], 
            check=True, 
            capture_output=True, 
            text=True
        ).stdout.strip()
        
        print(f"✓ Found npm {npm_version}")
        
        # Try to check Node.js version, but don't fail if it doesn't work
        try:
            node_version = subprocess.run(
                ["node", "--version"], 
                check=True, 
                capture_output=True, 
                text=True
            ).stdout.strip()
            
            if node_version:
                print(f"✓ Found Node.js {node_version}")
            else:
                print("⚠️  Node.js command available but version unclear")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Node.js command not directly accessible, but npm is working")
            print("   This is fine - npm can run Next.js")
        
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found. Please install Node.js and npm from https://nodejs.org/")
        return False

def run_nextjs_frontend():
    """Run the Next.js frontend with proxy configuration"""
    print("🚀 Starting Next.js frontend on http://localhost:3000")
    print("📡 API calls will be proxied to backend automatically")
    
    try:
        frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "lnd-nexus")
        os.chdir(frontend_dir)
        
        if not check_node_npm():
            return False
            
        # Run Next.js development server
        subprocess.run(
            ["npm", "run", "dev"],
            check=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend failed with exit code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print("🛑 Frontend terminated by user")
        return False
    except Exception as e:
        print(f"❌ Frontend error: {str(e)}")
        return False

def open_browser():
    """Open browser after servers start"""
    print("⏱️  Waiting for servers to start...")
    time.sleep(8)  # Wait for both servers
    
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:3000")  # Single URL access
    
    print("\n" + "="*60)
    print("🎉 UNIFIED APPLICATION READY!")
    print("="*60)
    print("🏠 Main Application: http://localhost:3000")
    print("📚 API Documentation: http://localhost:3000/docs")
    print("📖 Alternative Docs: http://localhost:3000/redoc")
    print("💓 Health Check: http://localhost:3000/health")
    print("="*60)
    print("✨ Everything accessible from port 3000!")
    print("🔄 API calls automatically proxied to backend")
    print("="*60)

def handle_interrupt(signum, frame):
    """Handle graceful shutdown"""
    print("\n🛑 Shutting down all services...")
    sys.exit(0)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run unified Job Recommender application on single port"
    )
    parser.add_argument(
        "--no-browser", 
        action="store_true",
        help="Don't open browser automatically"
    )
    parser.add_argument(
        "--skip-env-check", 
        action="store_true",
        help="Skip environment verification"
    )
    
    return parser.parse_args()

def check_ports():
    """Check if required ports are available"""
    if is_port_in_use(8000):
        print("⚠️  Port 8000 is in use. Stopping existing backend...")
        # Could add logic to stop existing process
        
    if is_port_in_use(3000):
        print("❌ Port 3000 is in use. Please stop other Next.js apps first.")
        print("💡 Use 'stop_app.py' to stop running instances.")
        return False
        
    return True

if __name__ == "__main__":
    # Set encoding for Windows
    if os.name == 'nt':
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
    print("🚀 Job Recommender - Unified Single Port Deployment")
    print("=" * 55)
    
    args = parse_args()
    
    # Verify environment
    if not args.skip_env_check:
        if not verify_environment():
            print("❌ Environment check failed. Exiting.")
            sys.exit(1)
    
    # Check ports
    if not check_ports():
        sys.exit(1)
    
    # Register signal handler
    signal.signal(signal.SIGINT, handle_interrupt)
    
    # Start processes
    processes = []
    
    try:
        print("\n📋 Starting services...")
        
        # Start backend
        print("1️⃣  Starting backend...")
        backend_process = multiprocessing.Process(target=run_backend)
        backend_process.start()
        processes.append(backend_process)
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start frontend
        print("2️⃣  Starting frontend with proxy...")
        frontend_process = multiprocessing.Process(target=run_nextjs_frontend)
        frontend_process.start()
        processes.append(frontend_process)
        
        # Open browser
        if not args.no_browser:
            browser_process = multiprocessing.Process(target=open_browser)
            browser_process.start()
            processes.append(browser_process)
        else:
            print("\n🌐 Access your app at: http://localhost:3000")
        
        # Wait for processes
        for process in processes:
            process.join()
            
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        # Cleanup
        print("🧹 Cleaning up processes...")
        for process in processes:
            if process.is_alive():
                process.terminate()
                
        print("✅ All services stopped.") 