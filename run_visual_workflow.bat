@echo off
echo Starting Job Recommender Visual Workflow Test...
mkdir screenshots 2>nul
python tests/visual_workflow_test.py %*
pause 