@echo off
cls
echo ================================================
echo  Starting Job Recommender Streamlit App
echo ================================================
echo.

echo Step 1: Checking backend status...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing | Out-Null; Write-Host '✅ Backend is already running' } catch { Write-Host '❌ Backend not running - starting now...' }"

echo.
echo Step 2: Starting backend if needed...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing | Out-Null } catch { Start-Process python -ArgumentList 'run_cors_backend.py' -WindowStyle Minimized; Write-Host 'Backend starting in background...'; Start-Sleep 8 }"

echo.
echo Step 3: Verifying backend health...
powershell -Command "for ($i=1; $i -le 5; $i++) { try { Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing | Out-Null; Write-Host '✅ Backend is healthy'; break } catch { Write-Host 'Waiting for backend... (' $i '/5)'; Start-Sleep 2 } }"

echo.
echo Step 4: Starting Streamlit app...
echo Opening Streamlit at: http://localhost:8501
echo.
echo ================================================
echo  Both services starting - Check browsers!
echo ================================================
echo  Backend API: http://localhost:8000/docs
echo  Streamlit App: http://localhost:8501
echo ================================================
echo.

REM Start Streamlit in the current window
streamlit run streamlit_app.py

pause 