#!/bin/bash

echo "====================================================="
echo "    Perfect Visual Workflow for Job Recommender"
echo "====================================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in your PATH."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Create screenshots directory if it doesn't exist
mkdir -p workflow_screenshots

# Parse command line arguments
ARGS=""

for arg in "$@"; do
    if [[ "$arg" == "--employer-only" || "$arg" == "--candidate-only" || 
          "$arg" == "--no-slow" || "$arg" == "--use-existing" ]]; then
        ARGS="$ARGS $arg"
    fi
done

# Install required packages if needed
echo "Checking for required Python packages..."

if ! python3 -c "import selenium" &> /dev/null; then
    echo "Installing selenium..."
    pip3 install selenium || python3 -m pip install selenium
fi

if ! python3 -c "import webdriver_manager" &> /dev/null; then
    echo "Installing webdriver-manager..."
    pip3 install webdriver-manager || python3 -m pip install webdriver-manager
fi

echo
echo "Starting perfect visual workflow..."
echo

# Make the script executable if needed
chmod +x perfect_visual_workflow.py

# Run the script
python3 perfect_visual_workflow.py $ARGS

echo
echo "Workflow completed!" 