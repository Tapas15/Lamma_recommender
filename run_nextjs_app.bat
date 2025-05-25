@echo off
call myenv\Scripts\activate.bat
echo Starting Job Recommender Application with Next.js frontend...
python run_nextjs_app.py
pause
