@echo off
echo ====================================================
echo  L&D Nexus - Installation and Setup
echo ====================================================
echo.

echo Setting up backend...
cd backend
pip install -r requirements.txt
echo Backend dependencies installed!
echo.

echo Setting up frontend...
cd ..\frontend\lnd-nexus
npm install
echo Frontend dependencies installed!
echo.

echo Creating necessary directories...
mkdir ..\..\backend\utils\translations 2>nul
mkdir ..\public\images\en 2>nul
mkdir ..\public\images\ar 2>nul
echo Directories created!
echo.

echo Copying default files...
copy ..\public\logo.png ..\public\images\en\logo.png 2>nul
copy ..\public\logo.png ..\public\images\ar\logo.png 2>nul
echo Default files copied!
echo.

echo Setup complete!
echo.
echo To start the application:
echo - Backend: cd backend && python main.py
echo - Frontend: cd frontend\lnd-nexus && npm run dev
echo.
echo Thank you for using L&D Nexus!
echo ==================================================== 