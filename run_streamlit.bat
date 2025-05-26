@echo off
echo Starting Job Recommender Streamlit Application...
echo.

REM Check if virtual environment exists
if not exist "myenv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run setup.py first to create the virtual environment.
    pause
    exit /b 1
)

REM Activate virtual environment
call myenv\Scripts\activate.bat

REM Check if backend is running
echo Checking if backend API is running...
python check_api_status.py >nul 2>&1
if errorlevel 1 (
    echo.
    echo Warning: Backend API is not running!
    echo Starting backend in a new window...
    start "Job Recommender Backend" cmd /c "call myenv\Scripts\activate.bat && python run_backend.py"
    echo Waiting 10 seconds for backend to start...
    timeout /t 10 /nobreak >nul
)

REM Start Streamlit application
echo.
echo Starting Streamlit application...
echo.
echo The application will open in your default web browser.
echo If it doesn't open automatically, go to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application.
echo.

streamlit run streamlit_app.py

echo.
echo Streamlit application stopped.
pause 