@echo off
echo ================================================
echo  Job Recommender - Single Port Deployment  
echo ================================================
echo.
echo Starting unified application on port 3000...
echo Frontend and Backend accessible from same URL!
echo.

call myenv\Scripts\activate.bat
python run_unified_app.py

pause 