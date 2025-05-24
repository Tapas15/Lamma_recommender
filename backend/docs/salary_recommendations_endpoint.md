# Salary Recommendations API Endpoint Documentation

## Overview

The salary recommendations API provides data-driven salary insights for job roles based on various factors including job title, skills, experience, location, and company characteristics. This endpoint helps employers make informed compensation decisions and candidates understand their market value.

## Endpoint

```
POST /recommendations/salary
```

## Authentication

Requires a valid JWT token.

## Request Body

The request body should be a JSON object with the following structure:

```json
{
  "job_title": "Senior Software Engineer",
  "required_skills": ["JavaScript", "React", "Node.js", "AWS"],
  "experience_years": 5,
  "location": "San Francisco, CA",
  "remote_position": false,
  "industry": "Technology",
  "company_size": "51-200 employees"
}
```

### Required Fields

- `job_title`: String representing the job title

### Optional Fields

- `required_skills`: Array of strings representing required skills
- `experience_years`: Integer representing years of experience
- `location`: String representing the job location
- `remote_position`: Boolean indicating if the position is remote
- `industry`: String representing the industry
- `company_size`: String representing company size (e.g., "51-200 employees")

## Response

```json
{
  "job_title": "Senior Software Engineer",
  "salary_recommendation": {
    "range": {
      "min": 145000,
      "max": 210000
    },
    "median": 177500,
    "currency": "USD"
  },
  "market_comparison": {
    "percentiles": {
      "10th": 120000,
      "25th": 135000,
      "50th": 150000,
      "75th": 172500,
      "90th": 195000
    },
    "regional_comparison": [
      {
        "location": "Oakland, CA",
        "median_salary": 135000,
        "difference_percentage": -10
      },
      {
        "location": "San Jose, CA",
        "median_salary": 157500,
        "difference_percentage": 5
      },
      {
        "location": "Sacramento, CA",
        "median_salary": 120000,
        "difference_percentage": -20
      }
    ],
    "industry_comparison": [
      {
        "industry": "Technology",
        "median_salary": 165000,
        "difference_percentage": 10
      },
      {
        "industry": "Finance",
        "median_salary": 172500,
        "difference_percentage": 15
      },
      {
        "industry": "Healthcare",
        "median_salary": 150000,
        "difference_percentage": 0
      }
    ]
  },
  "factors": [
    {
      "factor": "Extensive experience",
      "impact": "positive",
      "description": "Senior professionals with 8+ years experience command premium salaries"
    },
    {
      "factor": "High cost of living location",
      "impact": "positive",
      "description": "Salaries in San Francisco are typically higher to offset living costs"
    },
    {
      "factor": "Technology industry",
      "impact": "positive",
      "description": "The Technology industry typically offers competitive compensation"
    },
    {
      "factor": "In-demand skills",
      "impact": "positive",
      "description": "Your skill set includes high-demand technologies that command a premium"
    }
  ],
  "metadata": {
    "request_params": {
      "job_title": "Senior Software Engineer",
      "required_skills": ["JavaScript", "React", "Node.js", "AWS"],
      "experience_years": 5,
      "location": "San Francisco, CA",
      "remote_position": false,
      "industry": "Technology",
      "company_size": "51-200 employees"
    },
    "data_freshness": "2023-Q4",
    "confidence_level": "high"
  }
}
```

## Error Handling

### Common Errors

- `400 Bad Request`: Missing job title or invalid input
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Server-side processing error

## Salary Calculation Methodology

The salary recommendations are calculated based on several factors:

1. **Base Salary Range**: Determined by job title, with different ranges for different levels
2. **Experience Adjustment**: Salary increases with experience level (entry, mid, senior, etc.)
3. **Location Adjustment**: Adjusts for cost of living in different locations
4. **Industry Factor**: Different industries have different compensation standards
5. **Skills Premium**: In-demand skills can command higher compensation
6. **Company Size**: Larger companies typically offer higher compensation

## Example Usage

```python
import requests

url = "https://api.example.com/recommendations/salary"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}
payload = {
    "job_title": "Senior Software Engineer",
    "required_skills": ["JavaScript", "React", "Node.js", "AWS"],
    "experience_years": 5,
    "location": "San Francisco, CA",
    "remote_position": false,
    "industry": "Technology",
    "company_size": "51-200 employees"
}

response = requests.post(url, json=payload, headers=headers)
results = response.json()
```

## Best Practices

1. Always provide a specific job title for the most accurate recommendations
2. Include location information for region-specific salary data
3. List all required skills to account for skill premiums
4. Specify experience level for appropriate salary ranges
5. Use the industry parameter to get industry-specific compensation data 