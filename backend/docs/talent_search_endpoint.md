# Talent Search API Endpoint Documentation

## Overview

The talent search API provides a powerful way for employers to find qualified candidates based on specific criteria. It uses vector embeddings for semantic matching and supports various filtering options.

## Endpoint

```
POST /recommendations/talent-search
```

## Authentication

Requires a valid JWT token with employer privileges.

## Request Body

The request body should be a JSON object with the following structure:

```json
{
  "skills": ["Python", "JavaScript", "React"],
  "job_title": "Full Stack Developer",
  "industry": "Technology",
  "location": "New York, NY"
}
```

### Required Fields

- `skills`: Array of strings or a single string representing required skills

### Optional Fields

- `job_title`: String representing the job title
- `industry`: String representing the industry
- `location`: String representing the desired location

## Query Parameters

- `min_match_score` (int, default: 0): Minimum match score (0-100)
- `limit` (int, default: 10): Maximum number of results to return
- `include_details` (bool, default: true): Whether to include detailed candidate information
- `sort_by` (string, default: "match_score"): Sort results by "match_score", "experience_years", or "availability"
- `experience_min` (int): Minimum years of experience
- `experience_max` (int): Maximum years of experience
- `location_radius` (int): Distance in miles from specified location
- `include_remote` (bool, default: false): Include remote candidates
- `education_level` (string): Comma-separated list of education levels
- `availability` (string): Comma-separated list of availability options

## Response

```json
{
  "candidates": [
    {
      "candidate_id": "60d21b4667d0d8992e610c85",
      "match_score": 85,
      "match_factors": {
        "skills_match": 90,
        "experience_match": 80,
        "education_match": 70
      },
      "candidate_details": {
        "full_name": "John Doe",
        "location": "New York, NY",
        "experience_years": 5,
        "availability": "Immediate",
        "skills": ["Python", "JavaScript", "React", "Node.js"]
      }
    }
  ],
  "total_count": 1,
  "metadata": {
    "search_params": {
      "skills": ["Python", "JavaScript", "React"],
      "job_title": "Full Stack Developer"
    },
    "filters_applied": {
      "experience_min": 3,
      "experience_max": 10,
      "education_level": null,
      "availability": null,
      "location_radius": null,
      "include_remote": false
    }
  }
}
```

## Error Handling

### Common Errors

- `400 Bad Request`: Missing required parameters or invalid input
- `403 Forbidden`: User is not an employer
- `500 Internal Server Error`: Server-side processing error

### Recent Bug Fixes

1. **Fixed: "'dict' object has no attribute 'lower'"**
   - The error occurred when comparing location strings where one of the values was not a string
   - Fix: Added type checking before string operations
   - Added string conversion for input parameters to ensure compatibility

2. **Input Sanitization**
   - Added validation for search parameters
   - Ensured skills parameter is always a list of strings
   - Added null checks for job_title and industry fields

## Example Usage

```python
import requests

url = "https://api.example.com/recommendations/talent-search"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}
payload = {
    "skills": ["Python", "React", "AWS"],
    "job_title": "Backend Developer",
    "location": "Remote"
}
params = {
    "experience_min": 2,
    "sort_by": "match_score",
    "include_remote": True
}

response = requests.post(url, json=payload, params=params, headers=headers)
results = response.json()
```

## Best Practices

1. Always provide specific skills for better matching
2. Use the query parameters to refine results rather than filtering client-side
3. Start with broader search criteria and narrow down if too many results are returned
4. For location-based searches, consider using the `include_remote` parameter to widen the candidate pool 