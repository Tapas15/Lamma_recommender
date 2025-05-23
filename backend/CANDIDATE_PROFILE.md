# Extended Candidate Profile

This document explains how to use the enhanced candidate registration endpoint that supports a more detailed profile structure.

## API Endpoint

```
POST /register/extended-candidate
```

## Request Format

The request should be a JSON object with the following structure:

```json
{
  "email": "candidate@example.com",
  "password": "securepassword123",
  "full_name": "Test Candidate",
  "phone": "+1-555-123-4567",
  "location": "New York, USA",
  "experience_years": "5+ years",
  "education_summary": "MSc Computer Science",
  "bio": "Software engineer specializing in AI and machine learning applications.",
  "about": "Experienced Software Engineer with a strong background in...",
  "links": {
    "linkedin": "https://www.linkedin.com/in/testcandidate",
    "github": "https://github.com/testcandidate",
    "portfolio": "https://testcandidate.dev",
    "resume": "https://example.com/resumes/testcandidate_resume.pdf"
  },
  "skills": {
    "languages_frameworks": ["Python", "FastAPI", "Flask", "SQL", "Bash"],
    "ai_ml_data": ["Machine Learning", "Deep Learning", "Data Analysis"],
    "tools_platforms": ["Docker", "Git", "AWS", "PostgreSQL", "MongoDB"],
    "soft_skills": ["Team collaboration", "Agile development"]
  },
  "experience": [
    {
      "title": "Machine Learning Engineer",
      "company": "AI Tech Solutions",
      "location": "New York, NY",
      "duration": "Jan 2021 – Present",
      "responsibilities": [
        "Built and deployed ML models for fraud detection",
        "Created RESTful APIs using FastAPI for AI service delivery"
      ]
    }
  ],
  "education": [
    {
      "degree": "MSc in Computer Science",
      "institution": "Columbia University",
      "duration": "2017 – 2019"
    }
  ],
  "certifications": [
    "AWS Certified Machine Learning – Specialty",
    "TensorFlow Developer Certificate"
  ],
  "preferred_job_locations": ["New York", "San Francisco", "Remote"],
  "job_search_status": {
    "currently_looking": true,
    "available_from": "2025-06-01",
    "desired_job_titles": ["Machine Learning Engineer", "Data Scientist"],
    "preferred_employment_type": ["Full-time", "Remote", "Contract"],
    "salary_expectation_usd": {
      "min": 90000,
      "max": 120000
    },
    "notice_period_days": 30,
    "relocation_willingness": true
  }
}
```

## Example Usage

```bash
curl -X POST http://localhost:8000/register/extended-candidate \
  -H "Content-Type: application/json" \
  -d @sample_candidate_request.json
```

## Fields

| Field                   | Type                | Description                                      | Required |
|-------------------------|---------------------|--------------------------------------------------|----------|
| email                   | String              | Email address (must be unique)                   | Yes      |
| password                | String              | Account password                                 | Yes      |
| full_name               | String              | Full name of the candidate                       | Yes      |
| phone                   | String              | Contact phone number                             | No       |
| location                | String              | Current location                                 | No       |
| experience_years        | String              | Summary of years of experience                   | No       |
| education_summary       | String              | Brief summary of education                       | No       |
| bio                     | String              | Short biography                                  | No       |
| about                   | String              | Detailed about section                           | No       |
| links                   | Object              | Professional profile links                       | No       |
| skills                  | Object              | Categorized skills                               | No       |
| experience              | Array of Objects    | Work experience history                          | No       |
| education               | Array of Objects    | Education history                                | No       |
| certifications          | Array of Strings    | Professional certifications                      | No       |
| preferred_job_locations | Array of Strings    | Preferred locations for work                     | No       |
| job_search_status       | Object              | Current job search preferences                   | No       |

## Additional Notes

- The system will generate a unique ID for each new candidate
- Password is stored in hashed format
- The profile data is used to generate vector embeddings for AI-powered job matching
- All fields except email, password, and full_name are optional 