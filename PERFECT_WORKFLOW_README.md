# Perfect Visual Workflow for Job Recommender

This project provides an enhanced, robust version of the visual workflow demonstration for the Job Recommender platform. It ensures the demo runs perfectly every time with better error handling, visual enhancements, and comprehensive diagnostics.

## Key Features

- **Enhanced Error Handling**: More robust exception handling and recovery mechanisms
- **Visual Improvements**: Smooth scrolling, pulsating highlights, and better element focusing
- **System Diagnostics**: Detailed system information and service status checking
- **Automatic Screenshots**: Timestamped screenshots saved for every significant step
- **Credential Management**: Save and reuse test credentials between runs
- **Progress Tracking**: Clear, step-by-step progress indicators with emoji visual cues
- **Cross-Platform Support**: Windows batch file and Linux/Mac shell script included

## Quick Start

### On Windows

1. Open Command Prompt or PowerShell
2. Navigate to your project directory
3. Run the batch file:
   ```
   run_perfect_workflow.bat
   ```

### On Linux/Mac

1. Open Terminal
2. Navigate to your project directory
3. Make the script executable (first time only):
   ```
   chmod +x run_perfect_workflow.sh
   ```
4. Run the shell script:
   ```
   ./run_perfect_workflow.sh
   ```

## Command Line Options

The following options are available for both scripts:

- `--employer-only`: Run only the employer workflow (skip candidate)
- `--candidate-only`: Run only the candidate workflow (skip employer)
- `--no-slow`: Disable slow mode to run the workflow quickly
- `--use-existing`: Use existing accounts from previous runs (if available)

Examples:

```
# Run only the employer workflow with fast speed
run_perfect_workflow.bat --employer-only --no-slow

# Run only the candidate workflow using existing accounts
./run_perfect_workflow.sh --candidate-only --use-existing
```

## Understanding the Output

The scripts produce detailed terminal output with the following indicators:

- 🚀 = Section header
- 🔷 = Step indicator
- ✅ = Success message
- ⚠️ = Warning message
- ❌ = Error message
- 📸 = Screenshot saved

## Screenshots

All screenshots are saved in the `workflow_screenshots` directory with timestamped filenames like:
- `employer_registration_complete_20230824_123456.png`
- `candidate_dashboard_explored_20230824_124530.png`

## Project Structure

- `perfect_visual_workflow.py` - Main workflow script with enhanced error handling
- `run_perfect_workflow.bat` - Windows batch file for easy execution
- `run_perfect_workflow.sh` - Linux/Mac shell script for easy execution 
- `tests/enhanced_selenium.py` - Advanced Selenium helper functions
- `tests/visual_demo.py` - Original visual demo script (used as a base)
- `workflow_credentials.json` - Generated file storing test credentials

## Troubleshooting

### Services Not Running

If you see errors about services not running:

1. Check that MongoDB is running
2. Start the backend manually: `python run_backend.py`
3. Start the frontend manually: `python -m streamlit run streamlit_app.py`
4. Run the workflow again with: `run_perfect_workflow.bat --use-existing`

### Browser Issues

If the browser fails to initialize:

1. Make sure Chrome is installed
2. Update Chrome to the latest version
3. Try updating webdriver-manager: `pip install --upgrade webdriver-manager`

### Element Not Found Errors

If you see many "Element not found" warnings:

1. The UI structure may have changed
2. Try running the workflow with `--no-slow` to reduce timing issues
3. Check if the frontend application has been modified recently

## Advanced Features

The enhanced workflow includes several advanced features:

1. **Multi-browser support**: Can be extended to support Firefox and Edge
2. **Element highlighting styles**: Background, outline, or border highlighting
3. **Pulsating effect**: Makes important elements more noticeable
4. **Human-like typing**: Simulates realistic typing patterns
5. **Multiple locator strategies**: Tries multiple ways to find elements
6. **Smooth scrolling**: Provides more visually pleasing navigation
7. **System diagnostics**: Checks environment before running tests

## Extending the Workflow

To add new steps to the workflow:

1. Add functions to `perfect_visual_workflow.py`
2. Use the `enhanced_selenium.py` helpers for reliable element interaction
3. Follow the established pattern for error handling and screenshots 