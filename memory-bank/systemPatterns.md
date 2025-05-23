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
   │   ├── app.py
   │   └── utils/
   ├── pages/
   ├── streamlit_app.py
   └── setup scripts
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
1. [Decision 1]
   - **Context**: [Why this decision was needed]
   - **Decision**: [What was decided]
   - **Consequences**: [Impact of this decision]

## Security Patterns
[Description of security measures and patterns implemented]

## Performance Patterns
[Description of performance optimization patterns]

## Error Handling
[Description of error handling patterns]

## Testing Patterns
[Description of testing strategies and patterns]

## Notes
[Any additional technical patterns or considerations] 