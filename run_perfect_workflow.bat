@echo off
echo =====================================================
echo    Perfect Visual Workflow for Job Recommender
echo =====================================================
echo.

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Create screenshots directory if it doesn't exist
if not exist workflow_screenshots mkdir workflow_screenshots

:: Check for command line arguments
set ARGS=

if "%1"=="--employer-only" set ARGS=%ARGS% --employer-only
if "%1"=="--candidate-only" set ARGS=%ARGS% --candidate-only
if "%1"=="--no-slow" set ARGS=%ARGS% --no-slow
if "%1"=="--use-existing" set ARGS=%ARGS% --use-existing

if "%2"=="--employer-only" set ARGS=%ARGS% --employer-only
if "%2"=="--candidate-only" set ARGS=%ARGS% --candidate-only
if "%2"=="--no-slow" set ARGS=%ARGS% --no-slow
if "%2"=="--use-existing" set ARGS=%ARGS% --use-existing

if "%3"=="--employer-only" set ARGS=%ARGS% --employer-only
if "%3"=="--candidate-only" set ARGS=%ARGS% --candidate-only
if "%3"=="--no-slow" set ARGS=%ARGS% --no-slow
if "%3"=="--use-existing" set ARGS=%ARGS% --use-existing

:: Install required packages if needed
echo Checking for required Python packages...
python -c "import selenium" >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing selenium...
    pip install selenium
)

python -c "import webdriver_manager" >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing webdriver-manager...
    pip install webdriver-manager
)

echo.
echo Starting perfect visual workflow...
echo.

:: Run the script
python perfect_visual_workflow.py %ARGS%

echo.
echo Workflow completed! Press any key to exit.
pause 