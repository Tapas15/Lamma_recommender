# Job Recommender Application - Run Instructions

This document provides instructions for running the Job Recommender application, which consists of a FastAPI backend and a Streamlit frontend.

## Prerequisites

Before running the application, ensure you have the following installed:

1. Python 3.8+ with pip
2. MongoDB (running locally or accessible via connection string)
3. Ollama (for local embeddings)
4. Required Python packages:
   ```
   pip install -r backend/requirements.txt
   pip install streamlit
   ```

### Installing Ollama

The setup script will attempt to install Ollama automatically, but you can also install it manually:

**Windows:**
- Download and install from [ollama.com/download/windows](https://ollama.com/download/windows)
- After installation, start Ollama from the Start Menu

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
- Download and install from [ollama.com/download/mac](https://ollama.com/download/mac)

After installation, you need to pull the required model:
```bash
ollama pull llama3.2
```

## Running the Application

### Option 1: Run Both Services Together (Recommended)

The easiest way to run the complete application is to use the provided `run_app.py` script:

```bash
python run_app.py
```

This script will:
- Start the FastAPI backend on http://localhost:8000
- Start the Streamlit frontend on http://localhost:8501
- Open browser tabs for both services automatically

To stop the application, press `Ctrl+C` in the terminal.

### Option 2: Run Services Separately

If you prefer to run the services in separate terminals:

1. Start the backend:
   ```bash
   python run_backend.py
   ```

2. Start the frontend (in a separate terminal):
   ```bash
   streamlit run streamlit_app.py
   ```

## Accessing the Application

- **Backend API**: http://localhost:8000
  - API Documentation: http://localhost:8000/docs
  - Alternative API Documentation: http://localhost:8000/redoc

- **Frontend Application**: http://localhost:8501

## Troubleshooting

If you encounter any issues:

1. Make sure MongoDB is running and accessible
2. Check that all required packages are installed
3. Verify that ports 8000 and 8501 are not being used by other applications
4. Check the terminal output for any error messages

## Environment Variables

The application uses the following environment variables (which can be set in a `.env` file):

- `MONGODB_URL`: MongoDB connection string (default: mongodb://localhost:27017)
- `DATABASE_NAME`: MongoDB database name (default: job_recommender_db)
- `SECRET_KEY`: Secret key for JWT token generation
- `OLLAMA_API_BASE`: Base URL for Ollama API (default: http://localhost:11434)
- `OLLAMA_MODEL`: Ollama model to use (default: llama3.2) 