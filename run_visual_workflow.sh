#!/bin/bash
echo "Starting Job Recommender Visual Workflow Test..."
mkdir -p screenshots
python tests/visual_workflow_test.py "$@" 