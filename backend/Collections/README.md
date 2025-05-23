# Job Recommender API Postman Collections

This directory contains Postman collections for testing the Job Recommender API at different levels of complexity:

## Collection Versions

### Simple Collection
- **Files**: `job_recommender_api_simple_complete.json`
- **Description**: Basic collection with minimal JSON payloads that contains all API endpoints.
- **Use Case**: Quick testing of API endpoints with minimal data.

### Basic Collection
- **Files**: `job_recommender_api_basic_complete.json`, `job_recommender_api_basic_complete_environment.json`
- **Description**: Moderately detailed payloads with all API endpoints.
- **Use Case**: Standard testing with a moderate level of detail.

### Extended Collection
- **Files**: `job_recommender_api_complete_extended.json`, `job_recommender_api_complete_extended_environment.json`
- **Description**: Comprehensive collection with fully detailed JSON payloads.
- **Use Case**: Thorough testing with complete data structures.

## How to Use

1. Import the desired collection and its corresponding environment file into Postman
2. Select the appropriate environment
3. Start with authentication endpoints (register and login)
4. Use the endpoints according to your testing needs

## API Sections

- **Authentication**: User registration and login
- **Profile Management**: Viewing and updating user profiles
- **Jobs**: Creating, viewing, updating, and deleting job postings
- **Projects**: Managing project-based work opportunities
- **Applications**: Job and project applications
- **Saved Items**: Bookmarking jobs and projects
- **Recommendations**: Personalized recommendations for jobs, projects, and candidates
- **Employer Management**: Tools for employers to manage jobs and view analytics

## Features

The collection covers the following functional areas:

1. **Authentication**
   - User registration (candidate and employer)
   - Login and token management
   - Profile management

2. **Jobs**
   - Creating, updating, and deleting job listings
   - Viewing all jobs
   - Semantic search for jobs

3. **Projects**
   - Creating, updating, and deleting project listings
   - Viewing all projects and filtering by status
   - Semantic search for projects

4. **Applications**
   - Job applications management
   - Project applications management
   - Application listing and filtering

5. **Saved Items**
   - Save jobs and projects for later
   - View and manage saved items

6. **Recommendations**
   - Get personalized job recommendations for candidates
   - Get personalized project recommendations for candidates
   - Get candidate recommendations for specific jobs or projects

## Getting Started

### Prerequisites

- [Postman](https://www.postman.com/downloads/) installed on your system
- The Job Recommender API running (default: http://localhost:8000)

### Installation

1. Import the collection file (`job_recommender_api_complete_extended.json`) into Postman
2. Import the environment file (`job_recommender_api_complete_extended_environment.json`) into Postman
3. Select the "Job Recommender API Environment" from the environment dropdown in Postman

### Usage

1. **Authentication**:
   - Start by using the "Register Candidate" or "Register Employer" request to create a user
   - Use the "Login" request to get an authentication token (automatically saved to environment)
   - All subsequent requests will use this token for authentication

2. **Basic Workflow for Candidates**:
   - Register as a candidate
   - Login to get token
   - Browse jobs and projects 
   - Save interesting jobs/projects
   - Apply to jobs/projects
   - Get personalized recommendations

3. **Basic Workflow for Employers**:
   - Register as an employer
   - Login to get token
   - Create job and project postings
   - View applications for your jobs/projects
   - Get candidate recommendations for your jobs/projects

### Environment Variables

The provided environment file includes the following variables:

- `base_url`: The base URL for the API (default: http://localhost:8000)
- `email`, `password`: User credentials for authentication
- `access_token`: Automatically populated after login
- `job_id`, `project_id`: IDs for specific jobs and projects
- `saved_job_id`, `saved_project_id`: IDs for saved items
- `employer_id`, `candidate_id`: User IDs for specific roles

## Testing Tips

1. **Sequential Testing**: 
   - Follow the logical flow of actions (register → login → create/view content → interact with content)
   
2. **Token Handling**: 
   - The login request automatically stores the token in the environment
   - All authenticated requests use this token automatically

3. **Request Chaining**:
   - Many requests can use the output from previous requests
   - For example, after creating a job, the response contains the job ID which can be used for subsequent requests 