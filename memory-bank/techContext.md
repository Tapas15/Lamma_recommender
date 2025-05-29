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
- **Streamlit**: Frontend framework for rapid UI development and testing
- **Next.js**: Modern React framework for production frontend
- **React**: Component-based UI library with TypeScript support
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Plotly**: Interactive data visualization library (current implementation)
- **Highcharts** (Planned): Advanced charting library for enhanced analytics
- **Pandas**: Data manipulation and analysis
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

### Performance Optimization
- **Caching**: In-memory caching for frequently accessed data
- **Database Indexing**: For faster query execution
- **Vector Search Optimization**: For improved response times
- **Query Optimization**: For more efficient database operations

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

### Analytics Endpoints
- `/analytics/recommendation-performance`: Get recommendation performance metrics
- `/analytics/user-engagement`: Get user engagement statistics
- `/analytics/feedback-analysis`: Get detailed feedback analysis

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
- `analytics`: Analytics data and metrics

### Indexes
- Text indexes for search functionality
- Vector indexes for semantic matching
- Compound indexes for filtered queries
- Performance-optimized indexes for frequent queries

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
- `test_market_trends.py`: Tests market trends endpoint
- `test_feedback_system.py`: Tests recommendation feedback system
- `test_skill_clusters.py`: Tests skill clusters endpoint
- `test_performance.py`: Tests performance of critical endpoints

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
- `test_results.json`: Test execution results
- `performance_metrics.json`: Performance test results

## Technical Constraints

### Performance
- Vector search performance optimization needed
- MongoDB connection pooling for better stability
- Batch processing for large datasets
- Caching implementation for frequently accessed data
- Response time optimization for critical endpoints

### Security
- JWT with proper expiration and refresh mechanism
- Password hashing with bcrypt
- Input validation with Pydantic
- CORS configuration for frontend access

### Scalability
- Database indexing for faster queries
- Caching strategy for performance improvement
- Potential for horizontal scaling
- Optimization for large datasets

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

### Performance Optimization
- Caching strategy for frequently accessed data
- Vector search optimization for faster responses
- Database query optimization for efficiency
- Response time monitoring and improvement

## Technical Challenges

### Resolved
- Basic authentication flow
- MongoDB connection setup
- Vector embedding generation
- Cross-platform setup scripts
- Unicode handling in setup scripts
- Permission issues during pip upgrade
- Import path issues in backend application

### In Progress
- Optimizing vector search performance
- Improving embedding generation
- Enhancing error handling
- Expanding test coverage
- Implementing caching strategy
- Optimizing response times for critical endpoints

### Upcoming
- Implementing caching strategy
- Setting up deployment pipeline
- Performance optimization
- Scaling strategy
- A/B testing framework implementation
- Monitoring and alerting setup

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
- Added testing for market trends endpoint
- Implemented feedback system endpoint testing
- Added skill clusters endpoint testing

### Response Validation
- Added status code checking
- Implemented JSON response validation
- Added error message display for failed requests
- Implemented performance metrics collection
- Added response time monitoring

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

## New API Endpoints

### Market Trends Endpoint
- Implemented `/ml/market-trends` GET endpoint
- Added support for timeframe parameters (3 months to 5 years)
- Included detailed trend information:
  - Current and projected demand scores
  - Growth rates and confidence scores
  - Salary projections and industry relevance
  - Complementary skills and market factors
- Created comprehensive documentation and test scripts

### Recommendation Feedback Endpoints
- Implemented `/recommendations/feedback` POST endpoint
- Added `/recommendations/feedback/summary` GET endpoint
- Included detailed feedback collection:
  - Relevance and accuracy scores
  - Qualitative feedback through comments
  - User action tracking (viewed, applied, saved, etc.)
  - Aggregated feedback statistics
- Created comprehensive documentation and test scripts

### Skill Clusters Endpoint
- Implemented `/ml/skills/clusters` GET endpoint
- Added confidence threshold filtering
- Included detailed cluster information:
  - Core skills and related skills
  - Industry relevance
  - Growth rates and market demand
  - Confidence scores for skill relationships
- Created comprehensive documentation and test scripts

### Analytics Endpoints
- Started implementing analytics endpoints
- Added initial data aggregation mechanisms
- Planned visualization data structures
- Created preliminary documentation

## Performance Optimization

### Caching Implementation
- Started implementing in-memory caching for frequently accessed data
- Defined cache invalidation strategies
- Identified critical endpoints for caching
- Implemented initial caching mechanism

### Vector Search Optimization
- Began optimizing vector search operations
- Implemented more efficient embedding comparison
- Enhanced database query patterns for vector operations
- Added performance monitoring for vector searches

### Database Query Optimization
- Improved query efficiency for critical endpoints
- Enhanced index usage for frequent queries
- Optimized projection to return only needed fields
- Implemented aggregation pipeline optimization

## Notes
- Focus on modular development
- Regular testing implementation
- Documentation updates needed
- Performance optimization required
- Cross-platform compatibility is a priority
- API testing is essential for stability
- Demo data generation enhances testing capabilities 
- Caching implementation is critical for performance
- Vector search optimization is key for response times
- New API endpoints are enhancing system capabilities 

### Data Visualization Stack
- **Current**: Plotly for interactive charts in Streamlit interface
- **Planned**: Highcharts integration for advanced dashboard visualizations
- **Chart Types in Development**:
  - Vector charts for skill relationship networks
  - Bubble charts for candidate/job matching visualization
  - Scatter plots for analytics correlation analysis
  - Timeline charts for career progression tracking
- **Visualization Features**:
  - Interactive drill-down capabilities
  - Responsive design for multi-device support
  - Accessibility compliance for inclusive design 