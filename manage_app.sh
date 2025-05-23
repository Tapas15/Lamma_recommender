#!/bin/bash

# Change to script directory to ensure proper path resolution
cd "$(dirname "$0")"

echo "Job Recommender Application Manager"
echo "=================================="
echo ""
echo "1. Start full application (backend + frontend)"
echo "2. Start backend only"
echo "3. Start frontend only"
echo "4. Stop all running services"
echo "5. Exit"
echo ""

read -p "Enter your choice (1-5): " CHOICE

case $CHOICE in
    1)
        echo "Starting full application..."
        . myenv/bin/activate && python run_app.py
        ;;
    2)
        echo "Starting backend only..."
        . myenv/bin/activate && python run_app.py --backend-only
        ;;
    3)
        echo "Starting frontend only..."
        . myenv/bin/activate && python run_app.py --frontend-only
        ;;
    4)
        echo "Stopping all services..."
        . myenv/bin/activate && python stop_app.py
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice."
        ;;
esac

echo ""
echo "Press Enter to exit..."
read 