"""
Service management for the Job Recommender System test suite.
Handles starting and stopping the backend and frontend services.
"""
import os
import sys
import time
import signal
import subprocess
import psutil
import requests
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from rich.console import Console

# Add parent directory to path to find the test_suite module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Console for rich output
console = Console()

class ServiceManager:
    """Manages the backend and frontend services for testing"""
    
    def __init__(self, backend_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:8501"):
        """Initialize the service manager"""
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.processes = {
            "combined": None,  # For run_app.py which runs both services
            "backend": None,
            "frontend": None
        }
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        
        # Find the appropriate Python executable based on virtual environment
        self.python_executable = self._get_python_executable()
        console.print(f"[yellow]Using Python executable: {self.python_executable}[/yellow]")
    
    def ensure_services_running(self) -> bool:
        """Ensure that backend and frontend services are running"""
        console.print("[bold]Checking if services are running...[/bold]")
        
        # Check if both services already running
        backend_running = self._check_service(self.backend_url, "/docs")
        frontend_running = self._check_service(self.frontend_url)
        
        if backend_running and frontend_running:
            console.print("[green]Both backend and frontend are already running![/green]")
            return True
        
        # Try using run_app.py first (preferred way to start both services)
        if (not backend_running or not frontend_running):
            if self._start_combined_services():
                console.print("[green]Started both services successfully using run_app.py![/green]")
                return True
                
        # If combined approach failed, try starting them individually
        if not backend_running:
            console.print("[yellow]Backend is not running. Attempting to start...[/yellow]")
            if not self._start_backend():
                console.print("[bold red]Failed to start backend.[/bold red]")
                return False
            console.print("[green]Backend started successfully![/green]")
        
        if not frontend_running:
            console.print("[yellow]Frontend is not running. Attempting to start...[/yellow]")
            if not self._start_frontend():
                console.print("[bold red]Failed to start frontend.[/bold red]")
                return False
            console.print("[green]Frontend started successfully![/green]")
        
        return True
    
    def _start_combined_services(self) -> bool:
        """Start both backend and frontend using run_app.py"""
        try:
            run_app_path = os.path.join(self.root_dir, "run_app.py")
            if os.path.exists(run_app_path):
                console.print("[yellow]Found run_app.py. Starting both services...[/yellow]")
                
                # Start both services with no browser (we don't want browsers opening during tests)
                process = self._start_process([self.python_executable, run_app_path, "--no-browser"])
                
                if process:
                    self.processes["combined"] = process
                    
                    # Wait for both services to start
                    console.print("[yellow]Waiting for services to start...[/yellow]")
                    
                    # Check both services with timeout
                    backend_started = False
                    frontend_started = False
                    for i in range(40):  # Wait up to 20 seconds
                        if not backend_started:
                            backend_started = self._check_service(self.backend_url, "/docs")
                        
                        if not frontend_started:
                            frontend_started = self._check_service(self.frontend_url)
                        
                        # If both started, we're good
                        if backend_started and frontend_started:
                            console.print("[green]Both backend and frontend started successfully![/green]")
                            return True
                            
                        time.sleep(0.5)
                        if i % 4 == 0:  # Status update every 2 seconds
                            console.print(f"[yellow]Waiting for services... Backend: {'✅' if backend_started else '⏳'} Frontend: {'✅' if frontend_started else '⏳'} ({i // 2} seconds)[/yellow]")
                    
                    # If we're here, at least one service didn't start in time
                    if backend_started and not frontend_started:
                        console.print("[yellow]Backend started but frontend is taking longer...[/yellow]")
                        return True  # Frontend might still be starting, let's be optimistic
                    elif not backend_started:
                        console.print("[bold red]Backend failed to start with run_app.py[/bold red]")
                        return False
            
            return False
        except Exception as e:
            console.print(f"[bold red]Error starting services: {str(e)}[/bold red]")
            return False
    
    def stop_services(self) -> None:
        """Stop the services that were started by this manager"""
        if self.processes["combined"]:
            console.print("[yellow]Stopping combined services...[/yellow]")
            self._stop_process(self.processes["combined"])
            self.processes["combined"] = None
        
        if self.processes["backend"]:
            console.print("[yellow]Stopping backend...[/yellow]")
            self._stop_process(self.processes["backend"])
            self.processes["backend"] = None
        
        if self.processes["frontend"]:
            console.print("[yellow]Stopping frontend...[/yellow]")
            self._stop_process(self.processes["frontend"])
            self.processes["frontend"] = None
        
        console.print("[green]All services stopped.[/green]")
    
    def _check_service(self, url: str, path: str = "") -> bool:
        """Check if a service is running at the given URL"""
        try:
            response = requests.get(f"{url}{path}", timeout=2)
            return response.status_code < 400  # Any successful or redirect status code
        except:
            return False
    
    def _start_backend(self) -> bool:
        """Start the backend service"""
        try:
            console.print("[yellow]Looking for various ways to start the backend...[/yellow]")
            
            # Try using run_backend.py
            run_backend_path = os.path.join(self.root_dir, "run_backend.py")
            if os.path.exists(run_backend_path):
                console.print("[yellow]Found run_backend.py. Starting backend using this script...[/yellow]")
                process = self._start_process([self.python_executable, run_backend_path])
                if process:
                    self.processes["backend"] = process
                else:
                    console.print("[yellow]Failed to start using run_backend.py, trying alternate methods...[/yellow]")
            
            # If process is None or not started, try alternate methods
            if not self.processes["backend"]:
                # Try direct uvicorn command for backend.app:app
                console.print("[yellow]Trying direct uvicorn command...[/yellow]")
                process = self._start_process([
                    self.python_executable, "-m", "uvicorn", "backend.app:app", 
                    "--host", "0.0.0.0", "--port", "8000", "--reload"
                ])
                if process:
                    self.processes["backend"] = process
                else:
                    console.print("[yellow]Failed to start with direct uvicorn, trying more methods...[/yellow]")
            
            # If still not started after all attempts
            if not self.processes["backend"]:
                console.print("[bold red]Could not find any way to start the backend.[/bold red]")
                return False
            
            # Wait for backend to start
            console.print("[yellow]Waiting for backend to start...[/yellow]")
            for i in range(40):  # Wait up to 20 seconds
                if self._check_service(self.backend_url, "/docs"):
                    return True
                time.sleep(0.5)
                if i % 4 == 0:  # Every 2 seconds
                    console.print(f"[yellow]Still waiting for backend... ({i // 2} seconds)[/yellow]")
            
            console.print("[bold red]Backend started but not responding. It may need more time to initialize.[/bold red]")
            return False
        except Exception as e:
            console.print(f"[bold red]Error starting backend: {str(e)}[/bold red]")
            return False
    
    def _start_frontend(self) -> bool:
        """Start the frontend service"""
        try:
            console.print("[yellow]Looking for various ways to start the frontend...[/yellow]")
            
            # Look for streamlit_app.py - this is the main approach that should work
            streamlit_app_path = os.path.join(self.root_dir, "streamlit_app.py")
            if os.path.exists(streamlit_app_path):
                console.print("[yellow]Found streamlit_app.py. Starting streamlit frontend...[/yellow]")
                
                # Start the frontend with direct streamlit command
                process = self._start_process([
                    self.python_executable, "-m", "streamlit", "run", streamlit_app_path, "--server.port=8501"
                ])
                
                if process:
                    self.processes["frontend"] = process
                    # Wait for frontend to start
                    console.print("[yellow]Waiting for frontend to start...[/yellow]")
                    for i in range(40):  # Wait up to 20 seconds
                        if self._check_service(self.frontend_url):
                            return True
                        time.sleep(0.5)
                        if i % 4 == 0:  # Every 2 seconds
                            console.print(f"[yellow]Still waiting for frontend... ({i // 2} seconds)[/yellow]")
                    
                    console.print("[bold yellow]Frontend started but not responding. It may need more time to initialize.[/bold yellow]")
                    return True
            
            # If still not started after all attempts
            if not self.processes["frontend"]:
                console.print("[bold red]Could not find any way to start the frontend.[/bold red]")
                return False
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Error starting frontend: {str(e)}[/bold red]")
            return False
    
    def _get_python_executable(self) -> str:
        """Determine the correct Python executable to use"""
        # Check if we're in a virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            # We're in a virtual environment, use the current Python
            return sys.executable
        
        # Check for a myenv directory in the project root
        myenv_dir = os.path.join(self.root_dir, "myenv")
        if os.path.exists(myenv_dir):
            # Use the Python from myenv
            if os.name == 'nt':  # Windows
                return os.path.join(myenv_dir, "Scripts", "python.exe")
            else:  # Unix/Linux/Mac
                return os.path.join(myenv_dir, "bin", "python")
        
        # Fall back to the current Python
        return sys.executable
        
    def _start_process(self, command: List[str]) -> Optional[subprocess.Popen]:
        """Start a process with the given command"""
        try:
            # On Windows, we need to pass encoding to handle non-ASCII output
            kwargs = {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "text": True,
                "encoding": "utf-8",
                "errors": "ignore"
            }
            
            # Use creationflags on Windows to avoid opening console windows
            if os.name == 'nt':  # Windows
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                kwargs["start_new_session"] = True
            
            console.print(f"[yellow]Starting process: {' '.join(command)}[/yellow]")
            process = subprocess.Popen(command, **kwargs)
            
            # Give the process a moment to start and check if it crashed immediately
            time.sleep(1)
            if process.poll() is not None:  # Process has terminated
                returncode = process.poll()
                stdout, stderr = process.communicate()
                console.print(f"[bold red]Process exited immediately with code {returncode}[/bold red]")
                if stdout:
                    console.print(f"[red]stdout: {stdout}[/red]")
                if stderr:
                    console.print(f"[red]stderr: {stderr}[/red]")
                return None
                
            return process
        except Exception as e:
            console.print(f"[bold red]Error starting process: {str(e)}[/bold red]")
            return None
    
    def _stop_process(self, process: subprocess.Popen) -> None:
        """Stop a process and all its children"""
        try:
            if os.name == 'nt':  # Windows
                # On Windows, we need to kill the process differently
                process.terminate()
                try:
                    process.wait(timeout=5)  # Wait up to 5 seconds for termination
                except subprocess.TimeoutExpired:
                    process.kill()  # Force kill if it doesn't terminate
                
                # Try to find and kill child processes
                try:
                    parent = psutil.Process(process.pid)
                    for child in parent.children(recursive=True):
                        child.terminate()
                    gone, still_alive = psutil.wait_procs(parent.children(), timeout=5)
                    for p in still_alive:
                        p.kill()
                except psutil.NoSuchProcess:
                    pass  # Process already gone
            else:
                # On Unix, send SIGTERM to process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except Exception as e:
            console.print(f"[yellow]Error while stopping process: {str(e)}[/yellow]") 