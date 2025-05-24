# System Patterns

## Architectural Patterns
1. **Microservices Architecture**
   - Separate FastAPI backend
   - Independent Streamlit frontend
   - Decoupled Ollama service
   - MongoDB database service

2. **RESTful API Design**
   - Clear endpoint structure
   - HTTP method semantics
   - JWT authentication
   - Async operations

3. **Event-Driven Updates**
   - Real-time UI updates
   - Async database operations
   - Background tasks for heavy computations

4. **Vector Search Architecture**
   - Embedding generation pipeline
   - MongoDB Atlas vector indexes
   - Semantic search functionality
   - Fallback text search mechanisms

5. **Feedback Collection Architecture**
   - User feedback capture endpoints
   - Structured feedback storage
   - Aggregation and analytics pipelines
   - Recommendation improvement mechanisms

6. **Skill Analysis Architecture**
   - Skill relationship modeling
   - Confidence-based clustering
   - Industry relevance mapping
   - Market demand calculation

## Design Patterns
1. **Repository Pattern**
   - Abstracted database operations
   - Clean separation of concerns
   - Reusable data access layer

2. **Factory Pattern**
   - Embedding generation
   - Database connection management
   - Configuration management

3. **Strategy Pattern**
   - Flexible recommendation algorithms
   - Pluggable embedding models
   - Customizable matching logic

## Component Relationships
1. **Frontend Components**
   - Page-based navigation
   - Shared state management
   - Reusable UI components

2. **Backend Services**
   - Authentication service
   - Recommendation service
   - Profile management service
   - Job posting service
   - Vector search service
   - Feedback collection service
   - Skill analysis service

3. **Data Flow**
   - Client request → API Gateway
   - API → Service Layer
   - Service Layer → Repository
   - Repository → Database

## Code Organization
1. **Directory Structure**
   ```
   Latest_lamma/
   ├── backend/
   │   ├── app.py               # Main FastAPI application
   │   ├── tests/               # Test scripts
   │   │   ├── README.md        # Test documentation
   │   │   ├── test_search_recommender.py # Search and recommendation tests
   │   │   ├── test_recommendation_system.py # Recommendation system tests
   │   │   └── check_all_embeddings.py # Embedding verification tool
   │   └── utils/               # Utility modules
   │       ├── __init__.py      # Package initialization
   │       ├── models.py        # Pydantic models
   │       ├── extended_models.py # Extended Pydantic models
   │       ├── database.py      # Database connection and operations
   │       └── embedding.py     # Vector embedding functions
   ├── pages/                   # Streamlit pages
   │   ├── profile.py           # User profile page
   │   ├── job_recommendations.py # Job recommendations page
   │   └── ...                  # Other pages
   ├── streamlit_app.py         # Main Streamlit application
   ├── run_backend.py           # Script to run the backend
   ├── run_app.py               # Script to run both backend and frontend
   └── setup scripts            # Various setup and run scripts
   ```

2. **Module Separation**
   - Clear module boundaries
   - Minimal dependencies
   - Focused responsibilities

## Testing Strategy
1. **Unit Tests**
   - Service layer testing
   - Repository testing
   - Utility function testing

2. **Integration Tests**
   - API endpoint testing
   - Database operations
   - Service interactions

3. **E2E Tests**
   - User flow testing
   - Visual demonstration
   - Automated scenarios

4. **Search & Recommendation Tests**
   - Embedding generation verification
   - Semantic search functionality testing
   - Recommendation algorithm validation
   - Vector index verification
   - Fallback mechanism testing

5. **Test Reporting**
   - Tabulated test results
   - Visual progress indicators
   - Detailed error reporting
   - Actionable recommendations

6. **Feedback System**
   - **Context**: Need to improve recommendations based on user input
   - **Decision**: Structured feedback collection with relevance and accuracy scores
   - **Consequences**: Better recommendation quality over time, requires analytics pipeline

7. **Skill Relationship Modeling**
   - **Context**: Need to understand relationships between skills
   - **Decision**: Confidence-based clustering with industry relevance mapping
   - **Consequences**: Better skill gap analysis, more relevant recommendations, requires regular updates

## Error Handling
1. **Exception Hierarchy**
   - Custom exceptions
   - Meaningful error messages
   - Proper error propagation

2. **Response Patterns**
   - Consistent error formats
   - HTTP status codes
   - Detailed error information

## Key Technical Decisions
1. **Database Selection**
   - **Context**: Need for flexible schema and document storage
   - **Decision**: MongoDB for document-based storage
   - **Consequences**: Flexible schema, good for JSON data, requires connection management

2. **Authentication Method**
   - **Context**: Need secure, stateless authentication
   - **Decision**: JWT with refresh tokens
   - **Consequences**: Stateless auth, token management required

3. **Embedding Generation**
   - **Context**: Need vector embeddings for recommendation
   - **Decision**: Ollama with llama3.2 model
   - **Consequences**: Local processing, no API costs, requires local setup

4. **Frontend Framework**
   - **Context**: Need rapid UI development
   - **Decision**: Streamlit for interactive web UI
   - **Consequences**: Fast development, some limitations in customization

5. **Testing Approach**
   - **Context**: Need to verify complex search and recommendation functionality
   - **Decision**: Comprehensive automated test scripts with detailed reporting
   - **Consequences**: Better quality assurance, early issue detection, requires test environment setup

## Security Patterns
- JWT token validation on protected endpoints
- Password hashing with bcrypt
- Environment variable-based secrets
- Input validation with Pydantic

## Performance Patterns
- Async database operations
- Optimized embedding generation
- Caching for frequently accessed data
- Pagination for large result sets
- Vector search optimization
- Confidence thresholds for skill clusters
- Parameterized endpoint responses

## API Design Patterns
- RESTful endpoint structure
- Consistent parameter naming
- Query parameter validation
- Structured response formats
- Detailed error messages
- Authentication middleware
- Backward compatibility support
- Versioned endpoints where needed
- Comprehensive documentation
- Test scripts for each endpoint

## Feedback and Analytics Patterns
- Structured feedback collection
- Relevance and accuracy scoring
- User action tracking
- Aggregated analytics
- Temporal trend analysis
- Industry-specific insights
- Recommendation improvement loops
- A/B testing preparation

## Notes
The system is designed with modularity and scalability in mind, allowing for easy extension of features and integration with additional services. The testing infrastructure provides comprehensive verification of critical functionality. Recent additions of feedback collection and skill analysis enhance the system's ability to learn and improve over time. 