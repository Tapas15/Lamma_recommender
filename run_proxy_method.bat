@echo off
cls
echo ================================================
echo  Job Recommender - Proxy Method Setup
echo ================================================
echo.
echo This implements the Create React App proxy pattern:
echo Reference: https://create-react-app.dev/docs/proxying-api-requests-in-development/
echo.
echo Available proxy methods:
echo 1. Next.js built-in rewrites (Enhanced - Default)
echo 2. Next.js middleware proxy
echo 3. Standalone Express proxy server
echo.
set /p choice="Choose method (1-3) or press Enter for default: "

if "%choice%"=="2" goto middleware
if "%choice%"=="3" goto standalone
goto nextjs

:nextjs
echo ================================================
echo Using Next.js Enhanced Rewrites (Default Method)
echo ================================================
echo.
echo ✅ Features:
echo - Environment variable support (BACKEND_URL)
echo - Enhanced CORS handling
echo - Automatic API request proxying
echo - Based on Create React App proxy pattern
echo.

REM Start backend
echo Starting FastAPI backend...
start "Backend-FastAPI" cmd /k "call myenv\Scripts\activate.bat && python run_cors_backend.py"

REM Wait for backend
timeout /t 5 /nobreak >nul

REM Start Next.js with enhanced proxy
echo Starting Next.js with enhanced proxy configuration...
cd frontend\lnd-nexus
start "Frontend-NextJS-Proxy" cmd /k "npm run dev"

goto finish

:middleware
echo ================================================
echo Using Next.js Middleware Proxy Method
echo ================================================
echo.
echo ✅ Features:
echo - Advanced request interception
echo - Custom header handling
echo - OPTIONS request support
echo - Runtime proxy configuration
echo.

REM Start backend
echo Starting FastAPI backend...
start "Backend-FastAPI" cmd /k "call myenv\Scripts\activate.bat && python run_cors_backend.py"

REM Wait for backend
timeout /t 5 /nobreak >nul

REM Start Next.js
echo Starting Next.js with middleware proxy...
cd frontend\lnd-nexus
start "Frontend-NextJS-Middleware" cmd /k "npm run dev"

goto finish

:standalone
echo ================================================
echo Using Standalone Express Proxy Server
echo ================================================
echo.
echo ✅ Features:
echo - Full control over proxy behavior
echo - Express.js based (like Create React App)
echo - Request/response logging
echo - Error handling
echo.

REM Check if proxy dependencies exist
if not exist node_modules\express (
  echo Installing proxy server dependencies...
  copy proxy-package.json package.json >nul
  npm install
)

REM Start backend
echo Starting FastAPI backend...
start "Backend-FastAPI" cmd /k "call myenv\Scripts\activate.bat && python run_cors_backend.py"

REM Wait for backend
timeout /t 5 /nobreak >nul

REM Start proxy server
echo Starting Express proxy server...
start "Proxy-Server" cmd /k "node setup_proxy_server.js"

goto finish

:finish
REM Wait for services to start
timeout /t 8 /nobreak >nul

echo.
echo ================================================
echo      🎉 PROXY METHOD DEPLOYMENT READY! 🎉
echo ================================================
echo.
echo 🌐 Unified Access Point: http://localhost:3000
echo.
echo 📚 Available Endpoints (all from port 3000):
echo    http://localhost:3000/           (Frontend App)
echo    http://localhost:3000/docs       (API Documentation)
echo    http://localhost:3000/redoc      (Alternative Docs)
echo    http://localhost:3000/health     (Health Check)
echo    http://localhost:3000/api/*      (All API endpoints)
echo.
echo ✨ Benefits of Proxy Method:
echo    - Single port access (no CORS issues)
echo    - Seamless API integration
echo    - Production-like setup in development
echo    - Environment variable support
echo.
echo 🔗 Reference: https://create-react-app.dev/docs/proxying-api-requests-in-development/
echo ================================================

REM Open browser
start http://localhost:3000

echo.
echo Press any key to close this window...
echo (Services will continue running in their own windows)
pause >nul 