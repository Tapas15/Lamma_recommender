# Technical Context

## Technologies Used

### Backend
- **FastAPI**: Main backend framework for API development
- **MongoDB**: NoSQL database for flexible data storage
- **PyMongo**: MongoDB driver for Python
- **PyJWT**: JSON Web Token implementation for authentication
- **Pydantic**: Data validation and settings management
- **Ollama**: Local embedding model for vector generation
- **Faker**: Library for generating realistic test data

### Frontend
- **Streamlit**: Frontend framework for rapid UI development
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive data visualization
- **NumPy**: Numerical computing

### Testing
- **Pytest**: Testing framework
- **Requests**: HTTP library for API testing
- **Selenium**: Browser automation for visual testing
- **Faker**: Generating realistic test data
- **JSON**: Storing test results and demo data

### Development Tools
- **Python**: Primary programming language
- **Git**: Version control
- **Batch/Shell scripts**: Cross-platform automation
- **Virtual Environment**: Dependency isolation

## Development Setup

### Prerequisites
- Python 3.9+
- MongoDB
- Ollama (for local embedding generation)
- Git

### Installation
1. Clone the repository
2. Run `setup.py` or `setup.bat`/`setup.sh` to set up the environment
3. Start the services using `start_services.bat`/`start_services.py`
4. Run the backend using `run_backend.bat`/`run_backend.py`
5. Run the frontend using `run_app.bat`/`run_app.py`

### Environment Setup
- Virtual environment for dependency management
- `requirements.txt` for Python dependencies
- Cross-platform setup scripts
- Automated service management

## API Structure

### Authentication Endpoints
- `/auth/register`: User registration
- `/auth/login`: User login and token generation
- `/auth/token`: Token validation and refresh

### User Management Endpoints
- `/users/me`: Get current user profile
- `/users/update`: Update user profile
- `/users/{user_id}`: Get user by ID

### Job Management Endpoints
- `/jobs/create`: Create new job posting
- `/jobs/update`: Update job posting
- `/jobs/{job_id}`: Get job by ID
- `/jobs/search`: Search jobs by criteria

### Recommendation Endpoints
- `/recommendations/jobs`: Get job recommendations for candidate
- `/recommendations/candidates`: Get candidate recommendations for job
- `/recommendations/learning`: Get learning recommendations for career goals
- `/recommendations/feedback`: Submit feedback on recommendations
- `/recommendations/feedback/summary`: Get aggregated feedback statistics

### ML Endpoints
- `/ml/learning-recommendations`: Enhanced learning recommendations
- `/ml/market-trends`: Skill market trend predictions
- `/ml/skills/clusters`: Skill relationship analysis

### Utility Endpoints
- `/health`: Service health check
- `/docs`: API documentation (Swagger UI)
- `/redoc`: Alternative API documentation (ReDoc)

## Database Structure

### Collections
- `users`: User profiles (candidates and employers)
- `jobs`: Job postings
- `projects`: Project postings
- `applications`: Job applications
- `skills`: Skill definitions and metadata
- `embeddings`: Vector embeddings for skills and profiles
- `feedback`: User feedback on recommendations

### Indexes
- Text indexes for search functionality
- Vector indexes for semantic matching
- Compound indexes for filtered queries

## Testing Infrastructure

### Test Scripts
- `test_endpoint.py`: Tests API endpoints with authentication
- `test_recommendation_system.py`: Tests recommendation functionality
- `test_search_recommender.py`: Tests search and recommendation system
- `test_search_recommender_with_mocks.py`: Tests with mock data
- `check_all_embeddings.py`: Verifies vector embeddings
- `visual_workflow_test.py`: Visual demonstration of system flow
- `complete_workflow_test.py`: End-to-end workflow testing
- `run_full_tests.py`: Runs all test scripts
- `run_mock_tests.py`: Runs tests with mock data

### Demo Data Generation
- `create_demo_candidates.py`: Generates candidate accounts
- `create_demo_employers.py`: Generates employer accounts
- `create_demo_jobs_projects.py`: Generates job and project postings
- `DEMO_DATA_README.md`: Documentation for demo data scripts

