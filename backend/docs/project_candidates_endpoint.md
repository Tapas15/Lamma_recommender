# Project Candidate Recommendations API Endpoint

## Overview

The project candidate recommendations API endpoint (`/recommendations/candidates-for-project/{project_id}` or `/recommendations/project-candidates/{project_id}`) has been enhanced with advanced filtering, sorting, and response formatting capabilities to provide more targeted and relevant candidate matches for specific project postings.

## Endpoint Details

- **URLs**: 
  - `/recommendations/candidates-for-project/{project_id}` (primary)
  - `/recommendations/project-candidates/{project_id}` (alternative, for backward compatibility)
- **Method**: `GET`
- **Authentication**: Required (JWT token)
- **Authorization**: Employer users only (project owner)

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_match_score` | integer | 0 | Minimum match score threshold (0-100) |
| `limit` | integer | 10 | Maximum number of results to return |
| `include_details` | boolean | true | Whether to include full candidate details in response |
| `sort_by` | string | "match_score" | Sort results by: "match_score", "experience_years", "availability_hours" |
| `availability_min_hours` | integer | null | Minimum weekly hours candidate is available for the project |
| `remote_only` | boolean | false | Include only candidates available for remote work |
| `experience_min` | integer | null | Minimum years of experience |
| `experience_max` | integer | null | Maximum years of experience |
| `skills_required` | string | null | Comma-separated list of additional required skills |
| `education_level` | string | null | Comma-separated list of education levels (e.g., "Bachelors,Masters") |
| `skills_proficiency_min` | integer | null | Minimum average skill proficiency level (1-10) |
| `include_applied` | boolean | false | Include candidates who have already applied to this project |
| `include_contacted` | boolean | false | Include candidates who have already been contacted for this project |
| `location` | string | null | Location to filter candidates by (city, state, country) |
| `location_radius` | integer | null | Radius in miles/km to search around the specified location |

## Response Format

```json
{
  "candidates": [
    {
      "candidate_id": "string",
      "match_score": 95.5,
      "explanation": "Candidate matches 90% of required skills and has relevant experience",
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
    "project_id": "project123",
    "project_title": "Mobile App Development Project",
    "project_type": "Mobile Application",
    "company": "Tech Solutions Inc.",
    "filters_applied": {
      "min_match_score": 80,
      "availability_min_hours": 15,
      "remote_only": true,
      "experience_min": 3,
      "experience_max": 10,
      "education_level": "Bachelors,Masters",
      "skills_required": "React Native,TypeScript",
      "skills_proficiency_min": 7,
      "include_applied": false,
      "include_contacted": false,
      "location": "San Francisco",
      "location_radius": 50
    },
    "statistics": {
      "average_match_score": 87.5,
      "skills_distribution": {
        "React Native": 8,
        "TypeScript": 7,
        "JavaScript": 10,
        "Redux": 6,
        "Node.js": 5
      },
      "query_time": "2023-05-15T14:32:10.123Z"
    }
  }
}
```

## Match Factors

The API calculates match factors to help explain why candidates match the project requirements:

- **Skills Match**: Percentage of required skills that the candidate possesses
- **Experience Match**: How well the candidate's experience matches the requirements

## Examples

### Basic Request

```
GET /recommendations/candidates-for-project/project123
```

### Advanced Request with Filters

```
GET /recommendations/candidates-for-project/project123?min_match_score=80&limit=20&include_details=true&sort_by=match_score&availability_min_hours=15&remote_only=true&experience_min=3&experience_max=10&education_level=Bachelors,Masters&skills_required=React%20Native,TypeScript&skills_proficiency_min=7&location=San%20Francisco&location_radius=50
```

### Alternative URL (Backward Compatibility)

```
GET /recommendations/project-candidates/project123?min_match_score=80&limit=20
```

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Bad request (e.g., invalid parameters) |
| 401 | Unauthorized (missing or invalid token) |
| 403 | Forbidden (non-employer users or not project owner) |
| 404 | Project not found |
| 500 | Server error |

## Notes

- The endpoint uses vector embeddings to calculate semantic similarity between project requirements and candidate profiles
- Match score is calculated based on skills, experience, and project requirements
- Candidates without embeddings will be matched using fallback text matching
- Location filtering currently uses simple text matching; future versions will implement proper geocoding
- Skills distribution statistics are only included when include_details=true
- Performance may vary based on the number of candidates in the database 