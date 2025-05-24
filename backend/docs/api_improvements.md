# Candidate Recommendations API Improvements

## Overview

The candidate recommendations API endpoint (`/recommendations/candidates/{job_id}`) has been enhanced with advanced filtering, sorting, and response formatting capabilities to provide more targeted and relevant candidate matches for specific job postings.

## Endpoint Details

- **URL**: `/recommendations/candidates/{job_id}`
- **Method**: `GET`
- **Authentication**: Required (JWT token)
- **Authorization**: Employer users only

## New Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_match_score` | integer | 0 | Minimum match score threshold (0-100) |
| `limit` | integer | 10 | Maximum number of results to return |
| `include_details` | boolean | true | Whether to include full candidate details |
| `sort_by` | string | "match_score" | Field to sort by (match_score, experience_years) |
| `experience_min` | integer | null | Minimum years of experience |
| `experience_max` | integer | null | Maximum years of experience |
| `location_radius` | integer | null | Distance in miles/km from job location |
| `include_remote` | boolean | false | Include candidates willing to work remotely |
| `education_level` | string | null | Comma-separated list of education levels (Bachelors,Masters,PhD) |
| `availability` | string | null | Comma-separated list of availability options (Immediate,2 weeks,1 month) |

## Response Format

The response format has been enhanced to include metadata about the search results:

```json
{
  "candidates": [
    {
      "candidate_id": "507f1f77bcf86cd799439011",
      "match_score": 85.5,
      "explanation": "Match score: 85.5. Matching skills: Python, JavaScript, React. Missing skills: GraphQL.",
      "candidate_details": {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "skills": [...],
        "experience": [...],
        "experience_years": "5",
        "education": [...],
        "education_summary": "Master's in Computer Science",
        "location": "New York, NY",
        "profile_summary": "Full-stack developer with 5 years of experience",
        "certifications": [...],
        "languages": [...],
        "preferred_job_type": "Full-time",
        "preferred_location": "New York",
        "preferred_salary": "$120,000",
        "job_search_status": {...}
      }
    },
    ...
  ],
  "total_count": 15,
  "filters_applied": {
    "min_match_score": 70,
    "experience_range": "3-10",
    "location_radius": 50,
    "include_remote": true,
    "education_level": "Bachelors,Masters",
    "availability": "Immediate,2 weeks"
  }
}
```

## Key Improvements

### 1. Advanced Filtering

- **Experience Range**: Filter candidates by minimum and maximum years of experience
- **Education Level**: Filter by education qualifications (Bachelors, Masters, PhD, etc.)
- **Availability**: Filter by candidate availability (immediate, 2 weeks notice, etc.)
- **Location**: Filter by proximity to job location and remote work preference

### 2. Customizable Results

- **Sorting Options**: Sort by match score or years of experience
- **Result Limiting**: Control the number of results returned
- **Detail Control**: Option to include or exclude detailed candidate information

### 3. Enhanced Response Format

- **Metadata**: Total count and applied filters included in response
- **Structured Data**: Consistent formatting of candidate details
- **Explanation**: Detailed explanation of match score calculation

## Example Usage

```
GET /recommendations/candidates/507f1f77bcf86cd799439011?min_match_score=80&limit=20&experience_min=3&experience_max=10&location_radius=50&include_remote=true&education_level=Bachelors,Masters&availability=Immediate,2%20weeks
```

## Implementation Notes

- Experience filtering uses regex pattern matching to extract numeric values from text fields
- Education filtering checks both structured education arrays and text summaries
- Location filtering uses simple string matching (in production, should use geocoding)
- Availability is determined from candidate's notice period or available date

## Future Enhancements

- Implement proper geocoding and distance calculation for location filtering
- Add more sorting options (location proximity, availability date, etc.)
- Support for skills-based filtering with minimum proficiency levels
- Pagination support for large result sets 