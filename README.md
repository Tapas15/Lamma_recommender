# Job Recommender System

A comprehensive job recommendation system with FastAPI backend and Streamlit frontend.

## Features

- Job and candidate recommendation engine using vector embeddings
- Skill gap analysis for candidates
- Career path recommendations
- Project recommendations
- Employer and candidate profiles
- Job and project posting and application management

## Project Structure

```
Latest_lamma/
├── backend/                  # FastAPI backend code
│   ├── app.py               # Main FastAPI application
│   ├── utils/               # Utility modules
│   │   ├── __init__.py      # Package initialization
│   │   ├── models.py        # Pydantic models
│   │   ├── extended_models.py # Extended Pydantic models
│   │   ├── database.py      # Database connection and operations
│   │   └── embedding.py     # Vector embedding functions
│   ├── init_db.py           # Database initialization script
│   └── maintenance.py       # Database maintenance utilities
├── pages/                    # Streamlit pages
│   ├── profile.py           # User profile page
│   ├── job_recommendations.py # Job recommendations page
│   └── ...                  # Other pages
├── streamlit_app.py          # Main Streamlit application
├── run_backend.py            # Script to run the backend
├── run_app.py               # Script to run both backend and frontend
├── run_app.bat              # Windows batch file to run the application
├── setup.py                 # Automated setup script
├── setup.bat                # Windows setup script
├── setup.sh                 # Unix setup script
├── RUN_INSTRUCTIONS.md      # Detailed run instructions
└── README.md                 # This file
```

## Setup

### Prerequisites

- Python 3.8+
- MongoDB
- Ollama (for local embeddings)

#### Installing Ollama

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

After installation, you can pull the required model:
```bash
ollama pull llama3.2
```

### Installation

#### Option 1: Automated Setup (Recommended)

Run the setup script which will automatically create a virtual environment, install dependencies, and set up the application:

On Windows:
```bash
setup.bat
```

On Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

Or directly with Python:
```bash
python setup.py
```

The setup script will:
- Create a Python virtual environment
- Install all required dependencies
- Set up environment variables
- Initialize the database
- Create platform-specific run scripts
- Provide an option to run the application immediately

#### Option 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Latest_lamma.git
cd Latest_lamma
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
pip install -r backend/requirements.txt
pip install streamlit
```

3. Set up environment variables:
```bash
# Create a .env file in the backend directory
echo "OLLAMA_API_BASE=http://localhost:11434" > backend/.env
echo "OLLAMA_MODEL=llama3.2" >> backend/.env
echo "SECRET_KEY=your_secret_key" >> backend/.env
echo "MONGODB_URL=mongodb://localhost:27017" >> backend/.env
echo "DATABASE_NAME=job_recommender" >> backend/.env
```

4. Initialize the database:
```bash
cd backend
python init_db.py
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

On Windows, you can also double-click the `run_app.bat` file.

### Option 2: Run Services Separately

If you prefer to run the services in separate terminals:

#### Backend

Run the FastAPI backend:
```bash
python run_backend.py
```

The API will be available at http://localhost:8000 and the API documentation at http://localhost:8000/docs

#### Frontend

Run the Streamlit frontend:
```bash
python -m streamlit run streamlit_app.py
```

The web application will be available at http://localhost:8501

For more detailed instructions, see the [RUN_INSTRUCTIONS.md](RUN_INSTRUCTIONS.md) file.

## Visual Demonstration

The application includes an automated visual demonstration that showcases the registration and login flow for both employers and candidates. This is useful for quickly understanding how the application works or for demonstration purposes.

To run the visual demo:

```bash
python tests/visual_demo.py
```

On Windows, you can also double-click the `run_visual_demo.bat` file.

The demo will:
1. Automatically start the backend and frontend services if needed
2. Open a Chrome browser and perform registration and login steps
3. Navigate through different sections of the application
4. Display the created test credentials at the end

For more options and details, see [tests/VISUAL_DEMO_README.md](tests/VISUAL_DEMO_README.md).

## Testing

### Comprehensive Test Suite

The application includes a comprehensive test suite that tests all API endpoints and user flows. To run the tests:

```bash
python tests/run_full_tests.py
```

