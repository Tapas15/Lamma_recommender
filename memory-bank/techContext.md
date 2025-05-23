# Technical Context

## Technology Stack
### Backend
- FastAPI (>= 0.95.0) - Main backend framework
- MongoDB (via motor >= 3.1.1) - Database
- Ollama - Local embedding model service
- Python-Jose - JWT authentication
- Passlib - Password hashing
- Pydantic (>= 2.0.0) - Data validation

### Frontend
- Streamlit (>= 1.45.0) - Web interface
- Plotly (>= 5.14.0) - Data visualization
- Pandas (>= 2.0.0) - Data manipulation

### Testing
- Pytest - Unit testing
- Selenium - E2E testing
- Webdriver-manager - Browser automation

## Development Environment
- Python 3.8+ required
- Virtual environment management
- Environment variables for configuration
- Platform-independent setup scripts

## Architecture
### Components
1. FastAPI Backend
   - RESTful API endpoints
   - Async database operations
   - JWT authentication
   - Vector embedding processing

2. Streamlit Frontend
   - Multiple pages architecture
   - Interactive UI components
   - Real-time data visualization

3. MongoDB Database
   - User profiles
   - Job listings
   - Application data
   - Vector embeddings storage

4. Ollama Service
   - Local embedding generation
   - Model: llama3.2

## Security
- JWT-based authentication
- Bcrypt password hashing
- Environment-based secrets
- Secure API endpoints

## Deployment
- Development: Local setup with automated scripts
- Services:
  - Backend: Port 8000
  - Frontend: Port 8501
  - MongoDB: Port 27017
  - Ollama: Port 11434

## Integration Points
- Frontend ↔ Backend API
- Backend ↔ MongoDB
- Backend ↔ Ollama
- Frontend ↔ Browser

## Performance Considerations
- Async database operations
- Local embedding generation
- Browser-based automation for testing

## Development Setup
### Prerequisites
- Python 3.8+
- MongoDB
- Ollama (for local embeddings)
- Web browser (Chrome recommended for testing)

### Installation Steps
1. Clone the repository
2. Run setup script (setup.bat, setup.sh, or setup.py)
3. Activate virtual environment
4. Run the application (run_app.py or run_app.bat)

## Dependencies
### Core Dependencies
- fastapi (>= 0.95.0) - Backend web framework
- uvicorn (>= 0.21.1) - ASGI server
- python-jose[cryptography] (>= 3.3.0) - JWT implementation
- passlib[bcrypt] (>= 1.7.4) - Password hashing
- motor (>= 3.1.1) - Async MongoDB driver
- pymongo (== 4.6.1) - MongoDB driver
- pydantic (>= 2.0.0) - Data validation
- streamlit (>= 1.45.0) - Frontend framework
- pandas (>= 2.0.0) - Data manipulation
- plotly (>= 5.14.0) - Data visualization

### Development Dependencies
- pytest (>= 7.3.1) - Testing framework
- pytest-asyncio (>= 0.21.0) - Async testing support
- selenium (>= 4.10.0) - Browser automation
- webdriver-manager (>= 3.8.6) - WebDriver management

## Technical Constraints
- MongoDB connection stability
- Embedding generation performance
- Memory usage optimization
- Cross-platform compatibility

## Environment Configuration
Environment variables are stored in a .env file in the backend directory:
- OLLAMA_API_BASE - URL for Ollama API (default: http://localhost:11434)
- OLLAMA_MODEL - Embedding model name (default: llama3.2)
- SECRET_KEY - JWT secret key
- MONGODB_URL - MongoDB connection string (default: mongodb://localhost:27017)
- DATABASE_NAME - MongoDB database name (default: job_recommender)

## Build Process
The project uses automated setup scripts that:
- Create a Python virtual environment
- Install all required dependencies
- Set up environment variables
- Initialize the database
- Create platform-specific run scripts

## Deployment Process
1. Run setup script to initialize environment
2. Start MongoDB service
3. Start Ollama service with required model
4. Run the application using provided scripts

## Monitoring and Logging
- Console logging for development
- Request logging for API calls
- Error tracking and reporting
- Performance monitoring 