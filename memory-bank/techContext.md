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
- [Requirement 1]
- [Requirement 2]

### Installation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Dependencies
### Core Dependencies
- [Dependency 1] - [Version] - [Purpose]
- [Dependency 2] - [Version] - [Purpose]

### Development Dependencies
- [Dev Dependency 1] - [Version] - [Purpose]
- [Dev Dependency 2] - [Version] - [Purpose]

## Technical Constraints
- [Constraint 1]
- [Constraint 2]

## Environment Configuration
[Description of environment variables and configuration]

## Build Process
[Description of build steps and configuration]

## Deployment Process
[Description of deployment workflow]

## Monitoring and Logging
[Description of monitoring and logging setup] 