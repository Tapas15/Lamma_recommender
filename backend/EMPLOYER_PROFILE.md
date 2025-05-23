# Extended Employer Profile

This document explains how to use the enhanced employer registration endpoint that supports a more detailed profile structure.

## API Endpoint

```
POST /register/extended-employer
```

## Request Format

The request should be a JSON object with the following structure:

```json
{
  "email": "test@employer.com",
  "password": "testpassword123",
  "full_name": "Jane Smith",
  "user_type": "employer",
  "position": "HR Manager",
  "bio": "HR Manager at Tech Solutions Inc. with expertise in tech recruitment.",
  "about": "Experienced HR professional with a strong background in talent acquisition...",
  "contact_email": "hr@techsolutions.com",
  "contact_phone": "+1-555-0123",
  "location": "San Francisco, CA",
  "company_details": {
    "company_name": "Tech Solutions Inc.",
    "company_description": "Tech Solutions Inc. is a leading provider of custom technology solutions...",
    "company_website": "https://techsolutions.com",
    "company_location": "San Francisco, CA",
    "company_size": "100-500 employees",
    "industry": "Technology",
    "founded_year": 2012,
    "company_logo": "https://techsolutions.com/assets/logo.png",
    "company_socials": {
      "linkedin": "https://www.linkedin.com/company/techsolutions",
      "twitter": "https://twitter.com/techsolutions",
      "glassdoor": "https://www.glassdoor.com/Overview/Working-at-Tech-Solutions"
    },
    "values": [
      "Innovation",
      "Integrity",
      "Collaboration",
      "Customer-Centricity"
    ],
    "mission": "To empower businesses through intelligent technology solutions that drive growth and efficiency.",
    "vision": "To be the world's most trusted partner in digital transformation."
  },
  "hiring_preferences": {
    "job_roles_hiring": ["Machine Learning Engineer", "Backend Developer", "DevOps Engineer"],
    "employment_types": ["Full-time", "Remote", "Contract"],
    "locations_hiring": ["San Francisco", "Remote", "Austin"],
    "salary_range_usd": {
      "min": 80000,
      "max": 140000
    },
    "remote_friendly": true,
    "tech_stack": ["Python", "AWS", "FastAPI", "Docker", "Kubernetes", "PostgreSQL"]
  }
}
```

## Required Fields

The following fields are required:
- `email` - The employer's email address
- `password` - A secure password
- `full_name` - The employer's full name
- `company_details.company_name` - The name of the company
- `company_details.industry` - The industry of the company

All other fields are optional.

## Response Format

The response will include all the employer details (excluding sensitive information like password):

```json
{
  "id": "61c3b4f2e3a8d5a45b01cfe2",
  "email": "test@employer.com",
  "full_name": "Jane Smith",
  "user_type": "employer",
  "position": "HR Manager",
  "bio": "HR Manager at Tech Solutions Inc. with expertise in tech recruitment.",
  "about": "Experienced HR professional with a strong background in talent acquisition...",
  "contact_email": "hr@techsolutions.com",
  "contact_phone": "+1-555-0123",
  "location": "San Francisco, CA",
  "created_at": "2023-06-01T12:00:00.000Z",
  "company_details": {
    "company_name": "Tech Solutions Inc.",
    "company_description": "Tech Solutions Inc. is a leading provider of custom technology solutions...",
    "company_website": "https://techsolutions.com",
    "company_location": "San Francisco, CA",
    "company_size": "100-500 employees",
    "industry": "Technology",
    "founded_year": 2012,
    "company_logo": "https://techsolutions.com/assets/logo.png",
    "company_socials": {
      "linkedin": "https://www.linkedin.com/company/techsolutions",
      "twitter": "https://twitter.com/techsolutions",
      "glassdoor": "https://www.glassdoor.com/Overview/Working-at-Tech-Solutions"
    },
    "values": [
      "Innovation",
      "Integrity",
      "Collaboration",
      "Customer-Centricity"
    ],
    "mission": "To empower businesses through intelligent technology solutions that drive growth and efficiency.",
    "vision": "To be the world's most trusted partner in digital transformation."
  },
  "hiring_preferences": {
    "job_roles_hiring": ["Machine Learning Engineer", "Backend Developer", "DevOps Engineer"],
    "employment_types": ["Full-time", "Remote", "Contract"],
    "locations_hiring": ["San Francisco", "Remote", "Austin"],
    "salary_range_usd": {
      "min": 80000,
      "max": 140000
    },
    "remote_friendly": true,
    "tech_stack": ["Python", "AWS", "FastAPI", "Docker", "Kubernetes", "PostgreSQL"]
  },
  "profile_completed": true,
  "is_active": true,
  "last_active": "2023-06-01T12:00:00.000Z",
  "verified": false,
  "total_jobs_posted": 0,
  "total_active_jobs": 0,
  "account_type": "standard",
  "profile_views": 0,
  "posted_jobs": []
}
```

## Error Responses

- `400 Bad Request` - If the email is already registered
- `422 Unprocessable Entity` - If the request data doesn't match the expected format
- `500 Internal Server Error` - If there's a server error during registration 