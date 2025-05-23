# Job Recommender - Visual Demo

This directory contains an automated visual demonstration script that shows the flow of registration and login for both employers and candidates using the Job Recommender platform.

## What it demonstrates

The `visual_demo.py` script automates the following processes through a web browser:

1. **Candidate Registration**: Fills out and submits the candidate registration form
2. **Candidate Login**: Logs in with the newly created candidate account
3. **Candidate Dashboard Exploration**: Navigates through job listings and recommendations
4. **Employer Registration**: Fills out and submits the employer registration form
5. **Employer Login**: Logs in with the newly created employer account
6. **Employer Dashboard Exploration**: Navigates through job posting and candidate search

## Requirements

- Python 3.8+
- Chrome browser
- The script will automatically install required packages:
  - Selenium
  - webdriver-manager

## Running the Demo

1. Make sure MongoDB is running (the script will attempt to start the application services)

2. Run the complete demo (both candidate and employer flows):
   ```
   python tests/visual_demo.py
   ```

3. To run only the candidate flow:
   ```
   python tests/visual_demo.py --candidate-only
   ```

4. To run only the employer flow:
   ```
   python tests/visual_demo.py --employer-only
   ```

5. To run the demo quickly without delays (less visual but faster):
   ```
   python tests/visual_demo.py --no-slow
   ```

## What happens during the demo

- The script will automatically start the frontend and backend services if they're not already running
- It will open a Chrome browser and perform the registration and login steps
- The browser interactions are slowed down to make the process visible
- At the end, it will display the credentials created during the demo
- The browser will close automatically after the demo completes

## Troubleshooting

If you encounter issues:

1. **Browser doesn't open**: Make sure Chrome is installed and accessible
2. **Services don't start**: Make sure MongoDB is running and ports 8000 and 8501 are available
3. **Registration fails**: There might be validation issues in the form - check console output
4. **Navigation fails**: The UI structure might have changed - the script may need updating

## Notes

- The script creates random test accounts each time it runs
- These accounts are not automatically deleted, but can be removed from MongoDB manually
- The script handles cleanup of started processes when it exits 