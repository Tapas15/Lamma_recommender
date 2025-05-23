# Job Recommender - Visual Workflow Test

This directory contains a visual workflow test script that demonstrates the complete end-to-end workflow for both employer and candidate users in the Job Recommender platform, with visual highlighting of each step.

## What it demonstrates

The `visual_workflow_test.py` script automates the following complete workflows with visual enhancements:

### Employer Workflow
1. **Registration** - Filling out the employer registration form with company details
2. **Login** - Logging in with the created credentials
3. **Job Posting** - Creating a new job listing with detailed information
4. **Project Posting** - Creating a new project opportunity
5. **Candidate Listing** - Viewing available candidates
6. **Candidate Recommendations** - Viewing recommended candidates for jobs

### Candidate Workflow
1. **Registration** - Filling out the candidate registration form with skills and experience
2. **Login** - Logging in with the created credentials
3. **Job Browsing** - Viewing available job listings
4. **Job Application** - Applying for a job with details
5. **Job Recommendations** - Viewing personalized job recommendations
6. **Project Browsing** - Exploring available projects
7. **Project Recommendations** - Viewing recommended projects

## Visual Features

The test includes the following visual enhancements:
- **Element Highlighting** - Each interactive element is highlighted in yellow with a red border
- **Smooth Scrolling** - The page automatically scrolls to each element before interaction
- **Screenshots** - Captures screenshots at each significant step of the workflow
- **Informative Output** - Provides detailed console output with emoji indicators

## Requirements

- Python 3.8+
- Chrome browser
- MongoDB (for backend)
- The script will automatically install required packages:
  - selenium
  - webdriver-manager

## Running the Test

1. Make sure MongoDB is running (the script will attempt to start the application services)

2. Run the complete workflow test:
   ```
   python tests/visual_workflow_test.py
   ```
   
   Or use the batch/shell scripts:
   ```
   run_visual_workflow.bat  # Windows
   ./run_visual_workflow.sh  # Linux/Mac
   ```

3. To run only the employer workflow:
   ```
   python tests/visual_workflow_test.py --employer-only
   ```

4. To run only the candidate workflow:
   ```
   python tests/visual_workflow_test.py --candidate-only
   ```

5. To use existing accounts instead of registering new ones:
   ```
   python tests/visual_workflow_test.py --use-existing
   ```

6. To run the test quickly without delays:
   ```
   python tests/visual_workflow_test.py --no-slow
   ```

7. To specify a custom screenshots directory:
   ```
   python tests/visual_workflow_test.py --screenshots-dir my_screenshots
   ```

## Screenshots

All screenshots are saved to the `screenshots` directory (or the directory specified with `--screenshots-dir`). Screenshots are named with a prefix indicating the workflow step and a timestamp.

Example screenshot names:
- `employer_registration_start_20230823_123456.png`
- `candidate_job_recommendations_20230823_124510.png`

## Error Handling

The script includes robust error handling:
- Screenshots are taken on errors to help with debugging
- Alternative selectors are tried when elements aren't found
- Detailed error messages are provided in the console
- The test continues as much as possible even if individual steps fail

## Implementation Details

The visual workflow test is organized into the following files:
- `tests/visual_workflow_test.py` - Main test script
- `tests/workflow_functions/employer.py` - Employer-specific workflow functions
- `tests/workflow_functions/candidate.py` - Candidate-specific workflow functions

Each function follows a consistent pattern:
1. Find and highlight the required UI elements
2. Interact with the elements (click, type, etc.)
3. Take screenshots at key points
4. Verify the expected outcome
5. Handle errors gracefully 