### Test Logging

To see detailed information about the API requests being made during tests, use the `--show-requests` flag:

```bash
python tests/run_full_tests.py --show-requests
```

Or use the provided convenience scripts:

On Windows:
```bash
run_tests_with_logging.bat
```

On Linux/Mac:
```bash
./run_tests_with_logging.sh
```

This will display:
- Formatted JSON data being sent in each request
- HTTP method and URL for each API call
- Headers included in each request
- Complete request body

This feature is particularly useful for:
- Debugging API issues
- Understanding the data flow
- Verifying correct request formatting
- Learning how the API works

### Additional Test Options

The test runner supports several command-line options:

```bash
python tests/run_full_tests.py --help
```

Options include:
- `--api-url`: Specify a custom API URL
- `--streamlit-url`: Specify a custom Streamlit URL
- `--no-services`: Don't start or manage services (assumes they are already running)
- `--no-cleanup`: Don't stop services after tests complete
- `--wait-time`: Additional time to wait for services to fully initialize (seconds)
- `--show-requests`: Show detailed HTTP request information

## Troubleshooting

### "No module named 'utils'" Error

If you encounter the error "No module named 'utils'" when running the backend, it's likely a Python import path issue. Try the following solutions:

1. Make sure you have `__init__.py` files in both the `backend/` and `backend/utils/` directories.
2. Run the backend using the provided `run_backend.py` script at the root level.
3. If running with uvicorn directly, use the module format:
```bash
python -m uvicorn backend.app:app --reload
```

### MongoDB Connection Issues

If you're having trouble connecting to MongoDB:

1. Ensure MongoDB is running on your system:
```bash
# Check MongoDB status on Linux/Mac
sudo systemctl status mongodb

# On Windows, check if the MongoDB service is running
```

2. Verify your MongoDB connection string in the `.env` file.

3. Run the database initialization script:
```bash
python backend/init_db.py
```

### Embedding Generation Issues

If you're having issues with embedding generation:

1. Make sure Ollama is installed and running:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags
```

2. Verify that the Llama model is available in Ollama:
```bash
ollama list
```

3. If not, pull the model:
```bash
ollama pull llama3.2
```

## API Documentation

Once the backend is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 

# Job Recommender System Test Framework

A comprehensive testing framework for the Job Recommender System API and Streamlit frontend.

## Overview

This testing framework provides end-to-end automated testing for the Job Recommender System, covering:

- Employer and candidate registration and login flows
- Job and project creation
- Job applications and recommendations
- Service management (automatic start/stop)
- Diagnostic tools for debugging

## Project Structure

```
├── tests/                   # Main testing directory
│   ├── run_full_tests.py    # Main test runner
│   └── test_suite/          # Test suite components
│       ├── README.md        # Detailed documentation
│       ├── test_api.py      # API wrapper
│       ├── test_config.py   # Configuration and test data
│       ├── test_flow.py     # Test flows
│       └── test_services.py # Service management
├── diagnostics/             # Diagnostic tools (not included in Git)
└── api_collections/         # API collection files (not included in Git)
```

## Features

- **Automated Service Management**: Automatically detects, starts, and stops the backend and frontend services
- **Complete Test Flows**: Tests the entire application from registration to recommendations
- **Robust Error Handling**: Provides detailed error reporting and diagnostics
- **Flexible Configuration**: Supports command-line options for customization
- **Real-time Reporting**: Uses Rich library for beautiful console output

## Running Tests

Run the full test suite with default settings:

```bash
python tests/run_full_tests.py
```

### Command-line Options

```bash
python tests/run_full_tests.py --help
```

- `--api-url`: Custom API URL (default: http://localhost:8000)
- `--streamlit-url`: Custom Streamlit URL (default: http://localhost:8501)
- `--no-services`: Don't start or manage services
- `--no-cleanup`: Don't stop services after tests complete

## Notes and Workarounds

- Employer registration doesn't return an ID, so we use a fallback ID for job creation
- Complex candidate data can cause server errors, so simplified candidate data is used

## Contributing

Feel free to extend the test suite by adding more test cases to the test flows or creating specialized diagnostic tools for specific functionality. 