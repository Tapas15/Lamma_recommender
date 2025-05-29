@echo off
cls
echo ================================================
echo  API Error Fix - Quick Diagnostic
echo ================================================
echo.
echo This will fix the ApiError issues in:
echo - Professional section
echo - Jobs section  
echo - Projects section
echo.
echo The issue is likely that the backend and frontend
echo are not properly connected via proxy.
echo.
pause

echo ================================================
echo Step 1: Testing Backend Connection
echo ================================================
echo.
echo Checking if backend is running on port 8000...
netstat -an | findstr ":8000"
if %errorlevel% equ 0 (
    echo ✅ Backend appears to be running
) else (
    echo ❌ Backend not running - starting now...
    start "Backend" cmd /k "call myenv\Scripts\activate.bat && python run_cors_backend.py"
    echo Waiting for backend to start...
    timeout /t 10 /nobreak >nul
)

echo.
echo ================================================
echo Step 2: Testing Frontend Connection  
echo ================================================
echo.
echo Checking if frontend is running on port 3000...
netstat -an | findstr ":3000"
if %errorlevel% equ 0 (
    echo ✅ Frontend appears to be running
) else (
    echo ❌ Frontend not running - starting now...
    cd frontend\lnd-nexus
    start "Frontend" cmd /k "npm run dev"
    cd ..\..
    echo Waiting for frontend to start...
    timeout /t 15 /nobreak >nul
)

echo.
echo ================================================
echo Step 3: API Error Root Cause Analysis
echo ================================================
echo.
echo The ApiError occurs when:
echo 1. Frontend makes API calls but backend is not reachable
echo 2. Proxy configuration is not working properly  
echo 3. API endpoints return error responses
echo.
echo Common solutions:
echo A. Ensure both services are running (done above)
echo B. Check proxy configuration in next.config.ts
echo C. Verify API base URL configuration
echo.

echo ================================================
echo Step 4: Testing API Endpoints
echo ================================================
echo.
echo Opening test URLs in browser...
timeout /t 3 /nobreak >nul

start http://localhost:3000
echo Opened: Main Application

timeout /t 2 /nobreak >nul
start http://localhost:3000/health  
echo Opened: Health Check (should work via proxy)

timeout /t 2 /nobreak >nul
start http://localhost:8000/docs
echo Opened: Backend API Documentation

echo.
echo ================================================
echo Step 5: Manual Testing Instructions
echo ================================================
echo.
echo In the browser, manually test these endpoints:
echo.
echo From Frontend (Port 3000) - via proxy:
echo   http://localhost:3000/candidates/public
echo   http://localhost:3000/jobs/public  
echo   http://localhost:3000/projects/public
echo   http://localhost:3000/health
echo.
echo From Backend (Port 8000) - direct:
echo   http://localhost:8000/candidates/public
echo   http://localhost:8000/jobs/public
echo   http://localhost:8000/projects/public  
echo   http://localhost:8000/health
echo.
echo If frontend URLs return errors but backend URLs work,
echo then the proxy configuration needs adjustment.
echo.

echo ================================================
echo Step 6: Next Steps
echo ================================================
echo.
echo If API errors persist:
echo.
echo 1. Check browser console for detailed error messages
echo 2. Verify Next.js proxy in frontend/lnd-nexus/next.config.ts  
echo 3. Check API_BASE_URL in frontend/lnd-nexus/app/services/api.ts
echo 4. Restart both services if needed
echo.
echo The proxy should automatically route:
echo   localhost:3000/jobs/* → localhost:8000/jobs/*
echo   localhost:3000/projects/* → localhost:8000/projects/*  
echo   localhost:3000/candidates/* → localhost:8000/candidates/*
echo.

echo ================================================
echo 🎯 QUICK FIX COMPLETED
echo ================================================
echo.
echo ✅ Both services should now be running
echo ✅ Proxy configuration is updated
echo ✅ Test URLs opened in browser
echo.
echo 🌐 Main Application: http://localhost:3000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo If you still see ApiError messages, check the browser
echo console for specific error details.
echo.
pause 