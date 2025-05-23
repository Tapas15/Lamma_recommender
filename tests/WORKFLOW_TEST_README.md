# Job Recommender - Complete Workflow Test

This directory contains a complete workflow test script that demonstrates end-to-end functionality for both employer and candidate users in the Job Recommender platform.

## What it demonstrates

The `complete_workflow_test.py` script automates the following complete workflows:

### Employer Workflow
1. **Registration** or login with existing credentials
2. **Job Posting** - Creating a new job listing with detailed information
3. **Project Posting** - Creating a new project opportunity
4. **Candidate Recommendations** - Viewing recommended candidates for jobs
5. **Profile Management** - Updating employer profile information
6. **Logout**

### Candidate Workflow
1. **Registration** or login with existing credentials
2. **Job Browsing** - Viewing available job listings
3. **Job Application** - Applying for a job with resume and cover letter
4. **Job Recommendations** - Viewing personalized job recommendations
5. **Project Browsing** - Exploring available projects
6. **Project Recommendations** - Viewing recommended projects
7. **Logout**

## Requirements

- Python 3.8+
- Chrome browser
- The script will automatically install required packages:
  - Selenium
  - webdriver-manager

## Running the Test

1. Make sure MongoDB is running (the script will attempt to start the application services)

2. Run the complete workflow test (both employer and candidate):
   ```
   python tests/complete_workflow_test.py
   ```
   
   Or use the batch file:
   ```
   run_complete_workflow.bat
   ```

3. To run only the employer workflow:
   ```
   python tests/complete_workflow_test.py --employer-only
   ```

4. To run only the candidate workflow:
   ```
   python tests/complete_workflow_test.py --candidate-only
   ```

5. To use existing accounts instead of registering new ones:
   ```
   python tests/complete_workflow_test.py --use-existing
   ```

6. To run the test quickly without delays:
   ```
   python tests/complete_workflow_test.py --no-slow
   ```

## Notes

- The script creates screenshots at crucial steps of the workflow
- Progress is logged in the console
- The script handles cleanup of any started processes
- Test accounts are randomly generated unless using the `--use-existing` flag

## Implementation Status

**Note**: This test is currently being implemented in phases. Currently, it provides the framework for the complete workflow, and individual functions are being added and refined as development progresses.

To implement your specific workflow test:

1. Fill in the `employer_complete_workflow()` function with your employer workflow steps
2. Fill in the `candidate_complete_workflow()` function with your candidate workflow steps
3. Update the helper functions as needed for your specific UI elements 