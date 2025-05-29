@echo off
cls
echo ================================================
echo  Job Recommender - Single Port Setup Guide
echo ================================================
echo.
echo This will start both services for single-port access:
echo 1. Backend (FastAPI) on port 8000
echo 2. Frontend (Next.js) on port 3000 with proxy to backend
echo.
echo Final Access: http://localhost:3000 (everything accessible from here)
echo.
pause

REM Start backend in background
echo ================================================
echo Starting Backend (FastAPI)...
echo ================================================
start "Backend-FastAPI" cmd /k "call myenv\Scripts\activate.bat && python run_cors_backend.py"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend
echo ================================================
echo Starting Frontend (Next.js)...
echo ================================================
echo Navigate to frontend directory and start Next.js...
cd frontend\lnd-nexus
start "Frontend-NextJS" cmd /k "npm run dev"

REM Wait for services to start
timeout /t 8 /nobreak >nul

echo.
echo ================================================
echo      🎉 SERVICES STARTED! 🎉
echo ================================================
echo.
echo 🌐 Access your unified application at:
echo    http://localhost:3000
echo.
echo 📚 All these work from the same URL:
echo    http://localhost:3000/docs        (API Documentation)
echo    http://localhost:3000/redoc       (Alternative Docs)
echo    http://localhost:3000/health      (Health Check)
echo    http://localhost:3000/api/*       (All API endpoints)
echo.
echo ✨ Everything accessible from port 3000!
echo 🔄 API calls automatically proxied to backend
echo.
echo ================================================

REM Open browser
start http://localhost:3000

echo.
echo Press any key to close this window...
echo (The services will continue running in their own windows)
pause >nul 