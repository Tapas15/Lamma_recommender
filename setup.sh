#!/bin/bash
echo "===================================================="
echo " L&D Nexus - Installation and Setup"
echo "===================================================="
echo

echo "Setting up backend..."
cd backend
pip install -r requirements.txt
echo "Backend dependencies installed!"
echo

echo "Setting up frontend..."
cd ../frontend/lnd-nexus
npm install
echo "Frontend dependencies installed!"
echo

echo "Creating necessary directories..."
mkdir -p ../../backend/utils/translations
mkdir -p ../public/images/en
mkdir -p ../public/images/ar
echo "Directories created!"
echo

echo "Copying default files..."
cp ../public/logo.png ../public/images/en/logo.png 2>/dev/null
cp ../public/logo.png ../public/images/ar/logo.png 2>/dev/null
echo "Default files copied!"
echo

echo "Setup complete!"
echo
echo "To start the application:"
echo "- Backend: cd backend && python main.py"
echo "- Frontend: cd frontend/lnd-nexus && npm run dev"
echo
echo "Thank you for using L&D Nexus!"
echo "====================================================" 