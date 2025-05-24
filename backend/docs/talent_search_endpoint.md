# Talent Search API Endpoint

## Overview

The talent search API endpoint (`/recommendations/talent-search`) provides advanced candidate search capabilities with multiple filtering options. This endpoint allows employers to search for candidates based on skills, experience, location, education, and availability.

## Endpoint Details

- **URL**: `/recommendations/talent-search`
- **Method**: `POST`
- **Authentication**: Required (JWT token)
- **Authorization**: Employer users only

## Request Parameters

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `skills` | array | Yes | List of required skills to search for |
| `job_title` | string | No | Job title to match against candidate profiles |
| `industry` | string | No | Industry to match against candidate profiles |
| `location` | string | No | Location to match against candidate profiles |
| `experience_years` | integer | No | Required years of experience |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_match_score` | integer | 0 | Minimum match score threshold (0-100) |
| `limit` | integer | 10 | Maximum number of results to return |
| `include_details` | boolean | true | Whether to include full candidate details in response |
| `sort_by` | string | "match_score" | Sort results by: "match_score", "experience_years", "availability" |
| `experience_min` | integer | null | Minimum years of experience |
| `experience_max` | integer | null | Maximum years of experience |
| `location_radius` | integer | null | Location search radius in miles/km |
| `include_remote` | boolean | false | Include remote candidates regardless of location |
| `education_level` | string | null | Comma-separated list of education levels (e.g., "Bachelors,Masters") |
| `availability` | string | null | Comma-separated list of availability options (e.g., "Immediate,2 weeks") |

## Response Format

```json
{
  "candidates": [
    {
      "candidate_id": "string",
      "match_score": 95.5,
      "match_factors": {
        "skills_match": 90,
        "experience_match": 100
      },
      "candidate_details": {
        // Full candidate profile (when include_details=true)
      }
    }
  ],
  "total_count": 10,
  "metadata": {
    "search_params": {
      "skills": ["Python", "React", "AWS"],
      "job_title": "Full Stack Developer",
      "industry": "Technology"
    },
    "filters_applied": {
      "experience_min": 3,
      "experience_max": 10,
      "education_level": "Bachelors,Masters",
      "availability": "Immediate,2 weeks",
      "location_radius": 50,
      "include_remote": true
    }
  }
}
```

## Match Factors

The API calculates match factors to help explain why candidates match the search criteria:

- **Skills Match**: Percentage of required skills that the candidate possesses
- **Experience Match**: How well the candidate's experience matches the requirements

## Examples

### Basic Search

```
POST /recommendations/talent-search
{
  "skills": ["Python", "React", "AWS"]
}
```

### Advanced Search with Filters

```
POST /recommendations/talent-search?min_match_score=80&limit=20&experience_min=3&experience_max=10&education_level=Bachelors,Masters&availability=Immediate,2%20weeks&include_remote=true
{
  "skills": ["Python", "React", "AWS"],
  "job_title": "Full Stack Developer",
  "industry": "Technology",
  "location": "San Francisco, CA"
}
```

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Bad request (e.g., missing required parameters) |
| 401 | Unauthorized (missing or invalid token) |
| 403 | Forbidden (non-employer users) |
| 500 | Server error (e.g., embedding generation failure) |

## Notes

- The endpoint uses vector embeddings to calculate semantic similarity between search queries and candidate profiles
- Location filtering currently uses simple text matching; future versions will implement proper geocoding
- Performance may vary based on the number of candidates in the database 