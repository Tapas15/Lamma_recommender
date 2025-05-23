@echo off
SETLOCAL

:: Set encoding to UTF-8 to avoid encoding issues
chcp 65001 > nul

echo Job Recommender Application Manager
echo ==================================
echo.
echo 1. Start full application (backend + frontend)
echo 2. Start backend only
echo 3. Start frontend only
echo 4. Stop all running services
echo 5. Exit
echo.

:MENU
SET /P CHOICE="Enter your choice (1-5): "

IF "%CHOICE%"=="1" (
    echo Starting full application...
    myenv\Scripts\python run_app.py
    goto END
)

IF "%CHOICE%"=="2" (
    echo Starting backend only...
    myenv\Scripts\python run_app.py --backend-only
    goto END
)

IF "%CHOICE%"=="3" (
    echo Starting frontend only...
    myenv\Scripts\python run_app.py --frontend-only
    goto END
)

IF "%CHOICE%"=="4" (
    echo Stopping all services...
    myenv\Scripts\python stop_app.py
    goto END
)

IF "%CHOICE%"=="5" (
    echo Exiting...
    goto END
)

echo Invalid choice. Please try again.
goto MENU

:END
pause 