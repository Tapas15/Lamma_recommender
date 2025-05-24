# Next.js Frontend Integration with FastAPI Backend

This document explains how to run the integrated Next.js frontend with the FastAPI backend for the Job Recommender application.

## Overview

The application consists of two main components:

1. **FastAPI Backend**: Provides the API endpoints for authentication, job recommendations, and other features.
2. **Next.js Frontend**: A modern React-based frontend that consumes the API endpoints.

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- MongoDB (running locally or accessible remotely)

## Setup Instructions

### 1. Install Backend Dependencies

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
# Navigate to the Next.js frontend directory
cd frontend/lnd-nexus

# Install dependencies
npm install
# or
yarn install
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory for the backend:

```
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=job_recommender
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

Create a `.env.local` file in the `frontend/lnd-nexus` directory:

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=L&D Nexus
```

## Running the Application

### Option 1: Development Mode

We provide a script that runs both the backend and frontend concurrently in development mode:

```bash
# On Windows
run_nextjs_app.bat

# On Linux/Mac
./run_nextjs_app.sh
# or
bash run_nextjs_app.sh
```

The frontend will be available at http://localhost:3005 (instead of the default 3000).

### Option 2: Production Mode

For production deployment, use the production scripts that build and serve the Next.js app:

```bash
# On Windows
run_nextjs_prod.bat

# On Linux/Mac
./run_nextjs_prod.sh
# or
bash run_nextjs_prod.sh
```

This will:
1. Build the Next.js frontend for production
2. Start the FastAPI backend in production mode
3. Start the Next.js frontend in production mode on port 3005

### Option 3: Running Components Separately

#### Start the Backend:

```bash
python run_backend.py
# or
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

#### Start the Next.js Frontend (Development):

```bash
cd frontend/lnd-nexus
npm run dev -- -p 3005
# or
yarn dev -p 3005
```

#### Start the Next.js Frontend (Production):

```bash
cd frontend/lnd-nexus
npm run build
npm run start:prod
# or
yarn build
yarn start:prod
```

## Accessing the Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Next.js Frontend**: http://localhost:3005

## API Integration

The Next.js frontend integrates with the backend API using the services defined in `frontend/lnd-nexus/app/services/api.ts`. This includes:

- Authentication (login, register, profile)
- Job listings and recommendations
- Skill gap analysis
- Career path recommendations
- Project management

## Authentication Flow

1. User logs in via the `/login` page
2. The frontend sends credentials to the backend's `/token` endpoint
3. Upon successful authentication, the backend returns a JWT token
4. The frontend stores this token in localStorage and uses it for subsequent API calls
5. The AuthContext provider manages the authentication state throughout the application

## Development Notes

- The Streamlit frontend (`streamlit_app.py`) is still available for testing purposes
- Both frontends (Streamlit and Next.js) can be used simultaneously with the same backend
- API endpoints are shared between both frontends
- The Next.js frontend runs on port 3005 to avoid conflicts with other applications

## Troubleshooting

### Node.js and npm Issues

If you see an error like `ERROR: npm is not installed or not in PATH`, you have two options:

#### Option 1: Install Node.js and npm globally
1. Install Node.js and npm from [https://nodejs.org/](https://nodejs.org/)
2. Make sure they are added to your PATH environment variable
3. Restart your terminal/command prompt after installation

You can verify your installation by running:
```bash
node --version
npm --version
```

#### Option 2: Use local Node.js and npm (recommended)
The application is configured to use local Node.js and npm installations if they exist in the frontend directory:

1. The scripts will automatically check for local npm and next executables in `frontend/lnd-nexus/node_modules/.bin`
2. If found, they will be used instead of global installations
3. This ensures compatibility and avoids version conflicts

If you're still having issues with Node.js detection:
1. Make sure the `frontend/lnd-nexus/node_modules/.bin` directory contains the npm and next executables
2. On Windows, look for `.cmd` files (e.g., `next.cmd`, `npm.cmd`)
3. Run the scripts with the `--skip-env-check` flag to bypass environment verification

### CORS Issues

If you encounter CORS errors when the Next.js frontend tries to access the backend API, ensure:

1. The backend is running with CORS middleware enabled (use `run_cors_backend.py` or `run_nextjs_app.py`)
2. The frontend is making requests to the correct backend URL (http://localhost:8000)
3. Your browser isn't blocking the requests

You can check the browser console (F12) for CORS-related errors.

### Port Conflicts

- If port 8000 is already in use, you can stop any running instances with `stop_app.py` or manually kill the process
- If port 3005 is already in use, you can specify a different port using the `--port` option or modify the scripts

### Other Issues

- For authentication issues, check that the JWT token is being properly stored and sent with requests
- If the Next.js app fails to start, verify that all dependencies are installed (`cd frontend/lnd-nexus && npm install`)
- If the backend fails to start with a reload error, try running it without reload mode or use the `run_cors_backend.py` script

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [MongoDB Documentation](https://docs.mongodb.com/) 