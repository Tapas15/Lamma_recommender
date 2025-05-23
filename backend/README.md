# Job Recommender Backend

This directory contains the backend implementation for the Job Recommender system, an AI-powered job matching platform that connects candidates and employers.

## Structure

- `app.py`: Main FastAPI application with all route handlers
- `utils/`: Utility modules for the application
  - `database.py`: MongoDB database connection and configuration
  - `models.py`: Pydantic models for data validation
  - `extended_models.py`: Enhanced versions of models with more detailed fields
  - `embedding.py`: Utilities for creating vector embeddings using Ollama
- `init_db.py`: Script to initialize the database collections and indexes
- `maintenance.py`: Script to check and maintain database collections
- `test_db_init.py`: Test script for database initialization

## Database Configuration

The system uses MongoDB for data storage. All collections are automatically initialized when the application starts.

### Collections
- `users`: User authentication and basic information
- `candidates`: Detailed candidate profiles and skills
- `employers`: Company profiles and hiring preferences
- `jobs`: Job listings with requirements and descriptions
- `projects`: Project opportunities posted by employers
- `job_applications`: Applications submitted by candidates for jobs
- `project_applications`: Applications submitted by candidates for projects
- `saved_jobs`: Jobs bookmarked by candidates
- `saved_projects`: Projects bookmarked by candidates
- `recommendations`: System-generated job and candidate matches
- `feedback`: User feedback on job matches and platform features
- `notifications`: User notifications for application updates, matches, etc.
- `vector_indexes`: Metadata for vector search indexes

Each collection is indexed appropriately for performance optimization.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install and run Ollama:
   - Follow instructions at [Ollama's website](https://ollama.com/) to install
   - Pull the Llama 3.2 model: `ollama pull llama3.2`
   - Ensure Ollama is running locally

3. Set up environment variables (create a `.env` file with):
   ```
   MONGODB_URL=your_mongodb_connection_string
   OLLAMA_API_BASE=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   SECRET_KEY=your_jwt_secret_key
   ```

4. Initialize the database (optional - also happens when app starts):
   ```
   python init_db.py
   ```

5. Run the application:
   ```
   python -m uvicorn app:app --reload
   ```

## Database Maintenance

The system includes scripts to help maintain the database:

1. `init_db.py` - Creates collections and indexes:
   ```
   python init_db.py
   ```

2. `maintenance.py` - Checks for missing collections and documents without embeddings:
   ```
   python maintenance.py
   ```

## Features

- User authentication (JWT tokens)
- Registration for candidates and employers with detailed profiles
- Job posting and management
- Project creation and management
- Vector search for semantic matching using Llama 3.2 embeddings via Ollama
- Job applications and tracking
- Recommendation system for jobs/candidates based on vector similarity
- Semantic search across jobs, projects, and candidates

## API Documentation

When running the application, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 