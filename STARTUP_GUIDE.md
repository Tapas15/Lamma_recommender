# Job Recommender System - Startup Guide

This guide explains how to start the Job Recommender System services when they are not running.

## Quick Start

For the simplest way to start all services:

1. Double-click `start_services.bat` (Windows)
   - Or run `python start_services.py` from the command line

This will start both the backend and frontend services and provide links to access them.

## Starting Services Individually

### Using run_app.py

The `run_app.py` script provides options to start services individually:

- **Start both services:**
  ```
  python run_app.py
  ```

- **Start only the backend API:**
  ```
  python run_app.py --backend-only
  ```

- **Start only the frontend:**
  ```
  python run_app.py --frontend-only
  ```

- **Start without opening browser windows:**
  ```
  python run_app.py --no-browser
  ```

### Direct Method

You can also start each service directly:

- **Backend API:**
  ```
  python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
  ```

- **Frontend:**
  ```
  streamlit run streamlit_app.py
  ```

## Troubleshooting

If services won't start, common issues include:

1. **Port already in use**: 
   - Run `python diagnostics/service_check.py` to check if ports 8000 or 8501 are already in use
   - This tool will help identify the process IDs using those ports

2. **Service starts but not responding**:
   - Check for error messages in the console
   - Make sure all dependencies are installed with `pip install -r requirements.txt`

3. **Database connection issues**:
   - Ensure MongoDB is running and accessible
   - Check connection string in the `.env` file (if used)

## Access the Services

Once services are running:

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Stopping Services

To stop the services:
- Press Ctrl+C in the terminal where you started the services
- Or run `python diagnostics/service_check.py` to identify PIDs and stop them manually 