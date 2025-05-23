@echo off
call myenv\Scripts\activate.bat
echo Starting Job Recommender API backend...
python run_backend.py
pause
