@echo off
cd frontend\lnd-nexus
echo Building Next.js frontend for production...
npm run build
echo Starting Next.js frontend production server...
npm start
pause
