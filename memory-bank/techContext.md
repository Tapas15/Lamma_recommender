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
- Tabulate - Formatted test output
- Requests - API testing
- NumPy - Data analysis in tests

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
   - Recommendation feedback collection
   - Skill clustering analysis

2. Streamlit Frontend
   - Multiple pages architecture
   - Interactive UI components
   - Real-time data visualization

3. MongoDB Database
   - User profiles
   - Job listings
   - Application data
   - Vector embeddings storage
   - Vector search indexes

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
- Feedback System ↔ Recommendation Engine
- Skill Clusters ↔ Career Path Planning

## Performance Considerations
- Async database operations
- Local embedding generation
- Browser-based automation for testing
- Vector search optimization
- Confidence thresholds for skill clustering
- Parameterized endpoint responses

## Testing Infrastructure
### Test Directory Structure
```
backend/tests/
├── README.md                    # Testing documentation
├── test_search_recommender.py   # Comprehensive search and recommendation tests
├── test_recommendation_system.py # Focused recommendation system tests
└── check_all_embeddings.py      # Vector embedding verification tool
```

### Test Types
- **Search & Recommendation Tests**: Verify semantic search and recommendation functionality
- **Embedding Verification**: Check vector embeddings across all collections
- **API Tests**: Verify API endpoint functionality
- **Integration Tests**: Test system component interactions
- **Unit Tests**: Test individual functions and modules
- **Feedback System Tests**: Verify feedback collection and analysis
- **Skill Clusters Tests**: Verify skill relationship analysis and clustering

### Test Environment
- Environment variables for test configuration
- Test user accounts for authentication
- MongoDB test collections
- Ollama for embedding generation during tests

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
- tabulate (>= 0.9.0) - Formatted test output
- requests (>= 2.28.0) - API testing
- numpy (>= 1.24.0) - Data analysis in tests

## Technical Constraints
- MongoDB connection stability
- Embedding generation performance
- Memory usage optimization
- Cross-platform compatibility
- MongoDB Atlas vector index setup
- Import path management
- Authentication token handling for testing

## Environment Configuration
Environment variables are stored in a .env file in the backend directory:
- OLLAMA_API_BASE - URL for Ollama API (default: http://localhost:11434)
- OLLAMA_MODEL - Embedding model name (default: llama3.2)
- SECRET_KEY - JWT secret key
- MONGODB_URL - MongoDB connection string (default: mongodb://localhost:27017)
- DATABASE_NAME - MongoDB database name (default: job_recommender)
- API_BASE_URL - URL for API testing (default: http://localhost:8000)
- TEST_CANDIDATE_EMAIL - Test candidate email for authentication
- TEST_CANDIDATE_PASSWORD - Test candidate password
- TEST_EMPLOYER_EMAIL - Test employer email for authentication
- TEST_EMPLOYER_PASSWORD - Test employer password

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
- Test result reporting and visualization 

## API Endpoints

### Authentication
- `POST /token` - User authentication
- `POST /register/candidate` - Register candidate
- `POST /register/employer` - Register employer

### Profile Management
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `PATCH /profile` - Partial profile update
- `DELETE /profile` - Delete user account

### Job Management
- `POST /jobs` - Create job posting
- `GET /jobs` - Get job listings
- `PATCH /jobs/{job_id}` - Update job posting
- `DELETE /jobs/{job_id}` - Delete job posting

### Project Management
- `POST /projects` - Create project
- `GET /projects` - Get projects
- `PATCH /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project

### Recommendations
- `GET /recommendations/jobs` - Get job recommendations
- `GET /recommendations/candidates/{job_id}` - Get candidate recommendations for job
- `GET /recommendations/projects` - Get project recommendations
- `GET /recommendations/candidates-for-project/{project_id}` - Get candidate recommendations for project
- `GET /recommendations/project-candidates/{project_id}` - Alternative path for project candidates
- `GET /recommendations/skill-gap` - Get skill gap analysis
- `GET /recommendations/learning` - Get learning recommendations
- `GET /recommendations/career-path` - Get career path recommendations
- `GET /recommendations/similar-jobs/{job_id}` - Get similar jobs
- `POST /recommendations/talent-search` - Search for talent with specific criteria

### Feedback System
- `POST /recommendations/feedback` - Submit recommendation feedback
- `GET /recommendations/feedback/summary` - Get feedback summary statistics

### Skill Analysis
- `GET /ml/skills/clusters` - Get skill clusters analysis

### Search
- `POST /jobs/search` - Search jobs semantically
- `POST /projects/search` - Search projects semantically
- `POST /candidates/search` - Search candidates semantically

### Analytics
- `GET /analytics/recommendations/impact` - Get recommendation impact metrics
- `GET /analytics/recommendations/performance` - Get recommendation algorithm performance 