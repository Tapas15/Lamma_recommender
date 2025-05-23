# Job Recommender Platform - Testing System

This document provides an overview of the testing system for the Job Recommender platform, including both visual demonstrations and complete workflow tests.

## Available Test Scripts

### 1. Visual Demonstration (`tests/visual_demo.py`)

A visual demonstration script that shows the registration and login flow for both employers and candidates. This script is designed to visually present the user interface and interactions.

**Features:**
- Demonstrates candidate registration and login
- Demonstrates employer registration and login
- Shows dashboard exploration for both user types
- Includes visual enhancements (highlighting, scrolling)
- Creates screenshots at key points

**Run with:**
```bash
python tests/visual_demo.py
# or
./run_visual_demo.sh
# or
run_visual_demo.bat
```

**Options:**
```bash
python tests/visual_demo.py --no-slow  # Run quickly without delays
python tests/visual_demo.py --candidate-only  # Only run candidate demo
python tests/visual_demo.py --employer-only  # Only run employer demo
```

### 2. Complete Workflow Test (`tests/complete_workflow_test.py`)

A comprehensive end-to-end test that demonstrates complete user workflows for both employers and candidates, including all major platform functionality.

**Features:**
- Complete employer workflow:
  - Registration/Login
  - Job posting
  - Project posting
  - Viewing candidate recommendations
  - Profile management
- Complete candidate workflow:
  - Registration/Login
  - Job browsing and application
  - Project browsing
  - Viewing job/project recommendations
  - Profile management

**Run with:**
```bash
python tests/complete_workflow_test.py
# or
./run_complete_workflow.bat
```

**Options:**
```bash
python tests/complete_workflow_test.py --no-slow  # Run quickly without delays
python tests/complete_workflow_test.py --candidate-only  # Only run candidate workflow
python tests/complete_workflow_test.py --employer-only  # Only run employer workflow
python tests/complete_workflow_test.py --use-existing  # Use existing accounts instead of registering
```

## Implementation Details

### Test Data

The test scripts generate random test data for:
- User emails and passwords
- Profile information
- Job and project details
- Application content

This ensures tests can be run multiple times without conflicts.

### Screenshots

Both test scripts save screenshots at key points in the workflow:
- After successful registration
- After successful login
- On dashboard pages
- For job/project listings
- For recommendation lists

Screenshots are saved to the current working directory.

### Service Management

Both test scripts can automatically:
- Check if backend and frontend services are running
- Start services if needed
- Clean up processes on exit

## Requirements

- Python 3.8+
- Chrome browser
- MongoDB (for backend)
- Required Python packages (auto-installed if missing):
  - selenium
  - webdriver-manager

## Error Handling

The test scripts include robust error handling:
- Detailed error messages
- Screenshots on failure
- Alternative approaches for UI interactions
- Cleanup of resources even on failure

## For Developers

See the following detailed documentation:
- [VISUAL_DEMO_README.md](tests/VISUAL_DEMO_README.md) - Details on the visual demo
- [WORKFLOW_TEST_README.md](tests/WORKFLOW_TEST_README.md) - Details on the complete workflow test
- [WORKFLOW_IMPLEMENTATION_PLAN.md](tests/WORKFLOW_IMPLEMENTATION_PLAN.md) - Plan for implementing workflow functionality

To extend the test scripts:
1. Review the existing code and structure
2. Add new functions for additional test scenarios
3. Update the main workflow functions to include your new test cases
4. Follow the established patterns for error handling and UI interaction 