### Test Data Storage
- `demo_candidates.json`: Generated candidate data
- `demo_employers.json`: Generated employer data
- `demo_jobs.json`: Generated job posting data
- `demo_projects.json`: Generated project data

## Technical Constraints

### Performance
- Vector search performance optimization needed
- MongoDB connection pooling for better stability
- Batch processing for large datasets

### Security
- JWT with proper expiration and refresh mechanism
- Password hashing with bcrypt
- Input validation with Pydantic
- CORS configuration for frontend access

### Scalability
- Database indexing for faster queries
- Caching strategy needed
- Potential for horizontal scaling

## Dependencies

### Core Dependencies
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `pydantic`: Data validation
- `pymongo`: MongoDB driver
- `python-jose`: JWT implementation
- `passlib`: Password hashing
- `streamlit`: Frontend framework
- `pandas`: Data manipulation
- `numpy`: Numerical computing
- `requests`: HTTP client
- `faker`: Test data generation

### Development Dependencies
- `pytest`: Testing
- `black`: Code formatting
- `isort`: Import sorting
- `flake8`: Linting
- `selenium`: Browser automation

## Technical Decisions

### Authentication
- JWT-based authentication for stateless API
- Token refresh mechanism for extended sessions
- Password hashing with bcrypt for security

### Database
- MongoDB chosen for flexible schema
- PyMongo for direct control over queries
- Vector indexes for semantic search

### API Design
- RESTful API design with clear resource paths
- Consistent response formatting
- Comprehensive error handling
- Input validation with Pydantic models

### Frontend
- Streamlit for rapid development
- Multi-page application structure
- Responsive design for different devices

### Testing
- Comprehensive test scripts for API validation
- Visual demonstration for workflow testing
- Demo data generation for realistic testing
- Automated test execution

## Technical Challenges

### Resolved
- Basic authentication flow
- MongoDB connection setup
- Vector embedding generation
- Cross-platform setup scripts
- Unicode handling in setup scripts
- Permission issues during pip upgrade

### In Progress
- Optimizing vector search performance
- Improving embedding generation
- Enhancing error handling
- Expanding test coverage

### Upcoming
- Implementing caching strategy
- Setting up deployment pipeline
- Performance optimization
- Scaling strategy

## Setup Script Improvements

### Unicode Handling
- Modified the `run_command` function in setup.py to handle Unicode properly:
  - Changed `text=True` to `text=False` in subprocess.run
  - Added proper UTF-8 decoding with error handling
  - Implemented fallback for decoding errors

### Permission Handling
- Made the pip upgrade step optional if it fails due to permission errors:
  - Added try/except block around pip upgrade command
  - Implemented continuation of setup process if upgrade fails
  - Added user-friendly error messages

### Error Handling
- Enhanced error handling throughout the setup script:
  - More descriptive error messages
  - Better exception handling
  - Graceful fallbacks for common issues

## API Testing Enhancements

### Authentication Testing
- Added JWT token authentication to test scripts
- Implemented proper header formatting for authenticated requests
- Added error handling for authentication failures

### Endpoint Testing
- Created test_endpoint.py for testing API endpoints
- Implemented health endpoint testing
- Added testing for ML learning recommendations endpoint
- Implemented comparison testing between original and ML endpoints

### Response Validation
- Added status code checking
- Implemented JSON response validation
- Added error message display for failed requests

## Demo Data Generation

### Candidate Generation
- Implemented realistic candidate profile generation
- Added randomized skills with different proficiency levels
- Created varied education and work experience histories
- Generated availability and remote work preferences

### Employer Generation
- Implemented realistic company profile generation
- Added varied company sizes and industries
- Created diverse location data
- Generated employer user accounts with proper roles

### Job and Project Generation
- Implemented job posting generation with realistic requirements
- Added project posting generation with specific needs
- Created varied compensation and duration data
- Associated postings with employer accounts

### Data Storage
- Saved generated data to JSON files for reference
- Implemented structured data format for easy parsing
- Added metadata for tracking generation parameters

## Notes
- Focus on modular development
- Regular testing implementation
- Documentation updates needed
- Performance optimization required
- Cross-platform compatibility is a priority
- API testing is essential for stability
- Demo data generation enhances testing capabilities 